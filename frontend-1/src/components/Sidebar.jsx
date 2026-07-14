import { NavLink } from "react-router-dom";
import {
  FaTachometerAlt,
  FaUsers,
  FaBuilding,
  FaCalendarCheck,
  FaCog,
  FaSignOutAlt,
} from "react-icons/fa";

function Sidebar() {
  return (
    <div className="sidebar">

      <div className="logo">
        <h2>EMS</h2>
      </div>

      <nav>

        <NavLink to="/dashboard">
          <FaTachometerAlt />
          <span>Dashboard</span>
        </NavLink>

        <NavLink to="/employees">
          <FaUsers />
          <span>Employees</span>
        </NavLink>

        <NavLink to="/departments">
          <FaBuilding />
          <span>Departments</span>
        </NavLink>

        <NavLink to="/attendance">
          <FaCalendarCheck />
          <span>Attendance</span>
        </NavLink>

        <NavLink to="/settings">
          <FaCog />
          <span>Settings</span>
        </NavLink>

      </nav>

      <button className="logout-btn">
        <FaSignOutAlt />
        Logout
      </button>

    </div>
  );
}

export default Sidebar;