import { useEffect, useState } from "react";

import "./Customers.css";

import {
  getCustomers,
  searchCustomers,
  filterCustomers,
} from "../api/customerApi";

import CustomerForm from "../components/customers/CustomerForm";
import CustomerTable from "../components/customers/CustomerTable";
import CustomerSearchFilter from "../components/customers/CustomerSearchFilter";
import CustomerExport from "../components/customers/CustomerExport";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] =
    useState(null);

  // ================= Load Customers =================

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      const data = await getCustomers();

      setCustomers(
        Array.isArray(data) ? data : []
      );
    } catch (error) {
      console.error(
        "Error loading customers:",
        error
      );

      setCustomers([]);
    }
  };

  // ================= Refresh =================

  const refreshData = async () => {
    await loadCustomers();
  };

  // ================= Search =================

  const handleSearch = async (search) => {
    try {
      if (!search.trim()) {
        await loadCustomers();
        return;
      }

      const data = await searchCustomers(
        search.trim()
      );

      setCustomers(
        Array.isArray(data) ? data : []
      );
    } catch (error) {
      console.error(
        "Error searching customers:",
        error
      );

      setCustomers([]);
    }
  };

  // ================= Filter =================

  const handleFilter = async (filters) => {
    try {
      const data = await filterCustomers(
        filters
      );

      setCustomers(
        Array.isArray(data) ? data : []
      );
    } catch (error) {
      console.error(
        "Error filtering customers:",
        error
      );

      setCustomers([]);
    }
  };

  return (
    <div className="companies-page">

      {/* Header */}

      <div className="companies-header">
        <h2>Customers</h2>

        <CustomerExport />
      </div>

      {/* Search & Filter */}

      <div className="customer-search">
        <CustomerSearchFilter
          onSearch={handleSearch}
          onFilter={handleFilter}
        />
      </div>

      {/* Customer Form */}

      <div className="table-card">
        <CustomerForm
          reload={refreshData}
          selectedCustomer={selectedCustomer}
          setSelectedCustomer={
            setSelectedCustomer
          }
        />
      </div>

      {/* Customer Table */}

      <div className="table-card">
        <CustomerTable
          customers={customers}
          reload={refreshData}
          setSelectedCustomer={
            setSelectedCustomer
          }
        />
      </div>

    </div>
  );
}