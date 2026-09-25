import {
  FiHome,
  FiBriefcase,
  FiGrid,
  FiShoppingBag,
  FiShoppingCart,
  FiArchive,
  FiUsers,
  FiTrendingUp,
  FiBarChart2,
  FiFileText,
  FiShield,
  FiSettings,
  FiLogOut,
  FiClock,
  FiCheckCircle,
} from "react-icons/fi";

import { NavLink, useNavigate } from "react-router-dom";
import "./Sidebar.css";

const menu = [
  {
    name: "Dashboard",
    path: "/dashboard",
    icon: <FiHome />,
  },

  {
    name: "Companies",
    path: "/companies",
    icon: <FiBriefcase />,
  },

  {
    name: "Categories",
    path: "/categories",
    icon: <FiGrid />,
  },

  {
    name: "Products",
    path: "/products",
    icon: <FiShoppingBag />,
  },

  {
    name: "Sales",
    path: "/sales",
    icon: <FiShoppingCart />,
  },

  {
    name: "Inventory",
    path: "/inventory",
    icon: <FiArchive />,
  },

  {
    name: "Data Import",
    path: "/data-import",
    icon: <FiFileText />,
  },

  {
    name: "Data Quality",
    path: "/data-quality",
    icon: <FiCheckCircle />,
  },

  {
    name: "Inventory Forecast",
    path: "/inventory/forecast",
    icon: <FiTrendingUp />,
  },

  {
    name: "Demand Forecast",
    path: "/forecast",
    icon: <FiTrendingUp />,
  },

  {
    name: "Customers",
    path: "/customers",
    icon: <FiUsers />,
  },

  {
    name: "Customer Analytics",
    path: "/customers/dashboard",
    icon: <FiBarChart2 />,
  },

  {
    name: "Analytics",
    path: "/analytics",
    icon: <FiBarChart2 />,
  },

  {
    name: "Reports",
    path: "/reports",
    icon: <FiFileText />,
  },

  {
    name: "Scheduled Reports",
    path: "/scheduled-reports",
    icon: <FiClock />,
  },

  {
    name: "Audit Logs",
    path: "/audit",
    icon: <FiShield />,
  },

  {
    name: "Settings",
    path: "/settings",
    icon: <FiSettings />,
  },
];

export default function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");

    navigate("/login");
  };

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

      <button
        className="logout"
        onClick={handleLogout}
      >
        <FiLogOut />
        <span>Logout</span>
      </button>
    </aside>
  );
}