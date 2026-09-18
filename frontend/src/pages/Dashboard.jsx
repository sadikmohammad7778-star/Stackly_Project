import { useEffect, useState } from "react";

import DashboardCards from "../components/dashboard/DashboardCards";
import SalesChart from "../components/dashboard/SalesChart";
import DepartmentChart from "../components/dashboard/DepartmentChart";
import EmployeeTable from "../components/dashboard/EmployeeTable";

import { getDashboardData } from "../api/DashboardApi";

import "./Dashboard.css";

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState({
    total_companies: 0,
    total_users: 0,
    total_categories: 0,
    total_products: 0,
    total_sales: 0,
    total_revenue: 0,
    low_stock_products: 0,
    out_of_stock_products: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getDashboardData();

      setDashboardData(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load dashboard.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <h2>Loading Dashboard...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>{error}</h2>

        <button onClick={loadDashboard}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard-page">

      <div className="dashboard-header">
        <div>
          <h1>RetailPulse Dashboard</h1>
          <p>Welcome back 👋</p>
        </div>
      </div>

      <DashboardCards data={dashboardData} />

      <div className="chart-section">

        <div className="chart-card">
          <h3>Monthly Revenue</h3>
          <SalesChart />
        </div>

        <div className="chart-card">
          <h3>Sales by Category</h3>
          <DepartmentChart />
        </div>

      </div>

      <div className="table-card">
        <h3>Top Selling Products</h3>
        <EmployeeTable />
      </div>

    </div>
  );
}