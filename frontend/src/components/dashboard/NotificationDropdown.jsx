import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useNotifications } from "../../context/NotificationContext";

import "./NotificationDropdown.css";

const getNotificationIcon = (type) => {
  const icons = {
    STOCKOUT_RISK: "🚨",
    LOW_STOCK: "⚠️",
    OVERSTOCK: "📦",
    IMPORT_COMPLETED: "✅",
    IMPORT_FAILED: "❌",
    SALES_ALERT: "💰",
    SYSTEM_ALERT: "⚙️",
  };

  return icons[type] || "🔔";
};

const getNotificationRoute = (notification) => {
  if (
    notification.type === "SYSTEM_ALERT" &&
    notification.resource_type === "Inventory" &&
    notification.resource_id
  ) {
    return `/inventory?inventory_id=${notification.resource_id}`;
  }

  if (
    notification.type === "SYSTEM_ALERT" &&
    notification.resource_type === "Sale" &&
    notification.resource_id
  ) {
    return `/sales?sale_id=${notification.resource_id}`;
  }

  if (
    notification.type === "SYSTEM_ALERT" &&
    notification.resource_type === "Import" &&
    notification.resource_id
  ) {
    return `/data-import?import_id=${notification.resource_id}`;
  }

  const routes = {
    SALES_ALERT: `/sales?sale_id=${notification.resource_id}`,
    STOCKOUT_RISK: `/inventory?inventory_id=${notification.resource_id}`,
    LOW_STOCK: `/inventory?inventory_id=${notification.resource_id}`,
    OVERSTOCK: `/inventory?inventory_id=${notification.resource_id}`,
    IMPORT_COMPLETED: `/data-import?import_id=${notification.resource_id}`,
    IMPORT_FAILED: `/data-import?import_id=${notification.resource_id}`,
    SYSTEM_ALERT: "/dashboard",
  };

  return routes[notification.type] || "/dashboard";
};

const formatRelativeTime = (createdAt) => {
  const diff = Math.floor(
    (Date.now() - new Date(createdAt).getTime()) / 1000
  );

  if (diff < 60) {
    return `${diff} second${diff === 1 ? "" : "s"} ago`;
  }

  const minutes = Math.floor(diff / 60);

  if (minutes < 60) {
    return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  }

  const hours = Math.floor(minutes / 60);

  if (hours < 24) {
    return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  }

  const days = Math.floor(hours / 24);

  return `${days} day${days === 1 ? "" : "s"} ago`;
};

const formatExactTime = (createdAt) =>
  new Date(createdAt).toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  }) + " IST";

export default function NotificationDropdown() {
  const navigate = useNavigate();

  const {
    notifications,
    unreadCount,
    loading,
    error,
    markAsRead,
    markAllAsRead,
    updateFilters,
  } = useNotifications();
  const [filter, setFilter] = useState("ALL");

  const handleFilterChange = (value) => {
    setFilter(value);

    if (value === "ALL") {
      updateFilters({});
      return;
    }

    if (value === "UNREAD") {
      updateFilters({
        is_read: false,
      });
      return;
    }

    updateFilters({
      notification_type: value,
    });
  };

  const handleNotificationClick = async (notification) => {
    try {
      if (!notification.is_read) {
        await markAsRead(notification.id);
      }

      navigate(getNotificationRoute(notification));
    } catch (error) {
      console.error("Error handling notification:", error);
    }
  };

  const handleReadAll = async () => {
    try {
      await markAllAsRead();
    } catch (error) {
      console.error("Error marking all notifications as read:", error);
    }
  };

  return (
    <div className="notification-dropdown">
      <div className="notification-header">
        <div className="notification-title">
          <h4>Notifications</h4>

          {unreadCount > 0 && (
            <span className="notification-count">
              {unreadCount}
            </span>
          )}
        </div>

        {unreadCount > 0 && (
          <button
            className="mark-all-btn"
            onClick={handleReadAll}
          >
            Mark All
          </button>
        )}
      </div>

      <div className="notification-filter">
        <select
          value={filter}
          onChange={(e) => handleFilterChange(e.target.value)}
        >
          <option value="ALL">All</option>
          <option value="UNREAD">Unread</option>
          <option value="LOW_STOCK">Low Stock</option>
          <option value="STOCKOUT_RISK">Stockout Risk</option>
          <option value="OVERSTOCK">Overstock</option>
          <option value="SALES_ALERT">Sales Alert</option>
          <option value="IMPORT_COMPLETED">Import Completed</option>
          <option value="IMPORT_FAILED">Import Failed</option>
          <option value="SYSTEM_ALERT">System Alert</option>
        </select>
      </div>

      {loading ? (
        <div className="empty">
          Loading notifications...
        </div>
      ) : error ? (
        <div className="empty notification-error">
          {error}
        </div>
      ) : notifications.length === 0 ? (
        <div className="empty">
          No notifications
        </div>
      ) : (
        notifications.map((item) => (
          <div
            key={item.id}
            className={`notification-item ${
              item.is_read ? "read" : "unread"
            } priority-${item.priority?.toLowerCase()}`}
            onClick={() => handleNotificationClick(item)}
          >
            <div className="notification-icon">
              {getNotificationIcon(item.type)}
            </div>

            <div className="notification-content">
              <div className="notification-item-header">
                <h5>{item.title}</h5>

                <span
                  className={`notification-priority priority-${item.priority?.toLowerCase()}`}
                >
                  {item.priority}
                </span>
              </div>

              <p>{item.message}</p>

              <div className="notification-meta">
                <span
                  className="notification-time"
                  title={formatExactTime(item.created_at)}
                >
                  {formatRelativeTime(item.created_at)}
                </span>

                {!item.is_read && (
                  <span className="unread-dot"></span>
                )}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}