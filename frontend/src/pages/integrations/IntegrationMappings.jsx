import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  FiArrowLeft,
  FiRefreshCw,
  FiSave,
  FiLoader,
  FiDatabase,
  FiCheckCircle,
  FiAlertCircle,
  FiArrowRight,
  FiFileText
} from "react-icons/fi";

import {
  getIntegration,
  previewIntegrationFile,
  getIntegrationMappings,
  saveIntegrationMappings
} from "../../api/integrationApi";

import "./IntegrationMappings.css";

const targetFields = [
  { value: "sku", label: "Product SKU", required: true },
  { value: "name", label: "Product Name", required: true },
  { value: "category_id", label: "Category", required: true },
  { value: "unit_price", label: "Unit Price", required: true },
  { value: "stock_quantity", label: "Stock Quantity", required: true },
  { value: "brand", label: "Brand", required: false },
  { value: "description", label: "Description", required: false },
  { value: "status", label: "Product Status", required: false }
];

export default function IntegrationMappings() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [integration, setIntegration] = useState(null);
  const [columns, setColumns] = useState([]);
  const [preview, setPreview] = useState([]);
  const [mappings, setMappings] = useState([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadMappingData();
  }, [id]);

  const loadMappingData = async () => {
    try {
      setLoading(true);
      setError("");

      const [integrationData, previewData, savedMappings] =
        await Promise.all([
          getIntegration(id),
          previewIntegrationFile(id),
          getIntegrationMappings(id)
        ]);

      setIntegration(integrationData);
      setColumns(previewData.columns || []);
      setPreview(previewData.preview || []);

      const existingMappings = savedMappings || [];

      const mappingRows = (previewData.columns || []).map((column) => {
        const existing = existingMappings.find(
          (item) => item.source_field === column
        );

        return {
          source_field: column,
          target_field: existing?.target_field || "",
          is_required:
            existing?.is_required || false,
          transformation_config:
            existing?.transformation_config || null
        };
      });

      setMappings(mappingRows);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to load field mapping information."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleTargetChange = (sourceField, targetField) => {
    setMappings((previous) =>
      previous.map((mapping) =>
        mapping.source_field === sourceField
          ? {
              ...mapping,
              target_field: targetField,
              is_required: targetFields.find(
                (field) => field.value === targetField
              )?.required || false,
              transformation_config:
                targetField === "category_id"
                  ? { operation: "category_lookup" }
                  : null
            }
          : mapping
      )
    );
  };

  const handleSaveMappings = async () => {
    try {
      setSaving(true);
      setError("");
      setMessage("");

      const activeMappings = mappings.filter(
        (mapping) => mapping.target_field
      );

      const requiredFields = targetFields
        .filter((field) => field.required)
        .map((field) => field.value);

      const mappedTargets = activeMappings.map(
        (mapping) => mapping.target_field
      );

      const missingFields = requiredFields.filter(
        (field) => !mappedTargets.includes(field)
      );

      if (missingFields.length > 0) {
        setError(
          `Please map all required fields: ${missingFields.join(", ")}`
        );
        return;
      }

      if (activeMappings.length === 0) {
        setError("Please configure at least one field mapping.");
        return;
      }

      await saveIntegrationMappings(
        id,
        activeMappings
      );

      setMessage("Field mappings saved successfully.");

      await loadMappingData();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to save field mappings."
      );
    } finally {
      setSaving(false);
    }
  };

  const getMappedCount = () =>
    mappings.filter((mapping) => mapping.target_field).length;

  if (loading) {
    return (
      <div className="mapping-loading">
        <FiLoader className="mapping-spinner" />
        <p>Loading field mappings...</p>
      </div>
    );
  }

  return (
    <div className="integration-mapping-page">
      <div className="mapping-header">
        <button
          className="mapping-back-button"
          onClick={() => navigate(`/integrations/${id}`)}
        >
          <FiArrowLeft />
          Back to Integration
        </button>

        <div className="mapping-title-row">
          <div>
            <span className="mapping-subtitle">
              ENTERPRISE DATA MANAGEMENT
            </span>

            <h1>Field Mapping</h1>

            <p>
              Map external source fields to RetailPulse product fields.
            </p>
          </div>

          <button
            className="mapping-refresh-button"
            onClick={loadMappingData}
          >
            <FiRefreshCw />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="mapping-alert mapping-alert-error">
          <FiAlertCircle />
          <span>{error}</span>
          <button onClick={() => setError("")}>×</button>
        </div>
      )}

      {message && (
        <div className="mapping-alert mapping-alert-success">
          <FiCheckCircle />
          <span>{message}</span>
          <button onClick={() => setMessage("")}>×</button>
        </div>
      )}

      <div className="mapping-connector-card">
        <div className="mapping-connector-icon">
          <FiDatabase />
        </div>

        <div>
          <h2>{integration?.name}</h2>
          <p>
            {integration?.source_type?.toUpperCase()} ·{" "}
            {integration?.target_module?.toUpperCase()}
          </p>
        </div>
      </div>

      <div className="mapping-stats">
        <div className="mapping-stat-card">
          <span>Source Columns</span>
          <h2>{columns.length}</h2>
        </div>

        <div className="mapping-stat-card">
          <span>Mapped Fields</span>
          <h2>{getMappedCount()}</h2>
        </div>

        <div className="mapping-stat-card">
          <span>Unmapped Fields</span>
          <h2>{columns.length - getMappedCount()}</h2>
        </div>

        <div className="mapping-stat-card">
          <span>Required Targets</span>
          <h2>{targetFields.filter((field) => field.required).length}</h2>
        </div>
      </div>

      <div className="mapping-section">
        <div className="mapping-section-header">
          <div>
            <h2>Configure Field Mappings</h2>
            <p>
              Select a RetailPulse target field for each source column.
            </p>
          </div>

          <span className="mapping-count">
            {getMappedCount()} / {columns.length} Mapped
          </span>
        </div>

        {columns.length === 0 ? (
          <div className="mapping-empty">
            <FiDatabase />
            <h3>No source columns found</h3>
            <p>
              Upload a CSV file before configuring field mappings.
            </p>
          </div>
        ) : (
          <div className="mapping-table-wrapper">
            <table className="mapping-table">
              <thead>
                <tr>
                  <th>Source Field</th>
                  <th></th>
                  <th>RetailPulse Target Field</th>
                  <th>Requirement</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {mappings.map((mapping) => {
                  const selectedTarget = targetFields.find(
                    (field) =>
                      field.value === mapping.target_field
                  );

                  return (
                    <tr key={mapping.source_field}>
                      <td>
                        <div className="mapping-source-field">
                          <FiFileText />
                          <strong>{mapping.source_field}</strong>
                        </div>
                      </td>

                      <td className="mapping-arrow">
                        <FiArrowRight />
                      </td>

                      <td>
                        <select
                          value={mapping.target_field}
                          onChange={(event) =>
                            handleTargetChange(
                              mapping.source_field,
                              event.target.value
                            )
                          }
                        >
                          <option value="">
                            Select target field
                          </option>

                          {targetFields.map((field) => {
                            const usedByAnother = mappings.some(
                              (item) =>
                                item.source_field !== mapping.source_field &&
                                item.target_field === field.value
                            );

                            return (
                              <option
                                key={field.value}
                                value={field.value}
                                disabled={usedByAnother}
                              >
                                {field.label}
                                {field.required ? " *" : ""}
                              </option>
                            );
                          })}
                        </select>
                      </td>

                      <td>
                        {selectedTarget?.required ? (
                          <span className="mapping-required">
                            Required
                          </span>
                        ) : (
                          <span className="mapping-optional">
                            Optional
                          </span>
                        )}
                      </td>

                      <td>
                        {mapping.target_field ? (
                          <span className="mapping-status-mapped">
                            <FiCheckCircle />
                            Mapped
                          </span>
                        ) : (
                          <span className="mapping-status-pending">
                            Pending
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className="mapping-footer">
          <button
            className="mapping-cancel-button"
            onClick={() => navigate(`/integrations/${id}`)}
          >
            Cancel
          </button>

          <button
            className="mapping-save-button"
            onClick={handleSaveMappings}
            disabled={saving || columns.length === 0}
          >
            {saving ? (
              <FiLoader className="mapping-spinner" />
            ) : (
              <FiSave />
            )}

            {saving ? "Saving..." : "Save Mappings"}
          </button>
        </div>
      </div>

      {preview.length > 0 && (
        <div className="mapping-section">
          <div className="mapping-section-header">
            <div>
              <h2>Source Data Preview</h2>
              <p>Preview of records from your uploaded CSV file.</p>
            </div>
          </div>

          <div className="mapping-table-wrapper">
            <table className="mapping-table">
              <thead>
                <tr>
                  {columns.map((column) => (
                    <th key={column}>{column}</th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {preview.map((row, index) => (
                  <tr key={index}>
                    {columns.map((column) => (
                      <td key={column}>
                        {String(row[column] ?? "")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}