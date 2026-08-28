import axiosInstance from "./axios";

// ============================================================
// Upload CSV file
// ============================================================

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


// ============================================================
// Validate import
// ============================================================

export const validateImport = async (importId) => {
  const response = await axiosInstance.post(
    "/imports/validate",
    {
      import_id: importId,
    }
  );

  return response.data;
};


// ============================================================
// Process import
// ============================================================

export const processImport = async (importId) => {
  const response = await axiosInstance.post(
    "/imports/process",
    {
      import_id: importId,
    }
  );

  return response.data;
};


// ============================================================
// Import history
// ============================================================

export const getImportHistory = async () => {
  const response = await axiosInstance.get(
    "/imports/history"
  );

  return response.data;
};


// ============================================================
// Import details
// ============================================================

export const getImportDetails = async (importId) => {
  const response = await axiosInstance.get(
    `/imports/${importId}`
  );

  return response.data;
};


// ============================================================
// Download failed records
// ============================================================

export const downloadFailedRecords = async (importId) => {
  const response = await axiosInstance.get(
    `/imports/${importId}/failed-records`,
    {
      responseType: "blob",
    }
  );

  return response;
};