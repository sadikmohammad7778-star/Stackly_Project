import { useEffect, useState } from "react";
import { updateSale } from "../../api/salesApi";
import { getCustomers } from "../../api/customerApi";
import "./CompanyModal.css";

export default function SaleEditModal({
    sale,
    isOpen,
    onClose,
    onSuccess,
}) {
    const [customers, setCustomers] = useState([]);
    const [loading, setLoading] = useState(false);

    const [formData, setFormData] = useState({
        customer_id: "",
        sales_channel: "",
        payment_method: "",
        discount: 0,
        tax: 0,
        status: "Paid",
    });

    useEffect(() => {
        if (sale) {
            setFormData({
                customer_id: sale.customer_id || "",
                sales_channel: sale.sales_channel || "",
                payment_method: sale.payment_method || "",
                discount: sale.discount || 0,
                tax: sale.tax || 0,
                status: sale.status || "Paid",
            });
        }
    }, [sale]);

    useEffect(() => {
        if (isOpen) {
            loadCustomers();
        }
    }, [isOpen]);

    const loadCustomers = async () => {
        try {
            const data = await getCustomers();
            setCustomers(data || []);
        } catch (error) {
            console.error(
                "Failed to load customers:",
                error
            );
        }
    };

    if (!isOpen || !sale) {
        return null;
    }

    const handleChange = (e) => {
        const { name, value } = e.target;

        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setLoading(true);

            await updateSale(sale.id, {
                customer_id: Number(formData.customer_id),
                sales_channel: formData.sales_channel,
                payment_method: formData.payment_method,
                discount: Number(formData.discount),
                tax: Number(formData.tax),
                status: formData.status,
            });

            alert("Sale updated successfully.");

            await onSuccess();

        } catch (error) {
            console.error(
                "Failed to update sale:",
                error
            );

            alert(
                error.response?.data?.detail ||
                "Failed to update sale."
            );

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay">

            <div className="modal">

                {/* Header */}

                <div className="modal-header">

                    <div>
                        <h2>Edit Sale</h2>

                        <p>
                            Invoice:{" "}
                            <strong>
                                {sale.invoice_number}
                            </strong>
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={onClose}
                        disabled={loading}
                    >
                        ✕
                    </button>

                </div>

                <form onSubmit={handleSubmit}>

                    <div className="form-grid">

                        {/* Customer */}

                        <div className="form-group">

                            <label>
                                Customer
                            </label>

                            <select
                                name="customer_id"
                                value={formData.customer_id}
                                onChange={handleChange}
                                disabled={loading}
                                required
                            >
                                <option value="">
                                    Select Customer
                                </option>

                                {customers.map(
                                    (customer) => (
                                        <option
                                            key={customer.id}
                                            value={customer.id}
                                        >
                                            {customer.first_name}{" "}
                                            {customer.last_name}
                                        </option>
                                    )
                                )}

                            </select>

                        </div>

                        {/* Sales Channel */}

                        <div className="form-group">

                            <label>
                                Sales Channel
                            </label>

                            <select
                                name="sales_channel"
                                value={formData.sales_channel}
                                onChange={handleChange}
                                disabled={loading}
                            >
                                <option value="Store">
                                    Store
                                </option>

                                <option value="Online">
                                    Online
                                </option>

                                <option value="Offline">
                                    Offline
                                </option>
                            </select>

                        </div>

                        {/* Payment */}

                        <div className="form-group">

                            <label>
                                Payment Method
                            </label>

                            <select
                                name="payment_method"
                                value={formData.payment_method}
                                onChange={handleChange}
                                disabled={loading}
                            >
                                <option value="Cash">
                                    Cash
                                </option>

                                <option value="Card">
                                    Card
                                </option>

                                <option value="UPI">
                                    UPI
                                </option>

                                <option value="Bank Transfer">
                                    Bank Transfer
                                </option>
                            </select>

                        </div>

                        {/* Status */}

                        <div className="form-group">

                            <label>
                                Status
                            </label>

                            <select
                                name="status"
                                value={formData.status}
                                onChange={handleChange}
                                disabled={loading}
                            >
                                <option value="Paid">
                                    Paid
                                </option>

                                <option value="Pending">
                                    Pending
                                </option>

                                <option value="Cancelled">
                                    Cancelled
                                </option>
                            </select>

                        </div>

                        {/* Discount */}

                        <div className="form-group">

                            <label>
                                Discount
                            </label>

                            <input
                                type="number"
                                name="discount"
                                min="0"
                                step="0.01"
                                value={formData.discount}
                                onChange={handleChange}
                                disabled={loading}
                            />

                        </div>

                        {/* Tax */}

                        <div className="form-group">

                            <label>
                                Tax
                            </label>

                            <input
                                type="number"
                                name="tax"
                                min="0"
                                step="0.01"
                                value={formData.tax}
                                onChange={handleChange}
                                disabled={loading}
                            />

                        </div>

                    </div>

                    {/* Buttons */}

                    <div className="modal-buttons">

                        <button
                            type="button"
                            onClick={onClose}
                            disabled={loading}
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            disabled={loading}
                        >
                            {loading
                                ? "Updating..."
                                : "Update Sale"}
                        </button>

                    </div>

                </form>

            </div>

        </div>
    );
}