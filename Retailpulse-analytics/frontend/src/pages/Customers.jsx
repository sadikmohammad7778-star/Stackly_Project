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
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      const response = await getCustomers();
      setCustomers(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleSearch = async (search) => {
    try {
      if (search.trim() === "") {
        loadCustomers();
        return;
      }

      const response = await searchCustomers(search);
      setCustomers(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleFilter = async (filters) => {
    try {
      const response = await filterCustomers(filters);
      setCustomers(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="companies-page">

      <div className="companies-header">
        <h2>Customers</h2>
        <CustomerExport />
      </div>

      <div className="customer-search">
        <CustomerSearchFilter
          onSearch={handleSearch}
          onFilter={handleFilter}
        />
      </div>

      <div className="table-card">
        <CustomerForm
          reload={loadCustomers}
          selectedCustomer={selectedCustomer}
          setSelectedCustomer={setSelectedCustomer}
        />
      </div>

      <div className="table-card">
        <CustomerTable
          customers={customers}
          reload={loadCustomers}
          setSelectedCustomer={setSelectedCustomer}
        />
      </div>

    </div>
  );
}