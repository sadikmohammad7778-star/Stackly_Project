import API from "./axios";

export const getRevenueReport = async () => {
  const response = await API.get("/analytics/revenue");
  return response.data;
};

export const getInventoryReport = async () => {
  const response = await API.get("/analytics/inventory");
  return response.data;
};