import "./SearchFilter.css";

export default function SearchFilter({
  search,
  setSearch,
  status,
  setStatus,
  onSearch,
}) {
  return (
    <div className="search-filter">
      <input
        type="text"
        placeholder="Search by Product or SKU..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <select
        value={status}
        onChange={(e) => setStatus(e.target.value)}
      >
        <option value="">All Status</option>
        <option value="In Stock">In Stock</option>
        <option value="Low Stock">Low Stock</option>
        <option value="Out of Stock">Out of Stock</option>
      </select>

      <button onClick={onSearch}>Search</button>
    </div>
  );
}