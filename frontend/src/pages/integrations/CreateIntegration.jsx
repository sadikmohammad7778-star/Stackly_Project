import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  FiArrowLeft,
  FiDatabase,
  FiCloud,
  FiFileText,
  FiSave,
  FiLoader,
  FiEye,
  FiEyeOff,
  FiShield,
  FiSettings
} from "react-icons/fi";

import { createIntegration } from "../../api/integrationApi";

import "./CreateIntegration.css";

export default function CreateIntegration() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [form, setForm] = useState({
    name: "",
    source_type: "csv",
    target_module: "products",
    sync_strategy: "insert"
  });

  const [postgres, setPostgres] = useState({
    host: "localhost",
    port: "5432",
    database: "",
    username: "",
    password: ""
  });

  const [rest, setRest] = useState({
    base_url: "",
    auth_type: "none",
    token: "",
    api_key: "",
    api_key_header: "X-API-Key",
    test_endpoint: "",
    data_endpoint: "",
    response_data_path: "",
    page_size: "30",
    total_path: "total",
    updated_at_field: ""
  });

  const handleFormChange = (e) => {
    const { name, value } = e.target;

    setForm((previous) => ({
      ...previous,
      [name]: value
    }));
  };

  const handlePostgresChange = (e) => {
    const { name, value } = e.target;

    setPostgres((previous) => ({
      ...previous,
      [name]: value
    }));
  };

  const handleRestChange = (e) => {
    const { name, value } = e.target;

    setRest((previous) => ({
      ...previous,
      [name]: value
    }));
  };

  const validatePostgres = () => {
    if (
      !postgres.host.trim() ||
      !postgres.database.trim() ||
      !postgres.username.trim() ||
      !postgres.password
    ) {
      return "Please complete all PostgreSQL connection fields.";
    }

    const port = Number(postgres.port);

    if (!Number.isInteger(port) || port < 1 || port > 65535) {
      return "Enter a valid PostgreSQL port between 1 and 65535.";
    }

    return "";
  };

  const validateRest = () => {
    if (
      !rest.base_url.trim() ||
      !rest.test_endpoint.trim() ||
      !rest.data_endpoint.trim()
    ) {
      return "Please complete the REST API endpoint configuration.";
    }

    try {
      const parsedUrl = new URL(rest.base_url);

      if (!["http:", "https:"].includes(parsedUrl.protocol)) {
        return "REST API URL must use HTTP or HTTPS.";
      }
    } catch {
      return "Please enter a valid REST API base URL.";
    }

    const pageSize = Number(rest.page_size);

    if (
      !Number.isInteger(pageSize) ||
      pageSize < 1 ||
      pageSize > 500
    ) {
      return "Page size must be between 1 and 500.";
    }

    if (
      rest.auth_type === "bearer" &&
      !rest.token.trim()
    ) {
      return "Please enter the Bearer token.";
    }

    if (
      rest.auth_type === "api_key" &&
      (!rest.api_key.trim() || !rest.api_key_header.trim())
    ) {
      return "Please enter the API key and header name.";
    }

    return "";
  };

  const buildPayload = () => {
    let connection_config = {};
    let credentials = null;

    if (form.source_type === "postgresql") {
      connection_config = {
        host: postgres.host.trim(),
        port: Number(postgres.port),
        database: postgres.database.trim()
      };

      credentials = {
        username: postgres.username.trim(),
        password: postgres.password
      };
    }

    if (form.source_type === "rest_api") {
      connection_config = {
        base_url: rest.base_url.trim().replace(/\/+$/, ""),
        auth_type: rest.auth_type,
        test_endpoint: rest.test_endpoint.trim().replace(/^\/+/, ""),
        data_endpoint: rest.data_endpoint.trim().replace(/^\/+/, ""),
        response_data_path: rest.response_data_path.trim(),
        pagination: {
          type: "offset",
          limit_param: "limit",
          offset_param: "skip",
          page_size: Number(rest.page_size),
          total_path: rest.total_path.trim() || "total",
          max_pages: 100
        },
        incremental: {
          enabled: Boolean(rest.updated_at_field.trim()),
          updated_at_field: rest.updated_at_field.trim()
        }
      };

      if (rest.auth_type === "bearer") {
        credentials = {
          token: rest.token
        };
      }

      if (rest.auth_type === "api_key") {
        credentials = {
          api_key: rest.api_key
        };

        connection_config.api_key_header =
          rest.api_key_header.trim();
      }
    }

    return {
      ...form,
      name: form.name.trim(),
      connection_config,
      credentials
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (form.name.trim().length < 2) {
      setError("Integration name must contain at least 2 characters.");
      return;
    }

    if (form.source_type === "postgresql") {
      const validationError = validatePostgres();

      if (validationError) {
        setError(validationError);
        return;
      }
    }

    if (form.source_type === "rest_api") {
      const validationError = validateRest();

      if (validationError) {
        setError(validationError);
        return;
      }
    }

    try {
      setLoading(true);

      const createdIntegration = await createIntegration(
        buildPayload()
      );

      setSuccess("Integration created successfully.");

      setTimeout(() => {
        navigate(`/integrations/${createdIntegration.id}`);
      }, 1000);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to create integration."
      );
    } finally {
      setLoading(false);
    }
  };

  const sourceOptions = [
    {
      value: "csv",
      label: "CSV File",
      description: "Import records from CSV files.",
      icon: <FiFileText />
    },
    {
      value: "postgresql",
      label: "PostgreSQL",
      description: "Connect to an external PostgreSQL database.",
      icon: <FiDatabase />
    },
    {
      value: "rest_api",
      label: "REST API",
      description: "Connect to external REST API services.",
      icon: <FiCloud />
    }
  ];

  return (
    <div className="create-integration-page">
      <div className="create-integration-header">
        <button
          className="integration-back-button"
          type="button"
          onClick={() => navigate("/integrations")}
        >
          <FiArrowLeft />
          Back to Integrations
        </button>

        <span>ENTERPRISE DATA MANAGEMENT</span>

        <h1>Create New Integration</h1>

        <p>
          Configure an external data source and connect it to RetailPulse.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="create-integration-card">
          <div className="create-card-heading">
            <h2>Basic Configuration</h2>
            <p>Provide the basic connector information.</p>
          </div>

          <div className="integration-form-grid">
            <div className="integration-form-group full-width">
              <label>Integration Name *</label>

              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleFormChange}
                placeholder="Example: Product REST API Connector"
                minLength={2}
                maxLength={150}
                required
              />
            </div>

            <div className="integration-form-group">
              <label>Target Module *</label>

              <select
                name="target_module"
                value={form.target_module}
                onChange={handleFormChange}
              >
                <option value="products">Products</option>
                <option value="customers">Customers</option>
                <option value="sales">Sales</option>
                <option value="inventory">Inventory</option>
              </select>
            </div>

            <div className="integration-form-group">
              <label>Duplicate Handling Strategy *</label>

              <select
                name="sync_strategy"
                value={form.sync_strategy}
                onChange={handleFormChange}
              >
                <option value="insert">Insert</option>
                <option value="update">Update</option>
                <option value="skip">Skip</option>
                <option value="reject">Reject</option>
              </select>
            </div>
          </div>
        </div>

        <div className="create-integration-card">
          <div className="create-card-heading">
            <h2>Select Data Source</h2>
            <p>Choose the external source you want to connect.</p>
          </div>

          <div className="integration-source-options">
            {sourceOptions.map((option) => (
              <button
                type="button"
                key={option.value}
                className={`integration-source-option ${
                  form.source_type === option.value ? "selected" : ""
                }`}
                onClick={() =>
                  setForm((previous) => ({
                    ...previous,
                    source_type: option.value
                  }))
                }
              >
                <div className="source-option-icon">
                  {option.icon}
                </div>

                <strong>{option.label}</strong>
                <span>{option.description}</span>
              </button>
            ))}
          </div>
        </div>

        {form.source_type === "postgresql" && (
          <div className="create-integration-card">
            <div className="create-card-heading">
              <h2>PostgreSQL Configuration</h2>
              <p>Enter your external PostgreSQL database details.</p>
            </div>

            <div className="integration-form-grid">
              <div className="integration-form-group">
                <label>Host *</label>

                <input
                  type="text"
                  name="host"
                  value={postgres.host}
                  onChange={handlePostgresChange}
                  placeholder="localhost"
                  required
                />
              </div>

              <div className="integration-form-group">
                <label>Port *</label>

                <input
                  type="number"
                  name="port"
                  min="1"
                  max="65535"
                  value={postgres.port}
                  onChange={handlePostgresChange}
                  required
                />
              </div>

              <div className="integration-form-group">
                <label>Database Name *</label>

                <input
                  type="text"
                  name="database"
                  value={postgres.database}
                  onChange={handlePostgresChange}
                  placeholder="database_name"
                  required
                />
              </div>

              <div className="integration-form-group">
                <label>Username *</label>

                <input
                  type="text"
                  name="username"
                  value={postgres.username}
                  onChange={handlePostgresChange}
                  autoComplete="off"
                  required
                />
              </div>

              <div className="integration-form-group full-width">
                <label>Password *</label>

                <div className="integration-password-wrapper">
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={postgres.password}
                    onChange={handlePostgresChange}
                    autoComplete="new-password"
                    required
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword((previous) => !previous)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>
              </div>
            </div>

            <div className="integration-security-note">
              <FiShield />
              <span>
                Database credentials are submitted separately from the
                connection configuration and are not displayed in
                integration responses.
              </span>
            </div>
          </div>
        )}

        {form.source_type === "rest_api" && (
          <div className="create-integration-card">
            <div className="create-card-heading">
              <h2>REST API Configuration</h2>
              <p>Configure the API endpoint and authentication.</p>
            </div>

            <div className="integration-form-grid">
              <div className="integration-form-group full-width">
                <label>Base URL *</label>

                <input
                  type="url"
                  name="base_url"
                  value={rest.base_url}
                  onChange={handleRestChange}
                  placeholder="https://api.example.com"
                  required
                />
              </div>

              <div className="integration-form-group">
                <label>Test Endpoint *</label>

                <input
                  type="text"
                  name="test_endpoint"
                  value={rest.test_endpoint}
                  onChange={handleRestChange}
                  placeholder="products/1"
                  required
                />
              </div>

              <div className="integration-form-group">
                <label>Data Endpoint *</label>

                <input
                  type="text"
                  name="data_endpoint"
                  value={rest.data_endpoint}
                  onChange={handleRestChange}
                  placeholder="products"
                  required
                />
              </div>

              <div className="integration-form-group full-width">
                <label>Response Data Path</label>

                <input
                  type="text"
                  name="response_data_path"
                  value={rest.response_data_path}
                  onChange={handleRestChange}
                  placeholder="products"
                />

                <small>
                  Enter the JSON path containing the records array.
                  Leave empty if the API directly returns an array.
                </small>
              </div>

              <div className="integration-form-group">
                <label>Authentication Type</label>

                <select
                  name="auth_type"
                  value={rest.auth_type}
                  onChange={handleRestChange}
                >
                  <option value="none">No Authentication</option>
                  <option value="bearer">Bearer Token</option>
                  <option value="api_key">API Key</option>
                </select>
              </div>

              {rest.auth_type === "bearer" && (
                <div className="integration-form-group full-width">
                  <label>Bearer Token *</label>

                  <input
                    type="password"
                    name="token"
                    value={rest.token}
                    onChange={handleRestChange}
                    autoComplete="new-password"
                    required
                  />
                </div>
              )}

              {rest.auth_type === "api_key" && (
                <>
                  <div className="integration-form-group">
                    <label>API Key *</label>

                    <input
                      type="password"
                      name="api_key"
                      value={rest.api_key}
                      onChange={handleRestChange}
                      autoComplete="new-password"
                      required
                    />
                  </div>

                  <div className="integration-form-group">
                    <label>API Key Header *</label>

                    <input
                      type="text"
                      name="api_key_header"
                      value={rest.api_key_header}
                      onChange={handleRestChange}
                      required
                    />
                  </div>
                </>
              )}

              <div className="integration-form-group">
                <label>Page Size</label>

                <input
                  type="number"
                  name="page_size"
                  min="1"
                  max="500"
                  value={rest.page_size}
                  onChange={handleRestChange}
                />
              </div>

              <div className="integration-form-group">
                <label>Total Records Path</label>

                <input
                  type="text"
                  name="total_path"
                  value={rest.total_path}
                  onChange={handleRestChange}
                />
              </div>

              <div className="integration-form-group full-width">
                <label>Incremental Updated At Field</label>

                <input
                  type="text"
                  name="updated_at_field"
                  value={rest.updated_at_field}
                  onChange={handleRestChange}
                  placeholder="meta.updatedAt"
                />

                <small>
                  Leave empty to disable incremental synchronization.
                </small>
              </div>
            </div>

            <div className="integration-security-note">
              <FiShield />
              <span>
                Authentication credentials are encrypted by the backend
                and are not returned in API responses.
              </span>
            </div>
          </div>
        )}

        {form.source_type === "csv" && (
          <div className="create-integration-card csv-information">
            <FiFileText />

            <div>
              <h3>CSV Connector</h3>

              <p>
                Create the connector first. You can upload your CSV file
                and configure field mappings from the integration details.
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="integration-form-error">
            {error}
          </div>
        )}

        {success && (
          <div className="integration-form-success">
            {success}
          </div>
        )}

        <div className="create-integration-footer">
          <button
            type="button"
            className="integration-cancel-button"
            onClick={() => navigate("/integrations")}
            disabled={loading}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="integration-save-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <FiLoader className="integration-button-loader" />
                Creating...
              </>
            ) : (
              <>
                <FiSave />
                Create Integration
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}