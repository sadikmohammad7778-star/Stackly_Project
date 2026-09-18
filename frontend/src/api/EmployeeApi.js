import axiosInstance from "./axios";

export const getEmployees = async () => {
  const response = await axiosInstance.get("/employees");
  return response.data;
};

export const getEmployeeById = async (id) => {
  const response = await axiosInstance.get(`/employees/${id}`);
  return response.data;
};

export const createEmployee = async (employee) => {
  const response = await axiosInstance.post("/employees", employee);
  return response.data;
};

export const updateEmployee = async (id, employee) => {
  const response = await axiosInstance.put(`/employees/${id}`, employee);
  return response.data;
};

export const deleteEmployee = async (id) => {
  const response = await axiosInstance.delete(`/employees/${id}`);
  return response.data;
};