import axiosInstance from "./axios";

export const getSystemHealth = async () => {
  const response = await axiosInstance.get("/health/");
  return response.data;
};

export const getSystemHealthDetails = async () => {
  const response = await axiosInstance.get("/health/details");
  return response.data;
};

export const getPerformanceSummary = async () => {
  const response = await axiosInstance.get("/health/performance");
  return response.data;
};

export const getPerformanceMetrics = async () => {
  const response = await axiosInstance.get("/health/performance/metrics");
  return response.data;
};