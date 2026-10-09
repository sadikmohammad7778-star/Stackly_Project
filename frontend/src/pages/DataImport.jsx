import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

import {
  uploadImport,
  validateImport,
  processImport,
  getImportStatus,
  getImportHistory,
  getImportDetails,
  cancelImport,
  downloadTemplate,
  downloadFailedRecords,
} from "../api/importApi";

import {
  createApprovalRequest,
  submitApprovalRequest,
} from "../api/workflowApi";

import "./DataImport.css";

const ACTIVE_STATUSES = [
  "Processing",
  "Uploaded",
  "Validated",
];

const FINAL_STATUSES = [
  "Completed",
  "Completed With Errors",
  "Failed",
  "Validation Failed",
  "Cancelled",
];

const MAX_FILE_SIZE = 10 * 1024 * 1024;

export default function DataImport() {
  const [importType, setImportType] = useState("products");
  const [file, setFile] = useState(null);

  const [uploadData, setUploadData] = useState(null);
  const [validationData, setValidationData] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [resultData, setResultData] = useState(null);

  const [history, setHistory] = useState([]);
  const [details, setDetails] = useState(null);

  const [loading, setLoading] = useState(false);
  const [templateLoading, setTemplateLoading] = useState(false);
  const [error, setError] = useState("");

  const [searchParams] = useSearchParams();

  const pollingRef = useRef(null);

  const getErrorMessage = (err, fallback) => {
    return (
      err.response?.data?.detail?.message ||
      err.response?.data?.detail ||
      err.message ||
      fallback
    );
  };

  const clearPolling = () => {
    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
      pollingRef.current = null;
    }
  };

  const resetImportState = () => {
    setFile(null);
    setUploadData(null);
    setValidationData(null);
    setStatusData(null);
    setResultData(null);
    setDetails(null);
    setError("");
    clearPolling();
  };

  const loadHistory = async () => {
    try {
      const data = await getImportHistory();
      setHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load import history:", err);
      setError(
        getErrorMessage(
          err,
          "Failed to load import history."
        )
      );
    }
  };

  useEffect(() => {
    loadHistory();

    return () => {
      clearPolling();
    };
  }, []);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    setError("");
    setUploadData(null);
    setValidationData(null);
    setStatusData(null);
    setResultData(null);
    setDetails(null);
    clearPolling();

    if (!selectedFile) {
      setFile(null);
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith(".csv")) {
      setFile(null);
      event.target.value = "";
      setError("Only CSV files are allowed.");
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setFile(null);
      event.target.value = "";
      setError("File size must not exceed 10 MB.");
      return;
    }

    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a CSV file.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      setUploadData(null);
      setValidationData(null);
      setStatusData(null);
      setResultData(null);
      setDetails(null);

      const data = await uploadImport(importType, file);

      setUploadData(data);

      await loadHistory();
    } catch (err) {
      console.error("Upload failed:", err);
      setError(
        getErrorMessage(
          err,
          "Failed to upload import file."
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async () => {
    const importId = Number(uploadData?.import_id);

    if (!importId) {
      setError("Please upload the file first.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      setValidationData(null);
      setStatusData(null);
      setResultData(null);

      const data = await validateImport(importId);

      setValidationData(data);

      await loadHistory();
    } catch (err) {
      console.error("Validation failed:", err);
      setError(
        getErrorMessage(
          err,
          "Failed to validate import."
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (importId) => {
    const id = Number(importId);

    if (!id) {
      setError("Invalid import ID.");
      return;
    }

    try {
      setError("");

      const data = await getImportDetails(id);

      setDetails(data);
    } catch (err) {
      console.error("View details failed:", err);
      setError(
        getErrorMessage(
          err,
          "Failed to load import details."
        )
      );
    }
  };

  const pollImportStatus = async (importId) => {
    const id = Number(importId);

    if (!id) {
      setError("Invalid import ID.");
      setLoading(false);
      return;
    }

    try {
      const data = await getImportStatus(id);

      setStatusData(data);

      if (ACTIVE_STATUSES.includes(data.status)) {
        pollingRef.current = setTimeout(() => {
          pollImportStatus(id);
        }, 1000);

        return;
      }

      clearPolling();

      setResultData(data);
      setLoading(false);

      await loadHistory();

      if (FINAL_STATUSES.includes(data.status)) {
        await handleViewDetails(id);
      }
    } catch (err) {
      console.error("Status polling failed:", err);

      clearPolling();
      setLoading(false);

      setError(
        getErrorMessage(
          err,
          "Failed to track import progress."
        )
      );
    }
  };

  const handleCreateInventoryApproval = async () => {
    const importId = Number(uploadData?.import_id);

    if (!importId) {
      setError("Please upload the file first.");
      return;
    }

    if (!validationData) {
      setError("Please validate the import first.");
      return;
    }

    if (validationData.invalid_records > 0) {
      setError(
        "Approval request cannot be created because validation failed."
      );
      return;
    }

    if (validationData.valid_records === 0) {
      setError("There are no valid records to approve.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResultData(null);
      setDetails(null);

      const user = JSON.parse(
        localStorage.getItem("user") || "null"
      );

      const companyId = user?.company_id;

      if (!companyId) {
        setError(
          "Company information is missing. Please login again."
        );
        return;
      }

      const data = await createApprovalRequest({
        company_id: companyId,
        request_type: "inventory_import",
        related_entity_type: "import",
        related_entity_id: importId,
        requested_changes: {
          import_id: importId,
        },
        reason:
          "Inventory import approval requested from frontend.",
        priority: "medium",
      });

      await submitApprovalRequest(data.id, {
        comments:
          "Please review and approve the inventory import.",
      });

      setResultData({
        status: "Pending Approval",
        total_records: validationData.total_records,
        successful_records: 0,
        failed_records: 0,
        duplicate_records:
          validationData.duplicate_records || 0,
      });

      await loadHistory();

      alert(
        `Approval request #${data.id} submitted successfully.`
      );
    } catch (err) {
      console.error(
        "Inventory approval request failed:",
        err
      );

      setError(
        getErrorMessage(
          err,
          "Failed to create inventory approval request."
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async () => {
    const importId = Number(uploadData?.import_id);

    if (!importId) {
      setError("Please upload the file first.");
      return;
    }

    if (!validationData) {
      setError("Please validate the import first.");
      return;
    }

    if (validationData.invalid_records > 0) {
      setError(
        "Import cannot be processed because validation failed."
      );
      return;
    }

    if (validationData.valid_records === 0) {
      setError("There are no valid records to import.");
      return;
    }

    if (importType === "inventory") {
      await handleCreateInventoryApproval();
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResultData(null);
      setDetails(null);

      clearPolling();

      const data = await processImport(importId);

      setStatusData(data);

      await loadHistory();

      pollImportStatus(importId);
    } catch (err) {
      console.error("Processing failed:", err);

      setLoading(false);

      setError(
        getErrorMessage(
          err,
          "Failed to start import."
        )
      );
    }
  };

  const handleCancel = async (importId) => {
    const id = Number(importId);

    if (!id) {
      setError("Invalid import ID.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      clearPolling();

      await cancelImport(id);

      await loadHistory();

      const data = await getImportStatus(id);

      setStatusData(data);
      setResultData(data);

      await handleViewDetails(id);
    } catch (err) {
      console.error("Cancel failed:", err);

      setError(
        getErrorMessage(
          err,
          "Failed to cancel import."
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      setTemplateLoading(true);
      setError("");

      const response = await downloadTemplate(importType);

      const blob = new Blob([response.data], {
        type: "text/csv",
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = `${importType}_import_template.csv`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(
        "Template download failed:",
        err
      );

      setError(
        getErrorMessage(
          err,
          "Failed to download template."
        )
      );
    } finally {
      setTemplateLoading(false);
    }
  };

  const handleDownloadFailedRecords = async (importId) => {
    const id = Number(importId);

    if (!id) {
      setError("Invalid import ID.");
      return;
    }

    try {
      setError("");

      const response =
        await downloadFailedRecords(id);

      const blob = new Blob([response.data], {
        type: "text/csv",
      });

      const url =
        window.URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = url;
      link.download =
        `import_${id}_failed_records.csv`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(
        "Failed to download records:",
        err
      );

      setError(
        getErrorMessage(
          err,
          "Failed to download failed records."
        )
      );
    }
  };

  const handleImportTypeChange = (event) => {
    setImportType(event.target.value);

    setFile(null);
    setUploadData(null);
    setValidationData(null);
    setStatusData(null);
    setResultData(null);
    setDetails(null);
    setError("");

    clearPolling();

    const input =
      document.getElementById("import-file");

    if (input) {
      input.value = "";
    }
  };

  const removeFile = () => {
    setFile(null);
    setUploadData(null);
    setValidationData(null);
    setStatusData(null);
    setResultData(null);
    setDetails(null);
    setError("");

    clearPolling();

    const input =
      document.getElementById("import-file");

    if (input) {
      input.value = "";
    }
  };

  const closeDetails = () => {
    setDetails(null);
  };

  useEffect(() => {
    const importId =
      searchParams.get("import_id");

    if (importId) {
      handleViewDetails(Number(importId));
    }
  }, [searchParams]);

  return (
    <div className="data-import-page">
      <div className="data-import-header">
        <div>
          <h1>Data Import</h1>

          <p>
            Import Products, Inventory, Customers and Sales
            Transactions into RetailPulse.
          </p>
        </div>
      </div>

      {error && (
        <div className="import-error">
          {error}
        </div>
      )}

      <section className="import-card">
        <h2>Upload Data</h2>

        <div className="import-form">
          <div className="form-group">
            <label>Import Type</label>

            <select
              value={importType}
              onChange={handleImportTypeChange}
            >
              <option value="products">
                Products
              </option>

              <option value="inventory">
                Inventory
              </option>

              <option value="customers">
                Customers
              </option>

              <option value="sales">
                Sales Transactions
              </option>
            </select>
          </div>

          <div className="form-group">
            <label>CSV File</label>

            <input
              id="import-file"
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
            />
          </div>
        </div>

        <div className="template-section">
          <button
            type="button"
            className="secondary-button"
            onClick={handleDownloadTemplate}
            disabled={templateLoading}
          >
            {templateLoading
              ? "Downloading..."
              : "Download Template"}
          </button>
        </div>

        {file && (
          <div className="selected-file">
            <div>
              <strong>Selected file:</strong>{" "}
              {file.name}
            </div>

            <button
              type="button"
              onClick={removeFile}
            >
              Remove
            </button>
          </div>
        )}

        <button
          type="button"
          className="primary-button"
          onClick={handleUpload}
          disabled={!file || loading}
        >
          {loading
            ? "Uploading..."
            : "Upload File"}
        </button>
      </section>

      {uploadData && (
        <section className="import-card">
          <div className="section-title">
            <div>
              <h2>CSV Preview</h2>

              <p>
                Import ID:{" "}
                <strong>
                  {uploadData.import_id}
                </strong>
              </p>
            </div>

            <span className="record-count">
              {uploadData.total_records} records
            </span>
          </div>

          <div className="columns-list">
            {uploadData.columns.map(
              (column) => (
                <span key={column}>
                  {column}
                </span>
              )
            )}
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  {uploadData.columns.map(
                    (column) => (
                      <th key={column}>
                        {column}
                      </th>
                    )
                  )}
                </tr>
              </thead>

              <tbody>
                {uploadData.preview.map(
                  (row, index) => (
                    <tr key={index}>
                      {uploadData.columns.map(
                        (column) => (
                          <td key={column}>
                            {row[column]}
                          </td>
                        )
                      )}
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>

          <button
            type="button"
            className="primary-button"
            onClick={handleValidate}
            disabled={loading}
          >
            {loading
              ? "Validating..."
              : "Validate Data"}
          </button>
        </section>
      )}

      {validationData && (
        <section className="import-card">
          <h2>Validation Result</h2>

          <div className="summary-grid">
            <div className="summary-box">
              <span>Total Records</span>

              <strong>
                {validationData.total_records}
              </strong>
            </div>

            <div className="summary-box success">
              <span>Valid Records</span>

              <strong>
                {validationData.valid_records}
              </strong>
            </div>

            <div className="summary-box danger">
              <span>Invalid Records</span>

              <strong>
                {validationData.invalid_records}
              </strong>
            </div>

            <div className="summary-box warning">
              <span>Duplicates</span>

              <strong>
                {validationData.duplicate_records}
              </strong>
            </div>
          </div>

          {validationData.errors?.length > 0 && (
            <div className="validation-errors">
              <h3>Validation Errors</h3>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Row</th>
                      <th>Type</th>
                      <th>Error</th>
                    </tr>
                  </thead>

                  <tbody>
                    {validationData.errors.map(
                      (item, index) => (
                        <tr key={index}>
                          <td>
                            {item.row_number}
                          </td>

                          <td>
                            {item.error_type}
                          </td>

                          <td>
                            {item.error_message}
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <button
            type="button"
            className="primary-button"
            onClick={handleProcess}
            disabled={
              loading ||
              validationData.invalid_records > 0 ||
              validationData.valid_records === 0
            }
          >
            {loading
              ? importType === "inventory"
                ? "Creating Approval..."
                : "Processing..."
              : importType === "inventory"
                ? "Send for Approval"
                : "Import Data"}
          </button>
        </section>
      )}

      {statusData && (
        <section className="import-card">
          <h2>Import Progress</h2>

          <div className="progress-container">
            <div className="progress-header">
              <span>
                {statusData.status}
              </span>

              <strong>
                {statusData.progress_percentage || 0}%
              </strong>
            </div>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${
                    statusData.progress_percentage || 0
                  }%`,
                }}
              />
            </div>
          </div>

          <div className="summary-grid">
            <div className="summary-box">
              <span>Total</span>

              <strong>
                {statusData.total_records || 0}
              </strong>
            </div>

            <div className="summary-box success">
              <span>Successful</span>

              <strong>
                {statusData.successful_records || 0}
              </strong>
            </div>

            <div className="summary-box danger">
              <span>Failed</span>

              <strong>
                {statusData.failed_records || 0}
              </strong>
            </div>

            <div className="summary-box warning">
              <span>Skipped</span>

              <strong>
                {statusData.skipped_records || 0}
              </strong>
            </div>
          </div>
        </section>
      )}

      {resultData && (
        <section className="import-card">
          <h2>Import Result</h2>

          <div
            className={
              resultData.status === "Completed"
                ? "result-success"
                : "result-warning"
            }
          >
            {resultData.status}
          </div>

          <div className="summary-grid">
            <div className="summary-box">
              <span>Total Records</span>

              <strong>
                {resultData.total_records || 0}
              </strong>
            </div>

            <div className="summary-box success">
              <span>Successfully Added</span>

              <strong>
                {resultData.successful_records || 0}
              </strong>
            </div>

            <div className="summary-box danger">
              <span>Failed</span>

              <strong>
                {resultData.failed_records || 0}
              </strong>
            </div>

            <div className="summary-box warning">
              <span>Duplicates</span>

              <strong>
                {resultData.duplicate_records || 0}
              </strong>
            </div>
          </div>
        </section>
      )}

      <section className="import-card">
        <div className="section-title">
          <div>
            <h2>Import History</h2>

            <p>
              Previous import operations
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={loadHistory}
            disabled={loading}
          >
            Refresh
          </button>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Filename</th>
                <th>Total</th>
                <th>Success</th>
                <th>Failed</th>
                <th>Duplicates</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td
                    colSpan="9"
                    className="empty-state"
                  >
                    No imports found.
                  </td>
                </tr>
              ) : (
                history.map((item) => {
                  const importId = Number(item.id);

                  const canCancel = [
                    "Uploaded",
                    "Validated",
                    "Processing",
                  ].includes(item.status);

                  return (
                    <tr key={importId}>
                      <td>
                        #{importId}
                      </td>

                      <td>
                        {item.import_type}
                      </td>

                      <td>
                        {item.filename}
                      </td>

                      <td>
                        {item.total_records}
                      </td>

                      <td className="success-text">
                        {item.successful_records}
                      </td>

                      <td className="danger-text">
                        {item.failed_records}
                      </td>

                      <td className="warning-text">
                        {item.duplicate_records}
                      </td>

                      <td>
                        <span
                          className={`status-badge ${item.status
                            .toLowerCase()
                            .replace(/\s+/g, "-")}`}
                        >
                          {item.status}
                        </span>
                      </td>

                      <td>
                        <button
                          type="button"
                          className="view-button"
                          onClick={() =>
                            handleViewDetails(importId)
                          }
                        >
                          View
                        </button>

                        <button
                          type="button"
                          className="view-button"
                          onClick={() =>
                            handleStatus(importId)
                          }
                        >
                          Status
                        </button>

                        {canCancel && (
                          <button
                            type="button"
                            className="view-button"
                            onClick={() =>
                              handleCancel(importId)
                            }
                            disabled={loading}
                          >
                            Cancel
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </section>

      {details && (
        <section className="import-card">
          <div className="section-title">
            <div>
              <h2>
                Import #{details.import_id} Details
              </h2>
            </div>

            <div className="details-actions">
              {details.errors?.length > 0 && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    handleDownloadFailedRecords(
                      details.import_id
                    )
                  }
                >
                  Download Failed Records
                </button>
              )}

              <button
                type="button"
                className="secondary-button"
                onClick={closeDetails}
              >
                Close
              </button>
            </div>
          </div>

          <div className="details-grid">
            <div>
              <span>Status</span>

              <strong>
                {details.status}
              </strong>
            </div>

            <div>
              <span>Import Type</span>

              <strong>
                {details.import_type}
              </strong>
            </div>

            <div>
              <span>Filename</span>

              <strong>
                {details.filename}
              </strong>
            </div>

            <div>
              <span>Total Records</span>

              <strong>
                {details.total_records}
              </strong>
            </div>

            <div>
              <span>Successful</span>

              <strong>
                {details.successful_records}
              </strong>
            </div>

            <div>
              <span>Failed</span>

              <strong>
                {details.failed_records}
              </strong>
            </div>

            <div>
              <span>Duplicates</span>

              <strong>
                {details.duplicate_records}
              </strong>
            </div>

            <div>
              <span>Skipped</span>

              <strong>
                {details.skipped_records}
              </strong>
            </div>

            <div>
              <span>Processed</span>

              <strong>
                {details.processed_records}
              </strong>
            </div>

            <div>
              <span>Progress</span>

              <strong>
                {details.progress_percentage}%
              </strong>
            </div>
          </div>

          {details.errors?.length > 0 && (
            <div className="validation-errors">
              <h3>Import Errors</h3>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Row</th>
                      <th>Type</th>
                      <th>Status</th>
                      <th>Reason</th>
                    </tr>
                  </thead>

                  <tbody>
                    {details.errors.map(
                      (item, index) => (
                        <tr key={index}>
                          <td>
                            {item.row_number}
                          </td>

                          <td>
                            {item.error_type}
                          </td>

                          <td>
                            {item.status}
                          </td>

                          <td>
                            {item.error_message}
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}