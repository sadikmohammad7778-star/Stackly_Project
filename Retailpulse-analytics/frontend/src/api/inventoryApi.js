import API from "./axios";

export const getInventory = async (
  companyId,
  search = "",
  status = ""
) => {
  const response = await API.get("/inventory", {
    params: {
      company_id: companyId,
      search,
      status,
    },
  });

  return response.data;
};

export const getDashboard = async () => {
  const response = await API.get("/inventory/dashboard");
  return response.data;
};

export const getCategoryChart = async (companyId) => {
  const response = await API.get(
    `/inventory/category-chart?company_id=${companyId}`
  );
  return response.data;
};

export const getStatusChart = async (companyId) => {
  const response = await API.get(
    `/inventory/status-chart?company_id=${companyId}`
  );
  return response.data;
};

export const getMovements = async () => {
  const response = await API.get("/inventory/movements");
  return response.data;
};

export const addStock = async (data) => {
  const response = await API.post("/inventory/add-stock", data);
  return response.data;
};

export const removeStock = async (data) => {
  const response = await API.post("/inventory/remove-stock", data);
  return response.data;
};

export const adjustStock = async (data) => {
  const response = await API.post("/inventory/adjust-stock", data);
  return response.data;
};