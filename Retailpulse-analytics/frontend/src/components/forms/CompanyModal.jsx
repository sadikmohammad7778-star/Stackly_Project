import { useState } from "react";
import { createCompany } from "../../api/companyApi";
import "./CompanyModal.css";

export default function CompanyModal({
  isOpen,
  onClose,
  onSuccess,
}) {
  const initialForm = {
    company_name: "",
    email: "",
    phone: "",
    address: "",
  };

  const [formData, setFormData] = useState(initialForm);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const resetForm = () => {
    setFormData(initialForm);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      await createCompany(formData);

      alert("Company created successfully.");

      resetForm();

      onSuccess();

      onClose();

    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Failed to create company."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">

      <div className="modal">

        <h2>Add Company</h2>

        <form onSubmit={handleSubmit}>

          <input
            type="text"
            name="company_name"
            placeholder="Company Name"
            value={formData.company_name}
            onChange={handleChange}
            required
          />

          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="phone"
            placeholder="Phone Number"
            value={formData.phone}
            onChange={handleChange}
            required
          />

          <textarea
            name="address"
            placeholder="Address"
            value={formData.address}
            onChange={handleChange}
            required
          />

          <div className="modal-buttons">

            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save Company"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}