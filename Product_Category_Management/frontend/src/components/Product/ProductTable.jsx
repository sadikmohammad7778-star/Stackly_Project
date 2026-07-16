import { useEffect, useState } from "react";
import { FaEdit, FaTrash } from "react-icons/fa";
import { toast } from "react-toastify";

import {
  getProducts,
  deleteProduct as deleteProductApi,
  sortProducts,
  changeProductStatus,
} from "../../services/productService";

import { getCategories } from "../../services/categoryService";

import ProductModal from "./ProductModal";
import "./ProductTable.css";
import Loader from "../Common/Loader";

function ProductTable() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);

  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [brandFilter, setBrandFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortBy, setSortBy] = useState("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProducts();
    loadCategories();
  }, []);

  const loadProducts = async () => {
    try {
        const response = await getProducts();
        setProducts(response.data);
    } catch (error) {
        console.error(error);
    } finally {
        setLoading(false);
    }
   };

  const loadCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleSort = async (value) => {
    setSortBy(value);

    if (value === "") {
      loadProducts();
      return;
    }

    try {
      const response = await sortProducts(value);
      setProducts(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const deleteProduct = async (id) => {
        
    const confirmDelete = window.confirm(
        "Are you sure you want to delete this product?"
    );

    if (!confirmDelete) return;
    

    try {
        await deleteProductApi(id);

        toast.success("Product deleted successfully.");

        loadProducts();

    } catch (error) {
        console.error(error);

        toast.error("Unable to delete product.");
    }
   };

  const toggleStatus = async (product) => {
    try {
        const newStatus =
        product.status === "Active"
            ? "Inactive"
            : "Active";

        await changeProductStatus(
        product.id,
        newStatus
        );

        toast.success("Product status updated successfully.");

        loadProducts();

    } catch (error) {
        console.error(error);

        toast.error("Unable to update product status.");
    }
   };

  const filteredProducts = products
    .filter((product) =>
      product.name.toLowerCase().includes(search.toLowerCase())
    )
    .filter((product) =>
      categoryFilter === ""
        ? true
        : product.category_id === Number(categoryFilter)
    )
    .filter((product) =>
      brandFilter === ""
        ? true
        : (product.brand || "")
            .toLowerCase()
            .includes(brandFilter.toLowerCase())
    )
    .filter((product) =>
      statusFilter === ""
        ? true
        : product.status === statusFilter
    );

    if (loading) {
        return <Loader />;
    }

  return (
    <div className="product-table">

      <div className="table-header">
        <h2>Product Management</h2>

        <button
          className="add-btn"
          onClick={() => {
            setSelectedProduct(null);
            setIsModalOpen(true);
          }}
        >
          + Add Product
        </button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search Product..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="filters">

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          <option value="">All Categories</option>

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
          placeholder="Brand"
          value={brandFilter}
          onChange={(e) => setBrandFilter(e.target.value)}
        />

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => handleSort(e.target.value)}
        >
          <option value="">Sort By</option>
          <option value="name">Name</option>
          <option value="price">Price</option>
          <option value="recent">Recently Added</option>
        </select>

      </div>

      <table>

        <thead>
          <tr>
            <th>Name</th>
            <th>SKU</th>
            <th>Brand</th>
            <th>Price</th>
            <th>Stock</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>

          {filteredProducts.map((product) => (

            <tr key={product.id}>

              <td>{product.name}</td>
              <td>{product.sku}</td>
              <td>{product.brand}</td>
              <td>₹ {product.unit_price}</td>
              <td>{product.stock_quantity}</td>
              <td>

                <button
                    className={
                    product.status === "Active"
                        ? "active-btn"
                        : "inactive-btn"
                    }
                    onClick={() => toggleStatus(product)}
                >
                    {product.status}
                </button>

                </td>
              <td>

                <button
                  className="edit-btn"
                  onClick={() => {
                    setSelectedProduct(product);
                    setIsModalOpen(true);
                  }}
                >
                  <FaEdit />
                </button>

                <button
                  className="delete-btn"
                  onClick={() => deleteProduct(product.id)}
                >
                  <FaTrash />
                </button>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

      <ProductModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={loadProducts}
        product={selectedProduct}
      />

    </div>
  );
}

export default ProductTable;