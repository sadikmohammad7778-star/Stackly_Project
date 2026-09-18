import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
    FiPlus,
    FiEdit,
    FiTrash2,
    FiEye,
    FiSearch,
    FiDownload,
} from "react-icons/fi";

import SaleDetailsModal from "../components/forms/SaleDetailsModal";
import SaleEditModal from "../components/forms/SaleEditModal";

import "./Sales.css";

import {
    getSales,
    getSaleSummary,
    getSaleById,
    deleteSale,
    searchSales,
    downloadInvoicePDF,
    downloadInvoiceCSV,
} from "../api/salesApi";

import SaleModal from "../components/forms/SaleModal";


export default function Sales() {

    const [sales, setSales] = useState([]);

    const [summary, setSummary] = useState({
        total_sales: 0,
        total_revenue: 0,
        average_order_value: 0,
    });

    const [openModal, setOpenModal] = useState(false);

    const [loading, setLoading] = useState(true);

    const [search, setSearch] = useState("");

    const [paymentMethod, setPaymentMethod] = useState("");

    const [status, setStatus] = useState("");

    const [sort, setSort] = useState("date");

    const [order, setOrder] = useState("desc");

    const [error, setError] = useState("");
    
    const [selectedSale, setSelectedSale] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);

    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(7);

    const [searchParams] = useSearchParams();


    // ========================================================
    // Load Sales
    // ========================================================

    useEffect(() => {
        loadSales();
        loadSummary();
    }, []);

    useEffect(() => {
        const saleId = searchParams.get("sale_id");

        if (saleId) {
            handleView(Number(saleId));
        }
    }, [searchParams]);


    const loadSales = async () => {
        try {
            setLoading(true);
            setError("");

            const data = await getSales();

            setSales(data);
            setCurrentPage(1);

        } catch (error) {
            console.error(
                "Error loading sales:",
                error
            );

            setError(
                "Failed to load sales."
            );

        } finally {
            setLoading(false);
        }
    };

    // ========================================================
    // Load Summary
    // ========================================================

    const loadSummary = async () => {

        try {

            const data = await getSaleSummary();

            setSummary(data);

        } catch (error) {

            console.error(
                "Error loading sales summary:",
                error
            );

        }
    };


    // ========================================================
    // Search / Filter
    // ========================================================

    const handleSearch = async () => {

        try {

            setLoading(true);
            setError("");

            const data = await searchSales({
                keyword: search,
                payment_method: paymentMethod,
                status: status,
                sort: sort,
                order: order,
            });

            setSales(data);
            setCurrentPage(1);

        } catch (error) {

            console.error(
                "Error searching sales:",
                error
            );

            setError(
                "Failed to search sales."
            );

        } finally {

            setLoading(false);

        }
    };


    // ========================================================
    // Delete Sale
    // ========================================================

    const handleDelete = async (id) => {

        const confirmed = window.confirm(
            "Are you sure you want to delete this sale?"
        );

        if (!confirmed) return;

        try {

            await deleteSale(id);

            setCurrentPage(1);

            await loadSales();
            await loadSummary();

        } catch (error) {

            console.error(
                "Error deleting sale:",
                error
            );

            setError(
                "Failed to delete sale."
            );

        }
    };


    const handleView = async (id) => {
      try {
          const data = await getSaleById(id);

          setSelectedSale(data);
          setShowDetails(true);

      } catch (error) {
          console.error("Failed to load sale:", error);

          alert(
              error.response?.data?.detail ||
              "Failed to load sale details."
          );
      }
    };

    const handleEdit = async (id) => {
        try {
            const data = await getSaleById(id);

            setSelectedSale(data);
            setShowEditModal(true);
        } catch (error) {
            console.error("Failed to load sale for editing:", error);

            alert(
                error.response?.data?.detail ||
                "Failed to load sale."
            );
        }
    };

    
      


      // ========================================================
      // PDF Download
      // ========================================================

      const handlePDF = async (id) => {

          try {

              const blob =
                  await downloadInvoicePDF(id);

              const url =
                  window.URL.createObjectURL(blob);

              const link =
                  document.createElement("a");

              link.href = url;

              link.download =
                  `invoice-${id}.pdf`;

              document.body.appendChild(link);

              link.click();

              link.remove();

              window.URL.revokeObjectURL(url);

          } catch (error) {

              console.error(
                  "Error downloading PDF:",
                  error
              );

              setError(
                  "Failed to download invoice PDF."
              );

          }
      };


    // ========================================================
    // CSV Download
    // ========================================================

    const handleCSV = async (id) => {

        try {

            const blob =
                await downloadInvoiceCSV(id);

            const url =
                window.URL.createObjectURL(blob);

            const link =
                document.createElement("a");

            link.href = url;

            link.download =
                `invoice-${id}.csv`;

            document.body.appendChild(link);

            link.click();

            link.remove();

            window.URL.revokeObjectURL(url);

        } catch (error) {

            console.error(
                "Error downloading CSV:",
                error
            );

            setError(
                "Failed to download invoice CSV."
            );

        }
    };


    // ========================================================
    // Clear Filters
    // ========================================================

    const clearFilters = async () => {

        setSearch("");
        setPaymentMethod("");
        setStatus("");
        setSort("date");
        setOrder("desc");

        setCurrentPage(1);

        await loadSales();
    };

    const totalPages = Math.ceil(
      sales.length / itemsPerPage
    );

    const startIndex =
      (currentPage - 1) * itemsPerPage;

    const currentSales = sales.slice(
      startIndex,
      startIndex + itemsPerPage
    );


    


    return (
        <div className="sales-page">

            {/* =================================================
                Header
            ================================================= */}

            <div className="sales-header">

                <div>
                    <h2>Sales Management</h2>

                    <p>
                        Manage sales, invoices and
                        transactions
                    </p>
                </div>

                <button
                    className="add-sale-btn"
                    onClick={() =>
                        setOpenModal(true)
                    }
                >
                    <FiPlus />
                    Create Sale
                </button>

            </div>


            {/* =================================================
                Summary Cards
            ================================================= */}

            <div className="sales-summary">

                <div className="summary-card">

                    <span>Total Sales</span>

                    <h3>
                        {summary.total_sales}
                    </h3>

                </div>


                <div className="summary-card">

                    <span>Total Revenue</span>

                    <h3>
                        ₹
                        {Number(
                            summary.total_revenue || 0
                        ).toLocaleString("en-IN")}
                    </h3>

                </div>


                <div className="summary-card">

                    <span>
                        Average Order Value
                    </span>

                    <h3>
                        ₹
                        {Number(
                            summary.average_order_value || 0
                        ).toLocaleString("en-IN")}
                    </h3>

                </div>

            </div>


            {/* =================================================
                Error
            ================================================= */}

            {error && (
                <div className="sales-error">
                    {error}
                </div>
            )}


            {/* =================================================
                Filters
            ================================================= */}

            <div className="sales-filters">

                <div className="search-box">

                    <FiSearch />

                    <input
                        type="text"
                        placeholder="Search invoice or customer..."
                        value={search}
                        onChange={(e) =>
                            setSearch(e.target.value)
                        }
                        onKeyDown={(e) => {
                            if (e.key === "Enter") {
                                handleSearch();
                            }
                        }}
                    />

                </div>


                <select
                    value={paymentMethod}
                    onChange={(e) =>
                        setPaymentMethod(
                            e.target.value
                        )
                    }
                >
                    <option value="">
                        All Payments
                    </option>

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


                <select
                    value={status}
                    onChange={(e) =>
                        setStatus(e.target.value)
                    }
                >
                    <option value="">
                        All Status
                    </option>

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


                <select
                    value={sort}
                    onChange={(e) =>
                        setSort(e.target.value)
                    }
                >
                    <option value="date">
                        Sort by Date
                    </option>

                    <option value="total">
                        Sort by Amount
                    </option>

                    <option value="customer">
                        Sort by Customer
                    </option>

                </select>


                <select
                    value={order}
                    onChange={(e) =>
                        setOrder(e.target.value)
                    }
                >
                    <option value="desc">
                        Descending
                    </option>

                    <option value="asc">
                        Ascending
                    </option>

                </select>


                <button
                    className="filter-btn"
                    onClick={handleSearch}
                    disabled={loading}
                >
                    {loading ? "Searching..." : "Search"}
                </button>


                <button
                    className="clear-btn"
                    onClick={clearFilters}
                >
                    Clear
                </button>

            </div>


            {/* =================================================
                Sales Table
            ================================================= */}

            <div className="sales-table-card">

                <div className="table-header">

                    <h3>
                        Sales Transactions
                    </h3>

                    <span>
                        {sales.length} Records
                    </span>

                </div>


                {loading ? (

                    <div className="sales-loading">

                        <div className="sales-spinner"></div>

                        <span>
                            Loading sales...
                        </span>

                    </div>

                ) : sales.length === 0 ? (

                    <div className="sales-empty">
                        <h3>
                            No Sales Found
                        </h3>

                        <p>
                            There are no sales matching
                            your search or filters.
                        </p>
                    </div>

                ) : (

                    <div className="table-wrapper">

                        <table>

                            <thead>

                                <tr>

                                    <th>
                                        Invoice
                                    </th>

                                    <th>
                                        Customer
                                    </th>

                                    <th>
                                        Date
                                    </th>

                                    <th>
                                        Items
                                    </th>

                                    <th>
                                        Payment
                                    </th>

                                    <th>
                                        Total
                                    </th>

                                    <th>
                                        Status
                                    </th>

                                    <th>
                                        Actions
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {currentSales.map(
                                  (sale) => (

                                        <tr
                                            key={sale.id}
                                        >

                                            <td>
                                                <strong>
                                                    {
                                                        sale.invoice_number
                                                    }
                                                </strong>
                                            </td>


                                            <td>
                                                {
                                                    sale.customer_name
                                                }
                                            </td>


                                            <td>
                                                {new Date(
                                                    sale.sale_date
                                                ).toLocaleDateString(
                                                    "en-IN"
                                                )}
                                            </td>


                                            <td>
                                                {
                                                    sale.items?.length ||
                                                    0
                                                }
                                            </td>


                                            <td>
                                                {
                                                    sale.payment_method
                                                }
                                            </td>


                                            <td>
                                                <strong>
                                                    ₹
                                                    {Number(
                                                        sale.total_amount
                                                    ).toLocaleString(
                                                        "en-IN"
                                                    )}
                                                </strong>
                                            </td>


                                            <td>

                                                <span
                                                    className={`status-badge ${sale.status?.toLowerCase()}`}
                                                >
                                                    {
                                                        sale.status
                                                    }
                                                </span>

                                            </td>


                                            <td>

                                                <div className="action-buttons">

                                                    <button
                                                        className="view-btn"
                                                        onClick={() => handleView(sale.id)}
                                                        title="View Sale"
                                                    >
                                                        👁
                                                    </button>

                                                    <button
                                                        className="edit"
                                                        onClick={() => handleEdit(sale.id)}
                                                        title="Edit Sale"
                                                    >
                                                        <FiEdit />
                                                    </button>


                                                    <button
                                                        title="Download PDF"
                                                        className="pdf-btn"
                                                        onClick={() =>
                                                            handlePDF(
                                                                sale.id
                                                            )
                                                        }
                                                    >
                                                        <FiDownload />
                                                    </button>


                                                    <button
                                                        title="Download CSV"
                                                        className="csv-btn"
                                                        onClick={() =>
                                                            handleCSV(
                                                                sale.id
                                                            )
                                                        }
                                                    >
                                                        CSV
                                                    </button>


                                                    <button
                                                        title="Delete Sale"
                                                        className="delete-btn"
                                                        onClick={() =>
                                                            handleDelete(
                                                                sale.id
                                                            )
                                                        }
                                                    >
                                                        <FiTrash2 />
                                                    </button>

                                                </div>

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                        {totalPages > 1 && (
                          <div className="pagination">

                              <button
                                  onClick={() =>
                                      setCurrentPage((prev) =>
                                          Math.max(prev - 1, 1)
                                      )
                                  }
                                  disabled={currentPage === 1}
                              >
                                  Previous
                              </button>

                              <span>
                                  Page {currentPage} of {totalPages}
                              </span>

                              <button
                                  onClick={() =>
                                      setCurrentPage((prev) =>
                                          Math.min(
                                              prev + 1,
                                              totalPages
                                          )
                                      )
                                  }
                                  disabled={currentPage === totalPages}
                              >
                                  Next
                              </button>

                          </div>
                      )}

                    </div>

                )}

            </div>


            {/* =================================================
                Create Sale Modal
            ================================================= */}

            <SaleModal
                isOpen={openModal}
                onClose={() =>
                    setOpenModal(false)
                }
                onSuccess={async () => {

                    setOpenModal(false);

                    setCurrentPage(1);

                    await loadSales();
                    await loadSummary();

                }}
            />
            <SaleDetailsModal
                sale={selectedSale}
                isOpen={showDetails}
                onClose={() => {
                    setShowDetails(false);
                    setSelectedSale(null);
                }}
            />

            <SaleEditModal
                sale={selectedSale}
                isOpen={showEditModal}
                onClose={() => {
                    setShowEditModal(false);
                    setSelectedSale(null);
                }}
                onSuccess={async () => {
                    setShowEditModal(false);
                    setSelectedSale(null);

                    setCurrentPage(1);

                    await loadSales();
                    await loadSummary();
                }}
            />

        </div>
    );
}