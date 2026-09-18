import { useEffect, useState } from "react";

import {
  createAttendance,
  updateAttendance,
} from "../../api/attendanceApi";

import "./AttendanceModal.css";

export default function AttendanceModal({
  isOpen,
  onClose,
  onSuccess,
  employees = [],
  editAttendance = null,
}) {
  const initialForm = {
    employee_id: "",
    attendance_date: "",
    check_in: "",
    check_out: "",
    status: "Present",
  };

  const [formData, setFormData] = useState(initialForm);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setFormData(initialForm);
      return;
    }

    if (editAttendance) {
      setFormData({
        employee_id: editAttendance.employee_id,
        attendance_date: editAttendance.attendance_date,
        check_in: editAttendance.check_in
          ? editAttendance.check_in.substring(11, 16)
          : "",
        check_out: editAttendance.check_out
          ? editAttendance.check_out.substring(11, 16)
          : "",
        status: editAttendance.status,
      });
    } else {
      setFormData(initialForm);
    }
  }, [isOpen, editAttendance]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      const attendanceData = {
        attendance_date: formData.attendance_date,

        check_in: formData.check_in
          ? `${formData.attendance_date}T${formData.check_in}:00`
          : null,

        check_out: formData.check_out
          ? `${formData.attendance_date}T${formData.check_out}:00`
          : null,

        status: formData.status,
      };

      if (editAttendance) {
        await updateAttendance(
          editAttendance.id,
          attendanceData
        );

        alert("Attendance updated successfully.");
      } else {
        await createAttendance({
          employee_id: Number(formData.employee_id),
          ...attendanceData,
        });

        alert("Attendance marked successfully.");
      }

      setFormData(initialForm);
      onSuccess();
      onClose();

    } catch (error) {
      console.error("Attendance error:", error);

      alert(
        error.response?.data?.detail ||
        "Failed to save attendance."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">

      <div className="modal">

        <h2>
          {editAttendance
            ? "Edit Attendance"
            : "Mark Attendance"}
        </h2>

        <form onSubmit={handleSubmit}>

          <select
            name="employee_id"
            value={formData.employee_id}
            onChange={handleChange}
            disabled={!!editAttendance}
            required
          >
            <option value="">
              Select Employee
            </option>

            {employees.map((employee) => (
              <option
                key={employee.id}
                value={employee.id}
              >
                {employee.employee_code} -{" "}
                {employee.first_name}{" "}
                {employee.last_name}
              </option>
            ))}
          </select>

          <input
            type="date"
            name="attendance_date"
            value={formData.attendance_date}
            onChange={handleChange}
            required
          />

          <input
            type="time"
            name="check_in"
            value={formData.check_in}
            onChange={handleChange}
          />

          <input
            type="time"
            name="check_out"
            value={formData.check_out}
            onChange={handleChange}
          />

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option value="Present">Present</option>
            <option value="Absent">Absent</option>
            <option value="Leave">Leave</option>
          </select>

          <div className="modal-buttons">

            <button
              type="button"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Saving..."
                : editAttendance
                  ? "Update"
                  : "Save"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}