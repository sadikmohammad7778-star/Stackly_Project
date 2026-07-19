import { useEffect, useState } from "react";
import { FiPlus, FiEdit, FiTrash2 } from "react-icons/fi";

import "./Companies.css";

import {
  getSales,
  deleteSale,
} from "../api/salesApi";

import SaleModal from "../components/forms/SaleModal";

export default function Sales() {
  const [sales, setSales] = useState([]);
  const [openModal, setOpenModal] = useState(false);

  useEffect(() => {
    loadSales();
  }, []);

  const loadSales = async () => {
    try {
      const data = await getSales();
      setSales(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this sale?")) return;

    try {
      await deleteSale(id);
      loadSales();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="companies-page">

      <div className="companies-header">
        <h2>Sales</h2>

        <button onClick={() => setOpenModal(true)}>
          <FiPlus />
          Add Sale
        </button>
      </div>

      <div className="table-card">

        <table>

          <thead>
            <tr>
              <th>Invoice</th>
              <th>Customer</th>
              <th>Channel</th>
              <th>Payment</th>
              <th>Total</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>

            {sales.length > 0 ? (
              sales.map((sale) => (
                <tr key={sale.id}>
                  <td>{sale.invoice_number}</td>
                  <td>{sale.customer_name}</td>
                  <td>{sale.sales_channel}</td>
                  <td>{sale.payment_method}</td>
                  <td>₹{sale.total_amount}</td>
                  <td>
                    {new Date(sale.sale_date).toLocaleDateString()}
                  </td>

                  <td>
                    <button className="edit">
                      <FiEdit />
                    </button>

                    <button
                      className="delete"
                      onClick={() => handleDelete(sale.id)}
                    >
                      <FiTrash2 />
                    </button>
                  </td>

                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="7"
                  style={{ textAlign: "center" }}
                >
                  No Sales Found
                </td>
              </tr>
            )}

          </tbody>

        </table>

      </div>

      <SaleModal
        isOpen={openModal}
        onClose={() => setOpenModal(false)}
        onSuccess={loadSales}
      />

    </div>
  );
}