import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../services/authService";
import "./Signup.css";

export default function Signup() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    company_id: "",
    name: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });

    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await registerUser({
        company_id: Number(formData.company_id),
        name: formData.name,
        email: formData.email,
        password: formData.password,
      });

      setSuccess("Account created successfully!");

      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Registration failed."
      );
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-left">
        <div className="signup-logo">
          <div className="logo-icon">
            <span></span>
            <span></span>
          </div>

          <div>
            <h1>RetailPulse</h1>
            <p>Analytics</p>
          </div>
        </div>

        <div className="signup-content">
          <div className="signup-visual">
            <div className="visual-chart">
              <span></span>
              <span></span>
              <span></span>
              <span></span>
            </div>

            <div className="visual-arrow">↗</div>

            <div className="visual-circle"></div>
          </div>

          <h2>Grow with better insights.</h2>

          <p>
            Create your account and make smarter
            retail decisions with RetailPulse Analytics.
          </p>

          <div className="signup-tags">
            <span>Sales</span>
            <span>Inventory</span>
            <span>Analytics</span>
          </div>
        </div>
      </div>

      <div className="signup-right">
        <div className="signup-form">
          <div className="signup-header">
            <h2>Create Account</h2>
            <p>Create your RetailPulse account</p>
          </div>

          {error && (
            <div className="signup-error">
              {error}
            </div>
          )}

          {success && (
            <div className="signup-success">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Company ID</label>
              <input
                type="number"
                name="company_id"
                placeholder="Enter company ID"
                value={formData.company_id}
                onChange={handleChange}
                required
              />
            </div>

            <div className="field">
              <label>Full Name</label>
              <input
                type="text"
                name="name"
                placeholder="Enter your full name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="field">
              <label>Email</label>
              <input
                type="email"
                name="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="field">
              <label>Password</label>
              <input
                type="password"
                name="password"
                placeholder="Create a password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            <button type="submit">
              Create Account
            </button>
          </form>

          <p className="login-link">
            Already have an account?{" "}
            <span onClick={() => navigate("/login")}>
              Login
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}