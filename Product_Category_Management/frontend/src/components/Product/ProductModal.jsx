import { useState, useEffect } from "react";
import {
  createProduct,
  updateProduct,
} from "../../services/productService";
import "./ProductModal.css";
import { toast } from "react-toastify";

function ProductModal({ isOpen, onClose, onSuccess, product }) {

  const [formData, setFormData] = useState({
    company_id: 1,
    category_id: "",
    name: "",
    sku: "",
    brand: "",
    description: "",
    unit_price: "",
    cost_price: "",
    stock_quantity: "",
    unit_of_measure: "",
    status: "Active",
  });

  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    if (product) {
      setFormData(product);
    } else {
      setFormData({
        company_id: 1,
        category_id: "",
        name: "",
        sku: "",
        brand: "",
        description: "",
        unit_price: "",
        cost_price: "",
        stock_quantity: "",
        unit_of_measure: "",
        status: "Active",
      });
    }
  }, [product]);

  const loadCategories = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/categories"
      );
      setCategories(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {

        if (product) {

        await updateProduct(
            product.id,
            formData
        );

        toast.success("Product updated successfully.");

        } else {

        await createProduct(formData);

        toast.success("Product created successfully.");

        }

        onSuccess();
        onClose();

    } catch (error) {

        console.error(error);

        toast.error("Failed to save product.");

    }
   };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">

      <div className="product-modal">

        <h2>
          {product ? "Edit Product" : "Add Product"}
        </h2>

        <form onSubmit={handleSubmit}>

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

          <select
            name="category_id"
            value={formData.category_id}
            onChange={handleChange}
            required
          >
            <option value="">Select Category</option>

            {categories.map((category) => (
              <option
                key={category.id}
                value={category.id}
              >
                {category.name}
              </option>
            ))}

          </select>

          <input
            type="text"
            name="brand"
            placeholder="Brand"
            value={formData.brand}
            onChange={handleChange}
          />

          <textarea
            name="description"
            placeholder="Description"
            value={formData.description}
            onChange={handleChange}
          />

          <input
            type="number"
            name="unit_price"
            placeholder="Unit Price"
            value={formData.unit_price}
            onChange={handleChange}
          />

          <input
            type="number"
            name="cost_price"
            placeholder="Cost Price"
            value={formData.cost_price}
            onChange={handleChange}
          />

          <input
            type="number"
            name="stock_quantity"
            placeholder="Stock Quantity"
            value={formData.stock_quantity}
            onChange={handleChange}
          />

          <input
            type="text"
            name="unit_of_measure"
            placeholder="Unit of Measure"
            value={formData.unit_of_measure}
            onChange={handleChange}
          />

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option value="Active">Active</option>
            <option value="Inactive">Inactive</option>
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

export default ProductModal;