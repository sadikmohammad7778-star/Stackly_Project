import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// =====================================
// Attach JWT Token
// =====================================

API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// =====================================
// Customer CRUD
// =====================================

export const getCustomers = async () => {
  const response = await API.get("/customers/");
  return response.data;
};

export const getCustomer = async (id) => {
  const response = await API.get(`/customers/${id}`);
  return response.data;
};

export const createCustomer = async (data) => {
  const response = await API.post("/customers/", data);
  return response.data;
};

export const updateCustomer = async (id, data) => {
  const response = await API.put(`/customers/${id}`, data);
  return response.data;
};

export const deleteCustomer = async (id) => {
  const response = await API.delete(`/customers/${id}`);
  return response.data;
};

export const changeCustomerStatus = async (id, status) => {
  const response = await API.patch(
    `/customers/${id}/status`,
    null,
    {
      params: { status },
    }
  );

  return response.data;
};

// =====================================
// Search & Filter
// =====================================

export const searchCustomers = async (search) => {
  const response = await API.get("/customers/search/", {
    params: { search },
  });

  return response.data;
};

export const filterCustomers = async (filters) => {
  const response = await API.get("/customers/filter/", {
    params: filters,
  });

  return response.data;
};

// =====================================
// Dashboard
// =====================================

export const customerDashboard = async () => {
  const response = await API.get("/customers/dashboard");

  return response.data;
};

// =====================================
// Analytics & Charts
// =====================================

export const customerGrowth = async () => {
  const response = await API.get("/customers/growth");

  return response.data;
};

export const topCustomers = async () => {
  const response = await API.get("/customers/top-customers");

  return response.data;
};

export const revenueBySegment = async () => {
  const response = await API.get(
    "/customers/revenue-by-segment"
  );

  return response.data;
};

export const customerDistribution = async () => {
  const response = await API.get(
    "/customers/distribution"
  );

  return response.data;
};

// =====================================
// Customer Details
// =====================================

export const customerPurchaseHistory = async (id) => {
  const response = await API.get(
    `/customers/${id}/purchase-history`
  );

  return response.data;
};

export const customerTimeline = async (id) => {
  const response = await API.get(
    `/customers/${id}/timeline`
  );

  return response.data;
};

// =====================================
// Export
// =====================================

export const exportCustomersCSV = async () => {
  const response = await API.get(
    "/customers/export/csv",
    {
      responseType: "blob",
    }
  );

  return response;
};

export const exportCustomersPDF = async () => {
  const response = await API.get(
    "/customers/export/pdf",
    {
      responseType: "blob",
    }
  );

  return response;
};

export default API;