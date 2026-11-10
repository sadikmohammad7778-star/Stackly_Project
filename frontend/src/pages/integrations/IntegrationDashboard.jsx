import { useEffect, useState } from "react";
import {
  FiDatabase,
  FiActivity,
  FiCheckCircle,
  FiAlertCircle,
  FiRefreshCw,
  FiPlus,
  FiClock,
  FiArrowUpRight,
  FiServer,
  FiCloud
} from "react-icons/fi";

import {
  getIntegrations,
  getSyncHistory
} from "../../api/integrationApi";

import "./IntegrationDashboard.css";

export default function IntegrationDashboard() {
  const [integrations, setIntegrations] = useState([]);
  const [syncHistory, setSyncHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const integrationData = await getIntegrations();

      setIntegrations(integrationData);

      const historyResults = await Promise.allSettled(
        integrationData.map((integration) =>
          getSyncHistory(integration.id, 10, 0)
        )
      );

      const histories = historyResults.flatMap((result) =>
        result.status === "fulfilled"
          ? result.value.items || []
          : []
      );

      histories.sort(
        (a, b) =>
          new Date(b.created_at || b.started_at) -
          new Date(a.created_at || a.started_at)
      );

      setSyncHistory(histories);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to load integration dashboard."
      );
    } finally {
      setLoading(false);
    }
  };

  const totalIntegrations = integrations.length;

  const activeIntegrations = integrations.filter(
    (item) => item.is_enabled && item.status === "active"
  ).length;

  const successfulSyncs = syncHistory.filter(
    (item) => item.status === "completed"
  ).length;

  const failedSyncs = syncHistory.filter(
    (item) =>
      item.status === "failed" ||
      item.status === "completed_with_errors"
  ).length;

  const formatDate = (date) => {
    if (!date) return "Never";

    return new Date(date).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short"
    });
  };

  const getStatusClass = (status) => {
    if (status === "completed" || status === "active") {
      return "success";
    }

    if (status === "failed" || status === "inactive") {
      return "danger";
    }

    if (status === "completed_with_errors") {
      return "warning";
    }

    return "neutral";
  };

  const getConnectorIcon = (type) => {
    if (type === "postgresql") return <FiDatabase />;
    if (type === "rest_api") return <FiCloud />;
    return <FiServer />;
  };

  if (loading) {
    return (
      <div className="integration-loading">
        <FiRefreshCw className="loading-icon" />
        <p>Loading integration dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="integration-error">
        <FiAlertCircle />
        <p>{error}</p>
        <button onClick={loadDashboard}>Try Again</button>
      </div>
    );
  }

  return (
    <div className="integration-dashboard">
      <div className="integration-header">
        <div>
          <span className="integration-subtitle">
            ENTERPRISE DATA MANAGEMENT
          </span>
          <h1>Integration Dashboard</h1>
          <p>
            Monitor connectors, synchronization activities and data flows.
          </p>
        </div>

        <div className="integration-header-actions">
          <button
            className="integration-refresh"
            onClick={loadDashboard}
          >
            <FiRefreshCw />
            Refresh
          </button>

          <button
            className="integration-create"
            onClick={() => window.location.href = "/integrations/create"}
          >
            <FiPlus />
            New Integration
          </button>
        </div>
      </div>

      <div className="integration-stats">
        <div className="integration-stat-card">
          <div className="integration-stat-icon purple">
            <FiDatabase />
          </div>
          <div>
            <span>Total Integrations</span>
            <h2>{totalIntegrations}</h2>
            <small>Configured connectors</small>
          </div>
        </div>

        <div className="integration-stat-card">
          <div className="integration-stat-icon green">
            <FiActivity />
          </div>
          <div>
            <span>Active Connectors</span>
            <h2>{activeIntegrations}</h2>
            <small>Enabled integrations</small>
          </div>
        </div>

        <div className="integration-stat-card">
          <div className="integration-stat-icon blue">
            <FiCheckCircle />
          </div>
          <div>
            <span>Successful Syncs</span>
            <h2>{successfulSyncs}</h2>
            <small>Completed executions</small>
          </div>
        </div>

        <div className="integration-stat-card">
          <div className="integration-stat-icon red">
            <FiAlertCircle />
          </div>
          <div>
            <span>Failed Syncs</span>
            <h2>{failedSyncs}</h2>
            <small>Failed or partial executions</small>
          </div>
        </div>
      </div>

      <div className="integration-section">
        <div className="integration-section-header">
          <div>
            <h2>Connected Integrations</h2>
            <p>Overview of your configured data connectors.</p>
          </div>

          <span className="integration-count">
            {totalIntegrations} Connectors
          </span>
        </div>

        {integrations.length === 0 ? (
          <div className="integration-empty">
            <FiDatabase />
            <h3>No integrations configured</h3>
            <p>Create your first connector to start integrating data.</p>
          </div>
        ) : (
          <div className="integration-connector-grid">
            {integrations.map((integration) => (
              <div
                className="integration-connector-card"
                key={integration.id}
              >
                <div className="connector-card-top">
                  <div className="connector-icon">
                    {getConnectorIcon(integration.source_type)}
                  </div>

                  <span
                    className={`integration-status ${getStatusClass(
                      integration.is_enabled
                        ? integration.status
                        : "inactive"
                    )}`}
                  >
                    {integration.is_enabled
                      ? integration.status
                      : "Disabled"}
                  </span>
                </div>

                <h3>{integration.name}</h3>

                <p className="connector-type">
                  {integration.source_type.replace("_", " ").toUpperCase()}
                </p>

                <div className="connector-details">
                  <div>
                    <span>Target Module</span>
                    <strong>{integration.target_module}</strong>
                  </div>

                  <div>
                    <span>Sync Strategy</span>
                    <strong>{integration.sync_strategy}</strong>
                  </div>

                  <div>
                    <span>Last Synchronization</span>
                    <strong>
                      {formatDate(integration.last_sync_at)}
                    </strong>
                  </div>
                </div>

                <button
                  className="connector-view-button"
                  onClick={() =>
                    window.location.href = `/integrations/${integration.id}`
                  }
                >
                  View Details
                  <FiArrowUpRight />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="integration-section">
        <div className="integration-section-header">
          <div>
            <h2>Recent Synchronization History</h2>
            <p>Latest synchronization activities across connectors.</p>
          </div>
        </div>

        <div className="integration-table-wrapper">
          <table className="integration-history-table">
            <thead>
              <tr>
                <th>Sync ID</th>
                <th>Integration</th>
                <th>Trigger</th>
                <th>Status</th>
                <th>Processed</th>
                <th>Inserted</th>
                <th>Updated</th>
                <th>Failed</th>
                <th>Date</th>
              </tr>
            </thead>

            <tbody>
              {syncHistory.length === 0 ? (
                <tr>
                  <td colSpan="9" className="integration-no-history">
                    <FiClock />
                    No synchronization history available.
                  </td>
                </tr>
              ) : (
                syncHistory.slice(0, 10).map((sync) => {
                  const integration = integrations.find(
                    (item) => item.id === sync.integration_id
                  );

                  return (
                    <tr key={sync.id}>
                      <td>#{sync.id}</td>
                      <td>
                        {integration?.name || `Integration ${sync.integration_id}`}
                      </td>
                      <td>{sync.trigger_type}</td>
                      <td>
                        <span
                          className={`integration-status ${getStatusClass(
                            sync.status
                          )}`}
                        >
                          {sync.status.replaceAll("_", " ")}
                        </span>
                      </td>
                      <td>{sync.processed_records}</td>
                      <td>{sync.inserted_records}</td>
                      <td>{sync.updated_records}</td>
                      <td>{sync.failed_records}</td>
                      <td>
                        {formatDate(sync.created_at || sync.started_at)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}