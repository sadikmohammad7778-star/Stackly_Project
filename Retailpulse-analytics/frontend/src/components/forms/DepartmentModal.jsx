import { useEffect, useState } from "react";
import {
  createDepartment,
  updateDepartment,
} from "../../api/departmentApi";
import "./DepartmentModal.css";

export default function DepartmentModal({
  isOpen,
  department,
  onClose,
  onSuccess,
}) {
  const initialForm = {
    company_id: "",
    department_name: "",
    description: "",
  };

  const [formData, setFormData] = useState(initialForm);
  const [loading, setLoading] = useState(false);

  const isEditMode = Boolean(department);

  useEffect(() => {
    if (department) {
      setFormData({
        company_id: department.company_id || "",
        department_name: department.department_name || "",
        description: department.description || "",
      });
    } else {
      setFormData(initialForm);
    }
  }, [department, isOpen]);

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
      if (isEditMode) {
        const departmentData = {
          company_id: Number(formData.company_id),
          department_name: formData.department_name,
          description: formData.description,
        };

        await updateDepartment(
          department.id,
          departmentData
        );

        alert("Department updated successfully.");
      } else {
        const departmentData = {
          company_id: Number(formData.company_id),
          department_name: formData.department_name,
          description: formData.description,
        };

        await createDepartment(departmentData);

        alert("Department created successfully.");
      }

      resetForm();
      await onSuccess();
      onClose();
    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        `Failed to ${
          isEditMode ? "update" : "create"
        } department.`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>
          {isEditMode
            ? "Edit Department"
            : "Add Department"}
        </h2>

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
            type="number"
            name="company_id"
            placeholder="Company ID"
            value={formData.company_id}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="description"
            placeholder="Description"
            value={formData.description}
            onChange={handleChange}
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
                ? "Saving..."
                : isEditMode
                ? "Update Department"
                : "Save Department"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}