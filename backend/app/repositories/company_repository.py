from app.models.company import Company

class CompanyRepository:

    @staticmethod
    def get_by_email(db, email):

        return db.query(Company).filter(
            Company.email == email
        ).first()

    @staticmethod
    def create(db, company):

        db.add(company)

        db.commit()

        db.refresh(company)

        return company