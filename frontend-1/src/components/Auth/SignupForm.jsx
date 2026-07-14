import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  FaUserCircle,
  FaUser,
  FaEnvelope,
  FaLock,
  FaEye,
  FaEyeSlash,
} from "react-icons/fa";

function Signup() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);

  const [showConfirm, setShowConfirm] = useState(false);

  const [formData, setFormData] = useState({
    fullname: "",
    email: "",
    company: "",
    role: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (
      !formData.fullname ||
      !formData.email ||
      !formData.company ||
      !formData.role ||
      !formData.password ||
      !formData.confirmPassword
    ) {
      alert("Please fill all fields");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    alert("Account Created Successfully");

    navigate("/");
  };

  return (
    <div className="auth-container">
      <div className="auth-card">

        <div className="user-icon">
          <FaUserCircle />
        </div>

        <h2>Create Account</h2>

        <p>Sign up to access EEMS</p>

        <form onSubmit={handleSubmit}>

          <label>Full Name</label>

          <div className="input-group">
            <FaUser className="left-icon" />

            <input
              type="text"
              name="fullname"
              placeholder="Enter your name"
              value={formData.fullname}
              onChange={handleChange}
            />
          </div>

          <label>Email</label>

          <div className="input-group">
            <FaEnvelope className="left-icon" />

            <input
              type="email"
              name="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          <label>Company</label>

          <div className="input-group">
            <select
              name="company"
              value={formData.company}
              onChange={handleChange}
            >
              <option value="">Select Company</option>
              <option>Stackly </option>
              <option>prefoxys</option>
              <option>OpenAI</option>
            </select>
          </div>

          <label>Account Role</label>

          <div className="input-group">
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
            >
              <option value="">Select Role</option>
              <option>User</option>
              <option>Admin</option>
            </select>
          </div>

          <label>Password</label>

          <div className="input-group">
            <FaLock className="left-icon" />

            <input
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Create password"
              value={formData.password}
              onChange={handleChange}
            />

            {showPassword ? (
              <FaEyeSlash
                className="right-icon"
                onClick={() => setShowPassword(false)}
              />
            ) : (
              <FaEye
                className="right-icon"
                onClick={() => setShowPassword(true)}
              />
            )}
          </div>

          <label>Confirm Password</label>

          <div className="input-group">
            <FaLock className="left-icon" />

            <input
              type={showConfirm ? "text" : "password"}
              name="confirmPassword"
              placeholder="Confirm password"
              value={formData.confirmPassword}
              onChange={handleChange}
            />

            {showConfirm ? (
              <FaEyeSlash
                className="right-icon"
                onClick={() => setShowConfirm(false)}
              />
            ) : (
              <FaEye
                className="right-icon"
                onClick={() => setShowConfirm(true)}
              />
            )}
          </div>

          <button className="auth-btn">
            Sign Up
          </button>

        </form>

        <div className="bottom-text">
          Already have an account?{" "}
          <Link to="/">Login</Link>
        </div>

      </div>
    </div>
  );
}

export default Signup;