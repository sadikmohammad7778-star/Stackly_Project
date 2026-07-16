import { useState, useEffect } from "react";
import {
  createCategory,
  updateCategory,
} from "../../services/categoryService";
import "./CategoryModal.css";
import { toast } from "react-toastify";

function CategoryModal({ isOpen, onClose, onSuccess, category }) {
  const [formData, setFormData] = useState({
    company_id: 1,
    name: "",
    description: "",
    status: "Active",
  });

  useEffect(() => {
    if (category) {
      setFormData(category);
    } else {
      setFormData({
        company_id: 1,
        name: "",
        description: "",
        status: "Active",
      });
    }
  }, [category]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {

        if (category) {

        await updateCategory(
            category.id,
            formData
        );

        toast.success("Category updated successfully.");

        } else {

        await createCategory(formData);

        toast.success("Category created successfully.");

        }

        onSuccess();
        onClose();

    } catch (error) {

        console.error(error);

        toast.error("Failed to save category.");

    }
   };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">

        <h2>{category ? "Edit Category" : "Add Category"}</h2>

        <form onSubmit={handleSubmit}>

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

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option>Active</option>
            <option>Inactive</option>
          </select>

          <div className="modal-buttons">
            <button type="submit">
              Save
            </button>

            <button
              type="button"
              className="cancel-btn"
              onClick={onClose}
            >
              Cancel
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}

export default CategoryModal;