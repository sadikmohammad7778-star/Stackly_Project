import axiosInstance from "./axios";

const BASE_URL = "/integrations";

export const getIntegrations = async () => {
  const response = await axiosInstance.get(`${BASE_URL}/`);
  return response.data;
};

export const getIntegration = async (integrationId) => {
  const response = await axiosInstance.get(
    `${BASE_URL}/${integrationId}`
  );
  return response.data;
};

export const createIntegration = async (data) => {
  const response = await axiosInstance.post(`${BASE_URL}/`, data);
  return response.data;
};

export const updateIntegration = async (integrationId, data) => {
  const response = await axiosInstance.put(
    `${BASE_URL}/${integrationId}`,
    data
  );
  return response.data;
};

export const deleteIntegration = async (integrationId) => {
  const response = await axiosInstance.delete(
    `${BASE_URL}/${integrationId}`
  );
  return response.data;
};

export const testIntegrationConnection = async (integrationId) => {
  const response = await axiosInstance.post(
    `${BASE_URL}/${integrationId}/test-connection`
  );
  return response.data;
};

export const uploadIntegrationFile = async (integrationId, file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axiosInstance.post(
    `${BASE_URL}/${integrationId}/upload`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

export const previewIntegrationFile = async (integrationId) => {
  const response = await axiosInstance.get(
    `${BASE_URL}/${integrationId}/preview`
  );
  return response.data;
};

export const getIntegrationMappings = async (integrationId) => {
  const response = await axiosInstance.get(
    `${BASE_URL}/${integrationId}/mappings`
  );
  return response.data;
};

export const saveIntegrationMappings = async (integrationId, mappings) => {
  const response = await axiosInstance.put(
    `${BASE_URL}/${integrationId}/mappings`,
    { mappings }
  );
  return response.data;
};

export const synchronizeIntegration = async (integrationId, triggerType) => {
  const response = await axiosInstance.post(
    `${BASE_URL}/${integrationId}/sync`,
    { trigger_type: triggerType }
  );
  return response.data;
};

export const getSyncHistory = async (
  integrationId,
  limit = 20,
  offset = 0
) => {
  const response = await axiosInstance.get(
    `${BASE_URL}/${integrationId}/syncs`,
    { params: { limit, offset } }
  );
  return response.data;
};

export const getSyncDetails = async (integrationId, syncId) => {
  const response = await axiosInstance.get(
    `${BASE_URL}/${integrationId}/syncs/${syncId}`
  );
  return response.data;
};

export const getSyncErrors = async (
  integrationId,
  syncId,
  limit = 20,
  offset = 0
) => {
  const response = await axiosInstance.get(
    `${BASE_URL}/${integrationId}/syncs/${syncId}/errors`,
    { params: { limit, offset } }
  );
  return response.data;
};

export const retrySyncError = async (
  integrationId,
  syncId,
  errorId
) => {
  const response = await axiosInstance.post(
    `${BASE_URL}/${integrationId}/syncs/${syncId}/errors/${errorId}/retry`
  );
  return response.data;
};

export const getIntegrationSchedule = async (integrationId) => {
  const response = await axiosInstance.get(
    `${BASE_URL}/${integrationId}/schedule`
  );
  return response.data;
};

export const createIntegrationSchedule = async (integrationId, data) => {
  const response = await axiosInstance.post(
    `${BASE_URL}/${integrationId}/schedule`,
    data
  );
  return response.data;
};

export const updateIntegrationSchedule = async (integrationId, data) => {
  const response = await axiosInstance.put(
    `${BASE_URL}/${integrationId}/schedule`,
    data
  );
  return response.data;
};

export const deleteIntegrationSchedule = async (integrationId) => {
  const response = await axiosInstance.delete(
    `${BASE_URL}/${integrationId}/schedule`
  );
  return response.data;
};