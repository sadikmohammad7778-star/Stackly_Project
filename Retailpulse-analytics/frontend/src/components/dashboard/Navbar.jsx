import { useEffect, useRef, useState } from "react";
import "./Navbar.css";

import {
  FiSearch,
  FiBell,
  FiSettings,
} from "react-icons/fi";

import NotificationDropdown from "./NotificationDropdown";
import { getUnreadCount } from "../../api/notificationApi";

export default function Navbar() {
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const notificationRef = useRef(null);

  const loadUnreadCount = async () => {
    try {
      const data = await getUnreadCount();
      setUnreadCount(data.count);
    } catch (error) {
      console.error("Failed to load unread count:", error);
    }
  };

  useEffect(() => {
    loadUnreadCount();

    const interval = setInterval(() => {
      loadUnreadCount();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (
        notificationRef.current &&
        !notificationRef.current.contains(event.target)
      ) {
        setShowNotifications(false);
      }
    };

    document.addEventListener("mousedown", handleOutsideClick);

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
        <h2>RetailPulse Analytics</h2>
        <p>{today}</p>
      </div>

      <div className="navbar-center">
        <div className="search">
          <FiSearch />
          <input
            type="text"
            placeholder="Search..."
          />
        </div>
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
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <NotificationDropdown
              refreshUnreadCount={loadUnreadCount}
            />
          )}
        </div>

        <button className="icon-btn">
          <FiSettings />
        </button>

        <div className="profile">
          <img
            src="https://i.pravatar.cc/100"
            alt="Profile"
          />

          <div>
            <h4>Mohammad Sadik</h4>
            <span>Company Admin</span>
          </div>
        </div>
      </div>
    </header>
  );
}