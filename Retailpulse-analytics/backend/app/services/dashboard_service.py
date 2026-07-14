from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.user import User
from app.models.employee import Employee
from app.models.department import Department


def get_dashboard_summary(db: Session):
    return {
        "total_companies": db.query(Company).count(),
        "total_users": db.query(User).count(),
        "total_employees": db.query(Employee).count(),
        "total_departments": db.query(Department).count(),
        "active_employees": db.query(Employee).filter(Employee.status == True).count(),
        "inactive_employees": db.query(Employee).filter(Employee.status == False).count(),
    }