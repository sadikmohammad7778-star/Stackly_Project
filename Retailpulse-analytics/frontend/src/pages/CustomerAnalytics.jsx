import { useEffect, useState } from "react";
import "./CustomerAnalytics.css";

import { customerDashboard } from "../api/customerApi";
import CustomerCharts from "../components/customers/CustomerCharts";

export default function CustomerAnalytics() {
  const [dashboard, setDashboard] = useState({
    total_customers: 0,
    active_customers: 0,
    new_customers: 0,
    returning_customers: 0,
    average_customer_spend: 0,
    total_revenue_generated: 0,
    average_purchase_frequency: 0,
  });

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await customerDashboard();
      setDashboard(response.data);
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    }
  };

  return (
    <div className="customer-analytics">

      <h1 className="page-title">
        📊 Customer Analytics Dashboard
      </h1>

      <div className="dashboard-cards">

        <div className="card">
          <div className="card-icon">👥</div>
          <h3>Total Customers</h3>
          <h2>{dashboard.total_customers}</h2>
        </div>

        <div className="card">
          <div className="card-icon">✅</div>
          <h3>Active Customers</h3>
          <h2>{dashboard.active_customers}</h2>
        </div>

        <div className="card">
          <div className="card-icon">🆕</div>
          <h3>New Customers</h3>
          <h2>{dashboard.new_customers}</h2>
        </div>

        <div className="card">
          <div className="card-icon">🔁</div>
          <h3>Returning Customers</h3>
          <h2>{dashboard.returning_customers}</h2>
        </div>

        <div className="card">
          <div className="card-icon">💰</div>
          <h3>Total Revenue</h3>
          <h2>₹ {dashboard.total_revenue_generated}</h2>
        </div>

        <div className="card">
          <div className="card-icon">💳</div>
          <h3>Average Customer Spend</h3>
          <h2>₹ {dashboard.average_customer_spend}</h2>
        </div>

        <div className="card">
          <div className="card-icon">📈</div>
          <h3>Purchase Frequency</h3>
          <h2>{dashboard.average_purchase_frequency}</h2>
        </div>

      </div>

      <CustomerCharts />

    </div>
  );
}