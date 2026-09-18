from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.employee import Employee
from app.schemas.attendance_schema import (
    AttendanceCreate,
    AttendanceUpdate,
)
from app.services.audit_service import create_audit_log


def create_attendance(
    db: Session,
    attendance: AttendanceCreate,
    user_id: int,
    company_id: int,
):
    employee = (
        db.query(Employee)
        .filter(
            Employee.id == attendance.employee_id,
            Employee.company_id == company_id,
        )
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    new_attendance = Attendance(
        **attendance.model_dump()
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Attendance",
        action="CREATE",
        description=(
            f"Created attendance record "
            f"for employee ID {employee.id} "
            f"on {attendance.attendance_date}"
        ),
    )

    return new_attendance


def get_all_attendance(
    db: Session,
    company_id: int,
):
    return (
        db.query(Attendance)
        .join(Employee)
        .filter(Employee.company_id == company_id)
        .all()
    )


def get_attendance_by_id(
    db: Session,
    attendance_id: int,
    company_id: int,
):
    attendance = (
        db.query(Attendance)
        .join(Employee)
        .filter(
            Attendance.id == attendance_id,
            Employee.company_id == company_id,
        )
        .first()
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found."
        )

    return attendance


def update_attendance(
    db: Session,
    attendance_id: int,
    attendance: AttendanceUpdate,
    user_id: int,
    company_id: int,
):
    existing = (
        db.query(Attendance)
        .join(Employee)
        .filter(
            Attendance.id == attendance_id,
            Employee.company_id == company_id,
        )
        .first()
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found."
        )

    for key, value in attendance.model_dump(
        exclude_unset=True
    ).items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Attendance",
        action="UPDATE",
        description=(
            f"Updated attendance record "
            f"for employee ID {existing.employee_id} "
            f"on {existing.attendance_date}"
        ),
    )

    return existing


def delete_attendance(
    db: Session,
    attendance_id: int,
    user_id: int,
    company_id: int,
):
    attendance = (
        db.query(Attendance)
        .join(Employee)
        .filter(
            Attendance.id == attendance_id,
            Employee.company_id == company_id,
        )
        .first()
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found."
        )

    employee_id = attendance.employee_id
    attendance_date = attendance.attendance_date

    db.delete(attendance)
    db.commit()

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Attendance",
        action="DELETE",
        description=(
            f"Deleted attendance record "
            f"for employee ID {employee_id} "
            f"on {attendance_date}"
        ),
    )

    return {
        "message": "Attendance deleted successfully."
    }