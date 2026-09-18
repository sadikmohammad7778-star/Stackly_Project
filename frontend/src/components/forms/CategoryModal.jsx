import { useEffect, useState } from "react";
import {
  createCategory,
  updateCategory,
} from "../../api/categoryApi";
import "./CompanyModal.css";

export default function CategoryModal({
  isOpen,
  onClose,
  onSuccess,
  category,
}) {
  const initialForm = {
    company_id: "",
    name: "",
    description: "",
  };

  const [formData, setFormData] = useState(initialForm);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (category) {
      setFormData({
        company_id: category.company_id || "",
        name: category.name || "",
        description: category.description || "",
      });
    } else {
      setFormData(initialForm);
    }
  }, [category, isOpen]);

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
      const payload = {
        ...formData,
        company_id: Number(formData.company_id),
      };

      if (category) {
        await updateCategory(category.id, payload);
        alert("Category updated successfully.");
      } else {
        await createCategory(payload);
        alert("Category created successfully.");
      }

      resetForm();
      onSuccess();
      onClose();

    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        (category
          ? "Failed to update category."
          : "Failed to create category.")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">

        <h2>
          {category ? "Edit Category" : "Add Category"}
        </h2>

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
              {loading
                ? "Saving..."
                : category
                ? "Update Category"
                : "Save Category"}
            </button>

          </div>

        </form>

      </div>
    </div>
  );
}