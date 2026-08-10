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

  // Search
  const [searchTerm, setSearchTerm] = useState("");

  // Add modal
  const [openModal, setOpenModal] = useState(false);

  // Edit modal
  const [editModalOpen, setEditModalOpen] = useState(false);

  const [selectedCategory, setSelectedCategory] = useState(null);

  // ================= Load Categories =================

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

  // ================= Delete Category =================

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this category?"
    );

    if (!confirmDelete) {
      return;
    }

    try {
      const response = await deleteCategory(id);

      await loadCategories();

      alert(
        response?.message ||
          "Category deleted successfully."
      );
    } catch (error) {
      console.error(
        "Error deleting category:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Failed to delete category."
      );
    }
  };

  // ================= Search =================

  const filteredCategories = categories.filter(
    (category) => {
      const search = searchTerm
        .toLowerCase()
        .trim();

      return (
        category.name
          ?.toLowerCase()
          .includes(search) ||
        category.description
          ?.toLowerCase()
          .includes(search)
      );
    }
  );

  return (
    <div className="companies-page">

      {/* ================= Header ================= */}

      <div className="companies-header">
        <h2>Categories</h2>

        <button
          onClick={() => setOpenModal(true)}
        >
          <FiPlus />
          Add Category
        </button>
      </div>

      {/* ================= Search ================= */}

      <div className="search-box">
        <FiSearch />

        <input
          type="text"
          placeholder="Search category..."
          value={searchTerm}
          onChange={(e) =>
            setSearchTerm(e.target.value)
          }
        />
      </div>

      {/* ================= Category Table ================= */}

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
            {filteredCategories.length > 0 ? (
              filteredCategories.map(
                (category) => (
                  <tr key={category.id}>

                    <td>
                      {category.name}
                    </td>

                    <td>
                      {category.description ||
                        "-"}
                    </td>

                    <td>

                      {/* Edit */}
                      <button
                        className="edit"
                        onClick={() => {
                          setSelectedCategory(
                            category
                          );
                          setEditModalOpen(true);
                        }}
                      >
                        <FiEdit />
                      </button>

                      {/* Delete */}
                      <button
                        className="delete"
                        onClick={() =>
                          handleDelete(
                            category.id
                          )
                        }
                      >
                        <FiTrash2 />
                      </button>

                    </td>

                  </tr>
                )
              )
            ) : (
              <tr>
                <td
                  colSpan="3"
                  style={{
                    textAlign: "center",
                    padding: "20px",
                  }}
                >
                  {searchTerm
                    ? "No matching categories found."
                    : "No Categories Found"}
                </td>
              </tr>
            )}
          </tbody>

        </table>
      </div>

      {/* ================= Add Category Modal ================= */}

      <CategoryModal
        isOpen={openModal}
        onClose={() =>
          setOpenModal(false)
        }
        onSuccess={loadCategories}
      />

      {/* ================= Edit Category Modal ================= */}

      <CategoryModal
        isOpen={editModalOpen}
        category={selectedCategory}
        onClose={() => {
          setEditModalOpen(false);
          setSelectedCategory(null);
        }}
        onSuccess={loadCategories}
      />

    </div>
  );
}