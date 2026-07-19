import { useEffect, useState } from "react";
import {
  FiPlus,
  FiEdit,
  FiTrash2,
  FiSearch,
} from "react-icons/fi";

import CategoryModal from "../components/forms/CategoryModal";

import "./Companies.css";

import {
  getCategories,
  deleteCategory,
} from "../api/categoryApi";

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [openModal, setOpenModal] = useState(false);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const data = await getCategories();
      setCategories(data);
    } catch (error) {
      console.error("Error loading categories:", error);
    }
  };

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this category?"
    );

    if (!confirmDelete) return;

    try {
      await deleteCategory(id);
      loadCategories();
    } catch (error) {
      console.error("Error deleting category:", error);
    }
  };

  return (
    <div className="companies-page">
      <div className="companies-header">
        <h2>Categories</h2>

        <button onClick={() => setOpenModal(true)}>
            <FiPlus />
            Add Category
        </button>
      </div>

      <div className="search-box">
        <FiSearch />

        <input
          type="text"
          placeholder="Search category..."
        />
      </div>

      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {categories.length > 0 ? (
              categories.map((category) => (
                <tr key={category.id}>
                  <td>{category.name}</td>
                  <td>{category.description || "-"}</td>

                  <td>
                    <button className="edit">
                      <FiEdit />
                    </button>

                    <button
                      className="delete"
                      onClick={() => handleDelete(category.id)}
                    >
                      <FiTrash2 />
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="3"
                  style={{ textAlign: "center" }}
                >
                  No Categories Found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <CategoryModal
        isOpen={openModal}
        onClose={() => setOpenModal(false)}
        onSuccess={loadCategories}
      />
    </div>
  );
}