import { useEffect, useState } from "react";
import { getAuditLogs } from "../api/auditApi";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import "./AuditLogs.css";

export default function AuditLogs() {
  const user = JSON.parse(localStorage.getItem("user"));
  const companyId = user?.company_id;

  const [logs, setLogs] = useState([]);
  const [search, setSearch] = useState("");
  const [module, setModule] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const rowsPerPage = 10;

  useEffect(() => {

    if (companyId) {
        loadLogs();
    }

    }, [companyId, search, module]);
  const loadLogs = async () => {

  if (!companyId) return;

  try {

    const data = await getAuditLogs(
      companyId,
      search,
      module
    );

    console.log("Audit Logs:", data);

    setLogs(data);
    setCurrentPage(1);

  } catch (error) {

    console.error(error);

  }

};

  // ===============================
  // KPI Cards
  // ===============================

  const totalLogs = logs.length;

  const totalCreates = logs.filter(
    (log) => log.action === "CREATE"
  ).length;

  const totalUpdates = logs.filter(
    (log) => log.action === "UPDATE"
  ).length;

  const totalDeletes = logs.filter(
    (log) => log.action === "DELETE"
  ).length;

  // ===============================
  // Pagination
  // ===============================

  const lastRow = currentPage * rowsPerPage;
  const firstRow = lastRow - rowsPerPage;

  const currentLogs = logs.slice(firstRow, lastRow);

  const totalPages = Math.ceil(logs.length / rowsPerPage);

  // ===============================
  // Badge Color
  // ===============================

  const badgeClass = (action) => {
    switch (action) {
      case "CREATE":
        return "badge create";

      case "UPDATE":
        return "badge update";

      case "DELETE":
        return "badge delete";

      default:
        return "badge";
    }
  };

  // ===============================
  // Export CSV
  // ===============================

  const exportCSV = () => {
    const headers = [
      "Module",
      "Action",
      "Description",
      "User",
      "Date",
    ];

    const rows = logs.map((log) => [
      log.module,
      log.action,
      log.description,
      log.user_id,
      new Date(log.created_at).toLocaleString(),
    ]);

    const csvContent = [headers, ...rows]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob(
      [csvContent],
      { type: "text/csv" }
    );

    const url =
      window.URL.createObjectURL(blob);

    const link =
      document.createElement("a");

    link.href = url;
    link.download = "audit_logs.csv";
    link.click();
  };

  // ===============================
  // Export PDF
  // ===============================

  const exportPDF = () => {
    const doc = new jsPDF();

    doc.text("Audit Logs Report", 14, 15);

    autoTable(doc, {
      head: [[
        "Module",
        "Action",
        "Description",
        "User",
        "Date",
      ]],

      body: logs.map((log) => [
        log.module,
        log.action,
        log.description,
        log.user_id,
        new Date(log.created_at).toLocaleString(),
      ]),
    });

    doc.save("audit_logs.pdf");
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

      {/* KPI Cards */}

      <div className="audit-cards">

        <div className="audit-card">
          <h3>{totalLogs}</h3>
          <p>Total Logs</p>
        </div>

        <div className="audit-card">
          <h3>{totalCreates}</h3>
          <p>Creates</p>
        </div>

        <div className="audit-card">
          <h3>{totalUpdates}</h3>
          <p>Updates</p>
        </div>

        <div className="audit-card">
          <h3>{totalDeletes}</h3>
          <p>Deletes</p>
        </div>

      </div>

      {/* Filters */}

      <div className="filters">

        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) =>
            setSearch(e.target.value)
          }
        />

        <select
          value={module}
          onChange={(e) =>
            setModule(e.target.value)
          }
        >
          <option value="">All Modules</option>
          <option value="Company">Company</option>
          <option value="Category">Category</option>
          <option value="Product">Product</option>
          <option value="Sales">Sales</option>
          <option value="Inventory">Inventory</option>
          <option value="Employee">Employee</option>
        </select>

      </div>

      {/* Table */}

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

          {currentLogs.length > 0 ? (

            currentLogs.map((log) => (

              <tr key={log.id}>

                <td>{log.id}</td>

                <td>{log.module}</td>

                <td>
                  <span
                    className={badgeClass(log.action)}
                  >
                    {log.action}
                  </span>
                </td>

                <td>{log.description}</td>

               <td>{log.user_name || log.user_id}</td>

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
                style={{ textAlign: "center" }}
              >
                No audit logs found.
              </td>
            </tr>

          )}

        </tbody>

      </table>

      {/* Pagination */}

      <div className="pagination">

        <button
          disabled={currentPage === 1}
          onClick={() =>
            setCurrentPage(currentPage - 1)
          }
        >
          Previous
        </button>

        <span>
          Page {currentPage} of{" "}
          {totalPages || 1}
        </span>

        <button
          disabled={
            currentPage === totalPages ||
            totalPages === 0
          }
          onClick={() =>
            setCurrentPage(currentPage + 1)
          }
        >
          Next
        </button>

      </div>

    </div>
  );
}