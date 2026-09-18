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
    inventory,
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
            const productId = Number(formData.product_id);
            const quantity = Number(formData.quantity);
            const reason = formData.reason.trim();
            const remarks = formData.remarks.trim() || null;

            if (!productId || productId <= 0) {
                alert("Please select a product.");
                return;
            }

            if (!quantity || quantity <= 0) {
                alert("Please enter a valid quantity.");
                return;
            }

            if (!reason) {
                alert("Please enter a reason.");
                return;
            }

            const data = {
                product_id: productId,
                quantity,
                reason,
                remarks,
            };

            console.log("Stock update data:", data);

            if (action === "add") {
                await addStock(data);
            } else if (action === "remove") {
                await removeStock(data);
            } else {
                await adjustStock(data);
            }

            alert("Stock updated successfully!");

            onSuccess();
            onClose();

            setFormData({
                product_id: "",
                quantity: "",
                reason: "",
                remarks: "",
            });
        } catch (error) {
            console.error("Stock update error:", error);

            const message =
                error.response?.data?.detail ||
                "Failed to update stock.";

            alert(message);
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

                <select
                    name="product_id"
                    value={formData.product_id}
                    onChange={handleChange}
                >
                    <option value="">Select Product</option>

                    {inventory.map((item) => {
                        const productId =
                            item.product_id ?? item.product?.id;

                        return (
                            <option
                                key={item.id}
                                value={productId}
                            >
                                {item.product?.name} - Stock:{" "}
                                {item.available_stock}
                            </option>
                        );
                    })}
                </select>

                <input
                    type="number"
                    name="quantity"
                    placeholder="Quantity"
                    min="1"
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