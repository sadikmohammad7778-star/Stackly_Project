import API from "./axios";

export const getAuditLogs = async (companyId) => {
  const response = await API.get("/audit-logs", {
    params: {
      company_id: companyId,
    },
  });

  return response.data;
};