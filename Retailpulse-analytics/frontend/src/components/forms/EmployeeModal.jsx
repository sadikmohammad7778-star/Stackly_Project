import { useState } from "react";
import { createEmployee } from "../../api/employeeApi";
import "./CompanyModal.css";

export default function EmployeeModal({
  isOpen,
  onClose,
  onSuccess,
}) {
  const initialData = {
    company_id: "",
    employee_code: "",
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    designation: "",
    salary: "",
    joining_date: "",
  };

  const [formData, setFormData] = useState(initialData);

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await createEmployee(formData);

      alert("Employee created successfully");

      onSuccess();

      onClose();

      setFormData(initialData);

    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="modal-overlay">

      <div className="modal">

        <h2>Add Employee</h2>

        <form onSubmit={handleSubmit}>

          <input
            name="company_id"
            placeholder="Company ID"
            onChange={handleChange}
            required
          />

          <input
            name="employee_code"
            placeholder="Employee Code"
            onChange={handleChange}
            required
          />

          <input
            name="first_name"
            placeholder="First Name"
            onChange={handleChange}
            required
          />

          <input
            name="last_name"
            placeholder="Last Name"
            onChange={handleChange}
            required
          />

          <input
            type="email"
            name="email"
            placeholder="Email"
            onChange={handleChange}
            required
          />

          <input
            name="phone"
            placeholder="Phone"
            onChange={handleChange}
            required
          />

          <input
            name="designation"
            placeholder="Designation"
            onChange={handleChange}
            required
          />

          <input
            type="number"
            name="salary"
            placeholder="Salary"
            onChange={handleChange}
            required
          />

          <input
            type="date"
            name="joining_date"
            onChange={handleChange}
            required
          />

          <div className="modal-buttons">

            <button
              type="button"
              onClick={onClose}
            >
              Cancel
            </button>

            <button type="submit">
              Save Employee
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}