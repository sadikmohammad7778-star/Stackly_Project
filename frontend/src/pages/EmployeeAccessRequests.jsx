import { useCallback, useEffect, useState } from "react";
import {
  submitAccessRequest,
  getMyAccessRequests,
  getAccessRequestHistory,
} from "../api/dataGovernanceApi";
import API from "../api/axios";
import "./EmployeeAccessRequests.css";

export default function EmployeeAccessRequests() {
  const [permissions, setPermissions] = useState([]);
  const [requests, setRequests] = useState([]);
  const [permissionId, setPermissionId] = useState("");
  const [reason, setReason] = useState("");
  const [priority, setPriority] = useState("medium");
  const [history, setHistory] = useState([]);
  const [historyRequestId, setHistoryRequestId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [permissionResponse, requestResponse] = await Promise.all([
        API.get("/data-governance/permissions"),
        getMyAccessRequests(),
      ]);

      const permissionData = permissionResponse.data;
      setPermissions(
        Array.isArray(permissionData)
          ? permissionData
          : permissionData.permissions || []
      );

      setRequests(requestResponse.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load access requests."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const createRequest = async (event) => {
    event.preventDefault();

    if (!permissionId || !reason.trim()) {
      setError("Select a permission and enter a reason.");
      return;
    }

    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      await submitAccessRequest({
        permission_id: Number(permissionId),
        reason: reason.trim(),
        priority,
      });

      setMessage("Access request submitted successfully.");
      setPermissionId("");
      setReason("");
      setPriority("medium");

      await loadData();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to submit the access request."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const viewHistory = async (requestId) => {
    setError("");

    try {
      const response = await getAccessRequestHistory(requestId);
      setHistory(response.data);
      setHistoryRequestId(requestId);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load request history."
      );
    }
  };

  if (loading) {
    return (
      <div className="employee-access-page">
        <p>Loading access requests...</p>
      </div>
    );
  }

  return (
    <div className="employee-access-page">
      <header className="employee-access-header">
        <div>
          <h1>Access Requests</h1>
          <p>
            Request additional permissions and track approval status.
          </p>
        </div>

        <button onClick={loadData} disabled={submitting}>
          Refresh
        </button>
      </header>

      {error && (
        <div className="employee-access-error">
          {error}
        </div>
      )}

      {message && (
        <div className="employee-access-success">
          {message}
        </div>
      )}

      <section className="employee-access-panel">
        <h2>Request a Permission</h2>

        <form onSubmit={createRequest}>
          <label htmlFor="permission">
            Permission
          </label>

          <select
            id="permission"
            value={permissionId}
            onChange={(event) =>
              setPermissionId(event.target.value)
            }
            required
          >
            <option value="">Select a permission</option>

            {permissions.map((permission) => (
              <option
                key={permission.id}
                value={permission.id}
              >
                {permission.code}
              </option>
            ))}
          </select>

          <label htmlFor="reason">
            Reason
          </label>

          <textarea
            id="reason"
            value={reason}
            onChange={(event) =>
              setReason(event.target.value)
            }
            placeholder="Explain why you need this permission."
            minLength={5}
            maxLength={2000}
            required
          />

          <label htmlFor="priority">
            Priority
          </label>

          <select
            id="priority"
            value={priority}
            onChange={(event) =>
              setPriority(event.target.value)
            }
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>

          <button type="submit" disabled={submitting}>
            {submitting
              ? "Submitting..."
              : "Submit Request"}
          </button>
        </form>
      </section>

      <section className="employee-access-panel">
        <h2>My Requests</h2>

        {requests.length === 0 ? (
          <p>You haven't submitted any access requests yet.</p>
        ) : (
          <div className="employee-access-table-wrap">
            <table>
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

                    <td>
                      {request.requested_changes?.permission_code ||
                        "—"}
                    </td>

                    <td>{request.priority}</td>
                    <td>{request.status}</td>

                    <td>
                      <button
                        onClick={() =>
                          viewHistory(request.id)
                        }
                      >
                        View History
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {historyRequestId !== null && (
        <section className="employee-access-panel">
          <div className="employee-access-history-header">
            <h2>
              History for Request #{historyRequestId}
            </h2>

            <button
              onClick={() => {
                setHistoryRequestId(null);
                setHistory([]);
              }}
            >
              Close
            </button>
          </div>

          {history.length === 0 ? (
            <p>No history records found.</p>
          ) : (
            <div className="employee-access-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Action</th>
                    <th>From</th>
                    <th>To</th>
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
                      <td>{item.comments || "—"}</td>
                      <td>
                        {item.created_at
                          ? new Date(
                              item.created_at
                            ).toLocaleString()
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
    </div>
  );
}