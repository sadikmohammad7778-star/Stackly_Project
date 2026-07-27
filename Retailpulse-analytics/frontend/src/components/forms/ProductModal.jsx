import { useState } from "react";
import { createProduct } from "../../api/productApi";
import "./CompanyModal.css";

export default function ProductModal({
  isOpen,
  onClose,
  onSuccess,
}) {
  const initialForm = {
    company_id: "",
    category_id: "",
    name: "",
    description: "",
    brand: "",
    unit_price: "",
    stock_quantity: "",
    status: "In Stock",
    is_active: true,
  };

  const [formData, setFormData] = useState(initialForm);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
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
      await createProduct({
        ...formData,
        company_id: Number(formData.company_id),
        category_id: Number(formData.category_id),
        unit_price: Number(formData.unit_price),
        stock_quantity: Number(formData.stock_quantity),
      });

      alert("Product created successfully.");

      resetForm();
      onSuccess();
      onClose();

    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Failed to create product."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">

        <h2>Add Product</h2>

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
            type="number"
            name="category_id"
            placeholder="Category ID"
            value={formData.category_id}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="name"
            placeholder="Product Name"
            value={formData.name}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="brand"
            placeholder="Brand"
            value={formData.brand}
            onChange={handleChange}
            required
          />

          <textarea
            name="description"
            placeholder="Description"
            value={formData.description}
            onChange={handleChange}
          />

          <input
            type="number"
            step="0.01"
            name="unit_price"
            placeholder="Unit Price"
            value={formData.unit_price}
            onChange={handleChange}
            required
          />

          <input
            type="number"
            name="stock_quantity"
            placeholder="Stock Quantity"
            value={formData.stock_quantity}
            onChange={handleChange}
            required
          />

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option value="In Stock">In Stock</option>
            <option value="Low Stock">Low Stock</option>
            <option value="Out of Stock">Out of Stock</option>
          </select>

          <label className="checkbox-label">
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
            />
            Active
          </label>

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
              {loading ? "Saving..." : "Save Product"}
            </button>

          </div>

        </form>

      </div>
    </div>
  );
}