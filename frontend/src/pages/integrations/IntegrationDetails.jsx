import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  FiArrowLeft,
  FiArrowUpRight,
  FiDatabase,
  FiCloud,
  FiServer,
  FiRefreshCw,
  FiUploadCloud,
  FiCheckCircle,
  FiAlertCircle,
  FiPlay,
  FiClock,
  FiFileText,
  FiActivity,
  FiLoader,
  FiPower,
  FiGitMerge,
  FiBarChart2
} from "react-icons/fi";

import {
  getIntegration,
  updateIntegration,
  testIntegrationConnection,
  uploadIntegrationFile,
  previewIntegrationFile,
  synchronizeIntegration,
  getSyncHistory
} from "../../api/integrationApi";

import "./IntegrationDetails.css";

const formatDate = (date) => {
  if (!date) return "Never";

  const parsedDate = new Date(date);

  if (Number.isNaN(parsedDate.getTime())) return "Invalid date";

  return parsedDate.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short"
  });
};

const getStatusClass = (status) => {
  const normalizedStatus = String(status || "").toLowerCase();

  if (
    ["active", "connected", "completed", "success", "enabled"].includes(
      normalizedStatus
    )
  ) {
    return "details-success";
  }

  if (
    ["failed", "inactive", "error", "disabled"].includes(
      normalizedStatus
    )
  ) {
    return "details-danger";
  }

  if (normalizedStatus === "completed_with_errors") {
    return "details-warning";
  }

  return "details-neutral";
};

const formatStatus = (status) => {
  return String(status || "Unknown").replaceAll("_", " ");
};

export default function IntegrationDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [integration, setIntegration] = useState(null);
  const [preview, setPreview] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [syncResult, setSyncResult] = useState(null);

  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [testResult, setTestResult] = useState(null);

  const loadDetails = useCallback(
    async (showLoader = true) => {
      try {
        if (showLoader) setLoading(true);

        setError("");

        const integrationData = await getIntegration(id);

        setIntegration(integrationData);

        const [historyData, previewData] = await Promise.all([
          getSyncHistory(id, 10, 0),
          integrationData.source_type === "csv"
            ? previewIntegrationFile(id).catch(() => null)
            : Promise.resolve(null)
        ]);

        setHistory(
          Array.isArray(historyData?.items)
            ? historyData.items
            : []
        );

        setPreview(previewData);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
          "Unable to load integration details."
        );
      } finally {
        if (showLoader) setLoading(false);
      }
    },
    [id]
  );

  useEffect(() => {
    loadDetails();
  }, [loadDetails]);

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await loadDetails(false);
    } finally {
      setRefreshing(false);
    }
  };

  const handleToggleIntegration = async () => {
    if (!integration || updatingStatus || syncing || uploading) return;

    try {
      setUpdatingStatus(true);
      setError("");
      setMessage("");

      const updated = await updateIntegration(id, {
        is_enabled: !integration.is_enabled
      });

      setIntegration(updated);

      setMessage(
        updated.is_enabled
          ? "Integration enabled successfully."
          : "Integration disabled successfully."
      );
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to update integration status."
      );
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleTestConnection = async () => {
    if (testing) return;

    try {
      setTesting(true);
      setError("");
      setMessage("");
      setTestResult(null);

      const result = await testIntegrationConnection(id);

      setTestResult(result);
      setMessage(result.message || "Connection test completed.");

      await loadDetails(false);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Connection test failed."
      );
    } finally {
      setTesting(false);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    setError("");
    setMessage("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!file.name.toLowerCase().endsWith(".csv")) {
      setError("Please select a valid CSV file.");
      setSelectedFile(null);
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("Maximum CSV file size is 10 MB.");
      setSelectedFile(null);
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a CSV file first.");
      return;
    }

    if (!integration?.is_enabled) {
      setError("Enable this integration before uploading a CSV file.");
      return;
    }

    try {
      setUploading(true);
      setError("");
      setMessage("");
      setSyncResult(null);

      const result = await uploadIntegrationFile(id, selectedFile);

      setMessage(result.message || "CSV uploaded successfully.");
      setSelectedFile(null);

      await loadDetails(false);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "CSV upload failed."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleSync = async (triggerType) => {
    if (!integration?.is_enabled) {
      setError("Enable this integration before synchronization.");
      return;
    }

    if (syncing || uploading) return;

    try {
      setSyncing(true);
      setError("");
      setMessage("");
      setSyncResult(null);

      const result = await synchronizeIntegration(id, triggerType);

      setSyncResult(result);

      setMessage(
        result.message ||
        `Synchronization ${formatStatus(result.status)}.`
      );

      await loadDetails(false);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Synchronization failed."
      );
    } finally {
      setSyncing(false);
    }
  };

  const handleViewSyncDetails = (syncId) => {
    navigate(`/integrations/${id}/syncs/${syncId}`);
  };

  const getConnectorIcon = () => {
    if (integration?.source_type === "postgresql") {
      return <FiDatabase />;
    }

    if (integration?.source_type === "rest_api") {
      return <FiCloud />;
    }

    return <FiServer />;
  };

  if (loading) {
    return (
      <div className="integration-details-loading">
        <FiLoader className="details-spinner" />
        <p>Loading integration details...</p>
      </div>
    );
  }

  if (error && !integration) {
    return (
      <div className="integration-details-error">
        <FiAlertCircle />
        <h3>Unable to load integration</h3>
        <p>{error}</p>

        <button onClick={() => navigate("/integrations")}>
          Back to Integrations
        </button>
      </div>
    );
  }

  if (!integration) return null;

  const sourceType = integration.source_type || "";
  const isCSV = sourceType === "csv";
  const isREST = sourceType === "rest_api";
  const isPostgreSQL = sourceType === "postgresql";

  return (
    <div className="integration-details-page">
      <div className="details-header">
        <button
          className="details-back-button"
          onClick={() => navigate("/integrations")}
        >
          <FiArrowLeft />
          Back to Integrations
        </button>

        <div className="details-title-row">
          <div>
            <span className="details-subtitle">
              ENTERPRISE DATA MANAGEMENT
            </span>

            <h1>{integration.name}</h1>

            <p>
              Manage connector configuration, synchronization and activity.
            </p>
          </div>

          <button
            className="details-refresh-button"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <FiRefreshCw
              className={refreshing ? "details-spinner" : ""}
            />
            Refresh
          </button>
        </div>
      </div>

      {message && (
        <div className="details-alert details-alert-success">
          <FiCheckCircle />
          {message}
          <button onClick={() => setMessage("")}>×</button>
        </div>
      )}

      {error && (
        <div className="details-alert details-alert-error">
          <FiAlertCircle />
          {error}
          <button onClick={() => setError("")}>×</button>
        </div>
      )}

      <div className="details-overview-card">
        <div className="details-connector-icon">
          {getConnectorIcon()}
        </div>

        <div className="details-overview-info">
          <h2>{integration.name}</h2>

          <p>
            {sourceType.replace("_", " ").toUpperCase()}
            {" · "}
            {(integration.target_module || "").toUpperCase()}
          </p>

          <span
            className={`details-status ${
              integration.is_enabled
                ? "details-success"
                : "details-danger"
            }`}
          >
            {integration.is_enabled ? "Enabled" : "Disabled"}
          </span>
        </div>

        <div className="details-overview-actions">
          <button
            className={
              integration.is_enabled
                ? "details-disable-button"
                : "details-enable-button"
            }
            onClick={handleToggleIntegration}
            disabled={
              updatingStatus ||
              syncing ||
              uploading
            }
          >
            {updatingStatus ? (
              <FiLoader className="details-spinner" />
            ) : (
              <FiPower />
            )}

            {updatingStatus
              ? "Updating..."
              : integration.is_enabled
                ? "Disable Integration"
                : "Enable Integration"}
          </button>

          {isCSV && (
            <button
              className="details-mapping-button"
              onClick={() => navigate(`/integrations/${id}/mappings`)}
            >
              <FiGitMerge />
              Configure Field Mappings
            </button>
          )}

          <button
              className="details-mapping-button"
              onClick={() => navigate(`/integrations/${id}/schedule`)}
            >
              <FiClock />
              Schedule Management
          </button>

          {!isCSV && (
            <button
              className="details-test-button"
              onClick={handleTestConnection}
              disabled={testing}
            >
              {testing ? (
                <FiLoader className="details-spinner" />
              ) : (
                <FiActivity />
              )}
              Test Connection
            </button>
          )}
        </div>
      </div>

      {testResult && (
        <div
          className={`details-alert ${
            testResult.status === "success"
              ? "details-alert-success"
              : "details-alert-error"
          }`}
        >
          {testResult.status === "success" ? (
            <FiCheckCircle />
          ) : (
            <FiAlertCircle />
          )}

          {testResult.message}
        </div>
      )}

      <div className="details-information-grid">
        <div className="details-information-card">
          <span>Target Module</span>
          <h3>{integration.target_module || "N/A"}</h3>
        </div>

        <div className="details-information-card">
          <span>Sync Strategy</span>
          <h3>{integration.sync_strategy || "N/A"}</h3>
        </div>

        <div className="details-information-card">
          <span>Last Synchronization</span>
          <h3>{formatDate(integration.last_sync_at)}</h3>
        </div>

        <div className="details-information-card">
          <span>Created At</span>
          <h3>{formatDate(integration.created_at)}</h3>
        </div>
      </div>

      {isCSV && (
        <div className="details-section">
          <div className="details-section-heading">
            <div>
              <h2>CSV File Management</h2>
              <p>Upload and preview your source data.</p>
            </div>

            <FiFileText />
          </div>

          <div className="details-upload-area">
            <FiUploadCloud />

            <h3>Upload CSV File</h3>

            <p>
              Select a CSV file to upload. Maximum file size is 10 MB.
            </p>

            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
              disabled={uploading || syncing}
            />

            {selectedFile && (
              <div className="details-selected-file">
                <FiFileText />
                {selectedFile.name}

                <span>
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </span>
              </div>
            )}

            <button
              className="details-primary-button"
              onClick={handleUpload}
              disabled={
                !selectedFile ||
                uploading ||
                syncing ||
                !integration.is_enabled
              }
            >
              {uploading ? (
                <FiLoader className="details-spinner" />
              ) : (
                <FiUploadCloud />
              )}

              {uploading ? "Uploading..." : "Upload CSV"}
            </button>

            {!integration.is_enabled && (
              <p className="details-disabled-message">
                Enable this integration before uploading a CSV file.
              </p>
            )}
          </div>

          {preview && (
            <div className="details-preview">
              <div className="details-section-heading">
                <div>
                  <h3>CSV Preview</h3>

                  <p>
                    {preview.filename || "Uploaded CSV"}
                    {" · "}
                    {preview.total_rows ?? 0} records
                  </p>
                </div>
              </div>

              <div className="details-table-wrapper">
                <table className="details-table">
                  <thead>
                    <tr>
                      {(preview.columns || []).map((column) => (
                        <th key={column}>{column}</th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>
                    {(preview.preview || []).map((row, index) => (
                      <tr key={index}>
                        {(preview.columns || []).map((column) => (
                          <td key={column}>
                            {String(row?.[column] ?? "")}
                          </td>
                        ))}
                      </tr>
                    ))}

                    {(!preview.preview ||
                      preview.preview.length === 0) && (
                      <tr>
                        <td
                          colSpan={preview.columns?.length || 1}
                          className="details-empty-row"
                        >
                          No preview records available.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {!isPostgreSQL && (
        <div className="details-section">
          <div className="details-section-heading">
            <div>
              <h2>Synchronization Management</h2>
              <p>Run manual or incremental data synchronization.</p>
            </div>

            <FiRefreshCw />
          </div>

          <div className="details-sync-actions">
            <div>
              <h3>Manual Synchronization</h3>
              <p>Process the available source records.</p>

              <button
                className="details-primary-button"
                onClick={() => handleSync("manual")}
                disabled={syncing || !integration.is_enabled}
              >
                {syncing ? (
                  <FiLoader className="details-spinner" />
                ) : (
                  <FiPlay />
                )}

                {syncing ? "Synchronizing..." : "Run Manual Sync"}
              </button>
            </div>

            {isREST && (
              <div>
                <h3>Incremental Synchronization</h3>

                <p>
                  Process records updated since the previous sync.
                </p>

                <button
                  className="details-secondary-button"
                  onClick={() => handleSync("incremental")}
                  disabled={syncing || !integration.is_enabled}
                >
                  <FiActivity />
                  Run Incremental Sync
                </button>
              </div>
            )}
          </div>

          {!integration.is_enabled && (
            <p className="details-disabled-message">
              Enable this integration before starting synchronization.
            </p>
          )}

          {syncing && (
            <div className="details-sync-progress">
              <FiLoader className="details-spinner" />
              Synchronization is running. Please wait...
            </div>
          )}
        </div>
      )}

      {syncResult && (
        <div className="details-section">
          <div className="details-section-heading">
            <div>
              <h2>Synchronization Result</h2>
              <p>Summary of the latest synchronization execution.</p>
            </div>

            <FiBarChart2 />
          </div>

          <div className="details-sync-result-header">
            <div>
              <span>Sync ID</span>
              <h3>#{syncResult.sync_id}</h3>
            </div>

            <span
              className={`details-status ${getStatusClass(
                syncResult.status
              )}`}
            >
              {formatStatus(syncResult.status)}
            </span>
          </div>

          <div className="details-sync-result-grid">
            <div>
              <span>Total Records</span>
              <h2>{syncResult.total_records ?? 0}</h2>
            </div>

            <div>
              <span>Processed</span>
              <h2>{syncResult.processed_records ?? 0}</h2>
            </div>

            <div>
              <span>Inserted</span>
              <h2>{syncResult.inserted_records ?? 0}</h2>
            </div>

            <div>
              <span>Updated</span>
              <h2>{syncResult.updated_records ?? 0}</h2>
            </div>

            <div>
              <span>Skipped</span>
              <h2>{syncResult.skipped_records ?? 0}</h2>
            </div>

            <div>
              <span>Failed</span>
              <h2>{syncResult.failed_records ?? 0}</h2>
            </div>

            <div>
              <span>Duration</span>
              <h2>{syncResult.duration_ms ?? 0} ms</h2>
            </div>
          </div>

          {(syncResult.failed_records || 0) > 0 && (
            <div className="details-sync-warning">
              <FiAlertCircle />
              Some records failed. Open synchronization history to inspect
              the failed records and retry eligible records.
            </div>
          )}

          {syncResult.sync_id && (
            <button
              className="details-secondary-button"
              onClick={() =>
                handleViewSyncDetails(syncResult.sync_id)
              }
            >
              View Synchronization Details
              <FiArrowUpRight />
            </button>
          )}
        </div>
      )}

      <div className="details-section">
        <div className="details-section-heading">
          <div>
            <h2>Synchronization History</h2>
            <p>Recent executions for this connector.</p>
          </div>

          <FiClock />
        </div>

        <div className="details-table-wrapper">
          <table className="details-table">
            <thead>
              <tr>
                <th>Sync ID</th>
                <th>Trigger</th>
                <th>Status</th>
                <th>Total</th>
                <th>Processed</th>
                <th>Inserted</th>
                <th>Updated</th>
                <th>Failed</th>
                <th>Duration</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan="11" className="details-empty-row">
                    No synchronization history available.
                  </td>
                </tr>
              ) : (
                history.map((sync) => (
                  <tr key={sync.id}>
                    <td>#{sync.id}</td>
                    <td>{sync.trigger_type || "N/A"}</td>

                    <td>
                      <span
                        className={`details-status ${getStatusClass(
                          sync.status
                        )}`}
                      >
                        {formatStatus(sync.status)}
                      </span>
                    </td>

                    <td>{sync.total_records ?? 0}</td>
                    <td>{sync.processed_records ?? 0}</td>
                    <td>{sync.inserted_records ?? 0}</td>
                    <td>{sync.updated_records ?? 0}</td>
                    <td>{sync.failed_records ?? 0}</td>
                    <td>{sync.duration_ms ?? 0} ms</td>

                    <td>
                      {formatDate(sync.created_at || sync.started_at)}
                    </td>

                    <td>
                      <button
                        className="details-secondary-button"
                        onClick={() => handleViewSyncDetails(sync.id)}
                      >
                        View Details
                        <FiArrowUpRight />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}