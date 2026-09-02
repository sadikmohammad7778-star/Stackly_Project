import { useEffect, useState } from "react";
import {
  FiPlus,
  FiSearch,
  FiEdit,
  FiTrash2,
} from "react-icons/fi";

import {
  getDepartments,
  deleteDepartment,
} from "../api/departmentApi";

import "./Departments.css";
import DepartmentModal from "../components/forms/DepartmentModal";

export default function Departments() {
  const [openModal, setOpenModal] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    try {
      const data = await getDepartments();
      setDepartments(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleAdd = () => {
    setSelectedDepartment(null);
    setOpenModal(true);
  };

  const handleEdit = (department) => {
    setSelectedDepartment(department);
    setOpenModal(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this department?")) return;

    try {
      await deleteDepartment(id);
      await loadDepartments();
    } catch (error) {
      console.error(error);
      alert("Failed to delete department.");
    }
  };

  const filteredDepartments = departments.filter((department) => {
    const searchText = search.toLowerCase().trim();

    if (!searchText) return true;

    return (
      department.department_name
        ?.toLowerCase()
        .includes(searchText) ||
      department.description
        ?.toLowerCase()
        .includes(searchText)
    );
  });

  return (
    <div className="departments-page">
      <div className="departments-header">
        <h2>Departments</h2>

        <button onClick={handleAdd}>
          <FiPlus />
          Add Department
        </button>
      </div>

      <div className="search-box">
        <FiSearch />

        <input
          type="text"
          placeholder="Search Department..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Department Name</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {filteredDepartments.length > 0 ? (
              filteredDepartments.map((department) => (
                <tr key={department.id}>
                  <td>{department.id}</td>

                  <td>{department.department_name}</td>

                  <td>{department.description}</td>

                  <td>
                    <button
                      className="edit"
                      onClick={() => handleEdit(department)}
                    >
                      <FiEdit />
                    </button>

                    <button
                      className="delete"
                      onClick={() => handleDelete(department.id)}
                    >
                      <FiTrash2 />
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" style={{ textAlign: "center" }}>
                  No Departments Found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <DepartmentModal
        isOpen={openModal}
        department={selectedDepartment}
        onClose={() => {
          setOpenModal(false);
          setSelectedDepartment(null);
        }}
        onSuccess={loadDepartments}
      />
    </div>
  );
}