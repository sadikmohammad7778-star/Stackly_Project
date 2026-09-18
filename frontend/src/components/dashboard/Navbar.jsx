import { useEffect, useRef, useState } from "react";
import "./Navbar.css";

import {
  FiSearch,
  FiBell,
  FiSettings,
} from "react-icons/fi";

import { useNavigate } from "react-router-dom";

import NotificationDropdown from "./NotificationDropdown";
import { useNotifications } from "../../context/NotificationContext";

export default function Navbar() {
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user") || "null");

  const {
    unreadCount,
    loadUnreadCount,
  } = useNotifications();

  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const [searchTerm, setSearchTerm] = useState("");

  const pages = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "Companies", path: "/companies" },
    { name: "Categories", path: "/categories" },
    { name: "Products", path: "/products" },
    { name: "Sales", path: "/sales" },
    { name: "Inventory", path: "/inventory" },
    { name: "Inventory Forecast", path: "/inventory/forecast" },
    { name: "Demand Forecast", path: "/forecast" },
    { name: "Customers", path: "/customers" },
    { name: "Customer Analytics", path: "/customers/dashboard" },
    { name: "Employees", path: "/employees" },
    { name: "Departments", path: "/departments" },
    { name: "Attendance", path: "/attendance" },
    { name: "Reports", path: "/reports" },
    { name: "Analytics", path: "/analytics" },
    { name: "Audit Logs", path: "/audit" },
    { name: "Settings", path: "/settings" },
  ];

  const filteredPages = pages.filter((page) =>
    page.name
      .toLowerCase()
      .includes(searchTerm.toLowerCase().trim())
  );

  const handlePageClick = (path) => {
    navigate(path);
    setSearchTerm("");
  };

  const [showNotifications, setShowNotifications] =
    useState(false);

  const notificationRef = useRef(null);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (
        notificationRef.current &&
        !notificationRef.current.contains(event.target)
      ) {
        setShowNotifications(false);
      }
    };

    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, []);

  const toggleNotifications = () => {
    setShowNotifications((prev) => !prev);
    loadUnreadCount();
  };

  return (
    <header className="navbar">
      <div className="navbar-left">
        <div>
          <h2>RetailPulse Analytics</h2>
          <span>{today}</span>
        </div>
      </div>

      <div className="navbar-center">
        <div className="search">
          <FiSearch />

          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) =>
              setSearchTerm(e.target.value)
            }
          />
        </div>

        {searchTerm.trim() && (
          <div className="search-results">
            {filteredPages.length > 0 ? (
              filteredPages.map((page) => (
                <div
                  key={page.path}
                  className="search-result-item"
                  onClick={() =>
                    handlePageClick(page.path)
                  }
                >
                  <FiSearch />
                  <span>{page.name}</span>
                </div>
              ))
            ) : (
              <div className="search-no-result">
                No page found
              </div>
            )}
          </div>
        )}
      </div>

      <div className="navbar-right">
        <div
          className="notification-wrapper"
          ref={notificationRef}
        >
          <button
            className="icon-btn"
            onClick={toggleNotifications}
          >
            <FiBell />

            {unreadCount > 0 && (
              <span className="notification-badge">
                {unreadCount > 99
                  ? "99+"
                  : unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <NotificationDropdown />
          )}
        </div>

        <button
          className="icon-btn"
          onClick={() => navigate("/settings")}
        >
          <FiSettings />
        </button>

        <div className="profile">
          <img
            src="https://i.pravatar.cc/100"
            alt="Profile"
          />

          <div>
            <h4>{user?.name || "User"}</h4>
            <span>{user?.role || "User"}</span>
          </div>
        </div>
      </div>
    </header>
  );
}