import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));

    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await loginUser(
        formData.email,
        formData.password
      );

      // Save Access Token
      login(response.access_token);

      // Save Refresh Token
      localStorage.setItem(
        "refresh_token",
        response.refresh_token
      );

      // Save Logged-in User
      localStorage.setItem(
        "user",
        JSON.stringify(response.user)
      );

      //  remember email
      if (rememberMe) {
        localStorage.setItem("remember_email", formData.email);
      } else {
        localStorage.removeItem("remember_email");
      }

      // Redirect to Dashboard
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Invalid email or password"
      );
    }
  };

  return (
    <div className="login-page">

      {/* LEFT SIDE */}
      <div className="login-brand-panel">
        <div className="brand-content">

          <div className="brand-logo">
            <div className="logo-icon">
              <span></span>
              <span></span>
              <span></span>
            </div>

            <div>
              <h1>RetailPulse</h1>
              <p>Analytics</p>
            </div>
          </div>

          <div className="retail-illustration">

            <div className="chart-card">
              <div className="chart-bars">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div className="chart-arrow">↗</div>
            </div>

            <div className="shopping-cart">
              <div className="cart-basket">
                <div></div>
                <div></div>
                <div></div>
              </div>
              <div className="cart-handle"></div>
              <div className="cart-wheel wheel-one"></div>
              <div className="cart-wheel wheel-two"></div>
            </div>

            <div className="shopping-bag bag-yellow">
              <div className="bag-handle"></div>
            </div>

            <div className="shopping-bag bag-purple">
              <div className="bag-handle"></div>
            </div>

          </div>

          <div className="brand-message">
            <h2>Make smarter retail decisions</h2>
            <p>with real-time analytics</p>
          </div>

        </div>
      </div>

      {/* RIGHT SIDE */}
      <div className="login-form-panel">

        <div className="login-form-container">

          <div className="welcome-section">
            <h2>Welcome Back</h2>
            <p>
              <span className="welcome-icon">◉</span>
              Sign in to your account
            </p>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>

            {/* EMAIL */}
            <div className="form-group">
              <label htmlFor="email">Email</label>

              <input
                id="email"
                type="email"
                name="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            {/* PASSWORD */}
            <div className="form-group">
              <label htmlFor="password">Password</label>

              <div className="password-wrapper">
                <input
                  id="password"
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  name="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(!showPassword)
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword ? "◉" : "◌"}
                </button>
              </div>
            </div>

            {/* REMEMBER + FORGOT */}
            <div className="login-options">

              <label className="remember-me">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) =>
                    setRememberMe(e.target.checked)
                  }
                />

                <span>Remember me</span>
              </label>

              <button
                type="button"
                className="forgot-password"
                onClick={() => navigate("/forgot-password")}
              >
                Forgot Password?
              </button>

            </div>

            {/* LOGIN BUTTON */}
            <button
              type="submit"
              className="login-button"
            >
              Sign In
            </button>

          </form>

          {/* SIGNUP */}
          <div className="register-section">
            <span>Don't have an account?</span>

            <button
              type="button"
              onClick={() => navigate("/signup")}
            >
              Register
            </button>
          </div>

        </div>

      </div>

    </div>
  );
}