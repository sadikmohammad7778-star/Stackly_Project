import API from "./axios";

export const getAuditLogs = async ({
  page = 1,
  limit = 10,
  search = "",
  userId = "",
  action = "",
  module = "",
  resourceType = "",
  status = "",
  dateFrom = "",
  dateTo = "",
  sortOrder = "desc",
} = {}) => {
  const params = {
    page,
    limit,
    search: search || undefined,
    user_id: userId || undefined,
    action: action || undefined,
    module: module || undefined,
    resource_type: resourceType || undefined,
    status: status || undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
    sort_order: sortOrder,
  };

  const response = await API.get("/audit-logs/", {
    params,
  });

  return response.data;
};

export const getAllAuditLogs = async ({
  search = "",
  userId = "",
  action = "",
  module = "",
  resourceType = "",
  status = "",
  dateFrom = "",
  dateTo = "",
  sortOrder = "desc",
} = {}) => {
  const allLogs = [];

  let page = 1;
  let totalPages = 1;

  while (page <= totalPages) {
    const params = {
      page,
      limit: 100,
      search: search || undefined,
      user_id: userId || undefined,
      action: action || undefined,
      module: module || undefined,
      resource_type: resourceType || undefined,
      status: status || undefined,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
      sort_order: sortOrder,
    };

    const response = await API.get("/audit-logs/", {
      params,
    });

    const data = response.data;

    allLogs.push(...(data.items || []));

    totalPages = data.total_pages || 1;
    page++;
  }

  return allLogs;
};

export const getAuditLogById = async (auditLogId) => {
  const response = await API.get(
    `/audit-logs/${auditLogId}`
  );

  return response.data;
};