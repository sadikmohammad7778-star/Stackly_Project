import { useEffect, useState } from "react";
import {
  FiPlus,
  FiSearch,
  FiEdit,
  FiTrash2,
} from "react-icons/fi";

import EmployeeModal from "../components/forms/EmployeeModal";

import {
  getEmployees,
  deleteEmployee,
} from "../api/employeeApi";

import "./Employees.css";

export default function Employees() {
  const [employees, setEmployees] = useState([]);
  const [openModal, setOpenModal] = useState(false);

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const data = await getEmployees();
      setEmployees(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this employee?"
    );

    if (!confirmDelete) return;

    try {
      await deleteEmployee(id);
      loadEmployees();
    } catch (error) {
      console.error(error);
      alert("Failed to delete employee.");
    }
  };

  return (
    <div className="employees-page">

      <div className="employees-header">

        <h2>Employees</h2>

        <button onClick={() => setOpenModal(true)}>
          <FiPlus />
          Add Employee
        </button>

      </div>

      <div className="search-box">

        <FiSearch />

        <input
          type="text"
          placeholder="Search Employee..."
        />

      </div>

      <div className="table-card">

        <table>

          <thead>

            <tr>

              <th>Code</th>
              <th>Name</th>
              <th>Email</th>
              <th>Designation</th>
              <th>Salary</th>
              <th>Actions</th>

            </tr>

          </thead>

          <tbody>

            {employees.length > 0 ? (

              employees.map((employee) => (

                <tr key={employee.id}>

                  <td>{employee.employee_code}</td>

                  <td>
                    {employee.first_name} {employee.last_name}
                  </td>

                  <td>{employee.email}</td>

                  <td>{employee.designation}</td>

                  <td>₹ {employee.salary}</td>

                  <td>

                    <button className="edit">
                      <FiEdit />
                    </button>

                    <button
                      className="delete"
                      onClick={() => handleDelete(employee.id)}
                    >
                      <FiTrash2 />
                    </button>

                  </td>

                </tr>

              ))

            ) : (

              <tr>

                <td colSpan="6" style={{ textAlign: "center" }}>
                  No Employees Found
                </td>

              </tr>

            )}

          </tbody>

        </table>

      </div>

      <EmployeeModal
        isOpen={openModal}
        onClose={() => setOpenModal(false)}
        onSuccess={loadEmployees}
      />

    </div>
  );
}