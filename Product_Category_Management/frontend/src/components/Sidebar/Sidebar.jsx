import { NavLink } from "react-router-dom";
import {
  FaHome,
  FaBoxes,
  FaTags,
  FaChartBar,
  FaCog,
  FaSignOutAlt,
} from "react-icons/fa";

import "./Sidebar.css";

function Sidebar() {
  return (
    <div className="sidebar">

      <div className="logo">
        <h2>ProductManager</h2>
      </div>

      <ul className="menu">

        <li>
          <NavLink to="/dashboard">
            <FaHome />
            <span>Dashboard</span>
          </NavLink>
        </li>

        <li>
          <NavLink to="/categories">
            <FaTags />
            <span>Categories</span>
          </NavLink>
        </li>

        <li>
          <NavLink to="/products">
            <FaBoxes />
            <span>Products</span>
          </NavLink>
        </li>

        <li>
          <NavLink to="/reports">
            <FaChartBar />
            <span>Reports</span>
          </NavLink>
        </li>

        <li>
          <NavLink to="/settings">
            <FaCog />
            <span>Settings</span>
          </NavLink>
        </li>

      </ul>

      <div className="logout">

        <NavLink to="/login">
          <FaSignOutAlt />
          <span>Logout</span>
        </NavLink>

      </div>

    </div>
  );
}

export default Sidebar;