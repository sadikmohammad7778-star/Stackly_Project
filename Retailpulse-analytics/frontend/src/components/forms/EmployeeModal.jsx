import { useEffect, useState } from "react";
import {
  createEmployee,
  updateEmployee,
} from "../../api/employeeApi";
import "./CompanyModal.css";

export default function EmployeeModal({
  isOpen,
  employee,
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

  const isEditMode = Boolean(employee);

  useEffect(() => {
    if (!isOpen) {
      setFormData(initialForm);
      return;
    }

    if (employee) {
      setFormData({
        first_name: employee.first_name || "",
        last_name: employee.last_name || "",
        email: employee.email || "",
        phone: employee.phone || "",
        designation: employee.designation || "",
        salary: employee.salary ?? "",
        joining_date: employee.joining_date
          ? employee.joining_date.split("T")[0]
          : "",
      });
    } else {
      setFormData(initialForm);
    }
  }, [isOpen, employee]);

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
      if (isEditMode) {
        const employeeData = {
          company_id: employee.company_id,
          employee_code: employee.employee_code,
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          phone: formData.phone,
          designation: formData.designation,
          salary: Number(formData.salary),
          joining_date: formData.joining_date,
          status: employee.status,
        };

        await updateEmployee(employee.id, employeeData);

        alert("Employee updated successfully.");
      } else {
        const employeeData = {
          ...formData,
          salary: Number(formData.salary),
        };

        await createEmployee(employeeData);

        alert("Employee created successfully.");
      }

      setFormData(initialForm);
      onSuccess();
      onClose();
    } catch (error) {
      console.error(
        isEditMode
          ? "Update employee error:"
          : "Create employee error:",
        error
      );

      const detail = error.response?.data?.detail;

      const message = Array.isArray(detail)
        ? detail
            .map((item) => {
              const field = item.loc?.slice(-1)[0] || "field";
              return `${field}: ${item.msg}`;
            })
            .join("\n")
        : detail ||
          (isEditMode
            ? "Failed to update employee."
            : "Failed to create employee.");

      alert(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">

        <h2>
          {isEditMode ? "Edit Employee" : "Add Employee"}
        </h2>

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
              {loading
                ? isEditMode
                  ? "Updating..."
                  : "Saving..."
                : isEditMode
                ? "Update Employee"
                : "Save Employee"}
            </button>

          </div>

        </form>

      </div>
    </div>
  );
}