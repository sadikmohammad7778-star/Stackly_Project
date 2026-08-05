import axios from "./axios";

export const getDashboard = () =>
    axios.get("/forecast/dashboard");

export const getProducts = () =>
    axios.get("/forecast/products");

export const getCategories = () =>
    axios.get("/forecast/categories");

export const getRecommendations = () =>
    axios.get("/forecast/recommendations");

export const getCharts = () =>
    axios.get("/forecast/charts");

export const generateForecast = (data) =>
    axios.post("/forecast/generate", data);

export const refreshForecast = (data) =>
    axios.post("/forecast/refresh", data);

export const exportForecastCSV = () =>
    axios.get("/export/forecast/csv", {
        responseType: "blob",
    });

export const exportForecastPDF = () =>
    axios.get("/export/forecast/pdf", {
        responseType: "blob",
    });