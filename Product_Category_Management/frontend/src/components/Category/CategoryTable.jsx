import { useEffect, useState } from "react";
import {
  getCategories,
  deleteCategory as deleteCategoryApi,
} from "../../services/categoryService";
import { FaEdit, FaTrash } from "react-icons/fa";
import { toast } from "react-toastify";

import CategoryModal from "./CategoryModal";
import "./CategoryTable.css";

function CategoryTable() {
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);

  useEffect(() => {
    loadCategories();
  }, []);

  // Load Categories
  const loadCategories = async () => {
    try {
     const response = await getCategories();
      

      setCategories(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  // Delete Category
  const deleteCategory = async (id) => {
    const confirmDelete = window.confirm(
        "Are you sure you want to delete this category?"
    );

    if (!confirmDelete) return;

    try {
        await deleteCategoryApi(id);

        toast.success("Category deleted successfully.");

        loadCategories();

    } catch (error) {
        console.error(error);

        toast.error("Unable to delete category.");
    }
   };

  return (
    <div className="category-table">

      <div className="table-header">

        <h2>Category Management</h2>

        <button
          className="add-btn"
          onClick={() => {
            setSelectedCategory(null);
            setIsModalOpen(true);
          }}
        >
          + Add Category
        </button>

      </div>

      {/* Search */}

      <div className="search-bar">

        <input
          type="text"
          placeholder="Search Category..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

      </div>

      {/* Table */}

      <table>

        <thead>

          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>

        </thead>

        <tbody>

          {categories
            .filter((category) =>
              category.name
                .toLowerCase()
                .includes(search.toLowerCase())
            )
            .map((category) => (

              <tr key={category.id}>

                <td>{category.name}</td>

                <td>{category.description}</td>

                <td>{category.status}</td>

                <td>

                  <button
                    className="edit-btn"
                    onClick={() => {
                      setSelectedCategory(category);
                      setIsModalOpen(true);
                    }}
                  >
                    <FaEdit />
                  </button>

                  <button
                    className="delete-btn"
                    onClick={() =>
                      deleteCategory(category.id)
                    }
                  >
                    <FaTrash />
                  </button>

                </td>

              </tr>

            ))}

        </tbody>

      </table>

      <CategoryModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={loadCategories}
        category={selectedCategory}
      />

    </div>
  );
}

export default CategoryTable;