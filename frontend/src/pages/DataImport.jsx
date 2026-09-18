import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import {
  uploadImport,
  validateImport,
  processImport,
  getImportHistory,
  getImportDetails,
  downloadFailedRecords,
} from "../api/importApi";

import "./DataImport.css";

export default function DataImport() {
  const [importType, setImportType] = useState("products");
  const [file, setFile] = useState(null);

  const [uploadData, setUploadData] = useState(null);
  const [validationData, setValidationData] = useState(null);
  const [resultData, setResultData] = useState(null);

  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [selectedImport, setSelectedImport] = useState(null);
  const [details, setDetails] = useState(null);
  const [searchParams] = useSearchParams();

  // ============================================================
  // Load Import History
  // ============================================================

  const loadHistory = async () => {
    try {
      const data = await getImportHistory();
      setHistory(data);
    } catch (err) {
      console.error("Failed to load import history:", err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // ============================================================
  // File Selection
  // ============================================================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    setError("");
    setUploadData(null);
    setValidationData(null);
    setResultData(null);

    if (!selectedFile) {
      setFile(null);
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith(".csv")) {
      setError("Only CSV files are allowed.");
      setFile(null);
      event.target.value = "";
      return;
    }

    // 10 MB limit
    const maxSize = 10 * 1024 * 1024;

    if (selectedFile.size > maxSize) {
      setError("File size must not exceed 10 MB.");
      setFile(null);
      event.target.value = "";
      return;
    }

    setFile(selectedFile);
  };

  // ============================================================
  // Upload
  // ============================================================

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
      setResultData(null);

      const data = await uploadImport(
        importType,
        file
      );

      setUploadData(data);

      await loadHistory();
    } catch (err) {
      console.error("Upload failed:", err);

      setError(
        err.response?.data?.detail?.message ||
          err.response?.data?.detail ||
          "Failed to upload import file."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // Validate
  // ============================================================

  const handleValidate = async () => {
    if (!uploadData?.import_id) {
      setError("Please upload the file first.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setValidationData(null);
      setResultData(null);

      const data = await validateImport(
        uploadData.import_id
      );

      setValidationData(data);

      await loadHistory();
    } catch (err) {
      console.error("Validation failed:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to validate import."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // Process
  // ============================================================

  const handleProcess = async () => {
    if (!uploadData?.import_id) {
      setError("Please upload the file first.");
      return;
    }

    if (
      !validationData ||
      validationData.invalid_records > 0
    ) {
      setError(
        "Import cannot be processed until validation passes."
      );
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResultData(null);

      const data = await processImport(
        uploadData.import_id
      );

      setResultData(data);

      await loadHistory();
    } catch (err) {
      console.error("Processing failed:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to process import."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // View Details
  // ============================================================

  const handleViewDetails = async (importId) => {
    try {
      setSelectedImport(importId);

      const data = await getImportDetails(
        importId
      );

      setDetails(data);
    } catch (err) {
      console.error(
        "Failed to load import details:",
        err
      );

      setError("Failed to load import details.");
    }
  };

  useEffect(() => {
    const importId = searchParams.get("import_id");

    if (importId) {
      handleViewDetails(Number(importId));
    }
  }, [searchParams]);

  

  const handleDownloadFailedRecords = async (importId) => {
  try {
    setError("");

    await downloadFailedRecords(
      importId
    );
  } catch (err) {
    console.error(
      "Failed to download records:",
      err
    );

    setError(
      err.response?.data?.detail ||
        "Failed to download failed records."
    );
  }
};
  // ============================================================
  // Remove File
  // ============================================================

  const removeFile = () => {
    setFile(null);
    setUploadData(null);
    setValidationData(null);
    setResultData(null);
    setError("");

    const input = document.getElementById(
      "import-file"
    );

    if (input) {
      input.value = "";
    }
  };

  return (
    <div className="data-import-page">

      {/* ================================================== */}
      {/* Header */}
      {/* ================================================== */}

      <div className="data-import-header">
        <div>
          <h1>Data Import</h1>

          <p>
            Import Products, Customers and Sales
            Transactions into RetailPulse.
          </p>
        </div>
      </div>

      {/* ================================================== */}
      {/* Error */}
      {/* ================================================== */}

      {error && (
        <div className="import-error">
          {error}
        </div>
      )}

      {/* ================================================== */}
      {/* Upload Card */}
      {/* ================================================== */}

      <section className="import-card">

        <h2>Upload Data</h2>

        <div className="import-form">

          {/* Import Type */}

          <div className="form-group">

            <label>
              Import Type
            </label>

            <select
              value={importType}
              onChange={(e) => {
                setImportType(e.target.value);
                setFile(null);
                setUploadData(null);
                setValidationData(null);
                setResultData(null);
                setError("");
              }}
            >
              <option value="products">
                Products
              </option>

              <option value="customers">
                Customers
              </option>

              <option value="sales">
                Sales Transactions
              </option>
            </select>

          </div>

          {/* File */}

          <div className="form-group">

            <label>
              CSV File
            </label>

            <input
              id="import-file"
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
            />

          </div>

        </div>

        {/* Selected File */}

        {file && (
          <div className="selected-file">

            <div>
              <strong>
                Selected file:
              </strong>{" "}
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

        {/* Upload Button */}

        <button
          className="primary-button"
          onClick={handleUpload}
          disabled={!file || loading}
        >
          {loading
            ? "Uploading..."
            : "Upload File"}
        </button>

      </section>

      {/* ================================================== */}
      {/* Preview */}
      {/* ================================================== */}

      {uploadData && (
        <section className="import-card">

          <div className="section-title">

            <div>
              <h2>
                CSV Preview
              </h2>

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

          {/* Columns */}

          <div className="columns-list">

            {uploadData.columns.map(
              (column) => (
                <span key={column}>
                  {column}
                </span>
              )
            )}

          </div>

          {/* Preview Table */}

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

          {/* Validate */}

          <button
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

      {/* ================================================== */}
      {/* Validation */}
      {/* ================================================== */}

      {validationData && (
        <section className="import-card">

          <h2>
            Validation Result
          </h2>

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

          {/* Errors */}

          {validationData.errors?.length > 0 && (
            <div className="validation-errors">

              <h3>
                Validation Errors
              </h3>

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

          {/* Process */}

          <button
            className="primary-button"
            onClick={handleProcess}
            disabled={
              loading ||
              validationData.invalid_records > 0
            }
          >
            {loading
              ? "Processing..."
              : "Import Data"}
          </button>

        </section>
      )}

      {/* ================================================== */}
      {/* Result */}
      {/* ================================================== */}

      {resultData && (
        <section className="import-card">

          <h2>
            Import Result
          </h2>

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
                {resultData.total_records}
              </strong>
            </div>

            <div className="summary-box success">
              <span>Successfully Added</span>
              <strong>
                {resultData.successful_records}
              </strong>
            </div>

            <div className="summary-box danger">
              <span>Failed</span>
              <strong>
                {resultData.failed_records}
              </strong>
            </div>

            <div className="summary-box warning">
              <span>Duplicates</span>
              <strong>
                {resultData.duplicate_records}
              </strong>
            </div>

          </div>

        </section>
      )}

      {/* ================================================== */}
      {/* Import History */}
      {/* ================================================== */}

      <section className="import-card">

        <div className="section-title">

          <div>
            <h2>
              Import History
            </h2>

            <p>
              Previous import operations
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={loadHistory}
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
                history.map((item) => (
                  <tr key={item.id}>

                    <td>
                      #{item.id}
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
                        className="view-button"
                        onClick={() =>
                          handleViewDetails(
                            item.id
                          )
                        }
                      >
                        View
                      </button>

                    </td>

                  </tr>
                ))
              )}

            </tbody>

          </table>

        </div>

      </section>

      {/* ================================================== */}
      {/* Details */}
      {/* ================================================== */}

      {details &&
        selectedImport === details.id && (
          <section className="import-card">

            <div className="section-title">

            <h2>
                Import #{details.id} Details
            </h2>

            <div className="details-actions">

                {details.errors?.some(
                (error) =>
                    error.error_type === "VALIDATION" ||
                    error.error_type === "PROCESSING"
                ) && (
                <button
                    className="secondary-button"
                    onClick={() =>
                    handleDownloadFailedRecords(
                        details.id
                    )
                    }
                >
                    Download Failed Records
                </button>
                )}

                <button
                className="secondary-button"
                onClick={() => {
                    setDetails(null);
                    setSelectedImport(null);
                }}
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

            </div>

            {details.errors?.length > 0 && (
              <div className="validation-errors">

                <h3>
                  Import Errors
                </h3>

                <div className="table-wrapper">

                  <table>

                    <thead>
                      <tr>
                        <th>Row</th>
                        <th>Type</th>
                        <th>Reason</th>
                      </tr>
                    </thead>

                    <tbody>

                      {details.errors.map(
                        (error, index) => (
                          <tr key={index}>

                            <td>
                              {error.row_number}
                            </td>

                            <td>
                              {error.error_type}
                            </td>

                            <td>
                              {error.error_message}
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