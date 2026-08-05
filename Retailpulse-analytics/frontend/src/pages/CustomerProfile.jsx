import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getCustomer } from "../api/customerApi";
import CustomerPurchaseHistory from "../components/customers/CustomerPurchaseHistory";
import CustomerTimeline from "../components/customers/CustomerTimeline";


export default function CustomerProfile() {
  const { id } = useParams();

  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadCustomer = async () => {
    try {
      const response = await getCustomer(id);
      setCustomer(response.data);
    } catch (error) {
      console.error("Error loading customer:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomer();
  }, [id]);

  if (loading) {
    return <h2>Loading...</h2>;
  }

  if (!customer) {
    return <h2>Customer not found.</h2>;
  }

  return (
    <div className="customer-profile">

      <h2>Customer Profile</h2>

      <hr />

      {/* Personal Information */}

      <h3>Personal Information</h3>

      <p>
        <strong>Name:</strong> {customer.full_name}
      </p>

      <p>
        <strong>Gender:</strong> {customer.gender || "-"}
      </p>

      <p>
        <strong>Date of Birth:</strong>{" "}
        {customer.date_of_birth || "-"}
      </p>

      <hr />

      {/* Contact Information */}

      <h3>Contact Information</h3>

      <p>
        <strong>Email:</strong> {customer.email}
      </p>

      <p>
        <strong>Phone:</strong> {customer.phone}
      </p>

      <hr />

      {/* Address */}

      <h3>Address</h3>

      <p>
        <strong>Address:</strong> {customer.address || "-"}
      </p>

      <p>
        <strong>City:</strong> {customer.city || "-"}
      </p>

      <p>
        <strong>State:</strong> {customer.state || "-"}
      </p>

      <p>
        <strong>Country:</strong> {customer.country || "-"}
      </p>

      <hr />

      {/* Business Information */}

      <h3>Business Information</h3>

      <p>
        <strong>Customer Type:</strong>{" "}
        {customer.customer_type}
      </p>

      <p>
        <strong>Status:</strong> {customer.status}
      </p>

      <p>
        <strong>Preferred Sales Channel:</strong>{" "}
        {customer.preferred_sales_channel || "-"}
      </p>

      <hr />

      {/* Purchase Summary */}

      <h3>Purchase Summary</h3>

      <p>
        <strong>Total Orders:</strong>{" "}
        {customer.purchase_summary?.total_orders ?? 0}
      </p>

      <p>
        <strong>Total Revenue:</strong> ₹{" "}
        {customer.purchase_summary?.total_revenue ?? 0}
      </p>

      <p>
        <strong>Average Order Value:</strong> ₹{" "}
        {customer.purchase_summary?.average_order_value ?? 0}
      </p>

      <p>
        <strong>Total Products Purchased:</strong>{" "}
        {customer.purchase_summary?.total_products_purchased ?? 0}
      </p>

      <p>
        <strong>Purchase Frequency:</strong>{" "}
        {customer.purchase_summary?.purchase_frequency ?? 0}
      </p>

      <p>
        <strong>First Purchase:</strong>{" "}
        {customer.purchase_summary?.first_purchase_date || "-"}
      </p>

      <p>
        <strong>Last Purchase:</strong>{" "}
        {customer.purchase_summary?.last_purchase_date || "-"}
      </p>

      <hr />

      {/* Purchase History */}

      <CustomerPurchaseHistory customerId={customer.id} />

      <hr />

      <CustomerTimeline customerId={customer.id} />

    </div>
  );
}