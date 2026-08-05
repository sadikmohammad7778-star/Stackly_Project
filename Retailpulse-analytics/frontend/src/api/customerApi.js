import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Attach JWT Token
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// =========================
// Customer CRUD
// =========================

export const getCustomers = () =>
  API.get("/customers/");

export const getCustomer = (id) =>
  API.get(`/customers/${id}`);

export const createCustomer = (data) =>
  API.post("/customers/", data);

export const updateCustomer = (id, data) =>
  API.put(`/customers/${id}`, data);

export const deleteCustomer = (id) =>
  API.delete(`/customers/${id}`);

// =========================
// Search & Filter
// =========================

export const searchCustomers = (search) =>
  API.get("/customers/search/", {
    params: { search },
  });

export const filterCustomers = (filters) =>
  API.get("/customers/filter/", {
    params: filters,
  });

// =========================
// Dashboard
// =========================

export const customerDashboard = () =>
  API.get("/customers/dashboard");

// =========================
// Charts
// =========================

export const customerGrowth = () =>
  API.get("/customers/growth");

export const topCustomers = () =>
  API.get("/customers/top-customers");

export const revenueByType = () =>
  API.get("/customers/revenue-by-type");

export const customerDistribution = () =>
  API.get("/customers/distribution");

// =========================
// Customer Details
// =========================

export const customerPurchaseHistory = (id) =>
  API.get(`/customers/${id}/purchase-history`);

export const customerTimeline = (id) =>
  API.get(`/customers/${id}/timeline`);

// =========================
// Export
// =========================

export const exportCustomersCSV = () =>
  API.get("/customers/export/csv", {
    responseType: "blob",
  });

export const exportCustomersPDF = () =>
  API.get("/customers/export/pdf", {
    responseType: "blob",
  });