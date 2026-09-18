import API from "./axios";

export const getSalesReport = async () => {
  const response = await API.get(
    "/reports/sales/summary"
  );

  return response.data;
};

export const getStockReport = async () => {
  const response = await API.get(
    "/reports/stock/summary"
  );

  return response.data;
};

export const getDetailedReport = async (
  reportType,
  filters = {}
) => {
  const response = await API.get(
    `/reports/${reportType}`,
    {
      params: filters,
    }
  );

  return response.data;
};

export const getReportHistory = async (
  page = 1,
  pageSize = 20
) => {
  const response = await API.get(
    "/reports/history",
    {
      params: {
        page,
        page_size: pageSize,
      },
    }
  );

  return response.data;
};

export const downloadReportHistory = async (
  historyId
) => {
  const response = await API.get(
    `/reports/history/${historyId}/download`,
    {
      responseType: "blob",
    }
  );

  return response.data;
};

export const getScheduledReports = async () => {
  const response = await API.get(
    "/scheduled-reports"
  );

  return response.data;
};

export const createScheduledReport = async (
  data
) => {
  const response = await API.post(
    "/scheduled-reports",
    data
  );

  return response.data;
};

export const updateScheduledReport = async (
  id,
  data
) => {
  const response = await API.put(
    `/scheduled-reports/${id}`,
    data
  );

  return response.data;
};

export const toggleScheduledReport = async (
  id
) => {
  const response = await API.patch(
    `/scheduled-reports/${id}/toggle`
  );

  return response.data;
};

export const deleteScheduledReport = async (
  id
) => {
  const response = await API.delete(
    `/scheduled-reports/${id}`
  );

  return response.data;
};