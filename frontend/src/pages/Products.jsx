import { useEffect, useState } from "react";
import {
  FiPlus,
  FiEdit,
  FiTrash2,
  FiSearch,
} from "react-icons/fi";

import "./Companies.css";

import ProductModal from "../components/forms/ProductModal";
import EditProductModal from "../components/forms/EditProductModal";

import {
  getProducts,
  deleteProduct,
  searchProducts,
} from "../api/productApi";

export default function Products() {
  const [products, setProducts] = useState([]);

  const [openModal, setOpenModal] = useState(false);

  const [editOpen, setEditOpen] = useState(false);

  const [selectedProduct, setSelectedProduct] = useState(null);

  const [search, setSearch] = useState("");

  // ================= Load Products =================

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const data = await getProducts();

      setProducts(
        Array.isArray(data) ? data : []
      );
    } catch (error) {
      console.error(
        "Error loading products:",
        error
      );
    }
  };

  // ================= Search Products =================

  const handleSearch = async (e) => {
    const value = e.target.value;

    setSearch(value);

    if (value.trim() === "") {
      await loadProducts();
      return;
    }

    try {
      const data = await searchProducts(
        value.trim()
      );

      setProducts(
        Array.isArray(data) ? data : []
      );
    } catch (error) {
      console.error(
        "Error searching products:",
        error
      );
    }
  };

  // ================= Delete Product =================

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this product?"
    );

    if (!confirmDelete) {
      return;
    }

    try {
      const response = await deleteProduct(id);

      alert(
        response?.message ||
          "Product deleted successfully."
      );

      await loadProducts();

    } catch (error) {
      console.error(
        "Error deleting product:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Failed to delete product."
      );
    }
  };

  // ================= Edit Product =================

  const handleEdit = (product) => {
    setSelectedProduct(product);
    setEditOpen(true);
  };

  return (
    <div className="companies-page">

      {/* ================= Header ================= */}

      <div className="companies-header">
        <h2>Products</h2>

        <button
          onClick={() => setOpenModal(true)}
        >
          <FiPlus />
          Add Product
        </button>
      </div>

      {/* ================= Search ================= */}

      <div className="product-search-box">
        <FiSearch />

        <input
          type="text"
          placeholder="Search Product..."
          value={search}
          onChange={handleSearch}
        />
      </div>

      {/* ================= Product Table ================= */}

      <div className="table-card">

        <table>

          <thead>
            <tr>
              <th>Name</th>
              <th>SKU</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>

            {products.length > 0 ? (

              products.map((product) => (

                <tr key={product.id}>

                  <td>
                    {product.name}
                  </td>

                  <td>
                    {product.sku}
                  </td>

                  <td>
                    ₹{product.unit_price}
                  </td>

                  <td>
                    {product.stock_quantity}
                  </td>

                  <td>

                    <span
                      className={`status ${
                        product.status
                          ?.toLowerCase()
                          .replace(/\s/g, "-")
                      }`}
                    >
                      {product.status}
                    </span>

                  </td>

                  <td>

                    {/* Edit */}

                    <button
                      className="edit"
                      onClick={() =>
                        handleEdit(product)
                      }
                    >
                      <FiEdit />
                    </button>

                    {/* Delete */}

                    <button
                      className="delete"
                      onClick={() =>
                        handleDelete(
                          product.id
                        )
                      }
                    >
                      <FiTrash2 />
                    </button>

                  </td>

                </tr>

              ))

            ) : (

              <tr>

                <td
                  colSpan="6"
                  style={{
                    textAlign: "center",
                    padding: "20px",
                  }}
                >
                  {search.trim()
                    ? "No matching products found."
                    : "No Products Found"}
                </td>

              </tr>

            )}

          </tbody>

        </table>

      </div>

      {/* ================= Add Product Modal ================= */}

      <ProductModal
        isOpen={openModal}
        onClose={() =>
          setOpenModal(false)
        }
        onSuccess={loadProducts}
      />

      {/* ================= Edit Product Modal ================= */}

      <EditProductModal
        isOpen={editOpen}
        onClose={() => {
          setEditOpen(false);
          setSelectedProduct(null);
        }}
        onSuccess={loadProducts}
        product={selectedProduct}
      />

    </div>
  );
}