import API from "../api/axios";

export const getDataQualityDashboard = async () => {
  const response = await API.get("/data-quality/dashboard");
  return response.data;
};

export const getDataQualityIssues = async (params = {}) => {
  const response = await API.get("/data-quality/issues", {
    params,
  });
  return response.data;
};

export const getDataQualityIssue = async (issueId) => {
  const response = await API.get(
    `/data-quality/issues/${issueId}`
  );
  return response.data;
};

export const updateDataQualityIssue = async (issueId, data) => {
  const response = await API.patch(
    `/data-quality/issues/${issueId}`,
    data
  );
  return response.data;
};

export const runDataQualityReconciliation = async () => {
  const response = await API.post(
    "/data-quality/reconcile/inventory"
  );
  return response.data;
};

export const getReconciliationHistory = async () => {
  const response = await API.get(
    "/data-quality/reconciliation/history"
  );
  return response.data;
};