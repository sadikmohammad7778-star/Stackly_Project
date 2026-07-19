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

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this product?")) return;

    try {
      await deleteProduct(id);
      loadProducts();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="companies-page">

      <div className="companies-header">
        <h2>Products</h2>

        <button onClick={() => setOpenModal(true)}>
          <FiPlus />
          Add Product
        </button>
      </div>

      <div className="search-box">
        <FiSearch />

        <input
            type="text"
            placeholder="Search Product..."
            value={search}
            onChange={async (e) => {
                const value = e.target.value;
                setSearch(value);

                if (value.trim() === "") {
                loadProducts();
                } else {
                try {
                    const data = await searchProducts(value);
                    setProducts(data);
                } catch (err) {
                    console.error(err);
                }
                }
            }}
        />
      </div>

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
                  <td>{product.name}</td>
                  <td>{product.sku}</td>
                  <td>₹{product.unit_price}</td>
                  <td>{product.stock_quantity}</td>
                  <td>
                    <span className={`status ${product.status.toLowerCase().replace(/\s/g, "-")}`}>
                        {product.status}
                    </span>
                  </td>
                  <td>
                   <button
                        className="edit"
                        onClick={() => {
                            setSelectedProduct(product);
                            setEditOpen(true);
                        }}
                        >
                        <FiEdit />
                    </button>

                    <button
                      className="delete"
                      onClick={() => handleDelete(product.id)}
                    >
                      <FiTrash2 />
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" style={{ textAlign: "center" }}>
                  No Products Found
                </td>
              </tr>
            )}

          </tbody>

        </table>

      </div>

      <ProductModal
        isOpen={openModal}
        onClose={() => setOpenModal(false)}
        onSuccess={loadProducts}
      />

      <EditProductModal
        isOpen={editOpen}
        onClose={() => setEditOpen(false)}
        onSuccess={loadProducts}
        product={selectedProduct}
      />

    </div>
  );
}