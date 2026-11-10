import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  FiArrowLeft,
  FiRefreshCw,
  FiCheckCircle,
  FiAlertCircle,
  FiClock,
  FiDatabase,
  FiRotateCw,
  FiLoader,
  FiFileText,
  FiActivity
} from "react-icons/fi";

import {
  getSyncDetails,
  getSyncErrors,
  retrySyncError
} from "../../api/integrationApi";

import "./IntegrationSyncDetails.css";

export default function IntegrationSyncDetails() {
  const { id, syncId } = useParams();
  const navigate = useNavigate();

  const [sync, setSync] = useState(null);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [retryingId, setRetryingId] = useState(null);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    loadSyncDetails();
  }, [id, syncId]);

  const loadSyncDetails = async (showLoader = true) => {
    try {
      if (showLoader) setLoading(true);

      setError("");

      const [syncData, errorData] = await Promise.all([
        getSyncDetails(id, syncId),
        getSyncErrors(id, syncId, 100, 0)
      ]);

      setSync(syncData);
      setErrors(errorData.items || []);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to load synchronization details."
      );
    } finally {
      if (showLoader) setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await loadSyncDetails(false);
    } finally {
      setRefreshing(false);
    }
  };

  const handleRetry = async (errorId) => {
    try {
      setRetryingId(errorId);
      setError("");
      setMessage("");

      const result = await retrySyncError(id, syncId, errorId);

      setMessage(
        result.message ||
        "Failed record retry completed."
      );

      await loadSyncDetails(false);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to retry this failed record."
      );
    } finally {
      setRetryingId(null);
    }
  };

  const formatDate = (date) => {
    if (!date) return "Not available";

    return new Date(date).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short"
    });
  };

  const getStatusClass = (status) => {
    if (
      ["completed", "resolved", "success"].includes(status)
    ) {
      return "sync-success";
    }

    if (
      ["failed", "error"].includes(status)
    ) {
      return "sync-danger";
    }

    if (
      ["completed_with_errors", "pending", "processing"].includes(status)
    ) {
      return "sync-warning";
    }

    return "sync-neutral";
  };

  if (loading) {
    return (
      <div className="sync-details-loading">
        <FiLoader className="sync-spinner" />
        <p>Loading synchronization details...</p>
      </div>
    );
  }

  if (!sync) {
    return (
      <div className="sync-details-error">
        <FiAlertCircle />
        <h3>Synchronization not found</h3>
        <p>{error || "Unable to find this synchronization record."}</p>

        <button onClick={() => navigate(`/integrations/${id}`)}>
          Back to Integration
        </button>
      </div>
    );
  }

  return (
    <div className="sync-details-page">
      <div className="sync-details-header">
        <button
          className="sync-back-button"
          onClick={() => navigate(`/integrations/${id}`)}
        >
          <FiArrowLeft />
          Back to Integration
        </button>

        <div className="sync-title-row">
          <div>
            <span className="sync-subtitle">
              ENTERPRISE DATA MANAGEMENT
            </span>

            <h1>Synchronization Details</h1>

            <p>
              Detailed execution information and failed record management.
            </p>
          </div>

          <button
            className="sync-refresh-button"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <FiRefreshCw className={refreshing ? "sync-spinner" : ""} />
            Refresh
          </button>
        </div>
      </div>

      {message && (
        <div className="sync-alert sync-alert-success">
          <FiCheckCircle />
          {message}
          <button onClick={() => setMessage("")}>×</button>
        </div>
      )}

      {error && (
        <div className="sync-alert sync-alert-error">
          <FiAlertCircle />
          {error}
          <button onClick={() => setError("")}>×</button>
        </div>
      )}

      <div className="sync-overview-card">
        <div className="sync-overview-top">
          <div>
            <span>Synchronization ID</span>
            <h2>#{sync.id}</h2>
          </div>

          <span
            className={`sync-status ${getStatusClass(sync.status)}`}
          >
            {sync.status?.replaceAll("_", " ")}
          </span>
        </div>

        <div className="sync-overview-information">
          <div>
            <span>Trigger Type</span>
            <strong>{sync.trigger_type}</strong>
          </div>

          <div>
            <span>Integration ID</span>
            <strong>#{sync.integration_id}</strong>
          </div>

          <div>
            <span>Started At</span>
            <strong>{formatDate(sync.started_at)}</strong>
          </div>

          <div>
            <span>Completed At</span>
            <strong>{formatDate(sync.completed_at)}</strong>
          </div>

          <div>
            <span>Duration</span>
            <strong>{sync.duration_ms ?? 0} ms</strong>
          </div>

          <div>
            <span>Triggered By</span>
            <strong>
              {sync.triggered_by ?? "System"}
            </strong>
          </div>
        </div>
      </div>

      <div className="sync-section">
        <div className="sync-section-heading">
          <div>
            <h2>Execution Summary</h2>
            <p>Synchronization record processing statistics.</p>
          </div>

          <FiActivity />
        </div>

        <div className="sync-stat-grid">
          <div className="sync-stat-card">
            <FiDatabase />
            <span>Total Records</span>
            <h2>{sync.total_records}</h2>
          </div>

          <div className="sync-stat-card">
            <FiCheckCircle />
            <span>Processed</span>
            <h2>{sync.processed_records}</h2>
          </div>

          <div className="sync-stat-card">
            <FiFileText />
            <span>Inserted</span>
            <h2>{sync.inserted_records}</h2>
          </div>

          <div className="sync-stat-card">
            <FiRefreshCw />
            <span>Updated</span>
            <h2>{sync.updated_records}</h2>
          </div>

          <div className="sync-stat-card">
            <FiClock />
            <span>Skipped</span>
            <h2>{sync.skipped_records}</h2>
          </div>

          <div className="sync-stat-card">
            <FiAlertCircle />
            <span>Failed</span>
            <h2>{sync.failed_records}</h2>
          </div>
        </div>
      </div>

      <div className="sync-section">
        <div className="sync-section-heading">
          <div>
            <h2>Failed Records</h2>
            <p>
              Review synchronization errors and retry eligible records.
            </p>
          </div>

          <span className="sync-error-count">
            {errors.length} Records
          </span>
        </div>

        <div className="sync-table-wrapper">
          <table className="sync-table">
            <thead>
              <tr>
                <th>Error ID</th>
                <th>Source Record</th>
                <th>Row Number</th>
                <th>Error Category</th>
                <th>Error Message</th>
                <th>Retry Count</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {errors.length === 0 ? (
                <tr>
                  <td colSpan="8" className="sync-empty">
                    <FiCheckCircle />
                    No failed records found.
                  </td>
                </tr>
              ) : (
                errors.map((item) => (
                  <tr key={item.id}>
                    <td>#{item.id}</td>

                    <td>
                      {item.source_record_id || "-"}
                    </td>

                    <td>
                      {item.row_number ?? "-"}
                    </td>

                    <td>
                      {item.error_category}
                    </td>

                    <td className="sync-error-message">
                      {item.error_message}
                    </td>

                    <td>{item.retry_count}</td>

                    <td>
                      <span
                        className={`sync-status ${getStatusClass(
                          item.retry_status
                        )}`}
                      >
                        {item.retry_status}
                      </span>
                    </td>

                    <td>
                      {item.retry_status === "resolved" ? (
                        <span className="sync-resolved">
                          <FiCheckCircle />
                          Resolved
                        </span>
                      ) : (
                        <button
                          className="sync-retry-button"
                          onClick={() => handleRetry(item.id)}
                          disabled={
                            !item.is_retryable ||
                            retryingId === item.id ||
                            item.retry_status === "processing"
                          }
                        >
                          {retryingId === item.id ? (
                            <FiLoader className="sync-spinner" />
                          ) : (
                            <FiRotateCw />
                          )}

                          {retryingId === item.id
                            ? "Retrying..."
                            : "Retry"}
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="sync-section">
        <div className="sync-section-heading">
          <div>
            <h2>Execution Metadata</h2>
            <p>Additional information recorded during synchronization.</p>
          </div>

          <FiFileText />
        </div>

        <div className="sync-metadata">
          <div>
            <span>Company ID</span>
            <strong>{sync.company_id}</strong>
          </div>

          <div>
            <span>Sync ID</span>
            <strong>{sync.id}</strong>
          </div>

          <div>
            <span>Created At</span>
            <strong>{formatDate(sync.created_at)}</strong>
          </div>

          <div>
            <span>Updated At</span>
            <strong>{formatDate(sync.completed_at)}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}