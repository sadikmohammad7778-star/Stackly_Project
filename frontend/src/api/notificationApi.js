import API from "./axios";

export const getNotifications = async (params = {}) => {
  const response = await API.get("/api/notifications", {
    params,
  });
  return response.data;
};

export const getUnreadCount = async () => {
  const response = await API.get("/api/notifications/unread-count");
  return response.data;
};

export const markAsRead = async (id) => {
  const response = await API.patch(`/api/notifications/${id}/read`);
  return response.data;
};

export const markAllAsRead = async () => {
  const response = await API.patch("/api/notifications/read-all");
  return response.data;
};