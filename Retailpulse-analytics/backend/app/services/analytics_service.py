from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.attendance import Attendance


def get_overview(db: Session):
    total_companies = db.query(Company).count()
    total_departments = db.query(Department).count()
    total_employees = db.query(Employee).count()

    active_employees = (
        db.query(Employee)
        .filter(Employee.status == True)
        .count()
    )

    inactive_employees = (
        db.query(Employee)
        .filter(Employee.status == False)
        .count()
    )

    total_attendance = db.query(Attendance).count()

    return {
        "total_companies": total_companies,
        "total_departments": total_departments,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,
        "attendance_records": total_attendance,
    }


def employees_by_department(db: Session):
    return (
        db.query(
            Department.department_name,
            func.count(Employee.id).label("employees")
        )
        .join(
            Employee,
            Employee.department_id == Department.id
        )
        .group_by(Department.department_name)
        .all()
    )