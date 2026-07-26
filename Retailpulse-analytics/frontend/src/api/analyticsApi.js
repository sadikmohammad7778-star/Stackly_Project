import API from "./axios";

export const getDashboardKPIs = async (companyId, period) => {
  const response = await API.get(
    `/analytics/dashboard?company_id=${companyId}&period=${period}`
  );
  return response.data;
};

export const getRevenueTrend = async (companyId, period) => {
  const response = await API.get(
    `/analytics/revenue-trend?company_id=${companyId}&period=${period}`
  );
  return response.data;
};

export const getTopProducts = async (companyId, period) => {
  const response = await API.get(
    `/analytics/top-products?company_id=${companyId}&period=${period}`
  );
  return response.data;
};

export const getTopCategories = async (companyId, period) => {
  const response = await API.get(
    `/analytics/top-categories?company_id=${companyId}&period=${period}`
  );
  return response.data;
};

export const getPaymentMethods = async (companyId, period) => {
  const response = await API.get(
    `/analytics/payment-methods?company_id=${companyId}&period=${period}`
  );
  return response.data;
};

export const getSalesChannels = async (companyId, period) => {
  const response = await API.get(
    `/analytics/sales-channels?company_id=${companyId}&period=${period}`
  );
  return response.data;
};

export const getInventoryCategory = async (companyId, period) => {
  const response = await API.get(
    `/analytics/inventory-category?company_id=${companyId}&period=${period}`
  );
  return response.data;
};

export const getStockStatus = async (companyId, period) => {
  const response = await API.get(
    `/analytics/stock-status?company_id=${companyId}&period=${period}`
  );
  return response.data;
};

export const getInventoryValue = async (companyId, period) => {
  const response = await API.get(
    `/analytics/inventory-value?company_id=${companyId}&period=${period}`
  );
  return response.data;
};