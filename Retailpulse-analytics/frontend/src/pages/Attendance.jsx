import { useEffect, useState } from "react";
import {
  FiPlus,
  FiSearch,
  FiEdit,
  FiTrash2,
} from "react-icons/fi";

import AttendanceModal from "../components/forms/AttendanceModal";

import {
  getAttendance,
  deleteAttendance,
} from "../api/attendanceApi";

import { getEmployees } from "../api/employeeApi";

import "./Attendance.css";

export default function Attendance() {
  const [attendance, setAttendance] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [editAttendance, setEditAttendance] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadAttendance();
    loadEmployees();
  }, []);

  const loadAttendance = async () => {
    try {
      const data = await getAttendance();
      setAttendance(data);
    } catch (error) {
      console.error(error);
    }
  };

  const loadEmployees = async () => {
    try {
      const data = await getEmployees();
      setEmployees(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete attendance record?")) return;

    try {
      await deleteAttendance(id);
      loadAttendance();
    } catch (error) {
      console.error(error);
      alert("Failed to delete attendance.");
    }
  };

  const handleEdit = (item) => {
    setEditAttendance(item);
    setOpenModal(true);
  };

  const handleCloseModal = () => {
    setOpenModal(false);
    setEditAttendance(null);
  };

  const filteredAttendance = attendance.filter((item) => {
    const employee = employees.find(
      (emp) => emp.id === item.employee_id
    );

    if (!employee) return false;

    const searchText = search.toLowerCase().trim();

    if (!searchText) return true;

    const name =
      `${employee.first_name} ${employee.last_name}`.toLowerCase();

    const code =
      employee.employee_code?.toLowerCase() || "";

    return (
      name.includes(searchText) ||
      code.includes(searchText)
    );
  });

  const formatDate = (date) => {
    if (!date) return "-";

    return new Date(date).toLocaleDateString("en-IN");
  };

  const formatTime = (time) => {
    if (!time) return "-";

    return new Date(time).toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  return (
    <div className="attendance-page">

      <div className="attendance-header">
        <h2>Attendance</h2>

        <button
          onClick={() => {
            setEditAttendance(null);
            setOpenModal(true);
          }}
        >
          <FiPlus />
          Mark Attendance
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
              <th>Employee</th>
              <th>Date</th>
              <th>Check In</th>
              <th>Check Out</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>

            {filteredAttendance.length > 0 ? (

              filteredAttendance.map((item) => {

                const employee = employees.find(
                  (emp) => emp.id === item.employee_id
                );

                return (
                  <tr key={item.id}>

                    <td>
                      {employee
                        ? `${employee.employee_code} - ${employee.first_name} ${employee.last_name}`
                        : "Unknown Employee"}
                    </td>

                    <td>
                      {formatDate(item.attendance_date)}
                    </td>

                    <td>
                      {formatTime(item.check_in)}
                    </td>

                    <td>
                      {formatTime(item.check_out)}
                    </td>

                    <td>{item.status}</td>

                    <td>

                      <button
                        className="edit"
                        onClick={() => handleEdit(item)}
                      >
                        <FiEdit />
                      </button>

                      <button
                        className="delete"
                        onClick={() => handleDelete(item.id)}
                      >
                        <FiTrash2 />
                      </button>

                    </td>

                  </tr>
                );
              })

            ) : (

              <tr>
                <td
                  colSpan="6"
                  style={{ textAlign: "center" }}
                >
                  No Attendance Found
                </td>
              </tr>

            )}

          </tbody>

        </table>

      </div>

      <AttendanceModal
        isOpen={openModal}
        employees={employees}
        editAttendance={editAttendance}
        onClose={handleCloseModal}
        onSuccess={loadAttendance}
      />

    </div>
  );
}