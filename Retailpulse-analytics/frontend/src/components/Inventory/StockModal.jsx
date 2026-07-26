import { useState } from "react";
import {
  addStock,
  removeStock,
  adjustStock,
} from "../../api/inventoryApi";

import "./StockModal.css";

export default function StockModal({
  isOpen,
  onClose,
  onSuccess,
}) {
  const [formData, setFormData] = useState({
    product_id: "",
    quantity: "",
    reason: "",
    remarks: "",
  });

  const [action, setAction] = useState("add");

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    try {
      if (action === "add") {
        await addStock(formData);
      } else if (action === "remove") {
        await removeStock(formData);
      } else {
        await adjustStock(formData);
      }

      alert("Stock updated successfully!");

      onSuccess();
      onClose();
    } catch (error) {
      console.error(error);
      alert("Failed to update stock.");
    }
  };

  return (
    <div className="modal-overlay">
      <div className="stock-modal">

        <h2>Stock Management</h2>

        <select
          value={action}
          onChange={(e) => setAction(e.target.value)}
        >
          <option value="add">Add Stock</option>
          <option value="remove">Remove Stock</option>
          <option value="adjust">Adjust Stock</option>
        </select>

        <input
          type="number"
          name="product_id"
          placeholder="Product ID"
          value={formData.product_id}
          onChange={handleChange}
        />

        <input
          type="number"
          name="quantity"
          placeholder="Quantity"
          value={formData.quantity}
          onChange={handleChange}
        />

        <input
          type="text"
          name="reason"
          placeholder="Reason"
          value={formData.reason}
          onChange={handleChange}
        />

        <textarea
          name="remarks"
          placeholder="Remarks"
          value={formData.remarks}
          onChange={handleChange}
        />

        <div className="modal-buttons">
          <button onClick={handleSubmit}>
            Save
          </button>

          <button onClick={onClose}>
            Cancel
          </button>
        </div>

      </div>
    </div>
  );
}