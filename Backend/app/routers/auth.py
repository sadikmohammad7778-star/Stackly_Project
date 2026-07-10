from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login(data: dict):

    if data["email"] == "admin@gmail.com" and data["password"] == "admin123":
        return {
            "success": True,
            "message": "Login Successful"
        }

    return {
        "success": False,
        "message": "Invalid Email or Password"
    }