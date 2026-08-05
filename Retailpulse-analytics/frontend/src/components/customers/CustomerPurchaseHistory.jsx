import { useEffect, useState } from "react";

import { customerPurchaseHistory } from "../../api/customerApi";

export default function CustomerPurchaseHistory({
  customerId,
}) {

  const [history, setHistory] = useState([]);

  useEffect(() => {

    loadHistory();

  }, [customerId]);

  const loadHistory = async () => {

    try {

      const response = await customerPurchaseHistory(
        customerId
      );

      setHistory(response.data);

    } catch (error) {

      console.error(error);

    }

  };

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

                <td>{sale.created_at}</td>

                <td>₹ {sale.total_amount}</td>

                <td>{sale.payment_method}</td>

              </tr>

            ))

          )}

        </tbody>

      </table>

    </div>

  );

}