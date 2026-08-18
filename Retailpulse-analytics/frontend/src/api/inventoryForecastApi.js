import axios from "./axios";


export const getInventoryForecast = (forecastDays = 30) =>
    axios.get("/inventory/forecast", {
        params: {
            forecast_days: forecastDays,
        },
    });


export const getInventoryForecastSummary = () =>
    axios.get("/inventory/forecast/summary");


export const getInventoryRecommendations = (
    forecastDays = 30
) =>
    axios.get("/inventory/forecast/recommendations", {
        params: {
            forecast_days: forecastDays,
        },
    });


export const getProductInventoryRecommendation = (
    productId
) =>
    axios.get(
        `/inventory/forecast/recommendations/${productId}`
    );