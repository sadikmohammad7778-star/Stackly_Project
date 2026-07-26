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
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == attendance.employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    new_attendance = Attendance(**attendance.model_dump())

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        module="Attendance",
    )

    return new_attendance

def get_all_attendance(db: Session):
    return db.query(Attendance).all()


def get_attendance_by_id(
    db: Session,
    attendance_id: int
):
    attendance = (
        db.query(Attendance)
        .filter(Attendance.id == attendance_id)
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
):
    existing = (
        db.query(Attendance)
        .filter(Attendance.id == attendance_id)
        .first()
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found."
        )

    for key, value in attendance.model_dump(exclude_unset=True).items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        module="Attendance",
    )

    return existing


def delete_attendance(
    db: Session,
    attendance_id: int,
    user_id: int,
):
    attendance = (
        db.query(Attendance)
        .filter(Attendance.id == attendance_id)
        .first()
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found."
        )

    db.delete(attendance)
    db.commit()

    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        module="Attendance",
    )

    return {
        "message": "Attendance deleted successfully."
    }