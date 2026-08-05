import { useState } from "react";

export default function CustomerSearchFilter({
  onSearch,
  onFilter,
}) {
  const [search, setSearch] = useState("");

  const [filters, setFilters] = useState({
    customer_type: "",
    status: "",
    city: "",
    state: "",
    country: "",
  });

  const handleSearch = (e) => {
    const value = e.target.value;

    setSearch(value);
    onSearch(value);
  };

  const handleFilterChange = (e) => {
    const updatedFilters = {
      ...filters,
      [e.target.name]: e.target.value,
    };

    setFilters(updatedFilters);
    onFilter(updatedFilters);
  };

  return (
    <>
      <input
        type="text"
        placeholder="Search Customer..."
        value={search}
        onChange={handleSearch}
      />

      <select
        name="customer_type"
        value={filters.customer_type}
        onChange={handleFilterChange}
      >
        <option value="">Customer Type</option>
        <option value="Retail">Retail</option>
        <option value="Wholesale">Wholesale</option>
        <option value="Corporate">Corporate</option>
      </select>

      <select
        name="status"
        value={filters.status}
        onChange={handleFilterChange}
      >
        <option value="">Status</option>
        <option value="Active">Active</option>
        <option value="Inactive">Inactive</option>
      </select>

      <input
        type="text"
        name="city"
        placeholder="City"
        value={filters.city}
        onChange={handleFilterChange}
      />

      <input
        type="text"
        name="state"
        placeholder="State"
        value={filters.state}
        onChange={handleFilterChange}
      />

      <input
        type="text"
        name="country"
        placeholder="Country"
        value={filters.country}
        onChange={handleFilterChange}
      />
    </>
  );
}