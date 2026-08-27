import { useEffect, useState } from "react";
import { createEmployee } from "../../api/employeeApi";
import "./CompanyModal.css";

export default function EmployeeModal({
  isOpen,
  onClose,
  onSuccess,
}) {
  const initialForm = {
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    designation: "",
    salary: "",
    joining_date: "",
  };

  const [formData, setFormData] = useState(initialForm);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setFormData(initialForm);
    }
  }, [isOpen]);

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
      const employeeData = {
        ...formData,
        salary: Number(formData.salary),
      };

      await createEmployee(employeeData);

      alert("Employee created successfully.");

      setFormData(initialForm);
      onSuccess();
      onClose();

    } catch (error) {
      console.error("Create employee error:", error);

      alert(
        error.response?.data?.detail ||
        "Failed to create employee."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">

        <h2>Add Employee</h2>

        <form onSubmit={handleSubmit}>

          <input
            type="text"
            name="first_name"
            placeholder="First Name"
            value={formData.first_name}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="last_name"
            placeholder="Last Name"
            value={formData.last_name}
            onChange={handleChange}
            required
          />

          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="phone"
            placeholder="Phone"
            value={formData.phone}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="designation"
            placeholder="Designation"
            value={formData.designation}
            onChange={handleChange}
            required
          />

          <input
            type="number"
            name="salary"
            placeholder="Salary"
            value={formData.salary}
            onChange={handleChange}
            required
          />

          <input
            type="date"
            name="joining_date"
            value={formData.joining_date}
            onChange={handleChange}
            required
          />

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
              {loading ? "Saving..." : "Save Employee"}
            </button>

          </div>

        </form>

      </div>
    </div>
  );
}