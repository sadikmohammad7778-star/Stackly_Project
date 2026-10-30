import { useCallback, useEffect, useState } from "react";
import {
  getGovernanceDashboard,
  getGovernanceRoles,
  getGovernancePermissions,
  getPermissionMatrix,
  updateRolePermissions,
  revokeRolePermission,
  submitAccessRequest,
  getMyAccessRequests,
  getPendingAccessRequests,
  reviewAccessRequest,
  getAccessRequestHistory,
} from "../api/dataGovernanceApi";
import "./DataGovernance.css";

const sections = [
  "Overview",
  "Roles & Permissions",
  "Access Requests",
  "Approvals",
];

export default function DataGovernance() {
  const [activeSection, setActiveSection] = useState("Overview");
  const [dashboard, setDashboard] = useState(null);
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [matrix, setMatrix] = useState([]);
  const [myRequests, setMyRequests] = useState([]);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [selectedRole, setSelectedRole] = useState("");
  const [selectedPermissions, setSelectedPermissions] = useState([]);
  const [permissionToRequest, setPermissionToRequest] = useState("");
  const [requestReason, setRequestReason] = useState("");
  const [requestPriority, setRequestPriority] = useState("medium");
  const [history, setHistory] = useState([]);
  const [historyRequestId, setHistoryRequestId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    const results = await Promise.allSettled([
      getGovernanceDashboard(),
      getGovernanceRoles(),
      getGovernancePermissions(),
      getPermissionMatrix(),
      getMyAccessRequests(),
      getPendingAccessRequests(),
    ]);

    const [
      dashboardResult,
      rolesResult,
      permissionsResult,
      matrixResult,
      myRequestsResult,
      pendingResult,
    ] = results;

    if (dashboardResult.status === "fulfilled") {
      setDashboard(dashboardResult.value.data);
    }

    if (rolesResult.status === "fulfilled") {
      setRoles(rolesResult.value.data);
    }

    if (permissionsResult.status === "fulfilled") {
      setPermissions(permissionsResult.value.data);
    }

    if (matrixResult.status === "fulfilled") {
      setMatrix(matrixResult.value.data.matrix || []);
    }

    if (myRequestsResult.status === "fulfilled") {
      setMyRequests(myRequestsResult.value.data);
    }

    if (pendingResult.status === "fulfilled") {
      setPendingRequests(pendingResult.value.data);
    }

    const failures = results.filter(
      (result) => result.status === "rejected"
    );

    if (failures.length > 0) {
      setError(
        "Some sections could not be loaded. Check your permissions and backend connection."
      );
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const getRolePermissions = (role) => {
    const entry = matrix.find((item) => item.role === role);
    return entry?.permissions || [];
  };

  const openRole = (role) => {
    setSelectedRole(role);

    const assigned = getRolePermissions(role);

    setSelectedPermissions(
      permissions
        .filter((permission) => assigned.includes(permission.code))
        .map((permission) => permission.id)
    );
  };

  const togglePermission = (permissionId) => {
    setSelectedPermissions((current) =>
      current.includes(permissionId)
        ? current.filter((id) => id !== permissionId)
        : [...current, permissionId]
    );
  };

  const savePermissions = async () => {
    if (!selectedRole) return;

    const confirmed = window.confirm(
      `Replace all assigned permissions for "${selectedRole}"?`
    );

    if (!confirmed) return;

    setActionLoading(true);
    setError("");
    setMessage("");

    try {
      await updateRolePermissions(selectedRole, selectedPermissions);

      setMessage(`Permissions updated for ${selectedRole}.`);
      setSelectedRole("");
      await loadData();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to update role permissions."
      );
    } finally {
      setActionLoading(false);
    }
  };

  const revokePermission = async (role, permission) => {
    const confirmed = window.confirm(
      `Revoke ${permission.code} from ${role}?`
    );

    if (!confirmed) return;

    setActionLoading(true);
    setError("");
    setMessage("");

    try {
      await revokeRolePermission(role, permission.id);
      setMessage(`${permission.code} revoked from ${role}.`);
      await loadData();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to revoke permission."
      );
    } finally {
      setActionLoading(false);
    }
  };

  const createRequest = async (event) => {
    event.preventDefault();

    if (!permissionToRequest || !requestReason.trim()) {
      setError("Select a permission and enter a reason.");
      return;
    }

    setActionLoading(true);
    setError("");
    setMessage("");

    try {
      await submitAccessRequest({
        permission_id: Number(permissionToRequest),
        reason: requestReason.trim(),
        priority: requestPriority,
      });

      setMessage("Access request submitted successfully.");
      setPermissionToRequest("");
      setRequestReason("");
      setRequestPriority("medium");
      await loadData();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to submit access request."
      );
    } finally {
      setActionLoading(false);
    }
  };

  const reviewRequest = async (requestId, decision) => {
    const comments = window.prompt(
      `Enter a comment for this ${decision} decision:`
    );

    if (comments === null) return;

    setActionLoading(true);
    setError("");
    setMessage("");

    try {
      await reviewAccessRequest(requestId, decision, comments);
      setMessage(`Request ${requestId} ${decision}d successfully.`);
      await loadData();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to review access request."
      );
    } finally {
      setActionLoading(false);
    }
  };

  const showHistory = async (requestId) => {
    setError("");

    try {
      const response = await getAccessRequestHistory(requestId);
      setHistory(response.data);
      setHistoryRequestId(requestId);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to load request history."
      );
    }
  };

  const assignedPermissionCodes = new Set(
    matrix.flatMap((item) => item.permissions || [])
  );

  const availablePermissions = permissions.filter(
    (permission) => !assignedPermissionCodes.has(permission.code)
  );

  if (loading) {
    return (
      <div className="governance-page">
        <div className="governance-loading">Loading Data Governance...</div>
      </div>
    );
  }

  return (
    <div className="governance-page">
      <div className="governance-header">
        <div>
          <span className="governance-eyebrow">SECURITY & COMPLIANCE</span>
          <h1>Data Governance</h1>
          <p>Manage access, permissions, approvals, and governance activity.</p>
        </div>

        <button
          className="governance-refresh"
          onClick={loadData}
          disabled={actionLoading}
        >
          Refresh Data
        </button>
      </div>

      {error && <div className="governance-alert error">{error}</div>}
      {message && <div className="governance-alert success">{message}</div>}

      <div className="governance-tabs">
        {sections.map((section) => (
          <button
            key={section}
            className={activeSection === section ? "active" : ""}
            onClick={() => setActiveSection(section)}
          >
            {section}
          </button>
        ))}
      </div>

      {activeSection === "Overview" && (
        <>
          <div className="governance-stats">
            <StatCard label="Total Users" value={dashboard?.total_users ?? 0} />
            <StatCard label="Active Users" value={dashboard?.active_users ?? 0} />
            <StatCard
              label="Inactive Users"
              value={dashboard?.inactive_users ?? 0}
            />
            <StatCard label="Total Roles" value={dashboard?.total_roles ?? 0} />
            <StatCard
              label="Pending Requests"
              value={dashboard?.pending_access_requests ?? 0}
            />
            <StatCard
              label="Elevated Users"
              value={dashboard?.users_with_elevated_permissions ?? 0}
            />
          </div>

          <section className="governance-panel">
            <h2>Recent Permission Changes</h2>

            {dashboard?.recent_permission_changes?.length ? (
              <div className="governance-table-wrap">
                <table className="governance-table">
                  <thead>
                    <tr>
                      <th>Action</th>
                      <th>Module</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboard.recent_permission_changes.map((item, index) => (
                      <tr key={item.id ?? index}>
                        <td>{item.action}</td>
                        <td>{item.module}</td>
                        <td>{item.created_at || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="governance-empty">
                No recent permission changes were found.
              </p>
            )}
          </section>
        </>
      )}

      {activeSection === "Roles & Permissions" && (
        <div className="governance-two-column">
          <section className="governance-panel">
            <h2>Roles</h2>

            {roles.length === 0 ? (
              <p className="governance-empty">No roles found.</p>
            ) : (
              roles.map((role) => (
                <button
                  key={role.role}
                  className={`governance-role ${
                    selectedRole === role.role ? "selected" : ""
                  }`}
                  onClick={() => openRole(role.role)}
                >
                  <span>
                    <strong>{role.role}</strong>
                    <small>{role.user_count} users</small>
                  </span>
                  <span>{getRolePermissions(role.role).length} permissions</span>
                </button>
              ))
            )}
          </section>

          <section className="governance-panel">
            <h2>Permission Matrix</h2>

            {!selectedRole ? (
              <p className="governance-empty">
                Select a role to manage its permissions.
              </p>
            ) : (
              <>
                <h3>{selectedRole}</h3>

                <div className="governance-permission-list">
                  {permissions.map((permission) => (
                    <label
                      className="governance-permission-option"
                      key={permission.id}
                    >
                      <input
                        type="checkbox"
                        checked={selectedPermissions.includes(permission.id)}
                        onChange={() => togglePermission(permission.id)}
                      />
                      <span>
                        <strong>{permission.code}</strong>
                        <small>
                          {permission.module} · {permission.action}
                        </small>
                      </span>
                    </label>
                  ))}
                </div>

                <div className="governance-actions">
                  <button
                    className="governance-primary"
                    onClick={savePermissions}
                    disabled={actionLoading}
                  >
                    Save Permissions
                  </button>

                  <button
                    className="governance-secondary"
                    onClick={() => setSelectedRole("")}
                  >
                    Cancel
                  </button>
                </div>

                <h3>Currently Assigned</h3>

                {getRolePermissions(selectedRole).length === 0 ? (
                  <p className="governance-empty">
                    No permissions assigned.
                  </p>
                ) : (
                  getRolePermissions(selectedRole).map((code) => {
                    const permission = permissions.find(
                      (item) => item.code === code
                    );

                    return (
                      <div className="governance-assigned" key={code}>
                        <span>{code}</span>
                        <button
                          onClick={() =>
                            permission &&
                            revokePermission(selectedRole, permission)
                          }
                          disabled={actionLoading || !permission}
                        >
                          Revoke
                        </button>
                      </div>
                    );
                  })
                )}
              </>
            )}
          </section>
        </div>
      )}

      {activeSection === "Access Requests" && (
        <div className="governance-two-column">
          <section className="governance-panel">
            <h2>Request Access</h2>

            <form onSubmit={createRequest} className="governance-form">
              <label>
                Permission
                <select
                  value={permissionToRequest}
                  onChange={(event) => setPermissionToRequest(event.target.value)}
                  required
                >
                  <option value="">Select permission</option>
                  {availablePermissions.map((permission) => (
                    <option key={permission.id} value={permission.id}>
                      {permission.code}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Reason
                <textarea
                  value={requestReason}
                  onChange={(event) => setRequestReason(event.target.value)}
                  minLength={5}
                  maxLength={2000}
                  placeholder="Explain why you need this permission."
                  required
                />
              </label>

              <label>
                Priority
                <select
                  value={requestPriority}
                  onChange={(event) => setRequestPriority(event.target.value)}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </label>

              <button
                type="submit"
                className="governance-primary"
                disabled={actionLoading}
              >
                Submit Request
              </button>
            </form>
          </section>

          <section className="governance-panel">
            <h2>My Requests</h2>

            <RequestTable
              requests={myRequests}
              onHistory={showHistory}
            />
          </section>
        </div>
      )}

      {activeSection === "Approvals" && (
        <section className="governance-panel">
          <h2>Pending Approvals</h2>

          {pendingRequests.length === 0 ? (
            <p className="governance-empty">No pending approvals.</p>
          ) : (
            <div className="governance-table-wrap">
              <table className="governance-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Requester</th>
                    <th>Permission</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingRequests.map((request) => (
                    <tr key={request.id}>
                      <td>#{request.id}</td>
                      <td>{request.requested_by}</td>
                      <td>
                        {request.requested_changes?.permission_code || "—"}
                      </td>
                      <td>{request.priority}</td>
                      <td>
                        <span className="governance-status pending">
                          {request.status}
                        </span>
                      </td>
                      <td>
                        <div className="governance-inline-actions">
                          <button
                            onClick={() =>
                              reviewRequest(request.id, "approve")
                            }
                            disabled={actionLoading}
                          >
                            Approve
                          </button>
                          <button
                            className="danger"
                            onClick={() =>
                              reviewRequest(request.id, "reject")
                            }
                            disabled={actionLoading}
                          >
                            Reject
                          </button>
                          <button
                            onClick={() => showHistory(request.id)}
                          >
                            History
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {historyRequestId !== null && (
        <section className="governance-panel">
          <div className="governance-history-header">
            <h2>History for Request #{historyRequestId}</h2>
            <button
              className="governance-secondary"
              onClick={() => {
                setHistoryRequestId(null);
                setHistory([]);
              }}
            >
              Close
            </button>
          </div>

          {history.length === 0 ? (
            <p className="governance-empty">No history records found.</p>
          ) : (
            <div className="governance-table-wrap">
              <table className="governance-table">
                <thead>
                  <tr>
                    <th>Action</th>
                    <th>From</th>
                    <th>To</th>
                    <th>User</th>
                    <th>Comments</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.id}>
                      <td>{item.action}</td>
                      <td>{item.from_status || "—"}</td>
                      <td>{item.to_status || "—"}</td>
                      <td>{item.user_id ?? "—"}</td>
                      <td>{item.comments || "—"}</td>
                      <td>
                        {item.created_at
                          ? new Date(item.created_at).toLocaleString()
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      <div className="governance-footer">
        <span>{permissions.length} permissions available</span>
        <span>{roles.length} roles available</span>
        <span>{myRequests.length} requests submitted by you</span>
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="governance-stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function RequestTable({ requests, onHistory }) {
  if (requests.length === 0) {
    return (
      <p className="governance-empty">
        You haven't submitted any access requests.
      </p>
    );
  }

  return (
    <div className="governance-table-wrap">
      <table className="governance-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Permission</th>
            <th>Priority</th>
            <th>Status</th>
            <th>History</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((request) => (
            <tr key={request.id}>
              <td>#{request.id}</td>
              <td>{request.requested_changes?.permission_code || "—"}</td>
              <td>{request.priority}</td>
              <td>
                <span
                  className={`governance-status ${request.status}`}
                >
                  {request.status}
                </span>
              </td>
              <td>
                <button onClick={() => onHistory(request.id)}>
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}