import { useEffect, useState } from "react";
import {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
  deleteNotification,
} from "../../api/notificationApi";

import "./NotificationDropdown.css";

export default function NotificationDropdown({ refreshUnreadCount }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const loadNotifications = async () => {
    try {
      const [notificationData, unreadData] = await Promise.all([
        getNotifications(),
        getUnreadCount(),
      ]);

      setNotifications(notificationData);
      setUnreadCount(unreadData.count);
    } catch (error) {
      console.error("Error loading notifications:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();

    const interval = setInterval(() => {
      loadNotifications();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleRead = async (id) => {
    try {
      await markAsRead(id);
      await loadNotifications();

      if (refreshUnreadCount) {
        refreshUnreadCount();
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleReadAll = async () => {
    try {
      await markAllAsRead();
      await loadNotifications();

      if (refreshUnreadCount) {
        refreshUnreadCount();
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteNotification(id);
      await loadNotifications();

      if (refreshUnreadCount) {
        refreshUnreadCount();
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="notification-dropdown">
      <div className="notification-header">
        <h4>Notifications</h4>

        {unreadCount > 0 && (
          <button
            className="mark-all-btn"
            onClick={handleReadAll}
          >
            Mark All
          </button>
        )}
      </div>

      {loading ? (
        <p className="empty">Loading...</p>
      ) : notifications.length === 0 ? (
        <p className="empty">No Notifications</p>
      ) : (
        notifications.map((item) => (
          <div
            key={item.id}
            className={`notification-item ${
              item.is_read ? "read" : "unread"
            }`}
          >
            <div
              className="notification-content"
              onClick={() => handleRead(item.id)}
            >
              <h5>{item.title}</h5>

              <p>{item.message}</p>

              <small>
                {new Date(item.created_at).toLocaleString()}
              </small>
            </div>

            <button
              className="delete-btn"
              onClick={() => handleDelete(item.id)}
            >
              ✕
            </button>
          </div>
        ))
      )}
    </div>
  );
}