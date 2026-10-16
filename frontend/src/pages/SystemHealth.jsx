import { useEffect, useState } from "react";
import {
  getSystemHealthDetails,
  getPerformanceSummary,
  getPerformanceMetrics,
} from "../api/systemHealthApi";
import "./SystemHealth.css";

export default function SystemHealth() {
  const [health, setHealth] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      setError("");

      const results = await Promise.allSettled([
        getSystemHealthDetails(),
        getPerformanceSummary(),
        getPerformanceMetrics(),
      ]);

      if (results[0].status === "fulfilled") {
        setHealth(results[0].value);
        } else {
            setHealth({
                status: "unavailable",
                components: {
                api: { status: "unavailable" },
                database: { status: "unknown" },
                background_processor: { status: "unknown" },
                },
            });
        }

      if (results[1].status === "fulfilled") {
        setPerformance(results[1].value);
      }

      if (results[2].status === "fulfilled") {
        const data = results[2].value;
        setMetrics(Array.isArray(data) ? data : data.metrics || []);
      }

      const failedRequests = results.filter(
        (result) => result.status === "rejected"
        ).length;

        if (failedRequests > 0) {
            setError(
                `${failedRequests} monitoring request(s) failed. Some displayed data may be unavailable.`
            );
        }
    } catch {
      setError("Unable to load system health data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    const interval = setInterval(loadData, 30000);

    return () => clearInterval(interval);
  }, []);

  const getStatusClass = (status) => {
    if (["healthy", "running", "completed"].includes(
      String(status || "").toLowerCase()
    )) {
      return "health-status healthy";
    }

    if (["degraded", "warning"].includes(
      String(status || "").toLowerCase()
    )) {
      return "health-status warning";
    }

    return "health-status unhealthy";
  };

  const formatValue = (value) => {
    if (value === null || value === undefined || value === "") {
      return "N/A";
    }

    return value;
  };

  if (loading) {
    return <div className="system-health-loading">Loading system health...</div>;
  }

  return (
    <div className="system-health-page">
      <div className="system-health-header">
        <div>
          <h1>System Health Monitoring</h1>
          <p>Monitor application status, background jobs, and API performance.</p>
        </div>

        <button onClick={loadData} className="health-refresh-button">
          Refresh
        </button>
      </div>

      {error && <div className="health-error">{error}</div>}

      <section className="health-overview">
        <div className="health-card">
          <h3>Application Status</h3>
          <span className={getStatusClass(health?.status)}>
            {formatValue(health?.status)}
          </span>
        </div>

        <div className="health-card">
          <h3>Database Status</h3>
          <span className={getStatusClass(health?.components?.database?.status)}>
            {formatValue(health?.components?.database?.status)}
          </span>
          <p>
            Response time:{" "}
            {formatValue(health?.components?.database?.response_time_ms)} ms
          </p>
        </div>

        <div className="health-card">
          <h3>Background Worker</h3>
          <span
            className={getStatusClass(
              health?.components?.background_processor?.status
            )}
          >
            {formatValue(
              health?.components?.background_processor?.status
            )}
          </span>
          <p>
            Completed cycles:{" "}
            {formatValue(
              health?.components?.background_processor?.completed_cycles
            )}
          </p>
        </div>

        <div className="health-card">
          <h3>Average Response Time</h3>
          <strong>
            {formatValue(performance?.average_response_time_ms)} ms
          </strong>
        </div>

        <div className="health-card">
          <h3>Total Requests</h3>
          <strong>{formatValue(performance?.total_requests)}</strong>
        </div>

        <div className="health-card">
          <h3>Failed Requests</h3>
          <strong>{formatValue(
            performance?.failed_requests
          )}</strong>
        </div>
      </section>

      <section className="health-details-section">
        <h2>Component Details</h2>

        <div className="health-table-wrapper">
          <table className="health-table">
            <thead>
              <tr>
                <th>Component</th>
                <th>Status</th>
                <th>Details</th>
              </tr>
            </thead>

            <tbody>
              {Object.entries(health?.components || {}).map(
                ([name, component]) => (
                  <tr key={name}>
                    <td>{name.replaceAll("_", " ")}</td>
                    <td>
                      <span className={getStatusClass(component.status)}>
                        {formatValue(component.status)}
                      </span>
                    </td>
                    <td>
                      {component.response_time_ms !== undefined
                        ? `${component.response_time_ms} ms response time`
                        : component.last_heartbeat
                          ? `Last heartbeat: ${component.last_heartbeat}`
                          : component.name || "No additional details"}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="health-details-section">
        <h2>Recent API Performance</h2>

        <div className="health-table-wrapper">
          <table className="health-table">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Method</th>
                <th>Status Code</th>
                <th>Response Time</th>
                <th>Timestamp</th>
              </tr>
            </thead>

            <tbody>
              {metrics.length > 0 ? (
                metrics.slice().reverse().slice(0, 20).map((metric, index) => (
                  <tr key={metric.id || `${metric.timestamp}-${index}`}>
                    <td>{metric.endpoint || metric.path || "N/A"}</td>
                    <td>{metric.method || "N/A"}</td>
                    <td>{formatValue(metric.status_code)}</td>
                    <td>
                      {formatValue(metric.response_time_ms)} ms
                    </td>
                    <td>
                      {metric.timestamp
                        ? new Date(metric.timestamp).toLocaleString()
                        : "N/A"}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5">No performance metrics available.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <p className="health-last-updated">
        Last updated:{" "}
        {health?.timestamp
          ? new Date(health.timestamp).toLocaleString()
          : "Unavailable"}
      </p>
    </div>
  );
}