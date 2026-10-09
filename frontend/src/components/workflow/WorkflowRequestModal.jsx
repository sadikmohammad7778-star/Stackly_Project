import { useEffect, useState } from "react";

import {
  getApprovalRequest,
  getApprovalHistory,
  submitApprovalRequest,
  approveRequest,
  rejectRequest,
  cancelRequest,
} from "../../api/workflowApi";

import "./WorkflowRequestModal.css";

export default function WorkflowRequestModal({
  requestId,
  onClose,
  canSubmit = false,
  canApprove = false,
  onActionComplete,
}) {
  const [request, setRequest] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [comments, setComments] = useState("");
  const [showRejectInput, setShowRejectInput] = useState(false);

  useEffect(() => {
    loadRequestDetails();
  }, [requestId]);

  const loadRequestDetails = async () => {
    try {
      setLoading(true);
      setError("");

      const [requestData, historyData] =
        await Promise.all([
          getApprovalRequest(requestId),
          getApprovalHistory(requestId),
        ]);

      setRequest(requestData);
      setHistory(historyData || []);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to load request details."
      );
    } finally {
      setLoading(false);
    }
  };

  const formatText = (value) => {
    if (!value) return "-";

    return value
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  const handleSubmit = async () => {
    try {
      setActionLoading(true);
      setError("");

      await submitApprovalRequest(requestId, {
        comments: comments.trim() || null,
      });

      await loadRequestDetails();

      setComments("");

      if (onActionComplete) {
        onActionComplete();
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to submit request."
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleApprove = async () => {
    try {
      setActionLoading(true);
      setError("");

      await approveRequest(requestId, {
        comments: comments.trim() || null,
      });

      await loadRequestDetails();

      setComments("");

      if (onActionComplete) {
        onActionComplete();
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to approve request."
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!comments.trim()) {
      setError("Rejection reason is required.");
      return;
    }

    try {
      setActionLoading(true);
      setError("");

      await rejectRequest(requestId, {
        comments: comments.trim(),
      });

      await loadRequestDetails();

      setComments("");
      setShowRejectInput(false);

      if (onActionComplete) {
        onActionComplete();
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to reject request."
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    try {
      setActionLoading(true);
      setError("");

      await cancelRequest(requestId, {
        comments: comments.trim() || null,
      });

      await loadRequestDetails();

      setComments("");

      if (onActionComplete) {
        onActionComplete();
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to cancel request."
      );
    } finally {
      setActionLoading(false);
    }
  };

  if (!requestId) {
    return null;
  }

  return (
    <div className="workflow-modal-overlay">
      <div className="workflow-modal">

        <div className="workflow-modal-header">
          <div>
            <h2>
              Approval Request #{requestId}
            </h2>

            <p>
              Request details and approval history
            </p>
          </div>

          <button
            className="workflow-modal-close"
            onClick={onClose}
            disabled={actionLoading}
          >
            ×
          </button>
        </div>

        {loading && (
          <div className="workflow-modal-loading">
            Loading request details...
          </div>
        )}

        {error && (
          <div className="workflow-modal-error">
            {error}
          </div>
        )}

        {!loading && !error && request && (
          <>
            <div className="workflow-details-grid">

              <div className="workflow-detail-item">
                <span>Request Type</span>
                <strong>
                  {formatText(request.request_type)}
                </strong>
              </div>

              <div className="workflow-detail-item">
                <span>Priority</span>
                <strong
                  className={`workflow-priority ${request.priority}`}
                >
                  {formatText(request.priority)}
                </strong>
              </div>

              <div className="workflow-detail-item">
                <span>Status</span>
                <strong
                  className={`workflow-status ${request.status}`}
                >
                  {formatText(request.status)}
                </strong>
              </div>

              <div className="workflow-detail-item">
                <span>Requested By</span>
                <strong>
                  User #{request.requested_by}
                </strong>
              </div>

              <div className="workflow-detail-item">
                <span>Assigned Approver</span>
                <strong>
                  {request.assigned_approver_id
                    ? `User #${request.assigned_approver_id}`
                    : "Not Required"}
                </strong>
              </div>

              <div className="workflow-detail-item">
                <span>Created At</span>
                <strong>
                  {request.created_at
                    ? new Date(
                        request.created_at
                      ).toLocaleString()
                    : "-"}
                </strong>
              </div>

              <div className="workflow-detail-item">
                <span>Submitted At</span>
                <strong>
                  {request.submitted_at
                    ? new Date(
                        request.submitted_at
                      ).toLocaleString()
                    : "-"}
                </strong>
              </div>

              <div className="workflow-detail-item">
                <span>Completed At</span>
                <strong>
                  {request.completed_at
                    ? new Date(
                        request.completed_at
                      ).toLocaleString()
                    : "-"}
                </strong>
              </div>

            </div>

            <div className="workflow-detail-block">
              <h3>Reason</h3>

              <p>
                {request.reason || "No reason provided."}
              </p>
            </div>

            {request.requested_changes && (
              <div className="workflow-detail-block">
                <h3>Requested Changes</h3>

                <pre>
                  {JSON.stringify(
                    request.requested_changes,
                    null,
                    2
                  )}
                </pre>
              </div>
            )}

            <div className="workflow-history">

              <h3>Approval History</h3>

              {history.length === 0 ? (
                <div className="workflow-history-empty">
                  No approval history found.
                </div>
              ) : (
                <div className="workflow-history-list">

                  {history.map((item) => (
                    <div
                      className="workflow-history-item"
                      key={item.id}
                    >
                      <div className="workflow-history-marker" />

                      <div className="workflow-history-content">

                        <div className="workflow-history-top">
                          <strong>
                            {formatText(item.action)}
                          </strong>

                          <span>
                            {item.created_at
                              ? new Date(
                                  item.created_at
                                ).toLocaleString()
                              : "-"}
                          </span>
                        </div>

                        <p>
                          User #{item.user_id}
                        </p>

                        {item.from_status && (
                          <span>
                            {formatText(item.from_status)}
                            {" → "}
                            {formatText(item.to_status)}
                          </span>
                        )}

                        {item.comments && (
                          <div className="workflow-history-comment">
                            {item.comments}
                          </div>
                        )}

                      </div>
                    </div>
                  ))}

                </div>
              )}

            </div>

            {((canSubmit && request.status === "draft") ||
              (canApprove &&
                request.status === "pending_approval")) && (
              <div className="workflow-action-section">

                <h3>Actions</h3>

                {(canSubmit && request.status === "draft") && (
                  <textarea
                    className="workflow-action-comment"
                    placeholder="Add a comment..."
                    value={comments}
                    onChange={(e) =>
                      setComments(e.target.value)
                    }
                    disabled={actionLoading}
                  />
                )}

                {canApprove &&
                  request.status === "pending_approval" &&
                  showRejectInput && (
                    <textarea
                      className="workflow-action-comment"
                      placeholder="Enter rejection reason..."
                      value={comments}
                      onChange={(e) =>
                        setComments(e.target.value)
                      }
                      disabled={actionLoading}
                    />
                  )}

                <div className="workflow-action-buttons">

                  {canSubmit &&
                    request.status === "draft" && (
                      <>
                        <button
                          className="workflow-action-button submit"
                          onClick={handleSubmit}
                          disabled={actionLoading}
                        >
                          {actionLoading
                            ? "Processing..."
                            : "Submit"}
                        </button>

                        <button
                          className="workflow-action-button cancel"
                          onClick={handleCancel}
                          disabled={actionLoading}
                        >
                          Cancel
                        </button>
                      </>
                    )}

                  {canApprove &&
                    request.status === "pending_approval" && (
                      <>
                        {!showRejectInput && (
                          <button
                            className="workflow-action-button approve"
                            onClick={handleApprove}
                            disabled={actionLoading}
                          >
                            {actionLoading
                              ? "Processing..."
                              : "Approve"}
                          </button>
                        )}

                        {!showRejectInput && (
                          <button
                            className="workflow-action-button reject"
                            onClick={() =>
                              setShowRejectInput(true)
                            }
                            disabled={actionLoading}
                          >
                            Reject
                          </button>
                        )}

                        {showRejectInput && (
                          <>
                            <button
                              className="workflow-action-button reject"
                              onClick={handleReject}
                              disabled={actionLoading}
                            >
                              {actionLoading
                                ? "Processing..."
                                : "Confirm Reject"}
                            </button>

                            <button
                              className="workflow-action-button cancel"
                              onClick={() => {
                                setShowRejectInput(false);
                                setComments("");
                                setError("");
                              }}
                              disabled={actionLoading}
                            >
                              Back
                            </button>
                          </>
                        )}
                      </>
                    )}

                </div>

              </div>
            )}

          </>
        )}

      </div>
    </div>
  );
}