from app.services.company_service import CompanyService

class CompanyController:

    @staticmethod
    def register(db, data):

        if data.password != data.confirm_password:
            return {
                "success": False,
                "message": "Passwords do not match"
            }

        if len(data.password) < 8:
            return {
                "success": False,
                "message": "Password must be at least 8 characters"
            }

        return CompanyService.register_company(
            db,
            data
        )