from app.config.database import SessionLocal
from app.models.integration import Integration
from app.services.integration_rest_service import fetch_rest_api_records

db = SessionLocal()

try:
    integration = (
        db.query(Integration)
        .filter(
            Integration.id == 4,
            Integration.company_id == 3
        )
        .first()
    )

    if not integration:
        raise ValueError("Integration not found")

    records = fetch_rest_api_records(integration)

    print("Total records fetched:", len(records))
    print("First record:", records[0] if records else None)

finally:
    db.close()