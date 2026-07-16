import "./Settings.css";
import react from "react";

function Settings() {
  return (
    <div className="settings-container">

      <h1>Settings</h1>

      <div className="settings-card">

        <h2>Application Settings</h2>

        <div className="setting-item">
          <label>Company Name</label>
          <input
            type="text" 
            value="Product & Category Management"
            readOnly
          />
        </div>

        <div className="setting-item">
          <label>Application Version</label>
          <input
            type="text"
            value="Version 1.0"
            readOnly
          />
        </div>

        <div className="setting-item">
          <label>Default Currency</label>
          <select>
            <option>INR (₹)</option>
            <option>USD ($)</option>
          </select>
        </div>

        <div className="setting-item">
          <label>Theme</label>
          <select>
            <option>Light</option>
            <option>Dark</option>
          </select>
        </div>

        <button className="save-btn">
          Save Settings
        </button>

      </div>

    </div>
  );
}

export default Settings;