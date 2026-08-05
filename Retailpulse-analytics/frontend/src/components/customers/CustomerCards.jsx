export default function CustomerCards({ dashboard }) {

  return (

    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4,1fr)",
        gap: "15px",
        marginBottom: "30px",
      }}
    >

      <div className="card">
        <h4>Total Customers</h4>
        <h2>{dashboard.total_customers || 0}</h2>
      </div>

      <div className="card">
        <h4>Active Customers</h4>
        <h2>{dashboard.active_customers || 0}</h2>
      </div>

      <div className="card">
        <h4>New Customers</h4>
        <h2>{dashboard.new_customers || 0}</h2>
      </div>

      <div className="card">
        <h4>Returning Customers</h4>
        <h2>{dashboard.returning_customers || 0}</h2>
      </div>

      <div className="card">
        <h4>Total Revenue</h4>
        <h2>{dashboard.total_revenue_generated || 0}</h2>
      </div>

      <div className="card">
        <h4>Average Spend</h4>
        <h2>{dashboard.average_customer_spend || 0}</h2>
      </div>

      <div className="card">
        <h4>Purchase Frequency</h4>
        <h2>{dashboard.average_purchase_frequency || 0}</h2>
      </div>

    </div>

  );

}