from app.models.user import User


class UserRepository:

    @staticmethod
    def get_by_email(db, email):

        return db.query(User).filter(
            User.email == email
        ).first()

    @staticmethod
    def create(db, user):

        db.add(user)

        db.commit()

        db.refresh(user)

        return user