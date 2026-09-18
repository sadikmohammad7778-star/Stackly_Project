import { useEffect, useState } from "react";

import {
  getScheduledReports,
  createScheduledReport,
  updateScheduledReport,
  toggleScheduledReport,
  deleteScheduledReport,
} from "../api/reportApi";

import { getProducts } from "../api/productApi";
import { getCategories } from "../api/categoryApi";
import { getCustomers } from "../api/customerApi";

import "./ScheduledReports.css";

export default function ScheduledReports() {
  const [scheduledReports, setScheduledReports] = useState([]);

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [customers, setCustomers] = useState([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const [formData, setFormData] = useState({
    report_type: "sales",
    frequency: "daily",
    execution_time: "09:00",
    recipients: "",
    format: "PDF",
    is_active: true,
  });

  const [filters, setFilters] = useState({
    start_date: "",
    end_date: "",
    product_id: "",
    category_id: "",
    brand: "",
    customer_id: "",
    sales_status: "",
    stock_status: "",
  });

  useEffect(() => {
    loadScheduledReports();
    loadProducts();
    loadCategories();
    loadCustomers();

    const interval = setInterval(() => {
        loadScheduledReports();
    }, 10000);

    return () => {
        clearInterval(interval);
    };
  }, []);

  const loadScheduledReports = async (showLoading = true) => {
    try {
        if (showLoading) {
        setLoading(true);
        }

        setError("");

        const data = await getScheduledReports();

        setScheduledReports(data || []);
    } catch (error) {
        console.error(
        "Failed to load scheduled reports:",
        error
        );

        if (showLoading) {
        setError(
            error.response?.data?.detail ||
            "Failed to load scheduled reports"
        );
        }
    } finally {
        if (showLoading) {
        setLoading(false);
        }
    }
    };

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data || []);
    } catch (error) {
      console.error("Failed to load products:", error);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await getCategories();
      setCategories(data || []);
    } catch (error) {
      console.error("Failed to load categories:", error);
    }
  };

  const loadCustomers = async () => {
    try {
      const data = await getCustomers();
      setCustomers(data || []);
    } catch (error) {
      console.error("Failed to load customers:", error);
    }
  };

  const handleFormChange = (event) => {
    const { name, value, type, checked } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;

    setFilters((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const resetForm = () => {
    setFormData({
      report_type: "sales",
      frequency: "daily",
      execution_time: "09:00",
      recipients: "",
      format: "PDF",
      is_active: true,
    });

    setFilters({
      start_date: "",
      end_date: "",
      product_id: "",
      category_id: "",
      brand: "",
      customer_id: "",
      sales_status: "",
      stock_status: "",
    });

    setEditingId(null);
    setShowForm(false);
    setError("");
  };

  const buildScheduledFilters = () => {
    const cleanedFilters = {};

    Object.entries(filters).forEach(([key, value]) => {
      if (
        value !== "" &&
        value !== null &&
        value !== undefined
      ) {
        cleanedFilters[key] = value;
      }
    });

    return cleanedFilters;
  };

  const validateForm = () => {
    if (!formData.report_type) {
      return "Please select a report type";
    }

    if (!formData.frequency) {
      return "Please select a frequency";
    }

    if (!formData.execution_time) {
      return "Please select an execution time";
    }

    if (!formData.recipients.trim()) {
      return "Please enter at least one recipient email";
    }

    const emails = formData.recipients
      .split(",")
      .map((email) => email.trim())
      .filter(Boolean);

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const invalidEmail = emails.find(
      (email) => !emailPattern.test(email)
    );

    if (invalidEmail) {
      return `Invalid email address: ${invalidEmail}`;
    }

    if (
      filters.start_date &&
      filters.end_date &&
      filters.start_date > filters.end_date
    ) {
      return "Start date cannot be after end date";
    }

    return "";
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const validationError = validateForm();

    if (validationError) {
        setError(validationError);
        return;
    }

    try {
        setSaving(true);
        setError("");

        const payload = {
        ...formData,
        filters: JSON.stringify(buildScheduledFilters()),
        };

        let savedReport;

        if (editingId) {
        savedReport = await updateScheduledReport(
            editingId,
            payload
        );

        setScheduledReports((previous) =>
            previous.map((report) =>
            report.id === editingId
                ? savedReport
                : report
            )
        );
        } else {
        savedReport = await createScheduledReport(payload);

        setScheduledReports((previous) => [
            savedReport,
            ...previous,
        ]);
        }

        resetForm();
    } catch (error) {
        console.error(
        "Failed to save scheduled report:",
        error
        );

        setError(
        error.response?.data?.detail ||
            "Failed to save scheduled report"
        );
    } finally {
        setSaving(false);
    }
};
  const handleEdit = (report) => {
    let parsedFilters = {};

    try {
      parsedFilters = report.filters
        ? JSON.parse(report.filters)
        : {};
    } catch {
      parsedFilters = {};
    }

    setFormData({
      report_type: report.report_type || "sales",
      frequency: report.frequency || "daily",
      execution_time: report.execution_time || "09:00",
      recipients: report.recipients || "",
      format: report.format || "PDF",
      is_active: report.is_active ?? true,
    });

    setFilters({
      start_date: parsedFilters.start_date || "",
      end_date: parsedFilters.end_date || "",
      product_id: parsedFilters.product_id || "",
      category_id: parsedFilters.category_id || "",
      brand: parsedFilters.brand || "",
      customer_id: parsedFilters.customer_id || "",
      sales_status: parsedFilters.sales_status || "",
      stock_status: parsedFilters.stock_status || "",
    });

    setEditingId(report.id);
    setShowForm(true);
    setError("");
  };

  const handleToggle = async (id) => {
    try {
        const updatedReport =
        await toggleScheduledReport(id);

        setScheduledReports((previous) =>
        previous.map((report) =>
            report.id === id
            ? updatedReport
            : report
        )
        );
    } catch (error) {
        console.error(
        "Failed to toggle scheduled report:",
        error
        );

        setError(
        error.response?.data?.detail ||
            "Failed to update scheduled report"
        );
    }
    };

  const handleDelete = async (id) => {
    const confirmed = window.confirm(
        "Are you sure you want to delete this scheduled report?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await deleteScheduledReport(id);

        setScheduledReports((previous) =>
        previous.filter((report) => report.id !== id)
        );
    } catch (error) {
        console.error(
        "Failed to delete scheduled report:",
        error
        );

        setError(
        error.response?.data?.detail ||
            "Failed to delete scheduled report"
        );
    }
    };

  const getReportName = (type) => {
    const names = {
      sales: "Sales",
      inventory: "Inventory",
      customers: "Customer",
      products: "Product Performance",
      "stock-movements": "Stock Movement",
    };

    return names[type] || type;
  };

  const getProductName = (id) => {
    const product = products.find(
      (item) => String(item.id) === String(id)
    );

    return product
      ? `${product.name} - ${product.sku}`
      : id;
  };

  const getCategoryName = (id) => {
    const category = categories.find(
      (item) => String(item.id) === String(id)
    );

    return category ? category.name : id;
  };

  const getCustomerName = (id) => {
    const customer = customers.find(
      (item) => String(item.id) === String(id)
    );

    return customer
      ? `${customer.first_name} ${customer.last_name}`
      : id;
  };

  const formatFilters = (filterString) => {
    if (!filterString) {
      return "All";
    }

    try {
      const data = JSON.parse(filterString);

      const values = [];

      if (data.start_date || data.end_date) {
        values.push(
          `${data.start_date || "..."} → ${
            data.end_date || "..."
          }`
        );
      }

      if (data.product_id) {
        values.push(
          `Product: ${getProductName(data.product_id)}`
        );
      }

      if (data.category_id) {
        values.push(
          `Category: ${getCategoryName(data.category_id)}`
        );
      }

      if (data.brand) {
        values.push(`Brand: ${data.brand}`);
      }

      if (data.customer_id) {
        values.push(
          `Customer: ${getCustomerName(data.customer_id)}`
        );
      }

      if (data.sales_status) {
        values.push(
          `Sales: ${data.sales_status}`
        );
      }

      if (data.stock_status) {
        values.push(
          `Stock: ${data.stock_status}`
        );
      }

      return values.length ? values.join(" | ") : "All";
    } catch {
      return "All";
    }
  };

  const formatDate = (date) => {
    if (!date) {
      return "-";
    }

    return new Date(date).toLocaleString();
  };

  return (
    <div className="scheduled-reports-page">
      <div className="scheduled-header">
        <div>
          <h2>Scheduled Reports</h2>
          <p>
            Automatically generate and email reports on a schedule.
          </p>
        </div>

        <button
          className="create-schedule-btn"
          onClick={() => {
            setEditingId(null);
            setShowForm(true);
            setError("");
          }}
        >
          + Create Schedule
        </button>
      </div>

      {error && (
        <div className="scheduled-error">
          {error}
        </div>
      )}

      {showForm && (
        <div className="scheduled-card schedule-form-card">
          <div className="schedule-form-header">
            <div>
              <h2>
                {editingId
                  ? "Edit Scheduled Report"
                  : "Create Scheduled Report"}
              </h2>

              <p>
                Configure when and where your report should be delivered.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="schedule-form-grid">
              <div className="schedule-field">
                <label>Report Type</label>

                <select
                  name="report_type"
                  value={formData.report_type}
                  onChange={handleFormChange}
                >
                  <option value="sales">Sales</option>
                  <option value="inventory">Inventory</option>
                  <option value="customers">Customers</option>
                  <option value="products">
                    Product Performance
                  </option>
                  <option value="stock-movements">
                    Stock Movement
                  </option>
                </select>
              </div>

              <div className="schedule-field">
                <label>Frequency</label>

                <select
                  name="frequency"
                  value={formData.frequency}
                  onChange={handleFormChange}
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div className="schedule-field">
                <label>Execution Time</label>

                <input
                  type="time"
                  name="execution_time"
                  value={formData.execution_time}
                  onChange={handleFormChange}
                />
              </div>

              <div className="schedule-field">
                <label>Format</label>

                <select
                  name="format"
                  value={formData.format}
                  onChange={handleFormChange}
                >
                  <option value="PDF">PDF</option>
                  <option value="CSV">CSV</option>
                </select>
              </div>

              <div className="schedule-field schedule-full-width">
                <label>Recipients</label>

                <input
                  type="text"
                  name="recipients"
                  value={formData.recipients}
                  onChange={handleFormChange}
                  placeholder="email@example.com, another@example.com"
                />

                <small>
                  Separate multiple email addresses with commas.
                </small>
              </div>
            </div>

            <div className="schedule-filter-section">
              <h3>Report Filters</h3>

              <p>
                These filters will be used whenever the scheduled report runs.
              </p>

              <div className="schedule-form-grid">
                <div className="schedule-field">
                  <label>Start Date</label>

                  <input
                    type="date"
                    name="start_date"
                    value={filters.start_date}
                    onChange={handleFilterChange}
                  />
                </div>

                <div className="schedule-field">
                  <label>End Date</label>

                  <input
                    type="date"
                    name="end_date"
                    value={filters.end_date}
                    onChange={handleFilterChange}
                  />
                </div>

                <div className="schedule-field">
                  <label>Product</label>

                  <select
                    name="product_id"
                    value={filters.product_id}
                    onChange={handleFilterChange}
                  >
                    <option value="">
                      All Products
                    </option>

                    {products.map((product) => (
                      <option
                        key={product.id}
                        value={product.id}
                      >
                        {product.name} - {product.sku}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="schedule-field">
                  <label>Category</label>

                  <select
                    name="category_id"
                    value={filters.category_id}
                    onChange={handleFilterChange}
                  >
                    <option value="">
                      All Categories
                    </option>

                    {categories.map((category) => (
                      <option
                        key={category.id}
                        value={category.id}
                      >
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="schedule-field">
                  <label>Brand</label>

                  <input
                    type="text"
                    name="brand"
                    value={filters.brand}
                    onChange={handleFilterChange}
                    placeholder="Enter brand"
                  />
                </div>

                <div className="schedule-field">
                  <label>Customer</label>

                  <select
                    name="customer_id"
                    value={filters.customer_id}
                    onChange={handleFilterChange}
                  >
                    <option value="">
                      All Customers
                    </option>

                    {customers.map((customer) => (
                      <option
                        key={customer.id}
                        value={customer.id}
                      >
                        {customer.first_name} {customer.last_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="schedule-field">
                  <label>Sales Status</label>

                  <select
                    name="sales_status"
                    value={filters.sales_status}
                    onChange={handleFilterChange}
                  >
                    <option value="">All</option>
                    <option value="Paid">Paid</option>
                    <option value="Pending">Pending</option>
                    <option value="Cancelled">
                      Cancelled
                    </option>
                  </select>
                </div>

                <div className="schedule-field">
                  <label>Stock Status</label>

                  <select
                    name="stock_status"
                    value={filters.stock_status}
                    onChange={handleFilterChange}
                  >
                    <option value="">All</option>
                    <option value="In Stock">
                      In Stock
                    </option>
                    <option value="Low Stock">
                      Low Stock
                    </option>
                    <option value="Out of Stock">
                      Out of Stock
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <div className="schedule-active-row">
              <label className="switch-label">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleFormChange}
                />

                <span>Schedule Active</span>
              </label>
            </div>

            <div className="schedule-form-actions">
              <button
                type="submit"
                className="save-schedule-btn"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : editingId
                  ? "Update Schedule"
                  : "Create Schedule"}
              </button>

              <button
                type="button"
                className="cancel-schedule-btn"
                onClick={resetForm}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="scheduled-card">
        <div className="scheduled-section-header">
          <div>
            <h2>Scheduled Reports</h2>
            <p>
              Manage your automated report schedules.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="scheduled-loading">
            Loading scheduled reports...
          </div>
        ) : scheduledReports.length === 0 ? (
          <div className="scheduled-empty">
            <h3>No Scheduled Reports</h3>
            <p>
              Create your first scheduled report to automatically
              receive reports by email.
            </p>
          </div>
        ) : (
          <div className="scheduled-table-wrapper">
            <table className="scheduled-table">
              <thead>
                <tr>
                  <th>Report</th>
                  <th>Filters</th>
                  <th>Frequency</th>
                  <th>Time</th>
                  <th>Recipients</th>
                  <th>Format</th>
                  <th>Status</th>
                  <th>Last Generated</th>
                  <th>Last Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {scheduledReports.map((report) => (
                  <tr key={report.id}>
                    <td>
                      <strong>
                        {getReportName(report.report_type)}
                      </strong>
                    </td>

                    <td>
                      <div className="schedule-filters-text">
                        {formatFilters(report.filters)}
                      </div>
                    </td>

                    <td>
                      <span className="frequency-badge">
                        {report.frequency}
                      </span>
                    </td>

                    <td>
                      {report.execution_time}
                    </td>

                    <td>
                      <div className="recipient-text">
                        {report.recipients}
                      </div>
                    </td>

                    <td>
                      <span className="format-badge">
                        {report.format}
                      </span>
                    </td>

                    <td>
                      <span
                        className={
                          report.is_active
                            ? "schedule-status active"
                            : "schedule-status inactive"
                        }
                      >
                        {report.is_active
                          ? "Active"
                          : "Inactive"}
                      </span>
                    </td>

                    <td>
                      {formatDate(
                        report.last_generated_at
                      )}
                    </td>

                    <td>
                      <span
                        className={
                          report.last_status === "Success"
                            ? "last-success"
                            : report.last_status === "Failed"
                            ? "last-failed"
                            : "last-pending"
                        }
                      >
                        {report.last_status || "Not Run"}
                      </span>

                      {report.last_error && (
                        <div className="schedule-error-text">
                          {report.last_error}
                        </div>
                      )}
                    </td>

                    <td>
                      <div className="schedule-actions">
                        <button
                          className="edit-schedule-btn"
                          onClick={() =>
                            handleEdit(report)
                          }
                        >
                          Edit
                        </button>

                        <button
                          className={
                            report.is_active
                              ? "toggle-schedule-btn disable"
                              : "toggle-schedule-btn enable"
                          }
                          onClick={() =>
                            handleToggle(report.id)
                          }
                        >
                          {report.is_active
                            ? "Disable"
                            : "Enable"}
                        </button>

                        <button
                          className="delete-schedule-btn"
                          onClick={() =>
                            handleDelete(report.id)
                          }
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}