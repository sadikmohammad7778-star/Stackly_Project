import axiosInstance from "./axios";

export const createApprovalRequest = async (data) => {
  const response = await axiosInstance.post(
    "/workflows/requests",
    data
  );

  return response.data;
};

export const submitApprovalRequest = async (requestId, data = {}) => {
  const response = await axiosInstance.post(
    `/workflows/requests/${requestId}/submit`,
    data
  );

  return response.data;
};

export const getApprovalRequests = async () => {
  const response = await axiosInstance.get(
    "/workflows/requests"
  );

  return response.data;
};

export const getMyApprovalRequests = async () => {
  const response = await axiosInstance.get(
    "/workflows/my-requests"
  );

  return response.data;
};

export const getPendingApprovals = async () => {
  const response = await axiosInstance.get(
    "/workflows/pending"
  );

  return response.data;
};

export const getPendingApprovalCount = async () => {
  const response = await axiosInstance.get(
    "/workflows/pending-count"
  );

  return response.data;
};

export const getApprovalRequest = async (requestId) => {
  const response = await axiosInstance.get(
    `/workflows/requests/${requestId}`
  );

  return response.data;
};

export const getApprovalHistory = async (requestId) => {
  const response = await axiosInstance.get(
    `/workflows/requests/${requestId}/history`
  );

  return response.data;
};

export const approveRequest = async (requestId, data = {}) => {
  const response = await axiosInstance.post(
    `/workflows/requests/${requestId}/approve`,
    data
  );

  return response.data;
};

export const rejectRequest = async (requestId, data) => {
  const response = await axiosInstance.post(
    `/workflows/requests/${requestId}/reject`,
    data
  );

  return response.data;
};

export const cancelRequest = async (requestId, data = {}) => {
  const response = await axiosInstance.post(
    `/workflows/requests/${requestId}/cancel`,
    data
  );

  return response.data;
};

export const getWorkflowConfigurations = async () => {
  const response = await axiosInstance.get(
    "/workflows/configurations"
  );

  return response.data;
};

export const getWorkflowConfiguration = async (configId) => {
  const response = await axiosInstance.get(
    `/workflows/configurations/${configId}`
  );

  return response.data;
};

export const updateWorkflowConfiguration = async (configId, data) => {
  const response = await axiosInstance.put(
    `/workflows/configurations/${configId}`,
    data
  );

  return response.data;
};

export const createWorkflowConfiguration = async (data) => {
  const response = await axiosInstance.post(
    "/workflows/configurations",
    data
  );

  return response.data;
};