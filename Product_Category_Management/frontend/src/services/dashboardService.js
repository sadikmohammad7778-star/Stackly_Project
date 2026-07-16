import API from "./api";

export const getDashboardSummary = () => {
  return API.get("/dashboard/summary");
};