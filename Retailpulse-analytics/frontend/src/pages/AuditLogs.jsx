import { useEffect, useState } from "react";
import {
  getAuditLogs,
  getAllAuditLogs,
  getAuditLogById,
} from "../api/auditApi";

import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

import "./AuditLogs.css";
import AuditLogDetailsModal from "../components/audit/AuditLogDetailsModal";

export default function AuditLogs() {
  const user = JSON.parse(localStorage.getItem("user"));
  const companyId = user?.company_id;

  const [logs, setLogs] = useState([]);

  const [search, setSearch] = useState("");
  const [userId, setUserId] = useState("");
  const [action, setAction] = useState("");
  const [module, setModule] = useState("");
  const [resourceType, setResourceType] = useState("");
  const [status, setStatus] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortOrder, setSortOrder] = useState("desc");

  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const [selectedLog, setSelectedLog] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [auditStats, setAuditStats] = useState({
    total_creates: 0,
    total_updates: 0,
    total_deletes: 0,
  });

  const rowsPerPage = 10;

  const normalizedDateFrom = dateFrom
    ? `${dateFrom}T00:00:00`
    : "";

  const normalizedDateTo = dateTo
    ? `${dateTo}T23:59:59`
    : "";

  useEffect(() => {
    if (!companyId) return;

    loadLogs();

    const interval = setInterval(() => {
      loadLogs();
    }, 10000);

    return () => {
      clearInterval(interval);
    };
  }, [
    companyId,
    currentPage,
    search,
    userId,
    action,
    module,
    resourceType,
    status,
    dateFrom,
    dateTo,
    sortOrder,
  ]);

  useEffect(() => {
    setCurrentPage(1);
  }, [
    search,
    userId,
    action,
    module,
    resourceType,
    status,
    dateFrom,
    dateTo,
    sortOrder,
  ]);

  const loadLogs = async () => {
    if (!companyId) return;

    setLoading(true);
    setError("");

    try {
      const data = await getAuditLogs({
        page: currentPage,
        limit: rowsPerPage,
        search,
        userId,
        action,
        module,
        resourceType,
        status,
        dateFrom: normalizedDateFrom,
        dateTo: normalizedDateTo,
        sortOrder,
      });

      setLogs(data.items || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 0);

      setAuditStats({
        total_creates: data.total_creates || 0,
        total_updates: data.total_updates || 0,
        total_deletes: data.total_deletes || 0,
      });
    } catch (error) {
      console.error("Error loading audit logs:", error);

      setLogs([]);
      setTotal(0);
      setTotalPages(0);

      setAuditStats({
        total_creates: 0,
        total_updates: 0,
        total_deletes: 0,
      });

      setError(
        error.response?.data?.detail ||
        "Unable to load audit logs. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setSearch("");
    setUserId("");
    setAction("");
    setModule("");
    setResourceType("");
    setStatus("");
    setDateFrom("");
    setDateTo("");
    setSortOrder("desc");
    setCurrentPage(1);
  };

  const totalLogs = total;
  const totalCreates = auditStats.total_creates;
  const totalUpdates = auditStats.total_updates;
  const totalDeletes = auditStats.total_deletes;

  const badgeClass = (actionValue) => {
    switch (actionValue) {
      case "CREATE":
      case "STOCK_IN":
        return "badge create";

      case "UPDATE":
      case "ADJUST":
        return "badge update";

      case "DELETE":
      case "STOCK_OUT":
        return "badge delete";

      default:
        return "badge";
    }
  };

  const exportCSV = async () => {
    try {
      const allLogs = await getAllAuditLogs({
        search,
        userId,
        action,
        module,
        resourceType,
        status,
        dateFrom: normalizedDateFrom,
        dateTo: normalizedDateTo,
        sortOrder,
      });

      const headers = [
        "ID",
        "Module",
        "Action",
        "Resource Type",
        "Resource ID",
        "Description",
        "User",
        "Status",
        "IP Address",
        "Date",
      ];

      const rows = allLogs.map((log) => [
        log.id,
        log.module,
        log.action,
        log.resource_type || "",
        log.resource_id || "",
        log.description,
        log.user_name || log.user_id,
        log.status,
        log.ip_address || "",
        new Date(log.created_at).toLocaleString(),
      ]);

      const csvContent = [headers, ...rows]
        .map((row) =>
          row
            .map((value) =>
              `"${String(value ?? "").replaceAll('"', '""')}"`
            )
            .join(",")
        )
        .join("\n");

      const blob = new Blob([csvContent], {
        type: "text/csv;charset=utf-8;",
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = "audit_logs.csv";

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error exporting CSV:", error);
      alert("Failed to export audit logs.");
    }
  };

  const exportPDF = async () => {
    try {
      const allLogs = await getAllAuditLogs({
        search,
        userId,
        action,
        module,
        resourceType,
        status,
        dateFrom: normalizedDateFrom,
        dateTo: normalizedDateTo,
        sortOrder,
      });

      const doc = new jsPDF("landscape", "mm", "a4");

      doc.setFontSize(18);
      doc.text("Audit Logs Report", 14, 15);

      doc.setFontSize(9);

      const filterText = [
        search && `Search: ${search}`,
        userId && `User: ${userId}`,
        action && `Action: ${action}`,
        module && `Module: ${module}`,
        resourceType && `Resource: ${resourceType}`,
        status && `Status: ${status}`,
        dateFrom && `From: ${dateFrom}`,
        dateTo && `To: ${dateTo}`,
      ]
        .filter(Boolean)
        .join(" | ");

      if (filterText) {
        doc.text(filterText, 14, 21);
      }

      autoTable(doc, {
        startY: filterText ? 27 : 22,

        head: [[
          "ID",
          "Module",
          "Action",
          "Resource",
          "Resource ID",
          "Description",
          "User",
          "Status",
          "IP",
          "Date",
        ]],

        body: allLogs.map((log) => [
          log.id,
          log.module,
          log.action,
          log.resource_type || "-",
          log.resource_id || "-",
          log.description,
          log.user_name || log.user_id,
          log.status,
          log.ip_address || "-",
          new Date(log.created_at).toLocaleString(),
        ]),

        styles: {
          fontSize: 7,
          cellPadding: 2,
          overflow: "linebreak",
          valign: "middle",
        },

        headStyles: {
          fontSize: 7,
        },

        columnStyles: {
          0: { cellWidth: 12 },
          1: { cellWidth: 27 },
          2: { cellWidth: 25 },
          3: { cellWidth: 27 },
          4: { cellWidth: 25 },
          5: { cellWidth: 70 },
          6: { cellWidth: 20 },
          7: { cellWidth: 20 },
          8: { cellWidth: 25 },
          9: { cellWidth: 40 },
        },

        margin: {
          top: filterText ? 27 : 22,
          left: 10,
          right: 10,
          bottom: 15,
        },
      });

      doc.save("audit_logs.pdf");
    } catch (error) {
      console.error("Error exporting PDF:", error);
      alert("Failed to export audit logs.");
    }
  };

  const handleLogClick = async (auditLogId) => {
    try {
      const data = await getAuditLogById(auditLogId);

      setSelectedLog(data);
    } catch (error) {
      console.error("Error loading audit log details:", error);
      alert("Unable to load audit log details.");
    }
  };

  return (
    <div className="audit-page">
      <div className="page-header">
        <h2>Audit Logs</h2>

        <div className="export-buttons">
          <button onClick={exportCSV}>
            Export CSV
          </button>

          <button onClick={exportPDF}>
            Export PDF
          </button>
        </div>
      </div>

      <div className="audit-cards">
        <div className="audit-card">
          <h3>{totalLogs}</h3>
          <p>Total Logs</p>
        </div>

        <div className="audit-card">
          <h3>{totalCreates}</h3>
          <p>
            {module === "Inventory" ? "Stock In" : "Creates"}
          </p>
        </div>

        <div className="audit-card">
          <h3>{totalUpdates}</h3>
          <p>
            {module === "Inventory" ? "Adjustments" : "Updates"}
          </p>
        </div>

        <div className="audit-card">
          <h3>{totalDeletes}</h3>
          <p>
            {module === "Inventory" ? "Stock Out" : "Deletes"}
          </p>
        </div>
      </div>

      <div className="filters">
        <input
          type="text"
          placeholder="Search logs..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <input
          type="number"
          min="1"
          placeholder="User ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />

        <select
          value={action}
          onChange={(e) => setAction(e.target.value)}
        >
          <option value="">All Actions</option>
          <option value="CREATE">CREATE</option>
          <option value="UPDATE">UPDATE</option>
          <option value="DELETE">DELETE</option>
          <option value="LOGIN">LOGIN</option>
          <option value="LOGOUT">LOGOUT</option>
          <option value="REGISTER">REGISTER</option>
          <option value="IMPORT">IMPORT</option>
          <option value="EXPORT">EXPORT</option>
          <option value="STOCK_IN">STOCK_IN</option>
          <option value="STOCK_OUT">STOCK_OUT</option>
          <option value="ADJUST">ADJUST</option>
          <option value="STATUS_CHANGE">STATUS_CHANGE</option>
        </select>

        <select
          value={module}
          onChange={(e) => setModule(e.target.value)}
        >
          <option value="">All Modules</option>
          <option value="Company">Company</option>
          <option value="Category">Category</option>
          <option value="Product">Product</option>
          <option value="Sales">Sales</option>
          <option value="Inventory">Inventory</option>
          <option value="Employee">Employee</option>
          <option value="Department">Department</option>
          <option value="Customer">Customer</option>
          <option value="Authentication">Authentication</option>
          <option value="User">User</option>
        </select>

        <select
          value={resourceType}
          onChange={(e) => setResourceType(e.target.value)}
        >
          <option value="">All Resources</option>
          <option value="Company">Company</option>
          <option value="Category">Category</option>
          <option value="Product">Product</option>
          <option value="Sale">Sale</option>
          <option value="Inventory">Inventory</option>
          <option value="Employee">Employee</option>
          <option value="Department">Department</option>
          <option value="Customer">Customer</option>
          <option value="User">User</option>
        </select>

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="SUCCESS">SUCCESS</option>
          <option value="FAILED">FAILED</option>
        </select>

        <input
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          title="From date"
        />

        <input
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          title="To date"
        />

        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
        >
          <option value="desc">Newest First</option>
          <option value="asc">Oldest First</option>
        </select>

        <button
          type="button"
          onClick={clearFilters}
        >
          Clear Filters
        </button>
      </div>

      <table className="audit-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Module</th>
            <th>Action</th>
            <th>Description</th>
            <th>User</th>
            <th>Date</th>
          </tr>
        </thead>

        <tbody>
          {loading ? (
            <tr>
              <td
                colSpan="6"
                style={{
                  textAlign: "center",
                  padding: "30px",
                }}
              >
                Loading audit logs...
              </td>
            </tr>
          ) : error ? (
            <tr>
              <td
                colSpan="6"
                style={{
                  textAlign: "center",
                  padding: "30px",
                  color: "red",
                }}
              >
                {error}
              </td>
            </tr>
          ) : logs.length > 0 ? (
            logs.map((log) => (
              <tr
                key={log.id}
                onClick={() => handleLogClick(log.id)}
                style={{ cursor: "pointer" }}
              >
                <td>{log.id}</td>

                <td>{log.module}</td>

                <td>
                  <span className={badgeClass(log.action)}>
                    {log.action}
                  </span>
                </td>

                <td>{log.description}</td>

                <td>
                  {log.user_name || log.user_id}
                </td>

                <td>
                  {new Date(
                    log.created_at
                  ).toLocaleString()}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td
                colSpan="6"
                style={{
                  textAlign: "center",
                  padding: "30px",
                }}
              >
                No activity found for the selected filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="pagination">
        <button
          disabled={
            loading ||
            currentPage === 1
          }
          onClick={() =>
            setCurrentPage((prev) => prev - 1)
          }
        >
          Previous
        </button>

        <span>
          Page {currentPage} of {totalPages || 1}
        </span>

        <button
          disabled={
            loading ||
            currentPage >= totalPages ||
            totalPages === 0
          }
          onClick={() =>
            setCurrentPage((prev) => prev + 1)
          }
        >
          Next
        </button>
      </div>

      {selectedLog && (
        <AuditLogDetailsModal
          log={selectedLog}
          onClose={() => setSelectedLog(null)}
        />
      )}
    </div>
  );
}