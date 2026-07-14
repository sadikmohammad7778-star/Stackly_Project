import { FaBell, FaUserCircle } from "react-icons/fa";

function Navbar() {
  return (
    <header className="navbar">

      <div>
        <h2>Employee Management System</h2>
      </div>

      <div className="navbar-right">

        <FaBell className="nav-icon" />

        <div className="profile">

          <FaUserCircle className="profile-icon" />

          <div>
            <h4>Admin</h4>
            <p>Administrator</p>
          </div>

        </div>

      </div>

    </header>
  );
}

export default Navbar;