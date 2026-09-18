import Sidebar from "../components/dashboard/Sidebar";
import Navbar from "../components/dashboard/Navbar";
import { Outlet } from "react-router-dom";

import "./DashboardLayout.css";

export default function DashboardLayout(){

    return(

        <div className="layout">

            <Sidebar/>

            <div className="main-content">

                <Navbar/>

                <div className="page-content">

                    <Outlet/>

                </div>

            </div>

        </div>

    );

}