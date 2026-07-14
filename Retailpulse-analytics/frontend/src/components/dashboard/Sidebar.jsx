import {
  FiHome,
  FiBriefcase,
  FiUsers,
  FiGrid,
  FiBarChart2,
  FiCalendar,
  FiFileText,
  FiSettings,
  FiLogOut,
} from "react-icons/fi";
import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const menu = [
  { name: "Dashboard", path: "/dashboard", icon: <FiHome /> },
  { name: "Companies", path: "/companies", icon: <FiBriefcase /> },
  { name: "Employees", path: "/employees", icon: <FiUsers /> },
  { name: "Departments", path: "/departments", icon: <FiGrid /> },
  { name: "Analytics", path: "/analytics", icon: <FiBarChart2 /> },
  { name: "Attendance", path: "/attendance", icon: <FiCalendar /> },
  { name: "Reports", path: "/reports", icon: <FiFileText /> },
  { name: "Settings", path: "/settings", icon: <FiSettings /> },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div>
        <div className="logo">
          <h2>RetailPulse</h2>
          <span>Analytics</span>
        </div>

        <nav>
          {menu.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive ? "menu active" : "menu"
              }
            >
              {item.icon}
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      <button className="logout">
        <FiLogOut />
        Logout
      </button>
    </aside>
  );
}