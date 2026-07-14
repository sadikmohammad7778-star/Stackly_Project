import "./Navbar.css";
import {
  FiSearch,
  FiBell,
  FiSettings,
} from "react-icons/fi";

export default function Navbar() {

  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <header className="navbar">

      <div className="navbar-left">

        <h2>RetailPulse Analytics</h2>

        <p>{today}</p>

      </div>

      <div className="navbar-center">

        <div className="search">

          <FiSearch />

          <input
            type="text"
            placeholder="Search..."
          />

        </div>

      </div>

      <div className="navbar-right">

        <button className="icon-btn">

          <FiBell />

        </button>

        <button className="icon-btn">

          <FiSettings />

        </button>

        <div className="profile">

          <img
            src="https://i.pravatar.cc/100"
            alt="Profile"
          />

          <div>

            <h4>Mohammad Sadik</h4>

            <span>Company Admin</span>

          </div>

        </div>

      </div>

    </header>
  );
}