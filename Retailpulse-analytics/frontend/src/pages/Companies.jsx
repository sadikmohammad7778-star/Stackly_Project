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

  const [openModal, setOpenModal] = useState(false);

  const [editModalOpen, setEditModalOpen] = useState(false);

  const [selectedCompany, setSelectedCompany] = useState(null);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      const data = await getCompanies();
      setCompanies(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id) => {

    const confirmDelete = window.confirm(
      "Are you sure you want to delete this company?"
    );

    if (!confirmDelete) return;

    try {

      await deleteCompany(id);

      loadCompanies();

    } catch (error) {

      console.error(error);

    }

  };

  return (

    <div className="companies-page">

      <div className="companies-header">

        <h2>Companies</h2>

        <button onClick={() => setOpenModal(true)}>

          <FiPlus />

          Add Company

        </button>

      </div>

      <div className="search-box">

        <FiSearch />

        <input
          type="text"
          placeholder="Search company..."
        />

      </div>

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

            {companies.map((company) => (

              <tr key={company.id}>

                <td>{company.company_name}</td>

                <td>{company.email}</td>

                <td>{company.phone}</td>

                <td>{company.address}</td>

                <td>

                  <button
                    className="edit"
                    onClick={() => {

                      setSelectedCompany(company);

                      setEditModalOpen(true);

                    }}
                  >

                    <FiEdit />

                  </button>

                  <button
                    className="delete"
                    onClick={() => handleDelete(company.id)}
                  >

                    <FiTrash2 />

                  </button>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

      <CompanyModal
        isOpen={openModal}
        onClose={() => setOpenModal(false)}
        onSuccess={loadCompanies}
      />

      <EmployeeCompanyModal
        isOpen={editModalOpen}
        company={selectedCompany}
        onClose={() => setEditModalOpen(false)}
        onSuccess={loadCompanies}
      />

    </div>

  );

}