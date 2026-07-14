import { useEffect, useState } from "react";
import { updateCompany } from "../../api/companyApi";
import "./CompanyModal.css";

export default function EditCompanyModal({
  isOpen,
  onClose,
  company,
  onSuccess,
}) {
  const [formData, setFormData] = useState({
    company_name: "",
    email: "",
    phone: "",
    address: "",
  });

  useEffect(() => {
    if (company) {
      setFormData(company);
    }
  }, [company]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await updateCompany(company.id, formData);

      alert("Company updated successfully.");

      onSuccess();

      onClose();

    } catch (error) {
      console.error(error);
      alert("Update failed.");
    }
  };

  return (
    <div className="modal-overlay">

      <div className="modal">

        <h2>Edit Company</h2>

        <form onSubmit={handleSubmit}>

          <input
            name="company_name"
            value={formData.company_name}
            onChange={handleChange}
            required
          />

          <input
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            required
          />

          <textarea
            name="address"
            value={formData.address}
            onChange={handleChange}
            required
          />

          <div className="modal-buttons">

            <button
              type="button"
              onClick={onClose}
            >
              Cancel
            </button>

            <button type="submit">
              Update
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}