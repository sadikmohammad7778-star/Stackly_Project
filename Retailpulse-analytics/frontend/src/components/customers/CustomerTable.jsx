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

      reload();

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

          <th>Name</th>

          <th>Email</th>

          <th>Phone</th>

          <th>Customer Type</th>

          <th>Status</th>

          <th>Actions</th>

        </tr>

      </thead>

      <tbody>

        {customers.length === 0 ? (

          <tr>

            <td colSpan="7">
              No Customers Found
            </td>

          </tr>

        ) : (

          customers.map((customer) => (

            <tr key={customer.id}>

              <td>{customer.customer_id}</td>

              <td>

                <button
                  onClick={() =>
                    navigate(`/customers/${customer.id}`)
                  }
                >
                  {customer.full_name}
                </button>

              </td>

              <td>{customer.email}</td>

              <td>{customer.phone}</td>

              <td>{customer.customer_type}</td>

              <td>{customer.status}</td>

              <td>

                <button
                  onClick={() =>
                    setSelectedCustomer(customer)
                  }
                >
                  Edit
                </button>

                <button
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