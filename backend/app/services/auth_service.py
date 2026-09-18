from app.utils.hash import hash_password, verify_password


class AuthService:

    @staticmethod
    def encrypt_password(password: str):
        return hash_password(password)

    @staticmethod
    def check_password(plain_password: str, hashed_password: str):
        return verify_password(
            plain_password,
            hashed_password
        )