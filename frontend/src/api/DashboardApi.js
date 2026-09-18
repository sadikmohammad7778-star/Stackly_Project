import axiosInstance from "./axios";

export const getDashboardData = async () => {
  const response = await axiosInstance.get("/dashboard/summary");
  return response.data;
};

export const getSalesByCategory = async () => {
  const response = await axiosInstance.get(
    "/dashboard/sales-by-category"
  );
  return response.data;
};

export const getMonthlySales = async () => {
  const response = await axiosInstance.get(
    "/dashboard/monthly-sales"
  );
  return response.data;
};

export const getTopProducts = async () => {
  const response = await axiosInstance.get(
    "/dashboard/top-products"
  );
  return response.data;
};