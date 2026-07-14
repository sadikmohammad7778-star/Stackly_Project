import RevenueChart from "../components/dashboard/RevenueChart";
import EmployeePieChart from "../components/dashboard/EmployeePieChart";
import AttendanceChart from "../components/dashboard/AttendanceChart";

import {
  FiTrendingUp,
  FiUsers,
  FiBriefcase,
  FiCalendar,
} from "react-icons/fi";

import "./Analytics.css";

export default function Analytics() {

  return (

    <div className="analytics-page">

      <div className="analytics-header">

        <h2>Analytics Dashboard</h2>

      </div>

      {/* Summary Cards */}

      <div className="analytics-cards">

        <div className="analytics-card">

          <FiTrendingUp className="card-icon" />

          <h3>Total Revenue</h3>

          <h1>₹4,82,500</h1>

        </div>

        <div className="analytics-card">

          <FiUsers className="card-icon" />

          <h3>Total Employees</h3>

          <h1>215</h1>

        </div>

        <div className="analytics-card">

          <FiBriefcase className="card-icon" />

          <h3>Companies</h3>

          <h1>12</h1>

        </div>

        <div className="analytics-card">

          <FiCalendar className="card-icon" />

          <h3>Attendance</h3>

          <h1>97%</h1>

        </div>

      </div>

      {/* Charts */}

      <div className="analytics-grid">

        <div className="chart-card">

          <h3>Revenue Overview</h3>

          <RevenueChart />

        </div>

        <div className="chart-card">

          <h3>Department Distribution</h3>

          <EmployeePieChart />

        </div>

      </div>

      <div className="chart-card">

        <h3>Weekly Attendance</h3>

        <AttendanceChart />

      </div>

    </div>

  );

}