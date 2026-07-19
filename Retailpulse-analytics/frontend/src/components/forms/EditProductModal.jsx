import { useEffect, useState } from "react";
import { updateProduct } from "../../api/productApi";
import "./CompanyModal.css";

export default function EditProductModal({
  isOpen,
  onClose,
  onSuccess,
  product,
}) {
  const [formData, setFormData] = useState({
    company_id: "",
    category_id: "",
    name: "",
    sku: "",
    description: "",
    unit_price: "",
    stock_quantity: "",
    status: "In Stock",
    is_active: true,
  });

  useEffect(() => {
    if (product) {
      setFormData({
        company_id: product.company_id,
        category_id: product.category_id,
        name: product.name,
        sku: product.sku,
        description: product.description || "",
        unit_price: product.unit_price,
        stock_quantity: product.stock_quantity,
        status: product.status,
        is_active: product.is_active,
      });
    }
  }, [product]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await updateProduct(product.id, {
        ...formData,
        company_id: Number(formData.company_id),
        category_id: Number(formData.category_id),
        unit_price: Number(formData.unit_price),
        stock_quantity: Number(formData.stock_quantity),
      });

      alert("Product updated successfully.");

      onSuccess();
      onClose();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Failed to update product.");
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">

        <h2>Edit Product</h2>

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
            name="sku"
            placeholder="SKU"
            value={formData.sku}
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

          <div className="modal-buttons">
            <button type="button" onClick={onClose}>
              Cancel
            </button>

            <button type="submit">
              Update Product
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}