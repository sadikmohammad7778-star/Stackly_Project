import { useEffect, useState } from "react";

import {
  getMyApprovalRequests,
  getPendingApprovals,
  getPendingApprovalCount,
} from "../api/workflowApi";

import WorkflowRequestModal from "../components/workflow/WorkflowRequestModal";

import "./Workflow.css";

export default function Workflow() {
  const [myRequests, setMyRequests] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [myRequestCount, setMyRequestCount] = useState(0);
  const [assignedCount, setAssignedCount] = useState(0);
  const [selectedRequestId, setSelectedRequestId] = useState(null);
  const [selectedRequestMode, setSelectedRequestMode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadWorkflowData();
  }, []);

  const loadWorkflowData = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        myRequestsData,
        pendingData,
        countData,
      ] = await Promise.all([
        getMyApprovalRequests(),
        getPendingApprovals(),
        getPendingApprovalCount(),
      ]);

      setMyRequests(myRequestsData.items || []);
      setPendingApprovals(pendingData.items || []);

      setMyRequestCount(myRequestsData.total || 0);
      setAssignedCount(pendingData.total || 0);
      setPendingCount(countData.pending_count || 0);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Failed to load workflow."
      );
    } finally {
      setLoading(false);
    }
  };

  const openMyRequest = (requestId) => {
    setSelectedRequestId(requestId);
    setSelectedRequestMode("my");
  };

  const openPendingRequest = (requestId) => {
    setSelectedRequestId(requestId);
    setSelectedRequestMode("pending");
  };

  const closeRequest = () => {
    setSelectedRequestId(null);
    setSelectedRequestMode(null);
  };

  if (loading) {
    return (
      <div className="workflow-loading">
        <h2>Loading Workflow...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div className="workflow-error">
        <h2>{error}</h2>

        <button onClick={loadWorkflowData}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="workflow-page">

      <div className="workflow-header">
        <div>
          <h1>Workflow & Approval Management</h1>

          <p>
            Manage approval requests and workflow activities
          </p>
        </div>
      </div>

      <div className="workflow-cards">

        <div className="workflow-card">
          <div className="workflow-card-content">
            <p>Pending Approvals</p>
            <h2>{pendingCount}</h2>
          </div>

          <div className="workflow-card-icon pending">
            ⏳
          </div>
        </div>

        <div className="workflow-card">
          <div className="workflow-card-content">
            <p>My Requests</p>
            <h2>{myRequestCount}</h2>
          </div>

          <div className="workflow-card-icon requests">
            📋
          </div>
        </div>

        <div className="workflow-card">
          <div className="workflow-card-content">
            <p>Assigned to Me</p>
            <h2>{assignedCount}</h2>
          </div>

          <div className="workflow-card-icon assigned">
            👤
          </div>
        </div>

      </div>

      <div className="workflow-section">

        <div className="workflow-section-header">
          <h2>My Approval Requests</h2>

          <span>
            {myRequestCount} Requests
          </span>
        </div>

        {myRequests.length === 0 ? (
          <div className="workflow-empty">
            No approval requests found.
          </div>
        ) : (
          <div className="workflow-table-wrapper">

            <table className="workflow-table">

              <thead>
                <tr>
                  <th>ID</th>
                  <th>Request Type</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>

                {myRequests.map((request) => (
                  <tr key={request.id}>

                    <td>
                      #{request.id}
                    </td>

                    <td>
                      {request.request_type}
                    </td>

                    <td>
                      <span
                        className={`workflow-priority ${request.priority}`}
                      >
                        {request.priority}
                      </span>
                    </td>

                    <td>
                      <span
                        className={`workflow-status ${request.status}`}
                      >
                        {request.status}
                      </span>
                    </td>

                    <td>
                      {request.created_at
                        ? new Date(
                            request.created_at
                          ).toLocaleDateString()
                        : "-"}
                    </td>

                    <td>
                      <button
                        className="workflow-view-button"
                        onClick={() =>
                          openMyRequest(request.id)
                        }
                      >
                        View
                      </button>
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>
        )}

      </div>

      <div className="workflow-section">

        <div className="workflow-section-header">
          <h2>Pending Approvals</h2>

          <span>
            {assignedCount} Pending
          </span>
        </div>

        {pendingApprovals.length === 0 ? (
          <div className="workflow-empty">
            No pending approvals.
          </div>
        ) : (
          <div className="workflow-table-wrapper">

            <table className="workflow-table">

              <thead>
                <tr>
                  <th>ID</th>
                  <th>Request Type</th>
                  <th>Requested By</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>

                {pendingApprovals.map((request) => (
                  <tr key={request.id}>

                    <td>
                      #{request.id}
                    </td>

                    <td>
                      {request.request_type}
                    </td>

                    <td>
                      User #{request.requested_by}
                    </td>

                    <td>
                      <span
                        className={`workflow-priority ${request.priority}`}
                      >
                        {request.priority}
                      </span>
                    </td>

                    <td>
                      <span
                        className={`workflow-status ${request.status}`}
                      >
                        {request.status}
                      </span>
                    </td>

                    <td>
                      <button
                        className="workflow-view-button"
                        onClick={() =>
                          openPendingRequest(request.id)
                        }
                      >
                        View
                      </button>
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>
        )}

      </div>

      {selectedRequestId && (
        <WorkflowRequestModal
          requestId={selectedRequestId}
          canSubmit={selectedRequestMode === "my"}
          canApprove={selectedRequestMode === "pending"}
          onClose={closeRequest}
          onActionComplete={loadWorkflowData}
        />
      )}

    </div>
  );
}