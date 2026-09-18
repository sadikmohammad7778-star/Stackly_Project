import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
} from "../api/notificationApi";

import { useAuth } from "./AuthContext";

const NotificationContext = createContext();

export function NotificationProvider({ children }) {
  const { token } = useAuth();

  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({});

  const loadNotifications = async (newFilters = filters) => {
    if (!token) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const data = await getNotifications({
        page: 1,
        page_size: 20,
        ...newFilters,
      });

      setNotifications(data.items || []);
      setUnreadCount(data.unread_count || 0);
    } catch (error) {
      console.error("Error loading notifications:", error);

      if (error.response?.status === 401) {
        setNotifications([]);
        setUnreadCount(0);
        setError("Session expired. Please login again.");
      } else {
        setError("Failed to load notifications.");
      }
    } finally {
      setLoading(false);
    }
  };

  const updateFilters = (newFilters) => {
    setFilters(newFilters);
  };

  const loadUnreadCount = async () => {
    if (!token) {
      return;
    }

    try {
      const data = await getUnreadCount();

      setUnreadCount(data.unread_count || 0);
    } catch (error) {
      console.error(
        "Error loading unread count:",
        error
      );

      if (error.response?.status === 401) {
        setUnreadCount(0);
      }
    }
  };

  const markNotificationAsRead = async (
    notificationId
  ) => {
    try {
      const updatedNotification =
        await markAsRead(notificationId);

      setNotifications((prev) =>
        prev.map((notification) =>
          notification.id === notificationId
            ? updatedNotification
            : notification
        )
      );

      await loadUnreadCount();
    } catch (error) {
      console.error(
        "Error marking notification as read:",
        error
      );
    }
  };

  const markAllNotificationsAsRead = async () => {
    try {
      await markAllAsRead();

      setNotifications((prev) =>
        prev.map((notification) => ({
          ...notification,
          is_read: true,
        }))
      );

      setUnreadCount(0);
    } catch (error) {
      console.error(
        "Error marking all notifications as read:",
        error
      );
    }
  };

  useEffect(() => {
    if (!token) {
      setNotifications([]);
      setUnreadCount(0);
      setLoading(false);
      setError(null);

      setFilters((previous) =>
        Object.keys(previous).length === 0
          ? previous
          : {}
      );

      return;
    }

    loadNotifications();

    const interval = setInterval(() => {
      loadNotifications();
    }, 30000);

    return () => {
      clearInterval(interval);
    };
  }, [token, filters]);

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        loading,
        error,
        filters,
        loadNotifications,
        updateFilters,
        loadUnreadCount,
        markAsRead: markNotificationAsRead,
        markAllAsRead: markAllNotificationsAsRead,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  return useContext(NotificationContext);
}