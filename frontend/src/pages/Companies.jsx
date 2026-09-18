import { useEffect, useState } from "react";
import {
  FiPlus,
  FiSearch,
  FiEdit,
  FiTrash2,
} from "react-icons/fi";

import CompanyModal from "../components/forms/CompanyModal";
import EmployeeCompanyModal from "../components/forms/EmployeeCompanyModal";

import {
  getCompanies,
  deleteCompany,
} from "../api/companyApi";

import "./Companies.css";

export default function Companies() {
  const [companies, setCompanies] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  const [openModal, setOpenModal] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);

  const [selectedCompany, setSelectedCompany] = useState(null);

  // Load companies when page opens
  useEffect(() => {
    loadCompanies();
  }, []);

  // Get companies from backend
  const loadCompanies = async () => {
    try {
      const data = await getCompanies();
      setCompanies(data);
    } catch (error) {
      console.error("Error loading companies:", error);
    }
  };

  // Delete company
  const handleDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this company?"
    );

    if (!confirmDelete) {
      return;
    }

    try {
      const response = await deleteCompany(id);

      alert(
        response.message || "Company deleted successfully."
      );

      await loadCompanies();
    } catch (error) {
      console.error("Error deleting company:", error);

      alert(
        error.response?.data?.detail ||
          "Failed to delete company."
      );
    }
  };

  // Filter companies based on search
  const filteredCompanies = companies.filter((company) => {
    const search = searchTerm.toLowerCase().trim();

    return (
      company.company_name
        ?.toLowerCase()
        .includes(search)
    );
  });

  return (
    <div className="companies-page">

      {/* Header */}
      <div className="companies-header">
        <h2>Companies</h2>

        <button onClick={() => setOpenModal(true)}>
          <FiPlus />
          Add Company
        </button>
      </div>

      {/* Search */}
      <div className="company-search-box">
        <FiSearch />

        <input
          type="text"
          placeholder="Search company..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Company Table */}
      <div className="table-card">
        <table>

          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Address</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {filteredCompanies.length > 0 ? (
              filteredCompanies.map((company) => (
                <tr key={company.id}>

                  <td>
                    {company.company_name}
                  </td>

                  <td>
                    {company.email}
                  </td>

                  <td>
                    {company.phone}
                  </td>

                  <td>
                    {company.address}
                  </td>

                  <td>

                    {/* Edit */}
                    <button
                      className="edit"
                      onClick={() => {
                        setSelectedCompany(company);
                        setEditModalOpen(true);
                      }}
                    >
                      <FiEdit />
                    </button>

                    {/* Delete */}
                    <button
                      className="delete"
                      onClick={() =>
                        handleDelete(company.id)
                      }
                    >
                      <FiTrash2 />
                    </button>

                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="5"
                  style={{
                    textAlign: "center",
                    padding: "20px",
                  }}
                >
                  No companies found.
                </td>
              </tr>
            )}
          </tbody>

        </table>
      </div>

      {/* Add Company Modal */}
      <CompanyModal
        isOpen={openModal}
        onClose={() => setOpenModal(false)}
        onSuccess={loadCompanies}
      />

      {/* Edit Company Modal */}
      <EmployeeCompanyModal
        isOpen={editModalOpen}
        company={selectedCompany}
        onClose={() => setEditModalOpen(false)}
        onSuccess={loadCompanies}
      />

    </div>
  );
}