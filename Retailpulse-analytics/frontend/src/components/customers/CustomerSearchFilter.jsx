import { useState } from "react";

export default function CustomerSearchFilter({
  onSearch,
  onFilter,
}) {
  const [search, setSearch] = useState("");

  const [filters, setFilters] = useState({
    segment: "",
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
    const { name, value } = e.target;

    const updatedFilters = {
      ...filters,
      [name]: value,
    };

    setFilters(updatedFilters);

    onFilter(updatedFilters);
  };

  return (
    <div className="customer-search-filter">

      <input
        type="text"
        placeholder="Search Customer..."
        value={search}
        onChange={handleSearch}
      />

      <select
        name="segment"
        value={filters.segment}
        onChange={handleFilterChange}
      >
        <option value="">All Segments</option>
        <option value="New">New</option>
        <option value="Regular">Regular</option>
        <option value="Loyal">Loyal</option>
        <option value="VIP">VIP</option>
      </select>

      <select
        name="status"
        value={filters.status}
        onChange={handleFilterChange}
      >
        <option value="">All Status</option>
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

    </div>
  );
}