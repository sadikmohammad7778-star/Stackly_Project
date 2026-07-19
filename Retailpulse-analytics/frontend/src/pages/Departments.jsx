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

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this department?")) return;

    try {
      await deleteDepartment(id);
      loadDepartments();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="departments-page">

      <div className="departments-header">

        <h2>Departments</h2>

        <button onClick={() => setOpenModal(true)}>
          <FiPlus />
          Add Department
        </button>
      </div>

      <div className="search-box">

        <FiSearch />

        <input
          type="text"
          placeholder="Search Department..."
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

            {departments.map((department) => (

              <tr key={department.id}>

                <td>{department.id}</td>

                <td>{department.department_name}</td>

                <td>{department.description}</td>

                <td>

                  <button className="edit">
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

            ))}

          </tbody>

        </table>

      </div>
      <button className="edit">
        <FiEdit />
      </button>

    </div>
  );
}