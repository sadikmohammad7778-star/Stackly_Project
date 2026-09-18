import { useNavigate } from "react-router-dom";
import { deleteCustomer } from "../../api/customerApi";

export default function CustomerTable({
  customers,
  reload,
  setSelectedCustomer,
}) {
  const navigate = useNavigate();

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this customer?"
    );

    if (!confirmDelete) return;

    try {
      await deleteCustomer(id);
      await reload();
    } catch (error) {
      console.error(error);
      alert("Unable to delete customer.");
    }
  };

  return (
    <table className="customer-table">
      <thead>
        <tr>
          <th>Customer ID</th>
          <th>Customer Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Segment</th>
          <th>Total Orders</th>
          <th>Total Spend</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        {customers.length === 0 ? (
          <tr>
            <td colSpan="9">No Customers Found</td>
          </tr>
        ) : (
          customers.map((customer) => (
            <tr key={customer.id}>
              <td>{customer.customer_id}</td>

              <td>
                <button
                  type="button"
                  onClick={() =>
                    navigate(`/customers/${customer.id}`)
                  }
                >
                  {customer.first_name} {customer.last_name}
                </button>
              </td>

              <td>{customer.email}</td>

              <td>{customer.phone}</td>

              <td>
                <span
                  className={`badge ${
                    (customer.segment || "new").toLowerCase()
                  }`}
                >
                  {customer.segment || "New"}
                </span>
              </td>

              <td>{customer.total_orders || 0}</td>

              <td>
                ₹{Number(customer.total_spend || 0).toFixed(2)}
              </td>

              <td>
                <span
                  className={
                    customer.status === "Active"
                      ? "status-active"
                      : "status-inactive"
                  }
                >
                  {customer.status}
                </span>
              </td>

              <td>
                <button
                  type="button"
                  className="edit-btn"
                  onClick={() =>
                    setSelectedCustomer(customer)
                  }
                >
                  Edit
                </button>

                <button
                  type="button"
                  className="delete-btn"
                  onClick={() =>
                    handleDelete(customer.id)
                  }
                >
                  Delete
                </button>
              </td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}