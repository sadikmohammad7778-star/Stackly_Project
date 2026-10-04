import axiosInstance from "./axios";

export const uploadImport = async (importType, file) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await axiosInstance.post(
    `/imports/upload?import_type=${importType}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

export const validateImport = async (importId) => {
  const response = await axiosInstance.post(
    "/imports/validate",
    {
      import_id: importId,
    }
  );

  return response.data;
};

export const processImport = async (importId) => {
  const response = await axiosInstance.post(
    "/imports/process",
    {
      import_id: importId,
    }
  );

  return response.data;
};

export const getImportStatus = async (importId) => {
  const response = await axiosInstance.get(
    `/imports/${importId}/status`
  );

  return response.data;
};

export const getImportHistory = async () => {
  const response = await axiosInstance.get(
    "/imports/history"
  );

  return response.data;
};

export const getImportDetails = async (importId) => {
  const response = await axiosInstance.get(
    `/imports/${importId}`
  );

  return response.data;
};

export const cancelImport = async (importId) => {
  const response = await axiosInstance.post(
    `/imports/${importId}/cancel`
  );

  return response.data;
};

export const downloadTemplate = async (importType) => {
  const response = await axiosInstance.get(
    `/imports/template/${importType}`,
    {
      responseType: "blob",
    }
  );

  return response;
};

export const downloadFailedRecords = async (importId) => {
  const response = await axiosInstance.get(
    `/imports/${importId}/failed-records`,
    {
      responseType: "blob",
    }
  );

  return response;
};