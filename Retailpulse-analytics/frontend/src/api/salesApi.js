import API from "./axios";

export const getSales = async () => {
  const response = await API.get("/sales/");
  return response.data;
};

export const createSale = async (sale) => {
  const response = await API.post("/sales/", sale);
  return response.data;
};

export const updateSale = async (id, sale) => {
  const response = await API.put(`/sales/${id}`, sale);
  return response.data;
};

export const deleteSale = async (id) => {
  const response = await API.delete(`/sales/${id}`);
  return response.data;
};

export const getSaleSummary = async () => {
  const response = await API.get("/sales/summary/dashboard");
  return response.data;
};