import "./SaleDetailsModal.css";

import { downloadInvoicePDF } from "../../api/salesApi";

export default function SaleDetailsModal({
    sale,
    isOpen,
    onClose,
}) {

    // --------------------------------------------------
    // Don't render when modal is closed
    // --------------------------------------------------

    if (!isOpen || !sale) {
        return null;
    }


    // --------------------------------------------------
    // Calculate Subtotal
    // --------------------------------------------------

    const subtotal =
        sale.items?.reduce(
            (sum, item) =>
                sum +
                Number(item.quantity || 0) *
                Number(item.unit_price || 0),
            0
        ) || 0;


    // --------------------------------------------------
    // Download Invoice PDF
    // --------------------------------------------------

    const handleDownloadPDF = async () => {

        try {

            const blob =
                await downloadInvoicePDF(sale.id);

            const url =
                window.URL.createObjectURL(blob);

            const link =
                document.createElement("a");

            link.href = url;

            link.download =
                `Invoice-${sale.id}.pdf`;

            document.body.appendChild(link);

            link.click();

            link.remove();

            window.URL.revokeObjectURL(url);

        } catch (error) {

            console.error(
                "Failed to download invoice:",
                error
            );

            alert(
                error.response?.data?.detail ||
                "Failed to download invoice."
            );
        }
    };


    // --------------------------------------------------
    // Render
    // --------------------------------------------------

    return (

        <div className="sale-details-overlay">

            <div className="sale-details-modal">


                {/* ==================================================
                    Header
                ================================================== */}

                <div className="sale-details-header">

                    <div>

                        <h2>
                            Sale Details
                        </h2>

                        <p>
                            Invoice:{" "}

                            <strong>
                                {sale.invoice_number}
                            </strong>
                        </p>

                    </div>


                    <button
                        type="button"
                        className="sale-details-close"
                        onClick={onClose}
                        title="Close"
                    >
                        ×
                    </button>

                </div>


                {/* ==================================================
                    Sale Information
                ================================================== */}

                <div className="sale-details-section">

                    <h3>
                        Sale Information
                    </h3>


                    <div className="sale-details-grid">


                        <div>

                            <span>
                                Invoice
                            </span>

                            <strong>
                                {sale.invoice_number}
                            </strong>

                        </div>


                        <div>

                            <span>
                                Customer
                            </span>

                            <strong>
                                {sale.customer_name ||
                                    "N/A"}
                            </strong>

                        </div>


                        <div>

                            <span>
                                Date
                            </span>

                            <strong>
                                {sale.sale_date
                                    ? new Date(
                                        sale.sale_date
                                    ).toLocaleString(
                                        "en-IN"
                                    )
                                    : "N/A"}
                            </strong>

                        </div>


                        <div>

                            <span>
                                Sales Channel
                            </span>

                            <strong>
                                {sale.sales_channel ||
                                    "N/A"}
                            </strong>

                        </div>


                        <div>

                            <span>
                                Payment Method
                            </span>

                            <strong>
                                {sale.payment_method ||
                                    "N/A"}
                            </strong>

                        </div>


                        <div>

                            <span>
                                Status
                            </span>

                            <strong
                                className={`sale-status ${
                                    sale.status?.toLowerCase() || ""
                                }`}
                            >
                                {sale.status ||
                                    "N/A"}
                            </strong>

                        </div>

                    </div>

                </div>


                {/* ==================================================
                    Customer Information
                ================================================== */}

                <div className="sale-details-section">

                    <h3>
                        Customer
                    </h3>


                    <div className="customer-details">

                        <strong>
                            {sale.customer_name ||
                                "N/A"}
                        </strong>

                        <span>
                            Customer ID:{" "}
                            {sale.customer_id ||
                                "N/A"}
                        </span>

                    </div>

                </div>


                {/* ==================================================
                    Products
                ================================================== */}

                <div className="sale-details-section">

                    <h3>
                        Products
                    </h3>


                    <div className="sale-items-table">

                        <table>

                            <thead>

                                <tr>

                                    <th>
                                        Product
                                    </th>

                                    <th>
                                        SKU
                                    </th>

                                    <th>
                                        Qty
                                    </th>

                                    <th>
                                        Unit Price
                                    </th>

                                    <th>
                                        Discount
                                    </th>

                                    <th>
                                        Tax
                                    </th>

                                    <th>
                                        Total
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {sale.items &&
                                sale.items.length > 0 ? (

                                    sale.items.map(
                                        (item) => (

                                            <tr
                                                key={
                                                    item.id
                                                }
                                            >

                                                <td>
                                                    {
                                                        item.product_name ||
                                                        "Unknown Product"
                                                    }
                                                </td>


                                                <td>
                                                    {
                                                        item.sku ||
                                                        "N/A"
                                                    }
                                                </td>


                                                <td>
                                                    {
                                                        item.quantity
                                                    }
                                                </td>


                                                <td>
                                                    ₹
                                                    {Number(
                                                        item.unit_price ||
                                                        0
                                                    ).toLocaleString(
                                                        "en-IN"
                                                    )}
                                                </td>


                                                <td>
                                                    ₹
                                                    {Number(
                                                        item.discount ||
                                                        0
                                                    ).toLocaleString(
                                                        "en-IN"
                                                    )}
                                                </td>


                                                <td>
                                                    ₹
                                                    {Number(
                                                        item.tax ||
                                                        0
                                                    ).toLocaleString(
                                                        "en-IN"
                                                    )}
                                                </td>


                                                <td>

                                                    <strong>
                                                        ₹
                                                        {Number(
                                                            item.total ||
                                                            0
                                                        ).toLocaleString(
                                                            "en-IN"
                                                        )}
                                                    </strong>

                                                </td>

                                            </tr>

                                        )
                                    )

                                ) : (

                                    <tr>

                                        <td
                                            colSpan="7"
                                            style={{
                                                textAlign:
                                                    "center",
                                            }}
                                        >
                                            No products found.
                                        </td>

                                    </tr>

                                )}

                            </tbody>

                        </table>

                    </div>

                </div>


                {/* ==================================================
                    Billing Summary
                ================================================== */}

                <div className="sale-billing">


                    {/* Subtotal */}

                    <div>

                        <span>
                            Subtotal
                        </span>

                        <strong>
                            ₹
                            {subtotal.toLocaleString(
                                "en-IN"
                            )}
                        </strong>

                    </div>


                    {/* Discount */}

                    <div>

                        <span>
                            Discount
                        </span>

                        <strong>
                            - ₹
                            {Number(
                                sale.discount || 0
                            ).toLocaleString(
                                "en-IN"
                            )}
                        </strong>

                    </div>


                    {/* Tax */}

                    <div>

                        <span>
                            Tax
                        </span>

                        <strong>
                            + ₹
                            {Number(
                                sale.tax || 0
                            ).toLocaleString(
                                "en-IN"
                            )}
                        </strong>

                    </div>


                    {/* Grand Total */}

                    <div className="grand-total">

                        <span>
                            Grand Total
                        </span>

                        <strong>
                            ₹
                            {Number(
                                sale.total_amount || 0
                            ).toLocaleString(
                                "en-IN"
                            )}
                        </strong>

                    </div>

                </div>


                {/* ==================================================
                    Footer
                ================================================== */}

                <div className="sale-details-footer">


                    <button
                        type="button"
                        onClick={handleDownloadPDF}
                    >
                        Download Invoice
                    </button>


                    <button
                        type="button"
                        onClick={onClose}
                    >
                        Close
                    </button>

                </div>


            </div>

        </div>
    );
}