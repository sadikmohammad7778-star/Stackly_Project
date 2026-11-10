import requests

from urllib.parse import urlparse, urljoin
from fastapi import HTTPException

from app.services.credential_encryption import decrypt_credentials


def _get_nested_value(data, path):
    if not path:
        return data

    value = data

    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None

        value = value[key]

    return value


def _extract_records(payload, response_data_path):
    records = _get_nested_value(payload, response_data_path)

    if not isinstance(records, list):
        raise HTTPException(
            status_code=502,
            detail="REST API response must contain a list of records."
        )

    if not all(isinstance(record, dict) for record in records):
        raise HTTPException(
            status_code=502,
            detail="REST API returned invalid record structure."
        )

    return records


def _validate_response(response):
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else 502
        )

        raise HTTPException(
            status_code=502,
            detail=f"External REST API returned HTTP {status_code}."
        )

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="REST API returned invalid JSON."
        )


def fetch_rest_api_records(integration):
    if integration.source_type != "rest_api":
        raise HTTPException(
            status_code=400,
            detail="This service supports REST API integrations only."
        )

    config = integration.connection_config or {}

    base_url = config.get("base_url")
    endpoint = config.get("data_endpoint")

    if not base_url or not endpoint:
        raise HTTPException(
            status_code=400,
            detail="REST API base URL and data endpoint are required."
        )

    parsed_base = urlparse(base_url)

    if (
        parsed_base.scheme not in {"https", "http"}
        or not parsed_base.hostname
        or parsed_base.username
        or parsed_base.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid REST API base URL."
        )

    if (
        not isinstance(endpoint, str)
        or endpoint.startswith("//")
        or "://" in endpoint
        or "\\" in endpoint
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid REST API endpoint."
        )

    request_url = urljoin(
        base_url.rstrip("/") + "/",
        endpoint.lstrip("/")
    )

    parsed_request = urlparse(request_url)

    if (
        parsed_request.scheme != parsed_base.scheme
        or parsed_request.hostname != parsed_base.hostname
        or parsed_request.port != parsed_base.port
    ):
        raise HTTPException(
            status_code=400,
            detail="API endpoint must belong to the configured host."
        )

    auth_type = config.get("auth_type", "none")

    headers = {
        "Accept": "application/json"
    }

    if auth_type == "none":
        pass

    elif auth_type in {"bearer", "api_key"}:
        if not integration.encrypted_credentials:
            raise HTTPException(
                status_code=400,
                detail="REST API credentials are not configured."
            )

        credentials = decrypt_credentials(
            integration.encrypted_credentials
        )

        if auth_type == "bearer":
            token = credentials.get("access_token")

            if not token:
                raise HTTPException(
                    status_code=400,
                    detail="Bearer access token is missing."
                )

            headers["Authorization"] = f"Bearer {token}"

        elif auth_type == "api_key":
            api_key = credentials.get("api_key")

            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail="API key is missing."
                )

            header_name = config.get(
                "api_key_header",
                "X-API-Key"
            )

            if (
                not isinstance(header_name, str)
                or not header_name.isascii()
                or "\r" in header_name
                or "\n" in header_name
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid API key header."
                )

            headers[header_name] = api_key

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported REST API authentication type."
        )

    pagination = config.get("pagination") or {}
    pagination_type = pagination.get("type", "none")

    if pagination_type not in {"none", "offset", "page"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported pagination type."
        )

    try:
        if pagination_type == "none":
            response = requests.get(
                request_url,
                headers=headers,
                timeout=(5, 30),
                allow_redirects=False,
            )

            payload = _validate_response(response)

            return _extract_records(
                payload,
                config.get("response_data_path")
            )

        page_size = pagination.get("page_size", 30)
        max_pages = pagination.get("max_pages", 100)

        if (
            not isinstance(page_size, int)
            or isinstance(page_size, bool)
            or page_size < 1
            or page_size > 500
        ):
            raise HTTPException(
                status_code=400,
                detail="Pagination page size must be between 1 and 500."
            )

        if (
            not isinstance(max_pages, int)
            or isinstance(max_pages, bool)
            or max_pages < 1
            or max_pages > 1000
        ):
            raise HTTPException(
                status_code=400,
                detail="Maximum pagination pages must be between 1 and 1000."
            )

        limit_param = pagination.get("limit_param", "limit")

        if (
            not isinstance(limit_param, str)
            or not limit_param
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid pagination limit parameter."
            )

        if pagination_type == "offset":
            offset_param = pagination.get("offset_param", "skip")

            if (
                not isinstance(offset_param, str)
                or not offset_param
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid pagination offset parameter."
                )

        else:
            page_param = pagination.get("page_param", "page")
            start_page = pagination.get("start_page", 1)

            if (
                not isinstance(page_param, str)
                or not page_param
                or not isinstance(start_page, int)
                or isinstance(start_page, bool)
                or start_page < 0
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid page pagination configuration."
                )

        all_records = []
        total_records = None

        for page_index in range(max_pages):
            params = {
                limit_param: page_size
            }

            if pagination_type == "offset":
                params[offset_param] = page_index * page_size
            else:
                params[page_param] = start_page + page_index

            response = requests.get(
                request_url,
                headers=headers,
                params=params,
                timeout=(5, 30),
                allow_redirects=False,
            )

            payload = _validate_response(response)

            records = _extract_records(
                payload,
                config.get("response_data_path")
            )

            all_records.extend(records)

            if total_records is None:
                total_path = pagination.get("total_path")

                if total_path:
                    total_value = _get_nested_value(
                        payload,
                        total_path
                    )

                    if total_value is not None:
                        try:
                            total_records = int(total_value)
                        except (TypeError, ValueError):
                            raise HTTPException(
                                status_code=502,
                                detail="Invalid total records value in API response."
                            )

            if not records:
                break

            if (
                total_records is not None
                and len(all_records) >= total_records
            ):
                break

            if len(records) < page_size:
                break

        else:
            raise HTTPException(
                status_code=502,
                detail="Maximum pagination page limit reached."
            )

        return all_records

    except HTTPException:
        raise

    except requests.Timeout:
        raise HTTPException(
            status_code=504,
            detail="REST API request timed out."
        )

    except requests.HTTPError as exc:
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else 502
        )

        raise HTTPException(
            status_code=502,
            detail=f"External REST API returned HTTP {status_code}."
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to the external REST API."
        )