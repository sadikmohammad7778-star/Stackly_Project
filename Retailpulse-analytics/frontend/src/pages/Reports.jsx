import { useEffect, useState } from "react";
import { getSalesReport, getStockReport } from "../api/reportApi";

import {
  exportSalesExcel,
  exportInventoryExcel,
  exportSalesPDF,
  exportInventoryPDF,
} from "../api/exportApi";

import "./Reports.css";

export default function Reports() {
  const [salesReport, setSalesReport] = useState(null);
  const [stockReport, setStockReport] = useState(null);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const sales = await getSalesReport();
      const stock = await getStockReport();

      setSalesReport(sales);
      setStockReport(stock);
    } catch (error) {
      console.error(error);
    }
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

  return (
    <div className="reports-page">

      <h2>Reports</h2>

      <div className="reports-grid">

        <div className="report-card">
          <h3>Total Sales</h3>
          <p>{salesReport?.total_sales ?? 0}</p>
        </div>

        <div className="report-card">
          <h3>Total Revenue</h3>
          <p>₹ {salesReport?.total_revenue ?? 0}</p>
        </div>

        <div className="report-card">
          <h3>Average Order Value</h3>
          <p>₹ {salesReport?.average_order_value ?? 0}</p>
        </div>

        <div className="report-card">
          <h3>Total Products</h3>
          <p>{stockReport?.total_products ?? 0}</p>
        </div>

        <div className="report-card">
          <h3>In Stock</h3>
          <p>{stockReport?.in_stock ?? 0}</p>
        </div>

        <div className="report-card">
          <h3>Low Stock</h3>
          <p>{stockReport?.low_stock ?? 0}</p>
        </div>

        <div className="report-card">
          <h3>Out of Stock</h3>
          <p>{stockReport?.out_of_stock ?? 0}</p>
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
  );
}