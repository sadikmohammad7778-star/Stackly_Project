import { useState } from "react";
import { createAttendance } from "../../api/attendanceApi";
import "./AttendanceModal.css";

export default function AttendanceModal({
  isOpen,
  onClose,
  onSuccess,
}) {

  const initialForm = {
    employee_name: "",
    date: "",
    check_in: "",
    check_out: "",
    status: "Present",
  };

  const [formData, setFormData] = useState(initialForm);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleChange = (e) => {

    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

  };

  const resetForm = () => {
    setFormData(initialForm);
  };

  const handleSubmit = async (e) => {

    e.preventDefault();

    setLoading(true);

    try {

      await createAttendance(formData);

      alert("Attendance marked successfully.");

      resetForm();

      onSuccess();

      onClose();

    } catch (error) {

      console.error(error);

      alert("Failed to mark attendance.");

    } finally {

      setLoading(false);

    }

  };

  return (

    <div className="modal-overlay">

      <div className="modal">

        <h2>Mark Attendance</h2>

        <form onSubmit={handleSubmit}>

          <input
            type="text"
            name="employee_name"
            placeholder="Employee Name"
            value={formData.employee_name}
            onChange={handleChange}
            required
          />

          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            required
          />

          <input
            type="time"
            name="check_in"
            value={formData.check_in}
            onChange={handleChange}
            required
          />

          <input
            type="time"
            name="check_out"
            value={formData.check_out}
            onChange={handleChange}
            required
          />

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option>Present</option>
            <option>Absent</option>
            <option>Leave</option>
          </select>

          <div className="modal-buttons">

            <button
              type="button"
              onClick={onClose}
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save"}
            </button>

          </div>

        </form>

      </div>

    </div>

  );

}