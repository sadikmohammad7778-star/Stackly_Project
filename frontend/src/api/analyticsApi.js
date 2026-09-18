import API from "./axios";

// --------------------------------------------------
// Helper: Build date range
// --------------------------------------------------

const getDateRange = (filter) => {
    const today = new Date();

    const formatDate = (date) => {
        return date.toISOString().split("T")[0];
    };

    const dateTo = formatDate(
        new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1)
    );

    let dateFrom;

    switch (filter) {
        case "today":
            dateFrom = formatDate(today);
            break;

        case "week":
            dateFrom = formatDate(
                new Date(
                    today.getFullYear(),
                    today.getMonth(),
                    today.getDate() - 6
                )
            );
            break;

        case "month":
            dateFrom = formatDate(
                new Date(
                    today.getFullYear(),
                    today.getMonth(),
                    1
                )
            );
            break;

        case "year":
            dateFrom = formatDate(
                new Date(
                    today.getFullYear(),
                    0,
                    1
                )
            );
            break;

        default:
            dateFrom = formatDate(
                new Date(
                    today.getFullYear(),
                    today.getMonth(),
                    1
                )
            );
    }

    return {
        date_from: dateFrom,
        date_to: dateTo,
    };
};


// --------------------------------------------------
// Dashboard KPIs
// --------------------------------------------------

export const getDashboardKPIs = async (companyId) => {
    const response = await API.get(
        `/analytics/dashboard?company_id=${companyId}`
    );

    return response.data;
};


// --------------------------------------------------
// Revenue Trend
// --------------------------------------------------

export const getRevenueTrend = async (
    companyId,
    period = "daily",
    filter = "month"
) => {
    const { date_from, date_to } = getDateRange(filter);

    const response = await API.get(
        `/analytics/revenue-trend?company_id=${companyId}&period=${period}&date_from=${date_from}&date_to=${date_to}`
    );

    return response.data;
};


// --------------------------------------------------
// Top Products
// --------------------------------------------------

export const getTopProducts = async (
    companyId,
    sortBy = "revenue",
    filter = "month"
) => {
    const { date_from, date_to } = getDateRange(filter);

    const response = await API.get(
        `/analytics/top-products?company_id=${companyId}&sort_by=${sortBy}&date_from=${date_from}&date_to=${date_to}`
    );

    return response.data;
};


// --------------------------------------------------
// Top Categories
// --------------------------------------------------

export const getTopCategories = async (
    companyId,
    filter = "month"
) => {
    const { date_from, date_to } = getDateRange(filter);

    const response = await API.get(
        `/analytics/top-categories?company_id=${companyId}&date_from=${date_from}&date_to=${date_to}`
    );

    return response.data;
};


// --------------------------------------------------
// Payment Methods
// --------------------------------------------------

export const getPaymentMethods = async (
    companyId,
    filter = "month"
) => {
    const { date_from, date_to } = getDateRange(filter);

    const response = await API.get(
        `/analytics/payment-methods?company_id=${companyId}&date_from=${date_from}&date_to=${date_to}`
    );

    return response.data;
};


// --------------------------------------------------
// Sales Channels
// --------------------------------------------------

export const getSalesChannels = async (
    companyId,
    filter = "month"
) => {
    const { date_from, date_to } = getDateRange(filter);

    const response = await API.get(
        `/analytics/sales-channels?company_id=${companyId}&date_from=${date_from}&date_to=${date_to}`
    );

    return response.data;
};


// --------------------------------------------------
// Inventory Category
// --------------------------------------------------

export const getInventoryCategory = async (companyId) => {
    const response = await API.get(
        `/analytics/inventory-category?company_id=${companyId}`
    );

    return response.data;
};


// --------------------------------------------------
// Stock Status
// --------------------------------------------------

export const getStockStatus = async (companyId) => {
    const response = await API.get(
        `/analytics/stock-status?company_id=${companyId}`
    );

    return response.data;
};


// --------------------------------------------------
// Inventory Value
// --------------------------------------------------

export const getInventoryValue = async (companyId) => {
    const response = await API.get(
        `/analytics/inventory-value?company_id=${companyId}`
    );

    return response.data;
};