import axiosInstance from "./axios";

// Get All Attendance
export const getAttendance = async () => {
  const response = await axiosInstance.get("/attendance");
  return response.data;
};

// Get Attendance By ID
export const getAttendanceById = async (id) => {
  const response = await axiosInstance.get(`/attendance/${id}`);
  return response.data;
};

// Create Attendance
export const createAttendance = async (attendance) => {
  const response = await axiosInstance.post("/attendance", attendance);
  return response.data;
};

// Update Attendance
export const updateAttendance = async (id, attendance) => {
  const response = await axiosInstance.put(`/attendance/${id}`, attendance);
  return response.data;
};

// Delete Attendance
export const deleteAttendance = async (id) => {
  const response = await axiosInstance.delete(`/attendance/${id}`);
  return response.data;
};