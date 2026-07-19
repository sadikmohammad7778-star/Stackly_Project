import { useState } from "react";
import { createCategory } from "../../api/categoryApi";
import "./CompanyModal.css";

export default function CategoryModal({
  isOpen,
  onClose,
  onSuccess,
}) {
  const initialForm = {
    company_id: "",
    name: "",
    description: "",
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

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      await createCategory({
        ...formData,
        company_id: Number(formData.company_id),
      });

      alert("Category created successfully.");

      resetForm();

      onSuccess();

      onClose();

    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Failed to create category."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">

      <div className="modal">

        <h2>Add Category</h2>

        <form onSubmit={handleSubmit}>

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
            name="name"
            placeholder="Category Name"
            value={formData.name}
            onChange={handleChange}
            required
          />

          <textarea
            name="description"
            placeholder="Description"
            value={formData.description}
            onChange={handleChange}
          />

          <div className="modal-buttons">

            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save Category"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}