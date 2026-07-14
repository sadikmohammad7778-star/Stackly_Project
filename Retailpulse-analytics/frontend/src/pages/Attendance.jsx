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

import "./Attendance.css";

export default function Attendance() {

  const [attendance, setAttendance] = useState([]);
  const [openModal, setOpenModal] = useState(false);

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
    try {
      const data = await getAttendance();
      setAttendance(data);
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
    }
  };

  return (
    <div className="attendance-page">

      <div className="attendance-header">

        <h2>Attendance</h2>

        <button onClick={() => setOpenModal(true)}>
          <FiPlus />
          Mark Attendance
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

              <th>Employee</th>
              <th>Date</th>
              <th>Check In</th>
              <th>Check Out</th>
              <th>Status</th>
              <th>Actions</th>

            </tr>

          </thead>

          <tbody>

            {attendance.map((item) => (

              <tr key={item.id}>

                <td>{item.employee_name}</td>
                <td>{item.date}</td>
                <td>{item.check_in}</td>
                <td>{item.check_out}</td>
                <td>{item.status}</td>

                <td>

                  <button className="edit">
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

            ))}

          </tbody>

        </table>

      </div>

      <AttendanceModal
        isOpen={openModal}
        onClose={() => setOpenModal(false)}
        onSuccess={loadAttendance}
      />

    </div>
  );
}