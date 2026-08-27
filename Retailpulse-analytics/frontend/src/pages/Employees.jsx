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
  const [search, setSearch] = useState("");
  const [openModal, setOpenModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);

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

  const handleEdit = (employee) => {
  setSelectedEmployee(employee);
  setOpenModal(true);
};

  // Search / Filter employees
  const filteredEmployees = employees.filter((employee) => {
    const searchText = search.toLowerCase().trim();

    if (!searchText) return true;

    const fullName =
      `${employee.first_name} ${employee.last_name}`.toLowerCase();

    return (
      fullName.includes(searchText) ||
      employee.employee_code?.toLowerCase().includes(searchText) ||
      employee.email?.toLowerCase().includes(searchText) ||
      employee.designation?.toLowerCase().includes(searchText)
    );
  });

  return (
    <div className="employees-page">

      <div className="employees-header">

        <h2>Employees</h2>

        <button
            onClick={() => {
              setSelectedEmployee(null);
              setOpenModal(true);
            }}
          >
          <FiPlus />
          Add Employee
        </button>

      </div>

      <div className="search-box">

        <FiSearch />

        <input
          type="text"
          placeholder="Search Employee..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
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

            {filteredEmployees.length > 0 ? (

              filteredEmployees.map((employee) => (

                <tr key={employee.id}>

                  <td>{employee.employee_code}</td>

                  <td>
                    {employee.first_name} {employee.last_name}
                  </td>

                  <td>{employee.email}</td>

                  <td>{employee.designation}</td>

                  <td>₹ {employee.salary}</td>

                  <td>

                    <button
                      className="edit"
                      onClick={() => handleEdit(employee)}
                    >
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
        employee={selectedEmployee}
        onClose={() => {
          setOpenModal(false);
          setSelectedEmployee(null);
        }}
        onSuccess={loadEmployees}
      />

    </div>
  );
}