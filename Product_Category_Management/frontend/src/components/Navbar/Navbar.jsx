import { FaBell, FaSearch, FaUserCircle } from "react-icons/fa";
import "./Navbar.css";

function Navbar() {
  return (
    <div className="navbar">

      <h2 className="navbar-title">
        Product & Category Management
      </h2>

      <div className="navbar-right">

        <div className="search-box">
          <FaSearch />
          <input
            type="text"
            placeholder="Search..."
          />
        </div>

        <div className="nav-icons">
          <FaBell />
          <FaUserCircle className="profile-icon" />
        </div>

      </div>

    </div>
  );
}

export default Navbar;