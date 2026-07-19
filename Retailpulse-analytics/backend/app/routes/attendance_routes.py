from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependency import get_db

from app.schemas.attendance_schema import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
)

from app.services.attendance_service import (
    create_attendance,
    get_all_attendance,
    get_attendance_by_id,
    update_attendance,
    delete_attendance,
)

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)


@router.post("/", response_model=AttendanceResponse)
def create_attendance_api(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db),
):
    return create_attendance(db, attendance)


@router.get("/", response_model=list[AttendanceResponse])
def get_attendance(
    db: Session = Depends(get_db),
):
    return get_all_attendance(db)


@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance_by_id_api(
    attendance_id: int,
    db: Session = Depends(get_db),
):
    return get_attendance_by_id(db, attendance_id)


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance_api(
    attendance_id: int,
    attendance: AttendanceUpdate,
    db: Session = Depends(get_db),
):
    return update_attendance(db, attendance_id, attendance)


@router.delete("/{attendance_id}")
def delete_attendance_api(
    attendance_id: int,
    db: Session = Depends(get_db),
):
    return delete_attendance(db, attendance_id)