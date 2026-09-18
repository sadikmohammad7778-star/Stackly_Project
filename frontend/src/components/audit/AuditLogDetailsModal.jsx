import "./AuditLogDetailsModal.css";

export default function AuditLogDetailsModal({ log, onClose }) {
  if (!log) return null;

  return (
    <div className="audit-modal-overlay">
      <div className="audit-modal">

        <div className="audit-modal-header">
          <h3>Audit Log Details</h3>

          <button onClick={onClose}>
            ×
          </button>
        </div>

        <div className="audit-details">

          <p><strong>User:</strong> {log.user_name || log.user_id}</p>

          <p><strong>Action:</strong> {log.action}</p>

          <p><strong>Module:</strong> {log.module}</p>

          <p><strong>Resource:</strong> {log.resource_type || "-"}</p>

          <p><strong>Resource ID:</strong> {log.resource_id || "-"}</p>

          <p><strong>Description:</strong> {log.description}</p>

          <p><strong>Status:</strong> {log.status}</p>

          <p>
            <strong>Date:</strong>{" "}
            {new Date(log.created_at).toLocaleString()}
          </p>

          <p><strong>IP Address:</strong> {log.ip_address || "-"}</p>

          <p><strong>Browser:</strong> {log.browser || "-"}</p>

          <p><strong>User Agent:</strong> {log.user_agent || "-"}</p>

        </div>

        <div className="audit-values">

          <div>
            <h4>Before Values</h4>

            <pre>
              {log.before_values
                ? JSON.stringify(log.before_values, null, 2)
                : "No previous values"}
            </pre>
          </div>

          <div>
            <h4>After Values</h4>

            <pre>
              {log.after_values
                ? JSON.stringify(log.after_values, null, 2)
                : "No new values"}
            </pre>
          </div>

        </div>

      </div>
    </div>
  );
}