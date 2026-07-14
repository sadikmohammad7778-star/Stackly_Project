import { useState } from "react";
import "./Settings.css";

export default function Settings() {

  const [settings, setSettings] = useState({
    companyName: "RetailPulse Analytics",
    adminName: "Mohammad Sadik",
    email: "sadik@gmail.com",
    phone: "9876543210",
  });

  const handleChange = (e) => {

    setSettings({
      ...settings,
      [e.target.name]: e.target.value,
    });

  };

  const handleSubmit = (e) => {

    e.preventDefault();

    alert("Settings saved successfully.");

  };

  return (

    <div className="settings-page">

      <div className="settings-header">

        <h2>Settings</h2>

      </div>

      <div className="settings-card">

        <form onSubmit={handleSubmit}>

          <div className="form-group">

            <label>Company Name</label>

            <input
              name="companyName"
              value={settings.companyName}
              onChange={handleChange}
            />

          </div>

          <div className="form-group">

            <label>Admin Name</label>

            <input
              name="adminName"
              value={settings.adminName}
              onChange={handleChange}
            />

          </div>

          <div className="form-group">

            <label>Email</label>

            <input
              type="email"
              name="email"
              value={settings.email}
              onChange={handleChange}
            />

          </div>

          <div className="form-group">

            <label>Phone</label>

            <input
              name="phone"
              value={settings.phone}
              onChange={handleChange}
            />

          </div>

          <button type="submit">
            Save Settings
          </button>

        </form>

      </div>

    </div>

  );

}