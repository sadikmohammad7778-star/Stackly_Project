import { useState } from "react";
import { createDepartment } from "../../api/departmentApi";
import "./DepartmentModal.css";

export default function DepartmentModal({
  isOpen,
  onClose,
  onSuccess,
}) {
  const initialForm = {
    department_name: "",
    manager_name: "",
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
      await createDepartment(formData);

      alert("Department created successfully.");

      resetForm();

      onSuccess();

      onClose();

    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Failed to create department."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">

      <div className="modal">

        <h2>Add Department</h2>

        <form onSubmit={handleSubmit}>

          <input
            type="text"
            name="department_name"
            placeholder="Department Name"
            value={formData.department_name}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="manager_name"
            placeholder="Manager Name"
            value={formData.manager_name}
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
              {loading ? "Saving..." : "Save Department"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}