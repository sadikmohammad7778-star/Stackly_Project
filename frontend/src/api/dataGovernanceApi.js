import axiosInstance from "./axios";

export const getGovernanceDashboard = () =>
  axiosInstance.get("/data-governance/dashboard");

export const getGovernanceRoles = () =>
  axiosInstance.get("/data-governance/roles");

export const getGovernancePermissions = () =>
  axiosInstance.get("/data-governance/permissions");

export const getPermissionMatrix = () =>
  axiosInstance.get("/data-governance/permission-matrix");

export const updateRolePermissions = (role, permissionIds) =>
  axiosInstance.put(
    `/data-governance/roles/${encodeURIComponent(role)}/permissions`,
    { permission_ids: permissionIds }
  );

export const revokeRolePermission = (role, permissionId) =>
  axiosInstance.delete(
    `/data-governance/roles/${encodeURIComponent(role)}/permissions/${permissionId}`
  );

export const submitAccessRequest = (data) =>
  axiosInstance.post("/access-requests", data);

export const getMyAccessRequests = () =>
  axiosInstance.get("/access-requests/mine");

export const getPendingAccessRequests = () =>
  axiosInstance.get("/access-requests/pending");

export const reviewAccessRequest = (requestId, decision, comments) =>
  axiosInstance.post(`/access-requests/${requestId}/review`, {
    decision,
    comments,
  });

export const getAccessRequestHistory = (requestId) =>
  axiosInstance.get(`/access-requests/${requestId}/history`);