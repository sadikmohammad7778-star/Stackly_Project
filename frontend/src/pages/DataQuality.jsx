import { useEffect, useState } from "react";
import DataQualityCards from "../components/dataQuality/DataQualityCards";
import {
  getDataQualityDashboard,
  getDataQualityIssues,
  updateDataQualityIssue,
  runDataQualityReconciliation,
  getReconciliationHistory,
} from "../services/dataQualityApi";
import "./DataQuality.css";

const DataQuality = () => {
  const [dashboard, setDashboard] = useState(null);
  const [issues, setIssues] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reconciling, setReconciling] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState("");

  const [issuePage, setIssuePage] = useState(1);
  const [historyPage, setHistoryPage] = useState(1);

  const itemsPerPage = 10;

  const [filters, setFilters] = useState({
    status: "",
    severity: "",
    issue_type: "",
    module: "",
    search: "",
  });

  const [selectedIssue, setSelectedIssue] = useState(null);
  const [resolutionNote, setResolutionNote] = useState("");

  const loadDashboard = async () => {
    const data = await getDataQualityDashboard();
    setDashboard(data);
  };

  const loadIssues = async (currentFilters = filters) => {
    const data = await getDataQualityIssues(currentFilters);
    setIssues(Array.isArray(data) ? data : []);
  };

  const loadHistory = async () => {
    const data = await getReconciliationHistory();
    setHistory(Array.isArray(data) ? data : []);
  };

  const loadDataQuality = async () => {
    try {
      setLoading(true);
      setError("");

      await Promise.all([
        loadDashboard(),
        loadIssues(),
        loadHistory(),
      ]);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Failed to load data quality information."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDataQuality();
  }, []);

  const issueStartIndex =
    (issuePage - 1) * itemsPerPage;

  const issueEndIndex =
    issueStartIndex + itemsPerPage;

  const paginatedIssues = issues.slice(
    issueStartIndex,
    issueEndIndex
  );

  const totalIssuePages = Math.ceil(
    issues.length / itemsPerPage
  );

  const historyStartIndex =
    (historyPage - 1) * itemsPerPage;

  const historyEndIndex =
    historyStartIndex + itemsPerPage;

  const paginatedHistory = history.slice(
    historyStartIndex,
    historyEndIndex
  );

  const totalHistoryPages = Math.ceil(
    history.length / itemsPerPage
  );

  const handleFilterChange = (event) => {
    const { name, value } = event.target;

    setFilters((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleApplyFilters = async () => {
    try {
      setError("");
      setIssuePage(1);

      await loadIssues(filters);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Failed to filter issues."
      );
    }
  };

  const handleClearFilters = async () => {
    const clearedFilters = {
      status: "",
      severity: "",
      issue_type: "",
      module: "",
      search: "",
    };

    setFilters(clearedFilters);
    setIssuePage(1);

    try {
      setError("");

      await loadIssues(clearedFilters);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Failed to load issues."
      );
    }
  };

  const handleReconciliation = async () => {
    try {
      setReconciling(true);
      setError("");

      await runDataQualityReconciliation();

      setIssuePage(1);
      setHistoryPage(1);

      await loadDataQuality();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Failed to run reconciliation."
      );
    } finally {
      setReconciling(false);
    }
  };

  const handleSelectIssue = (issue) => {
    setSelectedIssue(issue);
    setResolutionNote(
      issue.resolution_note || ""
    );
  };

  const handleUpdateIssue = async (status) => {
    if (!selectedIssue) {
      return;
    }

    try {
      setUpdating(true);
      setError("");

      await updateDataQualityIssue(
        selectedIssue.id,
        {
          status,
          resolution_note: resolutionNote,
        }
      );

      setSelectedIssue(null);
      setResolutionNote("");

      setIssuePage(1);

      await loadDataQuality();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Failed to update issue."
      );
    } finally {
      setUpdating(false);
    }
  };

  const handlePreviousIssuePage = () => {
    setIssuePage((page) =>
      Math.max(page - 1, 1)
    );
  };

  const handleNextIssuePage = () => {
    setIssuePage((page) =>
      Math.min(page + 1, totalIssuePages)
    );
  };

  const handlePreviousHistoryPage = () => {
    setHistoryPage((page) =>
      Math.max(page - 1, 1)
    );
  };

  const handleNextHistoryPage = () => {
    setHistoryPage((page) =>
      Math.min(page + 1, totalHistoryPages)
    );
  };

  if (loading) {
    return (
      <div className="data-quality-page">
        <div className="data-quality-loading">
          Loading data quality...
        </div>
      </div>
    );
  }

  return (
    <div className="data-quality-page">
      <div className="data-quality-header">
        <div>
          <h1>Data Quality</h1>

          <p>
            Monitor data quality, reconciliation issues,
            and validation status.
          </p>
        </div>

        <button
          type="button"
          className="data-quality-reconcile-button"
          onClick={handleReconciliation}
          disabled={reconciling}
        >
          {reconciling
            ? "Running..."
            : "Run Reconciliation"}
        </button>
      </div>

      {error && (
        <div className="data-quality-error">
          {error}
        </div>
      )}

      <DataQualityCards
        dashboard={dashboard}
      />

      <div className="data-quality-summary">
        <div>
          <span>Last Reconciliation</span>

          <strong>
            {dashboard?.last_reconciliation
              ?.completed_at
              ? new Date(
                  dashboard.last_reconciliation.completed_at
                ).toLocaleString()
              : "Not available"}
          </strong>
        </div>

        <div>
          <span>Execution Status</span>

          <strong>
            {dashboard?.last_reconciliation
              ?.execution_status || "N/A"}
          </strong>
        </div>

        <div>
          <span>Issues Detected</span>

          <strong>
            {dashboard?.last_reconciliation
              ?.issues_detected ?? 0}
          </strong>
        </div>

        <div>
          <span>Records Checked</span>

          <strong>
            {dashboard?.last_reconciliation
              ?.records_checked ?? 0}
          </strong>
        </div>
      </div>

      <div className="data-quality-filters">
        <input
          type="text"
          name="search"
          placeholder="Search issues..."
          value={filters.search}
          onChange={handleFilterChange}
        />

        <select
          name="status"
          value={filters.status}
          onChange={handleFilterChange}
        >
          <option value="">All Statuses</option>
          <option value="OPEN">Open</option>
          <option value="INVESTIGATING">
            Investigating
          </option>
          <option value="RESOLVED">
            Resolved
          </option>
          <option value="IGNORED">
            Ignored
          </option>
        </select>

        <select
          name="severity"
          value={filters.severity}
          onChange={handleFilterChange}
        >
          <option value="">All Severities</option>
          <option value="ERROR">Error</option>
          <option value="WARNING">Warning</option>
        </select>

        <select
          name="module"
          value={filters.module}
          onChange={handleFilterChange}
        >
          <option value="">All Modules</option>
          <option value="Inventory">
            Inventory
          </option>
          <option value="Sales">
            Sales
          </option>
          <option value="Product">
            Product
          </option>
          <option value="Customer">
            Customer
          </option>
          <option value="Reports">
            Reports
          </option>
        </select>

        <select
          name="issue_type"
          value={filters.issue_type}
          onChange={handleFilterChange}
        >
          <option value="">
            All Issue Types
          </option>

          <option value="STOCK_MOVEMENT_MISMATCH">
            Stock Movement Mismatch
          </option>

          <option value="INVALID_STOCK_MOVEMENT">
            Invalid Stock Movement
          </option>

          <option value="SALE_TOTAL_MISMATCH">
            Sale Total Mismatch
          </option>

          <option value="INVALID_SALE_CUSTOMER">
            Invalid Sale Customer
          </option>

          <option value="SALE_WITHOUT_ITEMS">
            Sale Without Items
          </option>

          <option value="INVALID_SALE_QUANTITY">
            Invalid Sale Quantity
          </option>

          <option value="INVALID_SALE_ITEM_AMOUNT">
            Invalid Sale Item Amount
          </option>

          <option value="MISSING_SALE_DATA">
            Missing Sale Data
          </option>

          <option value="DUPLICATE_SKU">
            Duplicate SKU
          </option>

          <option value="INVALID_SKU">
            Invalid SKU
          </option>

          <option value="MISSING_PRODUCT_DATA">
            Missing Product Data
          </option>

          <option value="INACTIVE_PRODUCT_WITH_STOCK">
            Inactive Product With Stock
          </option>

          <option value="DUPLICATE_CUSTOMER_ID">
            Duplicate Customer ID
          </option>

          <option value="DUPLICATE_CUSTOMER_EMAIL">
            Duplicate Customer Email
          </option>

          <option value="DUPLICATE_CUSTOMER_PHONE">
            Duplicate Customer Phone
          </option>

          <option value="MISSING_CUSTOMER_DATA">
            Missing Customer Data
          </option>

          <option value="INVALID_CUSTOMER_ID">
            Invalid Customer ID
          </option>

          <option value="INVALID_CUSTOMER_EMAIL">
            Invalid Customer Email
          </option>

          <option value="INVALID_CUSTOMER_STATUS">
            Invalid Customer Status
          </option>

          <option value="DELETED_ACTIVE_CUSTOMER">
            Deleted Active Customer
          </option>
        </select>

        <button
          type="button"
          onClick={handleApplyFilters}
        >
          Apply
        </button>

        <button
          type="button"
          onClick={handleClearFilters}
        >
          Clear
        </button>
      </div>

      <div className="data-quality-section">
        <div className="data-quality-section-header">
          <div>
            <h2>Data Quality Issues</h2>

            <p>
              Review detected data inconsistencies
              and validation issues.
            </p>
          </div>
        </div>

        {issues.length === 0 ? (
          <div className="data-quality-empty">
            No data quality issues found.
          </div>
        ) : (
          <>
            <div className="data-quality-table-wrapper">
              <table className="data-quality-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Module</th>
                    <th>Record</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Detected</th>
                    <th>Action</th>
                  </tr>
                </thead>

                <tbody>
                  {paginatedIssues.map((issue) => (
                    <tr key={issue.id}>
                      <td>{issue.id}</td>

                      <td>
                        {issue.issue_type}
                      </td>

                      <td>
                        <span
                          className={`data-quality-severity ${issue.severity?.toLowerCase()}`}
                        >
                          {issue.severity}
                        </span>
                      </td>

                      <td>{issue.module}</td>

                      <td>
                        {issue.affected_record_type
                          ? `${issue.affected_record_type} #${issue.affected_record_id}`
                          : "-"}
                      </td>

                      <td>
                        {issue.description}
                      </td>

                      <td>
                        <span
                          className={`data-quality-status ${issue.status?.toLowerCase()}`}
                        >
                          {issue.status}
                        </span>
                      </td>

                      <td>
                        {issue.detected_at
                          ? new Date(
                              issue.detected_at
                            ).toLocaleString()
                          : "-"}
                      </td>

                      <td>
                        <button
                          type="button"
                          className="data-quality-view-button"
                          onClick={() =>
                            handleSelectIssue(issue)
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

            {totalIssuePages > 1 && (
              <div className="data-quality-pagination">
                <button
                  type="button"
                  disabled={issuePage === 1}
                  onClick={
                    handlePreviousIssuePage
                  }
                >
                  Previous
                </button>

                <span>
                  Page {issuePage} of{" "}
                  {totalIssuePages}
                </span>

                <button
                  type="button"
                  disabled={
                    issuePage === totalIssuePages
                  }
                  onClick={
                    handleNextIssuePage
                  }
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <div className="data-quality-section">
        <div className="data-quality-section-header">
          <div>
            <h2>
              Reconciliation History
            </h2>

            <p>
              Review previous reconciliation runs
              and their results.
            </p>
          </div>
        </div>

        {history.length === 0 ? (
          <div className="data-quality-empty">
            No reconciliation history available.
          </div>
        ) : (
          <>
            <div className="data-quality-table-wrapper">
              <table className="data-quality-table">
                <thead>
                  <tr>
                    <th>Run ID</th>
                    <th>Started</th>
                    <th>Completed</th>
                    <th>Records Checked</th>
                    <th>Issues Detected</th>
                    <th>Issues Resolved</th>
                    <th>Failed Checks</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {paginatedHistory.map((run) => (
                    <tr key={run.id}>
                      <td>{run.id}</td>

                      <td>
                        {run.started_at
                          ? new Date(
                              run.started_at
                            ).toLocaleString()
                          : "-"}
                      </td>

                      <td>
                        {run.completed_at
                          ? new Date(
                              run.completed_at
                            ).toLocaleString()
                          : "-"}
                      </td>

                      <td>
                        {run.records_checked ?? 0}
                      </td>

                      <td>
                        {run.issues_detected ?? 0}
                      </td>

                      <td>
                        {run.issues_resolved ?? 0}
                      </td>

                      <td>
                        {run.failed_checks ?? 0}
                      </td>

                      <td>
                        <span
                          className={`data-quality-status ${run.execution_status?.toLowerCase()}`}
                        >
                          {run.execution_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalHistoryPages > 1 && (
              <div className="data-quality-pagination">
                <button
                  type="button"
                  disabled={historyPage === 1}
                  onClick={
                    handlePreviousHistoryPage
                  }
                >
                  Previous
                </button>

                <span>
                  Page {historyPage} of{" "}
                  {totalHistoryPages}
                </span>

                <button
                  type="button"
                  disabled={
                    historyPage ===
                    totalHistoryPages
                  }
                  onClick={
                    handleNextHistoryPage
                  }
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {selectedIssue && (
        <div className="data-quality-modal-overlay">
          <div className="data-quality-modal">
            <div className="data-quality-modal-header">
              <div>
                <h2>
                  Issue #{selectedIssue.id}
                </h2>

                <p>
                  {selectedIssue.issue_type}
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  setSelectedIssue(null)
                }
              >
                ×
              </button>
            </div>

            <div className="data-quality-details">
              <div>
                <span>Severity</span>

                <strong>
                  {selectedIssue.severity}
                </strong>
              </div>

              <div>
                <span>Module</span>

                <strong>
                  {selectedIssue.module}
                </strong>
              </div>

              <div>
                <span>Status</span>

                <strong>
                  {selectedIssue.status}
                </strong>
              </div>

              <div>
                <span>Record</span>

                <strong>
                  {selectedIssue.affected_record_type
                    ? `${selectedIssue.affected_record_type} #${selectedIssue.affected_record_id}`
                    : "-"}
                </strong>
              </div>
            </div>

            <div className="data-quality-description">
              <span>Description</span>

              <p>
                {selectedIssue.description}
              </p>
            </div>

            {selectedIssue.details && (
              <div className="data-quality-description">
                <span>Details</span>

                <pre>
                  {JSON.stringify(
                    selectedIssue.details,
                    null,
                    2
                  )}
                </pre>
              </div>
            )}

            <div className="data-quality-resolution">
              <label htmlFor="resolution-note">
                Resolution Note
              </label>

              <textarea
                id="resolution-note"
                value={resolutionNote}
                onChange={(event) =>
                  setResolutionNote(
                    event.target.value
                  )
                }
                placeholder="Enter resolution details..."
              />
            </div>

            <div className="data-quality-modal-actions">
              <button
                type="button"
                disabled={updating}
                onClick={() =>
                  handleUpdateIssue(
                    "INVESTIGATING"
                  )
                }
              >
                Investigating
              </button>

              <button
                type="button"
                disabled={updating}
                onClick={() =>
                  handleUpdateIssue(
                    "RESOLVED"
                  )
                }
              >
                Resolve
              </button>

              <button
                type="button"
                disabled={updating}
                onClick={() =>
                  handleUpdateIssue(
                    "IGNORED"
                  )
                }
              >
                Ignore
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataQuality;