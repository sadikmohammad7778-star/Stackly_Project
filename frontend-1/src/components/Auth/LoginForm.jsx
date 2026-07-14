import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  FaUserCircle,
  FaEnvelope,
  FaLock,
  FaEye,
  FaEyeSlash,
} from "react-icons/fa";

function Login() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.email || !formData.password) {
      alert("Please fill all fields");
      return;
    }

    navigate("/dashboard");
  };

  return (
    <div className="auth-container">
      <div className="auth-card">

        <div className="user-icon">
          <FaUserCircle />
        </div>

        <h2>Welcome Back!</h2>

        <p>Login to your account</p>

        <form onSubmit={handleSubmit}>

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

          <label>Password</label>

          <div className="input-group">
            <FaLock className="left-icon" />

            <input
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Enter your password"
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

          <div className="options">

            <label>
              <input type="checkbox" />
              Remember me
            </label>

            <Link to="#">Forgot Password?</Link>

          </div>

          <button className="auth-btn">
            Login
          </button>

        </form>

        <div className="bottom-text">
          Don't have an account?{" "}
          <Link to="/signup">Sign Up</Link>
        </div>

      </div>
    </div>
  );
}

export default Login;