import { useEffect, useState } from "react";

import {
  getSalesReport,
  getStockReport,
  getDetailedReport,
  getReportHistory,
  downloadReportHistory,
} from "../api/reportApi";

import {
  exportSalesExcel,
  exportInventoryExcel,
  exportSalesPDF,
  exportInventoryPDF,
} from "../api/exportApi";

import "./Reports.css";
import { getProducts } from "../api/productApi";
import { getCategories } from "../api/categoryApi";
import { getCustomers } from "../api/customerApi";

export default function Reports() {
  const [salesReport, setSalesReport] = useState(null);
  const [stockReport, setStockReport] = useState(null);

  const [reportType, setReportType] = useState("sales");

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [customers, setCustomers] = useState([]);

  const [filters, setFilters] = useState({
    start_date: "",
    end_date: "",
    product_id: "",
    category_id: "",
    brand: "",
    customer_id: "",
    sales_status: "",
    stock_status: "",
    sort_by: "",
    sort_order: "desc",
    page: 1,
    page_size: 10,
  });

  const [detailedReport, setDetailedReport] = useState(null);

  const [loading, setLoading] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [error, setError] = useState("");

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

useEffect(() => {
  loadSummaryReports();
  loadHistory();
  loadProducts();
  loadCategories();
  loadCustomers();
}, []);

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
      console.error(
        "Failed to load categories:",
        error
      );
    }
  };

  const loadCustomers = async () => {
    try {
      const data = await getCustomers();

      setCustomers(data || []);
    } catch (error) {
      console.error(
        "Failed to load customers:",
        error
      );
    }
  };

  const loadSummaryReports = async () => {
    try {
      setSummaryLoading(true);

      const [sales, stock] = await Promise.all([
        getSalesReport(),
        getStockReport(),
      ]);

      setSalesReport(sales);
      setStockReport(stock);
    } catch (error) {
      console.error("Failed to load reports:", error);
    } finally {
      setSummaryLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      setHistoryLoading(true);

      const response = await getReportHistory(1, 20);

      setHistory(response?.data || []);
    } catch (error) {
      console.error("Failed to load report history:", error);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;

    setFilters((previous) => ({
      ...previous,
      [name]: value,
      page: 1,
    }));
  };

  const clearFilters = () => {
    setFilters({
      start_date: "",
      end_date: "",
      product_id: "",
      category_id: "",
      brand: "",
      customer_id: "",
      sales_status: "",
      stock_status: "",
      sort_by: "",
      sort_order: "desc",
      page: 1,
      page_size: 10,
    });

    setDetailedReport(null);
    setError("");
  };

  const buildFilters = (customFilters = filters) => {
    const cleanedFilters = {};

    Object.entries(customFilters).forEach(([key, value]) => {
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

  const generateReport = async (
    customFilters = filters
  ) => {
    try {
      setLoading(true);
      setError("");

      const data = await getDetailedReport(
        reportType,
        buildFilters(customFilters)
      );

      setDetailedReport(data);
    } catch (error) {
      console.error("Report generation failed:", error);

      setDetailedReport(null);

      setError(
        error.response?.data?.detail ||
          "Failed to generate report"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReportTypeChange = (event) => {
    setReportType(event.target.value);
    setDetailedReport(null);
    setError("");

    setFilters((previous) => ({
      ...previous,
      page: 1,
    }));
  };

  const handleSort = (column) => {
    const nextOrder =
      filters.sort_by === column &&
      filters.sort_order === "desc"
        ? "asc"
        : "desc";

    const updatedFilters = {
      ...filters,
      sort_by: column,
      sort_order: nextOrder,
      page: 1,
    };

    setFilters(updatedFilters);

    generateReport(updatedFilters);
  };

  const handlePageChange = (newPage) => {
    const updatedFilters = {
      ...filters,
      page: newPage,
    };

    setFilters(updatedFilters);

    generateReport(updatedFilters);
  };

  const downloadFile = (blob, fileName) => {
    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = fileName;

    document.body.appendChild(link);

    link.click();

    link.remove();

    window.URL.revokeObjectURL(url);
  };

  const handleExport = async (apiCall, fileName) => {
    try {
      const blob = await apiCall();

      downloadFile(blob, fileName);
    } catch (error) {
      console.error("Export failed:", error);
    }
  };

  const handleHistoryDownload = async (
    historyId,
    format
  ) => {
    try {
      const blob = await downloadReportHistory(
        historyId
      );

      const extension =
        format?.toLowerCase() || "pdf";

      downloadFile(
        blob,
        `report-${historyId}.${extension}`
      );
    } catch (error) {
      console.error(
        "History download failed:",
        error
      );

      alert("Failed to download report");
    }
  };

  const getColumns = () => {
    if (
      !detailedReport ||
      !detailedReport.data ||
      detailedReport.data.length === 0
    ) {
      return [];
    }

    return Object.keys(detailedReport.data[0]);
  };

  const formatColumnName = (column) => {
    return column
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  };

  const formatValue = (value) => {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return "-";
    }

    if (
      typeof value === "number" &&
      Number.isInteger(value) === false
    ) {
      return value.toFixed(2);
    }

    return String(value);
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

    return category
      ? category.name
      : id;
  };

  const getCustomerName = (id) => {
    const customer = customers.find(
      (item) => String(item.id) === String(id)
    );

    return customer
      ? `${customer.first_name} ${customer.last_name}`
      : id;
  };

  return (
    <div className="reports-page">

      <div className="reports-header">
        <div>
          <h2>Reports</h2>

          <p>
            Generate, analyze and manage business
            reports
          </p>
        </div>
      </div>

      {summaryLoading ? (
        <div className="reports-loading">
          Loading report summary...
        </div>
      ) : (
        <div className="reports-grid">

          <div className="report-card">
            <h3>Total Sales</h3>

            <p>
              {salesReport?.total_sales ?? 0}
            </p>
          </div>

          <div className="report-card">
            <h3>Total Revenue</h3>

            <p>
              ₹{" "}
              {Number(
                salesReport?.total_revenue ?? 0
              ).toLocaleString("en-IN")}
            </p>
          </div>

          <div className="report-card">
            <h3>Average Order Value</h3>

            <p>
              ₹{" "}
              {Number(
                salesReport?.average_order_value ?? 0
              ).toLocaleString("en-IN")}
            </p>
          </div>

          <div className="report-card">
            <h3>Total Products</h3>

            <p>
              {stockReport?.total_products ?? 0}
            </p>
          </div>

          <div className="report-card">
            <h3>In Stock</h3>

            <p>
              {stockReport?.in_stock ?? 0}
            </p>
          </div>

          <div className="report-card">
            <h3>Low Stock</h3>

            <p>
              {stockReport?.low_stock ?? 0}
            </p>
          </div>

          <div className="report-card">
            <h3>Out of Stock</h3>

            <p>
              {stockReport?.out_of_stock ?? 0}
            </p>
          </div>

        </div>
      )}

      <div className="report-card report-generator">

        <div className="section-header">
          <div>
            <h2>Generate Report</h2>

            <p>
              Apply multiple filters to generate a
              detailed report.
            </p>
          </div>
        </div>

        <div className="report-filter-grid">

          <div className="filter-field">
            <label>Report Type</label>

            <select
              value={reportType}
              onChange={handleReportTypeChange}
            >
              <option value="sales">
                Sales
              </option>

              <option value="inventory">
                Inventory
              </option>

              <option value="customers">
                Customers
              </option>

              <option value="products">
                Product Performance
              </option>

              <option value="stock-movements">
                Stock Movements
              </option>
            </select>
          </div>

          <div className="filter-field">
            <label>Start Date</label>

            <input
              type="date"
              name="start_date"
              value={filters.start_date}
              onChange={handleFilterChange}
            />
          </div>

          <div className="filter-field">
            <label>End Date</label>

            <input
              type="date"
              name="end_date"
              value={filters.end_date}
              onChange={handleFilterChange}
            />
          </div>

          <div className="filter-field">
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

          <div className="filter-field">
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

          <div className="filter-field">
            <label>Brand</label>

            <input
              type="text"
              name="brand"
              value={filters.brand}
              onChange={handleFilterChange}
              placeholder="Enter brand"
            />
          </div>

          <div className="filter-field">
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

          <div className="filter-field">
              <label>Sales Status</label>

              <select
                name="sales_status"
                value={filters.sales_status}
                onChange={handleFilterChange}
              >
                <option value="">
                  All
                </option>

                <option value="Paid">
                  Paid
                </option>

                <option value="Pending">
                  Pending
                </option>

                <option value="Cancelled">
                  Cancelled
                </option>
              </select>
            </div>

          <div className="filter-field">
            <label>Stock Status</label>

            <select
              name="stock_status"
              value={filters.stock_status}
              onChange={handleFilterChange}
            >
              <option value="">
                All
              </option>

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

        {error && (
          <div className="report-error">
            {error}
          </div>
        )}

        <div className="filter-actions">

          <button
            className="generate-btn"
            onClick={() => generateReport()}
            disabled={loading}
          >
            {loading
              ? "Generating..."
              : "Generate Report"}
          </button>

          <button
            className="clear-btn"
            onClick={clearFilters}
          >
            Clear Filters
          </button>

        </div>

      </div>

      {detailedReport && (
        <div className="report-card report-results">

          <div className="section-header">

            <div>
              <h2>
                {detailedReport.report_name}
              </h2>

              <p>
                Total Records:{" "}
                {detailedReport.total_records}
              </p>
            </div>

            <div className="report-period">

              <strong>
                Applied Filters
              </strong>

              <span>
                {filters.start_date &&
                filters.end_date
                  ? `${filters.start_date} → ${filters.end_date}`
                  : "All dates"}
              </span>

              {filters.brand && (
                <span>
                  Brand: {filters.brand}
                </span>
              )}

              {filters.product_id && (
                  <span>
                    Product: {getProductName(filters.product_id)}
                  </span>
                )}

                {filters.category_id && (
                  <span>
                    Category: {getCategoryName(filters.category_id)}
                  </span>
                )}

                {filters.customer_id && (
                  <span>
                    Customer: {getCustomerName(filters.customer_id)}
                  </span>
                )}

                {filters.sales_status && (
                  <span>
                    Sales Status: {filters.sales_status}
                  </span>
                )}

                {filters.stock_status && (
                  <span>
                    Stock Status: {filters.stock_status}
                  </span>
                )}
            </div>

          </div>

          {!detailedReport.data ||
          detailedReport.data.length === 0 ? (
            <div className="empty-report">
              No data found for the selected filters.
            </div>
          ) : (
            <>
              <div className="report-table-wrapper">

                <table className="report-table">

                  <thead>
                    <tr>
                      {getColumns().map((column) => (
                        <th
                          key={column}
                          onClick={() =>
                            handleSort(column)
                          }
                        >
                          <span>
                            {formatColumnName(
                              column
                            )}
                          </span>

                          {filters.sort_by ===
                            column && (
                            <span className="sort-icon">
                              {filters.sort_order ===
                              "asc"
                                ? " ↑"
                                : " ↓"}
                            </span>
                          )}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>

                    {detailedReport.data.map(
                      (row, rowIndex) => (
                        <tr
                          key={
                            row.id ||
                            row.product_id ||
                            rowIndex
                          }
                        >
                          {getColumns().map(
                            (column) => (
                              <td
                                key={column}
                              >
                                {formatValue(
                                  row[column]
                                )}
                              </td>
                            )
                          )}
                        </tr>
                      )
                    )}

                  </tbody>

                </table>

              </div>

              <div className="report-pagination">

                <button
                  disabled={
                    detailedReport.page <= 1 ||
                    loading
                  }
                  onClick={() =>
                    handlePageChange(
                      detailedReport.page - 1
                    )
                  }
                >
                  Previous
                </button>

                <span>
                  Page{" "}
                  {detailedReport.page} of{" "}
                  {detailedReport.total_pages}
                </span>

                <button
                  disabled={
                    detailedReport.page >=
                      detailedReport.total_pages ||
                    loading
                  }
                  onClick={() =>
                    handlePageChange(
                      detailedReport.page + 1
                    )
                  }
                >
                  Next
                </button>

              </div>
            </>
          )}

        </div>
      )}

      <div className="report-card">

        <div className="section-header">
          <div>
            <h2>Export Reports</h2>

            <p>
              Download existing report formats.
            </p>
          </div>
        </div>

        <div className="report-actions">

          <button
            className="export-btn"
            onClick={() =>
              handleExport(
                exportSalesExcel,
                "Sales_Report.xlsx"
              )
            }
          >
            📊 Sales Excel
          </button>

          <button
            className="export-btn"
            onClick={() =>
              handleExport(
                exportInventoryExcel,
                "Inventory_Report.xlsx"
              )
            }
          >
            📦 Inventory Excel
          </button>

          <button
            className="export-btn pdf-btn"
            onClick={() =>
              handleExport(
                exportSalesPDF,
                "Sales_Report.pdf"
              )
            }
          >
            📄 Sales PDF
          </button>

          <button
            className="export-btn pdf-btn"
            onClick={() =>
              handleExport(
                exportInventoryPDF,
                "Inventory_Report.pdf"
              )
            }
          >
            📄 Inventory PDF
          </button>

        </div>

      </div>

      <div className="report-card">

        <div className="section-header">

          <div>
            <h2>Report History</h2>

            <p>
              Previously generated reports
            </p>
          </div>

        </div>

        {historyLoading ? (
          <div className="reports-loading">
            Loading report history...
          </div>
        ) : history.length === 0 ? (
          <div className="empty-report">
            No report history available.
          </div>
        ) : (
          <div className="report-table-wrapper">

            <table className="report-table">

              <thead>
                <tr>
                  <th>Report Name</th>
                  <th>Generated By</th>
                  <th>Format</th>
                  <th>Status</th>
                  <th>Generated At</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>

                {history.map((item) => (
                  <tr key={item.id}>

                    <td>
                      {item.report_name}
                    </td>

                    <td>
                      User #{item.generated_by}
                    </td>

                    <td>
                      {item.format}
                    </td>

                    <td>
                      <span
                        className={
                          item.status === "Success"
                            ? "status-success"
                            : "status-failed"
                        }
                      >
                        {item.status}
                      </span>
                    </td>

                    <td>
                      {item.generated_at
                        ? new Date(
                            item.generated_at
                          ).toLocaleString()
                        : "-"}
                    </td>

                    <td>
                      {item.file_path ? (
                        <button
                          className="download-btn"
                          onClick={() =>
                            handleHistoryDownload(
                              item.id,
                              item.format
                            )
                          }
                        >
                          Download
                        </button>
                      ) : (
                        <span>
                          Not Available
                        </span>
                      )}
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