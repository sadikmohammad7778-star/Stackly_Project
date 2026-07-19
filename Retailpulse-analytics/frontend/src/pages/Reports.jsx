import { useEffect, useState } from "react";
import { getSalesReport, getStockReport } from "../api/reportApi";
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
      console.error("Error loading reports:", error);
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
    </div>
  );
}