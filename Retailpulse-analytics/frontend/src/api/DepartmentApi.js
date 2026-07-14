import axiosInstance from "./axios";

export const getDepartments = async () => {
  const response = await axiosInstance.get("/departments");
  return response.data;
};

export const getDepartmentById = async (id) => {
  const response = await axiosInstance.get(`/departments/${id}`);
  return response.data;
};

export const createDepartment = async (department) => {
  const response = await axiosInstance.post("/departments", department);
  return response.data;
};

export const updateDepartment = async (id, department) => {
  const response = await axiosInstance.put(`/departments/${id}`, department);
  return response.data;
};

export const deleteDepartment = async (id) => {
  const response = await axiosInstance.delete(`/departments/${id}`);
  return response.data;
};