import { useEffect, useMemo, useState } from "react";

import { getCategories } from "../../api/categoryApi";
import { createSale } from "../../api/salesApi";
import { getCompanies } from "../../api/companyApi";
import { getProducts } from "../../api/productApi";
import { getCustomers } from "../../api/customerApi";

import "./SaleModal.css";


export default function SaleModal({
    isOpen,
    onClose,
    onSuccess,
}) {

    // ========================================================
    // Data
    // ========================================================

    const [companies, setCompanies] = useState([]);
    const [customers, setCustomers] = useState([]);
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);

    // ========================================================
    // UI State
    // ========================================================

    const [loading, setLoading] = useState(false);
    const [loadingData, setLoadingData] = useState(false);
    const [error, setError] = useState("");
    const [quantityError, setQuantityError] = useState("");

    // ========================================================
    // Form
    // ========================================================

    const [formData, setFormData] = useState({
        company_id: "",
        customer_id: "",
        sales_channel: "Offline",
        payment_method: "Cash",

        discount: 0,
        tax: 0,

        items: [
            {
                product_id: "",
                category_id: "",
                quantity: "",
                unit_price: "",
                sku: "",
                available_stock: 0,
            },
        ],
    });


    // ========================================================
    // Load Dropdown Data
    // ========================================================

    useEffect(() => {

        if (!isOpen) {
            return;
        }

        loadDropdowns();

    }, [isOpen]);


    const loadDropdowns = async () => {

        try {

            setLoadingData(true);
            setError("");

            const [
                companyData,
                customerData,
                productData,
                categoryData,
            ] = await Promise.all([
                getCompanies(),
                getCustomers(),
                getProducts(),
                getCategories(),
            ]);

            setCompanies(companyData || []);
            setCustomers(customerData || []);
            setProducts(productData || []);
            setCategories(categoryData || []);

        } catch (error) {

            console.error(
                "Error loading sale form data:",
                error
            );

            setError(
                "Failed to load companies, customers or products."
            );

        } finally {

            setLoadingData(false);

        }
    };


    // ========================================================
    // Reset Form
    // ========================================================

    const resetForm = () => {

        setFormData({
            company_id: "",
            customer_id: "",
            sales_channel: "Offline",
            payment_method: "Cash",

            discount: 0,
            tax: 0,

            items: [
                {
                    product_id: "",
                    category_id: "",
                    quantity: "",
                    unit_price: "",
                    sku: "",
                    available_stock: 0,
                },
            ],
        });

        setQuantityError("");
        setError("");
    };


    // ========================================================
    // Close Modal
    // ========================================================

    const handleClose = () => {

        if (loading) {
            return;
        }

        resetForm();
        onClose();
    };


    // ========================================================
    // Main Form Change
    // ========================================================

    const handleChange = (e) => {

        const {
            name,
            value,
        } = e.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value,
        }));
    };


    // ========================================================
    // Company Change
    // ========================================================

    const handleCompanyChange = (e) => {

        const companyId = e.target.value;

        setFormData((previous) => ({
            ...previous,

            company_id: companyId,

            // Reset customer/product when company changes
            customer_id: "",

            items: [
                {
                    product_id: "",
                    category_id: "",
                    quantity: "",
                    unit_price: "",
                    sku: "",
                    available_stock: 0,
                },
            ],
        }));

        setQuantityError("");
    };


    // ========================================================
    // Product Change
    // Auto-fill:
    // Category
    // Price
    // SKU
    // Available Stock
    // ========================================================

    const handleProductChange = (e) => {

        const productId = Number(e.target.value);

        const selectedProduct = products.find(
            (product) =>
                product.id === productId
        );

        if (!selectedProduct) {

            setFormData((previous) => ({
                ...previous,

                items: [
                    {
                        ...previous.items[0],
                        product_id: "",
                        category_id: "",
                        quantity: "",
                        unit_price: "",
                        sku: "",
                        available_stock: 0,
                    },
                ],
            }));

            return;
        }

        const availableStock =
            Number(
                selectedProduct.stock_quantity || 0
            );

        setFormData((previous) => ({
            ...previous,

            items: [
                {
                    ...previous.items[0],

                    product_id:
                        selectedProduct.id,

                    category_id:
                        selectedProduct.category_id,

                    quantity: "",

                    unit_price:
                        selectedProduct.unit_price,

                    sku:
                        selectedProduct.sku,

                    available_stock:
                        availableStock,
                },
            ],
        }));

        setQuantityError("");
    };


    // ========================================================
    // Quantity Change
    // ========================================================

    const handleQuantityChange = (e) => {

        const value = e.target.value;

        const quantity =
            value === ""
                ? ""
                : Number(value);

        const availableStock =
            Number(
                formData.items[0]
                    .available_stock || 0
            );

        let message = "";

        if (quantity !== "") {

            if (quantity <= 0) {

                message =
                    "Quantity must be greater than zero.";

            } else if (
                quantity > availableStock
            ) {

                message =
                    `Only ${availableStock} item(s) available in stock.`;

            }
        }

        setQuantityError(message);

        setFormData((previous) => ({
            ...previous,

            items: [
                {
                    ...previous.items[0],
                    quantity,
                },
            ],
        }));
    };


    // ========================================================
    // Discount Change
    // ========================================================

    const handleDiscountChange = (e) => {

        const value = Number(e.target.value);

        setFormData((previous) => ({
            ...previous,
            discount:
                value >= 0
                    ? value
                    : 0,
        }));
    };


    // ========================================================
    // Tax Change
    // ========================================================

    const handleTaxChange = (e) => {

        const value = Number(e.target.value);

        setFormData((previous) => ({
            ...previous,
            tax:
                value >= 0
                    ? value
                    : 0,
        }));
    };


    // ========================================================
    // Selected Product
    // ========================================================

    const selectedProduct = useMemo(() => {

        const productId =
            Number(
                formData.items[0].product_id
            );

        return products.find(
            (product) =>
                product.id === productId
        );

    }, [
        products,
        formData.items,
    ]);


    // ========================================================
    // Selected Category
    // ========================================================

    const selectedCategory = useMemo(() => {

        const categoryId =
            Number(
                formData.items[0].category_id
            );

        return categories.find(
            (category) =>
                category.id === categoryId
        );

    }, [
        categories,
        formData.items,
    ]);


    // ========================================================
    // Filter Customers By Company
    // ========================================================

    const filteredCustomers = useMemo(() => {

        if (!formData.company_id) {
            return [];
        }

        return customers.filter(
            (customer) =>
                Number(customer.company_id) ===
                Number(formData.company_id)
        );

    }, [
        customers,
        formData.company_id,
    ]);


    // ========================================================
    // Filter Products By Company
    // ========================================================

    const filteredProducts = useMemo(() => {

        if (!formData.company_id) {
            return [];
        }

        return products.filter(
            (product) =>
                Number(product.company_id) ===
                Number(formData.company_id)
        );

    }, [
        products,
        formData.company_id,
    ]);


    // ========================================================
    // Billing Calculation
    // ========================================================

    const quantity =
        Number(
            formData.items[0].quantity || 0
        );

    const unitPrice =
        Number(
            formData.items[0].unit_price || 0
        );

    const discount =
        Number(
            formData.discount || 0
        );

    const tax =
        Number(
            formData.tax || 0
        );

    const subtotal =
        quantity * unitPrice;

    const taxableAmount =
        Math.max(
            0,
            subtotal - discount
        );

    const grandTotal =
        taxableAmount + tax;


    // ========================================================
    // Submit
    // ========================================================

    const handleSubmit = async (e) => {

        e.preventDefault();

        setError("");
        setQuantityError("");

        // ----------------------------------------------------
        // Basic Validation
        // ----------------------------------------------------

        if (!formData.company_id) {

            setError(
                "Please select a company."
            );

            return;
        }

        if (!formData.customer_id) {

            setError(
                "Please select a customer."
            );

            return;
        }

        if (!formData.items[0].product_id) {

            setError(
                "Please select a product."
            );

            return;
        }

        if (quantity <= 0) {

            setQuantityError(
                "Quantity must be greater than zero."
            );

            return;
        }

        if (
            quantity >
            Number(
                formData.items[0]
                    .available_stock || 0
            )
        ) {

            setQuantityError(
                `Only ${formData.items[0].available_stock} item(s) available in stock.`
            );

            return;
        }

        if (unitPrice <= 0) {

            setError(
                "Product has an invalid unit price."
            );

            return;
        }

        if (discount < 0) {

            setError(
                "Discount cannot be negative."
            );

            return;
        }

        if (tax < 0) {

            setError(
                "Tax cannot be negative."
            );

            return;
        }

        // ----------------------------------------------------
        // Create Sale
        // ----------------------------------------------------

        try {

            setLoading(true);

            const salePayload = {

                company_id:
                    Number(
                        formData.company_id
                    ),

                customer_id:
                    Number(
                        formData.customer_id
                    ),

                sales_channel:
                    formData.sales_channel,

                payment_method:
                    formData.payment_method,

                // Overall invoice discount/tax
                discount:
                    Number(
                        formData.discount
                    ),

                tax:
                    Number(
                        formData.tax
                    ),

                items: [
                    {
                        product_id:
                            Number(
                                formData.items[0]
                                    .product_id
                            ),

                        category_id:
                            Number(
                                formData.items[0]
                                    .category_id
                            ),

                        quantity:
                            Number(
                                formData.items[0]
                                    .quantity
                            ),

                        unit_price:
                            Number(
                                formData.items[0]
                                    .unit_price
                            ),

                        // We use invoice-level
                        // discount and tax.
                        discount: 0,

                        tax: 0,
                    },
                ],
            };

            await createSale(
                salePayload
            );

            alert(
                "Sale created successfully."
            );

            resetForm();

            onSuccess();

            onClose();

        } catch (err) {

            console.error("CREATE SALE ERROR:", err);

            console.error(
                "STATUS:",
                err.response?.status
            );

            console.error(
                "RESPONSE:",
                err.response?.data
            );

            setError(
                err.response?.data?.detail ||
                err.response?.data?.message ||
                "Failed to create sale."
            );

        } finally {

            setLoading(false);

        }
    };


    // ========================================================
    // Modal
    // ========================================================

    if (!isOpen) {
        return null;
    }


    return (
        <div className="modal-overlay">

            <div className="modal-content">

                {/* =================================================
                    Header
                ================================================= */}

                <div className="modal-header">

                    <div>

                        <h2>
                            Create Sale
                        </h2>

                        <p>
                            Create a new sales transaction
                        </p>

                    </div>

                    <button
                        type="button"
                        className="modal-close"
                        onClick={handleClose}
                        disabled={loading}
                    >
                        ×
                    </button>

                </div>


                {/* =================================================
                    Loading Dropdown Data
                ================================================= */}

                {loadingData ? (

                    <div className="modal-loading">
                        Loading sale information...
                    </div>

                ) : (

                    <form
                        onSubmit={handleSubmit}
                    >

                        {/* =================================================
                            Error
                        ================================================= */}

                        {error && (
                            <div className="form-error">
                                {error}
                            </div>
                        )}


                        {/* =================================================
                            Sale Information
                        ================================================= */}

                        <div className="form-section">

                            <h3>
                                Sale Information
                            </h3>


                            {/* Company */}

                            <div className="form-group">

                                <label>
                                    Company *
                                </label>

                                <select
                                    value={
                                        formData.company_id
                                    }
                                    onChange={
                                        handleCompanyChange
                                    }
                                    required
                                    disabled={loading}
                                >

                                    <option value="">
                                        Select Company
                                    </option>

                                    {companies.map(
                                        (company) => (

                                            <option
                                                key={
                                                    company.id
                                                }
                                                value={
                                                    company.id
                                                }
                                            >
                                                {
                                                    company.company_name
                                                }
                                            </option>

                                        )
                                    )}

                                </select>

                            </div>


                            {/* Customer */}

                            <div className="form-group">

                                <label>
                                    Customer *
                                </label>

                                <select
                                    name="customer_id"
                                    value={
                                        formData.customer_id
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    required
                                    disabled={
                                        loading ||
                                        !formData.company_id
                                    }
                                >

                                    <option value="">
                                        Select Customer
                                    </option>

                                    {filteredCustomers.map(
                                        (customer) => (

                                            <option
                                                key={
                                                    customer.id
                                                }
                                                value={
                                                    customer.id
                                                }
                                            >
                                                {
                                                    customer.first_name
                                                }{" "}
                                                {
                                                    customer.last_name
                                                }
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
                                    value={
                                        formData.sales_channel
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    disabled={loading}
                                >

                                    <option value="Offline">
                                        Offline
                                    </option>

                                    <option value="Online">
                                        Online
                                    </option>

                                    <option value="Store">
                                        Store
                                    </option>

                                </select>

                            </div>


                            {/* Payment Method */}

                            <div className="form-group">

                                <label>
                                    Payment Method
                                </label>

                                <select
                                    name="payment_method"
                                    value={
                                        formData.payment_method
                                    }
                                    onChange={
                                        handleChange
                                    }
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

                        </div>


                        {/* =================================================
                            Product Information
                        ================================================= */}

                        <div className="form-section">

                            <h3>
                                Product
                            </h3>


                            {/* Product */}

                            <div className="form-group">

                                <label>
                                    Product *
                                </label>

                                <select
                                    value={
                                        formData.items[0]
                                            .product_id
                                    }
                                    onChange={
                                        handleProductChange
                                    }
                                    required
                                    disabled={
                                        loading ||
                                        !formData.company_id
                                    }
                                >

                                    <option value="">
                                        Select Product
                                    </option>

                                    {filteredProducts.map(
                                        (product) => (

                                            <option
                                                key={
                                                    product.id
                                                }
                                                value={
                                                    product.id
                                                }
                                            >
                                                {
                                                    product.name
                                                }
                                                {" - "}
                                                {
                                                    product.sku
                                                }
                                            </option>

                                        )
                                    )}

                                </select>

                            </div>


                            {/* Product Details */}

                            {selectedProduct && (

                                <div className="product-info-grid">

                                    <div>
                                        <span>
                                            SKU
                                        </span>

                                        <strong>
                                            {
                                                selectedProduct.sku
                                            }
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Category
                                        </span>

                                        <strong>
                                            {
                                                selectedCategory?.name ||
                                                "N/A"
                                            }
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Unit Price
                                        </span>

                                        <strong>
                                            ₹
                                            {Number(
                                                selectedProduct.unit_price
                                            ).toLocaleString(
                                                "en-IN"
                                            )}
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Available Stock
                                        </span>

                                        <strong>
                                            {
                                                formData.items[0]
                                                    .available_stock
                                            }
                                        </strong>
                                    </div>

                                </div>

                            )}


                            {/* Quantity */}

                            <div className="form-group">

                                <label>
                                    Quantity *
                                </label>

                                <input
                                    type="number"
                                    min="1"
                                    value={
                                        formData.items[0]
                                            .quantity
                                    }
                                    onChange={
                                        handleQuantityChange
                                    }
                                    placeholder="Enter quantity"
                                    disabled={
                                        loading ||
                                        !selectedProduct
                                    }
                                    required
                                />

                                {quantityError && (
                                    <span className="field-error">
                                        {quantityError}
                                    </span>
                                )}

                            </div>

                        </div>


                        {/* =================================================
                            Billing
                        ================================================= */}

                        <div className="form-section">

                            <h3>
                                Billing Summary
                            </h3>


                            <div className="billing-row">

                                <span>
                                    Subtotal
                                </span>

                                <strong>
                                    ₹
                                    {subtotal.toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits: 2,
                                        }
                                    )}
                                </strong>

                            </div>


                            <div className="form-group">

                                <label>
                                    Discount
                                </label>

                                <input
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    value={
                                        formData.discount
                                    }
                                    onChange={
                                        handleDiscountChange
                                    }
                                    disabled={loading}
                                />

                            </div>


                            <div className="form-group">

                                <label>
                                    Tax
                                </label>

                                <input
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    value={
                                        formData.tax
                                    }
                                    onChange={
                                        handleTaxChange
                                    }
                                    disabled={loading}
                                />

                            </div>


                            <div className="billing-row">

                                <span>
                                    Discount
                                </span>

                                <strong>
                                    - ₹
                                    {discount.toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits: 2,
                                        }
                                    )}
                                </strong>

                            </div>


                            <div className="billing-row">

                                <span>
                                    Tax
                                </span>

                                <strong>
                                    + ₹
                                    {tax.toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits: 2,
                                        }
                                    )}
                                </strong>

                            </div>


                            <div className="billing-total">

                                <span>
                                    Grand Total
                                </span>

                                <strong>
                                    ₹
                                    {grandTotal.toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits: 2,
                                        }
                                    )}
                                </strong>

                            </div>

                        </div>


                        {/* =================================================
                            Buttons
                        ================================================= */}

                        <div className="modal-buttons">

                            <button
                                type="button"
                                onClick={handleClose}
                                disabled={loading}
                            >
                                Cancel
                            </button>


                            <button
                                type="submit"
                                disabled={
                                    loading ||
                                    loadingData ||
                                    !!quantityError ||
                                    !selectedProduct
                                }
                            >

                                {loading
                                    ? "Saving..."
                                    : "Save Sale"}

                            </button>

                        </div>

                    </form>

                )}

            </div>

        </div>
    );
}