from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/")
def health():
    return {
        "status": "OK",
        "application": "RetailPulse Analytics",
        "version": "1.0.0",
    }