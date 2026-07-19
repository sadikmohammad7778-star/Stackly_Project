import { useEffect, useState } from "react";
import {
  getRevenueReport,
  getInventoryReport,
} from "../api/analyticsApi";
import "./Analytics.css";

export default function Analytics() {
  const [revenue, setRevenue] = useState(null);
  const [inventory, setInventory] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const revenueData = await getRevenueReport();
      const inventoryData = await getInventoryReport();

      setRevenue(revenueData);
      setInventory(inventoryData);
    } catch (error) {
      console.error("Error loading analytics:", error);
    }
  };

  return (
    <div className="analytics-page">

      <h2>Analytics Dashboard</h2>

      <h3 className="section-title">Revenue Analytics</h3>

      <div className="analytics-grid">

        <div className="analytics-card">
          <h4>Today</h4>
          <p>₹ {revenue?.today ?? 0}</p>
        </div>

        <div className="analytics-card">
          <h4>This Week</h4>
          <p>₹ {revenue?.this_week ?? 0}</p>
        </div>

        <div className="analytics-card">
          <h4>This Month</h4>
          <p>₹ {revenue?.this_month ?? 0}</p>
        </div>

        <div className="analytics-card">
          <h4>This Year</h4>
          <p>₹ {revenue?.this_year ?? 0}</p>
        </div>

      </div>

      <h3 className="section-title">Inventory Analytics</h3>

      <div className="analytics-grid">

        <div className="analytics-card">
          <h4>Total Products</h4>
          <p>{inventory?.total_products ?? 0}</p>
        </div>

        <div className="analytics-card">
          <h4>In Stock</h4>
          <p>{inventory?.in_stock ?? 0}</p>
        </div>

        <div className="analytics-card">
          <h4>Low Stock</h4>
          <p>{inventory?.low_stock ?? 0}</p>
        </div>

        <div className="analytics-card">
          <h4>Out of Stock</h4>
          <p>{inventory?.out_of_stock ?? 0}</p>
        </div>

        <div className="analytics-card inventory-value">
          <h4>Inventory Value</h4>
          <p>₹ {inventory?.inventory_value ?? 0}</p>
        </div>

      </div>

    </div>
  );
}