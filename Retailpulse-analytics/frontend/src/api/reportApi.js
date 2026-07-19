import API from "./axios";

export const getSalesReport = async () => {
  const response = await API.get("/reports/sales");
  return response.data;
};

export const getStockReport = async () => {
  const response = await API.get("/reports/stock");
  return response.data;
};