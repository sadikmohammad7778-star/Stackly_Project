import {
  FiHome,
  FiBriefcase,
  FiGrid,
  FiShoppingBag,
  FiShoppingCart,
  FiBarChart2,
  FiFileText,
  FiSettings,
  FiLogOut,
} from "react-icons/fi";
import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const menu = [
  { name: "Dashboard", path: "/dashboard", icon: <FiHome /> },
  { name: "Companies", path: "/companies", icon: <FiBriefcase /> },
  { name: "Categories", path: "/categories", icon: <FiGrid /> },
  { name: "Products", path: "/products", icon: <FiShoppingBag /> },
  { name: "Sales", path: "/sales", icon: <FiShoppingCart /> },
  { name: "Analytics", path: "/analytics", icon: <FiBarChart2 /> },
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