import API from "./axios";

// ============================================================
// Get All Sales
// ============================================================

export const getSales = async () => {
    const response = await API.get("/sales/");
    return response.data;
};


// ============================================================
// Get Sale By ID
// ============================================================

export const getSaleById = async (id) => {
    const response = await API.get(`/sales/${id}`);
    return response.data;
};


// ============================================================
// Create Sale
// ============================================================

export const createSale = async (sale) => {
    const response = await API.post("/sales/", sale);
    return response.data;
};


// ============================================================
// Update Sale
// ============================================================

export const updateSale = async (id, sale) => {
    const response = await API.put(
        `/sales/${id}`,
        sale
    );

    return response.data;
};


// ============================================================
// Delete Sale
// ============================================================

export const deleteSale = async (id) => {
    const response = await API.delete(
        `/sales/${id}`
    );

    return response.data;
};


// ============================================================
// Sales Dashboard Summary
// ============================================================

export const getSaleSummary = async () => {
    const response = await API.get(
        "/sales/summary/dashboard"
    );

    return response.data;
};


// ============================================================
// Search / Filter / Sort Sales
// ============================================================

export const searchSales = async ({
    keyword = "",
    start_date = "",
    end_date = "",
    payment_method = "",
    status = "",
    sort = "date",
    order = "desc",
} = {}) => {

    const params = {};

    if (keyword) {
        params.keyword = keyword;
    }

    if (start_date) {
        params.start_date = start_date;
    }

    if (end_date) {
        params.end_date = end_date;
    }

    if (payment_method) {
        params.payment_method = payment_method;
    }

    if (status) {
        params.status = status;
    }

    params.sort = sort;
    params.order = order;

    const response = await API.get(
        "/sales/search",
        {
            params,
        }
    );

    return response.data;
};


// ============================================================
// Invoice PDF
// ============================================================

export const downloadInvoicePDF = async (id) => {
    const response = await API.get(
        `/sales/${id}/invoice/pdf`,
        {
            responseType: "blob",
        }
    );

    return response.data;
};


// ============================================================
// Invoice CSV
// ============================================================

export const downloadInvoiceCSV = async (id) => {
    const response = await API.get(
        `/sales/${id}/invoice/csv`,
        {
            responseType: "blob",
        }
    );

    return response.data;
};