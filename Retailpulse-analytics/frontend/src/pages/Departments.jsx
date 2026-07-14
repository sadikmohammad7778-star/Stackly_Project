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

export default function Departments() {

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

        <button>
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
              <th>Name</th>
              <th>Manager</th>
              <th>Actions</th>

            </tr>

          </thead>

          <tbody>

            {departments.map((department) => (

              <tr key={department.id}>

                <td>{department.id}</td>

                <td>{department.department_name}</td>

                <td>{department.manager_name}</td>

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

    </div>
  );
}