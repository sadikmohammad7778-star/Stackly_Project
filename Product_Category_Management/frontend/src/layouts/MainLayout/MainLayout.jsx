import { Outlet } from "react-router-dom";

import Sidebar from "../../components/Sidebar/Sidebar";
import Navbar from "../../components/Navbar/Navbar";

import "./MainLayout.css";

function MainLayout() {
  return (
    <div className="layout">
      <Sidebar />

      <div className="main-content">
        <Navbar />

        <div className="page-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

export default MainLayout;