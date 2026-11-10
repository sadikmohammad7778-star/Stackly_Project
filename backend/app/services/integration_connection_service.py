from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

import requests

from urllib.parse import urlparse

from app.models.integration import Integration
from app.services.credential_encryption import decrypt_credentials
from app.services.integration_service import get_integration_by_id


def test_postgresql_connection(
    db,
    integration_id: int,
    company_id: int,
):
    integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    if integration.source_type != "postgresql":
        raise HTTPException(
            status_code=400,
            detail="Connection testing is currently supported only for PostgreSQL integrations.",
        )

    if not integration.encrypted_credentials:
        raise HTTPException(
            status_code=400,
            detail="Integration credentials are not configured.",
        )

    config = integration.connection_config or {}

    required_fields = ["host", "port", "database"]

    missing_fields = [
        field for field in required_fields
        if config.get(field) is None
    ]

    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "PostgreSQL connection configuration is incomplete.",
                "missing_fields": missing_fields,
            },
        )

    credentials = decrypt_credentials(
        integration.encrypted_credentials
    )

    username = credentials.get("username")
    password = credentials.get("password")

    if not username or password is None:
        raise HTTPException(
            status_code=400,
            detail="PostgreSQL username and password are required.",
        )

    engine = None

    try:
        connection_url = URL.create(
            drivername="postgresql+psycopg2",
            username=username,
            password=password,
            host=config["host"],
            port=int(config["port"]),
            database=config["database"],
        )

        engine = create_engine(
            connection_url,
            connect_args={"connect_timeout": 5},
            pool_pre_ping=True,
        )

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        integration.status = "connected"
        db.commit()

        return {
            "integration_id": integration.id,
            "status": "success",
            "message": "PostgreSQL connection established successfully.",
        }

    except (SQLAlchemyError, ValueError, TypeError):
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to establish PostgreSQL connection. Verify the connection configuration and credentials.",
        )

    finally:
        if engine:
            engine.dispose()



def test_rest_api_connection(
    db,
    integration_id: int,
    company_id: int,
):
    integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    if integration.source_type != "rest_api":
        raise HTTPException(
            status_code=400,
            detail="This integration is not a REST API connector.",
        )

    config = integration.connection_config or {}
    base_url = config.get("base_url")

    if not base_url:
        raise HTTPException(
            status_code=400,
            detail="REST API base URL is required.",
        )

    parsed_url = urlparse(base_url)

    if (
        parsed_url.scheme not in ("http", "https")
        or not parsed_url.hostname
        or parsed_url.username
        or parsed_url.password
    ):
        raise HTTPException(
            status_code=400,
            detail="A valid HTTP or HTTPS base URL is required.",
        )

    auth_type = config.get("auth_type", "none")

    headers = {
        "Accept": "application/json",
    }

    if auth_type == "none":
        pass

    elif auth_type in {"bearer", "api_key"}:
        if not integration.encrypted_credentials:
            raise HTTPException(
                status_code=400,
                detail="REST API credentials are not configured.",
            )

        credentials = decrypt_credentials(
            integration.encrypted_credentials
        )

        if auth_type == "bearer":
            token = credentials.get("access_token")

            if not token:
                raise HTTPException(
                    status_code=400,
                    detail="Bearer access token is required.",
                )

            headers["Authorization"] = f"Bearer {token}"

        elif auth_type == "api_key":
            api_key = credentials.get("api_key")

            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail="API key is required.",
                )

            header_name = config.get(
                "api_key_header",
                "X-API-Key",
            )

            if (
                not isinstance(header_name, str)
                or not header_name
                or not header_name.isascii()
                or "\r" in header_name
                or "\n" in header_name
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid API key header name.",
                )

            headers[header_name] = api_key

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported REST API authentication type.",
        )

    test_endpoint = config.get("test_endpoint", "")

    if (
        not isinstance(test_endpoint, str)
        or test_endpoint.startswith("//")
        or "://" in test_endpoint
        or "\\" in test_endpoint
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid REST API test endpoint.",
        )

    from urllib.parse import urljoin

    test_url = urljoin(
        base_url.rstrip("/") + "/",
        test_endpoint.lstrip("/"),
    )

    parsed_test_url = urlparse(test_url)

    if (
        parsed_test_url.scheme != parsed_url.scheme
        or parsed_test_url.hostname != parsed_url.hostname
        or parsed_test_url.port != parsed_url.port
    ):
        raise HTTPException(
            status_code=400,
            detail="Test endpoint must belong to the configured API host.",
        )

    try:
        response = requests.get(
            test_url,
            headers=headers,
            timeout=(5, 10),
            allow_redirects=False,
        )

        if response.status_code in (401, 403):
            raise HTTPException(
                status_code=400,
                detail="REST API authentication failed.",
            )

        if not 200 <= response.status_code < 300:
            raise HTTPException(
                status_code=400,
                detail=f"REST API returned HTTP {response.status_code}.",
            )

        integration.status = "connected"
        db.commit()

        return {
            "integration_id": integration.id,
            "status": "success",
            "message": "REST API connection established successfully.",
        }

    except HTTPException:
        db.rollback()
        raise

    except requests.Timeout:
        db.rollback()
        raise HTTPException(
            status_code=504,
            detail="REST API connection timed out.",
        )

    except requests.RequestException:
        db.rollback()
        raise HTTPException(
            status_code=502,
            detail="Unable to reach the REST API. Verify the endpoint and network configuration.",
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="REST API connection test failed.",
        )