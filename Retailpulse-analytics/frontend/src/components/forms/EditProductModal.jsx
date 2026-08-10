import { useEffect, useState } from "react";

import { updateProduct } from "../../api/productApi";
import { getCompanies } from "../../api/companyApi";
import { getCategories } from "../../api/categoryApi";

import "./CompanyModal.css";

export default function EditProductModal({
  isOpen,
  onClose,
  onSuccess,
  product,
}) {
  const initialForm = {
    company_id: "",
    category_id: "",
    name: "",
    sku: "",
    description: "",
    unit_price: "",
    stock_quantity: "",
    status: "In Stock",
    is_active: true,
  };

  const [formData, setFormData] = useState(initialForm);

  const [companies, setCompanies] = useState([]);
  const [categories, setCategories] = useState([]);

  const [loading, setLoading] = useState(false);
  const [loadingLists, setLoadingLists] = useState(false);

  // ================= Load Companies & Categories =================

  useEffect(() => {
    if (isOpen) {
      loadDropdownData();
    }
  }, [isOpen]);

  const loadDropdownData = async () => {
    try {
      setLoadingLists(true);

      const [companyData, categoryData] = await Promise.all([
        getCompanies(),
        getCategories(),
      ]);

      setCompanies(
        Array.isArray(companyData)
          ? companyData
          : []
      );

      setCategories(
        Array.isArray(categoryData)
          ? categoryData
          : []
      );
    } catch (error) {
      console.error(
        "Error loading companies/categories:",
        error
      );

      alert(
        "Failed to load company and category lists."
      );
    } finally {
      setLoadingLists(false);
    }
  };

  // ================= Load Selected Product =================

  useEffect(() => {
    if (product) {
      setFormData({
        company_id: product.company_id ?? "",
        category_id: product.category_id ?? "",
        name: product.name ?? "",
        sku: product.sku ?? "",
        description: product.description ?? "",
        unit_price: product.unit_price ?? "",
        stock_quantity: product.stock_quantity ?? "",
        status: product.status ?? "In Stock",
        is_active:
          product.is_active ?? true,
      });
    }
  }, [product]);

  // ================= Handle Change =================

  const handleChange = (e) => {
    const {
      name,
      value,
      type,
      checked,
    } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "checkbox"
          ? checked
          : value,
    }));
  };

  // ================= Submit =================

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.company_id) {
      alert("Please select a company.");
      return;
    }

    if (!formData.category_id) {
      alert("Please select a category.");
      return;
    }

    setLoading(true);

    try {
      await updateProduct(product.id, {
        ...formData,

        company_id: Number(
          formData.company_id
        ),

        category_id: Number(
          formData.category_id
        ),

        unit_price: Number(
          formData.unit_price
        ),

        stock_quantity: Number(
          formData.stock_quantity
        ),
      });

      alert("Product updated successfully.");

      await onSuccess();

      onClose();

    } catch (error) {
      console.error(
        "Error updating product:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Failed to update product."
      );
    } finally {
      setLoading(false);
    }
  };

  // ================= Close =================

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-overlay">

      <div className="modal">

        <h2>Edit Product</h2>

        <form onSubmit={handleSubmit}>

          {/* ================= Company ================= */}

          <select
            name="company_id"
            value={formData.company_id}
            onChange={handleChange}
            required
            disabled={
              loading || loadingLists
            }
          >
            <option value="">
              {loadingLists
                ? "Loading companies..."
                : "Select Company"}
            </option>

            {companies.map((company) => (
              <option
                key={company.id}
                value={company.id}
              >
                {company.company_name}
              </option>
            ))}
          </select>

          {/* ================= Category ================= */}

          <select
            name="category_id"
            value={formData.category_id}
            onChange={handleChange}
            required
            disabled={
              loading || loadingLists
            }
          >
            <option value="">
              {loadingLists
                ? "Loading categories..."
                : "Select Category"}
            </option>

            {categories.map((category) => (
              <option
                key={category.id}
                value={category.id}
              >
                {category.name}
              </option>
            ))}
          </select>

          {/* ================= Product Name ================= */}

          <input
            type="text"
            name="name"
            placeholder="Product Name"
            value={formData.name}
            onChange={handleChange}
            required
            disabled={loading}
          />

          {/* ================= SKU ================= */}

          <input
            type="text"
            name="sku"
            placeholder="SKU"
            value={formData.sku}
            onChange={handleChange}
            required
            disabled={loading}
          />

          {/* ================= Description ================= */}

          <textarea
            name="description"
            placeholder="Description"
            value={formData.description}
            onChange={handleChange}
            disabled={loading}
          />

          {/* ================= Unit Price ================= */}

          <input
            type="number"
            step="0.01"
            min="0"
            name="unit_price"
            placeholder="Unit Price"
            value={formData.unit_price}
            onChange={handleChange}
            required
            disabled={loading}
          />

          {/* ================= Stock ================= */}

          <input
            type="number"
            min="0"
            name="stock_quantity"
            placeholder="Stock Quantity"
            value={formData.stock_quantity}
            onChange={handleChange}
            required
            disabled={loading}
          />

          {/* ================= Status ================= */}

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            disabled={loading}
          >
            <option value="In Stock">
              In Stock
            </option>

            <option value="Low Stock">
              Low Stock
            </option>

            <option value="Out of Stock">
              Out of Stock
            </option>
          </select>

          {/* ================= Active ================= */}

          <label className="checkbox-label">

            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              disabled={loading}
            />

            Active

          </label>

          {/* ================= Buttons ================= */}

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
              disabled={
                loading || loadingLists
              }
            >
              {loading
                ? "Updating..."
                : "Update Product"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}