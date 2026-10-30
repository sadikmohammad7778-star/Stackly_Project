from getpass import getpass

from app.config.database import SessionLocal
from app.models.user import User
from app.security.hashing import hash_password


def reset_employee_password():
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == 10)
            .first()
        )

        if not user:
            print("Employee user ID 10 was not found.")
            return

        print(f"Employee email: {user.email}")
        print(f"Current role: {user.role}")

        new_password = input("Enter new password: ")
        confirm_password = input("Confirm new password: ")

        if len(new_password) < 8:
            print("Password must contain at least 8 characters.")
            return

        if new_password != confirm_password:
            print("Passwords do not match.")
            return

        user.password = hash_password(new_password)

        db.commit()

        print("Employee password reset successfully.")

    except Exception as error:
        db.rollback()
        print(f"Password reset failed: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    reset_employee_password()