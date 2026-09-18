import { useEffect, useState } from "react";

import { customerPurchaseHistory } from "../../api/customerApi";

export default function CustomerPurchaseHistory({
  customerId,
}) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (customerId) {
      loadHistory();
    }
  }, [customerId]);

  const loadHistory = async () => {
    try {
      setLoading(true);

      const data = await customerPurchaseHistory(customerId);

      console.log("Purchase History:", data);

      setHistory(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(
        "Error loading purchase history:",
        error
      );

      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div>
        <h3>Purchase History</h3>
        <p>Loading purchase history...</p>
      </div>
    );
  }

  return (
    <div>
      <h3>Purchase History</h3>

      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Date</th>
            <th>Amount</th>
            <th>Payment Method</th>
          </tr>
        </thead>

        <tbody>
          {history.length === 0 ? (
            <tr>
              <td colSpan="4">
                No Purchase History
              </td>
            </tr>
          ) : (
            history.map((sale) => (
              <tr key={sale.id}>
                <td>{sale.id}</td>

                <td>
                  {sale.created_at
                    ? new Date(
                        sale.created_at
                      ).toLocaleDateString("en-IN")
                    : "-"}
                </td>

                <td>
                  ₹
                  {Number(
                    sale.total_amount || 0
                  ).toLocaleString("en-IN", {
                    minimumFractionDigits: 2,
                  })}
                </td>

                <td>
                  {sale.payment_method || "-"}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}