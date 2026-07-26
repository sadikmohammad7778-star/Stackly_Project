import API from "./axios";

// ----------------------
// Excel Export
// ----------------------

export const exportSalesExcel = async () => {
  const response = await API.get("/export/sales/excel", {
    responseType: "blob",
  });

  return response.data;
};

export const exportInventoryExcel = async () => {
  const response = await API.get("/export/inventory/excel", {
    responseType: "blob",
  });

  return response.data;
};

// ----------------------
// PDF Export
// ----------------------

export const exportSalesPDF = async () => {
  const response = await API.get("/export/sales/pdf", {
    responseType: "blob",
  });

  return response.data;
};

export const exportInventoryPDF = async () => {
  const response = await API.get("/export/inventory/pdf", {
    responseType: "blob",
  });

  return response.data;
};