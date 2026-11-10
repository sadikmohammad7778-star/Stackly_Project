import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  FiArrowLeft,
  FiClock,
  FiRefreshCw,
  FiCalendar,
  FiCheckCircle,
  FiAlertCircle,
  FiTrash2,
  FiSave,
  FiLoader,
  FiPower,
  FiActivity
} from "react-icons/fi";

import {
  getIntegration,
  getIntegrationSchedule,
  createIntegrationSchedule,
  updateIntegrationSchedule,
  deleteIntegrationSchedule
} from "../../api/integrationApi";

import "./IntegrationSchedule.css";

const initialForm = {
  frequency: "daily",
  day_of_week: 0,
  scheduled_time: "02:00",
  timezone: "Asia/Kolkata",
  is_active: true
};

const days = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday"
];

export default function IntegrationSchedule() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [integration, setIntegration] = useState(null);
  const [schedule, setSchedule] = useState(null);
  const [form, setForm] = useState(initialForm);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    loadSchedule();
  }, [id]);

  const loadSchedule = async () => {
    try {
      setLoading(true);
      setError("");

      const integrationData = await getIntegration(id);
      setIntegration(integrationData);

      try {
        const scheduleData = await getIntegrationSchedule(id);

        setSchedule(scheduleData);

        setForm({
          frequency: scheduleData.frequency || "daily",
          day_of_week: scheduleData.day_of_week ?? 0,
          scheduled_time: scheduleData.scheduled_time
            ? String(scheduleData.scheduled_time).slice(0, 5)
            : "02:00",
          timezone: scheduleData.timezone || "Asia/Kolkata",
          is_active: scheduleData.is_active ?? true
        });
      } catch (scheduleError) {
        if (scheduleError.response?.status === 404) {
          setSchedule(null);
          setForm(initialForm);
        } else {
          throw scheduleError;
        }
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to load schedule information."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");
      setMessage("");

      const payload = {
        frequency: form.frequency,
        scheduled_time: form.scheduled_time,
        timezone: form.timezone,
        is_active: form.is_active,
        day_of_week:
          form.frequency === "weekly"
            ? Number(form.day_of_week)
            : null
      };

      if (schedule) {
        await updateIntegrationSchedule(id, payload);
        setMessage("Integration schedule updated successfully.");
      } else {
        await createIntegrationSchedule(id, payload);
        setMessage("Integration schedule created successfully.");
      }

      await loadSchedule();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to save integration schedule."
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this integration schedule?"
    );

    if (!confirmed) return;

    try {
      setDeleting(true);
      setError("");
      setMessage("");

      await deleteIntegrationSchedule(id);

      setSchedule(null);
      setForm(initialForm);
      setMessage("Integration schedule deleted successfully.");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to delete integration schedule."
      );
    } finally {
      setDeleting(false);
    }
  };

  const formatDate = (date) => {
    if (!date) return "Not available";

    return new Date(date).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short"
    });
  };

  if (loading) {
    return (
      <div className="schedule-loading">
        <FiLoader className="schedule-spinner" />
        <p>Loading schedule information...</p>
      </div>
    );
  }

  if (!integration) {
    return (
      <div className="schedule-error-page">
        <FiAlertCircle />
        <h3>Integration not found</h3>
        <p>{error || "Unable to find this integration."}</p>

        <button onClick={() => navigate("/integrations")}>
          Back to Integrations
        </button>
      </div>
    );
  }

  return (
    <div className="integration-schedule-page">
      <div className="schedule-header">
        <button
          className="schedule-back-button"
          onClick={() => navigate(`/integrations/${id}`)}
        >
          <FiArrowLeft />
          Back to Integration
        </button>

        <div className="schedule-title-row">
          <div>
            <span className="schedule-subtitle">
              ENTERPRISE DATA MANAGEMENT
            </span>

            <h1>Schedule Management</h1>

            <p>
              Configure automated synchronization for your data connector.
            </p>
          </div>

          <button
            className="schedule-refresh-button"
            onClick={loadSchedule}
          >
            <FiRefreshCw />
            Refresh
          </button>
        </div>
      </div>

      {message && (
        <div className="schedule-alert schedule-alert-success">
          <FiCheckCircle />
          {message}
          <button onClick={() => setMessage("")}>×</button>
        </div>
      )}

      {error && (
        <div className="schedule-alert schedule-alert-error">
          <FiAlertCircle />
          {error}
          <button onClick={() => setError("")}>×</button>
        </div>
      )}

      <div className="schedule-integration-card">
        <div className="schedule-integration-icon">
          <FiCalendar />
        </div>

        <div>
          <h2>{integration.name}</h2>
          <p>
            {integration.source_type?.replace("_", " ").toUpperCase()}
            {" - "}
            {integration.target_module?.toUpperCase()}
          </p>

          <span
            className={
              integration.is_enabled
                ? "schedule-enabled"
                : "schedule-disabled"
            }
          >
            {integration.is_enabled ? "Enabled" : "Disabled"}
          </span>
        </div>
      </div>

      <div className="schedule-information-grid">
        <div className="schedule-information-card">
          <span>Schedule Status</span>
          <h3>
            {schedule
              ? schedule.is_active
                ? "Active"
                : "Inactive"
              : "Not Configured"}
          </h3>
        </div>

        <div className="schedule-information-card">
          <span>Frequency</span>
          <h3>{schedule?.frequency || "Not Configured"}</h3>
        </div>

        <div className="schedule-information-card">
          <span>Next Execution</span>
          <h3>{formatDate(schedule?.next_run_at)}</h3>
        </div>

        <div className="schedule-information-card">
          <span>Last Execution</span>
          <h3>{formatDate(schedule?.last_run_at)}</h3>
        </div>
      </div>

      <div className="schedule-section">
        <div className="schedule-section-heading">
          <div>
            <h2>
              {schedule ? "Update Synchronization Schedule" : "Create Synchronization Schedule"}
            </h2>

            <p>
              Set the frequency, time and timezone for automatic synchronization.
            </p>
          </div>

          <FiClock />
        </div>

        <form onSubmit={handleSubmit}>
          <div className="schedule-form-grid">
            <div className="schedule-form-group">
              <label>Synchronization Frequency *</label>

              <select
                name="frequency"
                value={form.frequency}
                onChange={handleChange}
                required
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>

            {form.frequency === "weekly" && (
              <div className="schedule-form-group">
                <label>Day of Week *</label>

                <select
                  name="day_of_week"
                  value={form.day_of_week}
                  onChange={handleChange}
                  required
                >
                  {days.map((day, index) => (
                    <option key={day} value={index}>
                      {day}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="schedule-form-group">
              <label>Scheduled Time *</label>

              <input
                type="time"
                name="scheduled_time"
                value={form.scheduled_time}
                onChange={handleChange}
                required
              />
            </div>

            <div className="schedule-form-group">
              <label>Timezone *</label>

              <select
                name="timezone"
                value={form.timezone}
                onChange={handleChange}
                required
              >
                <option value="Asia/Kolkata">
                  India Standard Time
                </option>

                <option value="UTC">
                  UTC
                </option>

                <option value="Asia/Dubai">
                  Gulf Standard Time
                </option>

                <option value="Europe/London">
                  London Time
                </option>

                <option value="America/New_York">
                  Eastern Time
                </option>
              </select>
            </div>
          </div>

          <label className="schedule-toggle">
            <input
              type="checkbox"
              name="is_active"
              checked={form.is_active}
              onChange={handleChange}
            />

            <span className="schedule-toggle-content">
              <strong>Enable Automatic Synchronization</strong>
              <small>
                Allow the scheduler to execute this integration automatically.
              </small>
            </span>

            <FiPower />
          </label>

          <div className="schedule-form-actions">
            {schedule && (
              <button
                type="button"
                className="schedule-delete-button"
                onClick={handleDelete}
                disabled={deleting || saving}
              >
                {deleting ? (
                  <FiLoader className="schedule-spinner" />
                ) : (
                  <FiTrash2 />
                )}

                Delete Schedule
              </button>
            )}

            <button
              type="button"
              className="schedule-cancel-button"
              onClick={() => navigate(`/integrations/${id}`)}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="schedule-save-button"
              disabled={saving || deleting}
            >
              {saving ? (
                <FiLoader className="schedule-spinner" />
              ) : (
                <FiSave />
              )}

              {saving
                ? "Saving..."
                : schedule
                  ? "Update Schedule"
                  : "Create Schedule"}
            </button>
          </div>
        </form>
      </div>

      {schedule && (
        <div className="schedule-section">
          <div className="schedule-section-heading">
            <div>
              <h2>Schedule Execution Information</h2>
              <p>Current automated synchronization configuration.</p>
            </div>

            <FiActivity />
          </div>

          <div className="schedule-execution-grid">
            <div>
              <span>Schedule ID</span>
              <strong>#{schedule.id}</strong>
            </div>

            <div>
              <span>Frequency</span>
              <strong>{schedule.frequency}</strong>
            </div>

            <div>
              <span>Scheduled Time</span>
              <strong>{schedule.scheduled_time}</strong>
            </div>

            <div>
              <span>Timezone</span>
              <strong>{schedule.timezone}</strong>
            </div>

            <div>
              <span>Next Run</span>
              <strong>{formatDate(schedule.next_run_at)}</strong>
            </div>

            <div>
              <span>Last Run Status</span>
              <strong>{schedule.last_run_status || "Not executed"}</strong>
            </div>

            <div>
              <span>Created At</span>
              <strong>{formatDate(schedule.created_at)}</strong>
            </div>

            <div>
              <span>Updated At</span>
              <strong>{formatDate(schedule.updated_at)}</strong>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}