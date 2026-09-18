import axiosInstance from "./axios";

// Get All Companies
export const getCompanies = async () => {
  const response = await axiosInstance.get("/companies");
  return response.data;
};

// Get Company By ID
export const getCompanyById = async (id) => {
  const response = await axiosInstance.get(`/companies/${id}`);
  return response.data;
};

// Create Company
export const createCompany = async (company) => {
  const response = await axiosInstance.post("/companies", company);
  return response.data;
};

// Update Company
export const updateCompany = async (id, company) => {
  const response = await axiosInstance.put(
    `/companies/${id}`,
    company
  );

  return response.data;
};

// Delete Company
export const deleteCompany = async (id) => {
  const response = await axiosInstance.delete(`/companies/${id}`);
  return response.data;
};