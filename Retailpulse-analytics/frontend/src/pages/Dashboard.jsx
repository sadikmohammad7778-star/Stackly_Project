import { useEffect, useState } from "react";

import DashboardCards from "../components/dashboard/DashboardCards";
import SalesChart from "../components/dashboard/SalesChart";
import DepartmentChart from "../components/dashboard/DepartmentChart";
import EmployeeTable from "../components/dashboard/EmployeeTable";

import { getDashboardData } from "../api/dashboardApi";

import "./Dashboard.css";

export default function Dashboard() {

  const [dashboardData, setDashboardData] = useState({
    companies: 0,
    employees: 0,
    departments: 0,
    attendance: 0,
  });

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="dashboard-page">

      <div className="dashboard-header">
        <div>
          <h1>RetailPulse Dashboard</h1>
          <p>Welcome back 👋</p>
        </div>
      </div>

      {/* Dashboard Cards */}
      <DashboardCards data={dashboardData} />

      {/* Charts */}
      <div className="chart-section">

        <div className="chart-card">
          <h3>Sales Overview</h3>
          <SalesChart />
        </div>

        <div className="chart-card">
          <h3>Departments</h3>
          <DepartmentChart />
        </div>

      </div>

      {/* Employee Table */}
      <div className="table-card">

        <h3>Recent Employees</h3>

        <EmployeeTable />

      </div>

    </div>
  );
}