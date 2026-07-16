import DashboardCards from "../../components/DashboardCards/DashboardCards";
import DashboardChart from "../../components/DashboardChart/DashboardChart";
import RecentProducts from "../../components/RecentProducts/RecentProducts";

import "./Dashboard.css";

function Dashboard() {
  return (
    <div className="dashboard">

      <h1 className="dashboard-title">
        Dashboard
      </h1>

      <DashboardCards />

      <DashboardChart />

      <RecentProducts />

    </div>
  );
}

export default Dashboard;