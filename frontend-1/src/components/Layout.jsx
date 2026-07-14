import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

function Layout() {
  return (
    <div className="layout">

      <Sidebar />

      <div className="main-container">

        <Navbar />

        <div className="page-content">
          <Outlet />
        </div>

      </div>

    </div>
  );
}

export default Layout;