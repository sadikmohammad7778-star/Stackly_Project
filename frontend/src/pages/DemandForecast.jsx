import { useEffect, useState } from "react";

import {
    getDashboard,
    getProducts,
    getCategories,
    getRecommendations,
    getCharts,
} from "../api/demandForecastApi";

import ForecastCards from "../components/forecast/ForecastCards";
import ForecastCharts from "../components/forecast/ForecastCharts";
import ForecastFilters from "../components/forecast/ForecastFilters";
import CategoryForecastTable from "../components/forecast/CategoryForecastTable";
import RecommendationTable from "../components/forecast/RecommendationTable";
import ForecastTable from "../components/forecast/ForecastTable";

const DemandForecast = () => {

    const [dashboard, setDashboard] = useState({});

    const [products, setProducts] = useState([]);

    const [categories, setCategories] = useState([]);

    const [recommendations, setRecommendations] = useState([]);

    const [charts, setCharts] = useState({});

    const [loading, setLoading] = useState(true);

    const loadData = async () => {

        try {

            const [
                dashboardRes,
                productsRes,
                categoriesRes,
                recommendationRes,
                chartRes,
            ] = await Promise.all([
                getDashboard(),
                getProducts(),
                getCategories(),
                getRecommendations(),
                getCharts(),
            ]);

            setDashboard(dashboardRes.data);
            console.log("Dashboard:", dashboardRes.data);

            setProducts(productsRes.data);

            setCategories(categoriesRes.data);

            setRecommendations(recommendationRes.data);

            setCharts(chartRes.data);

        } catch (error) {

            console.error(
                "Forecast Error",
                error,
            );

        } finally {

            setLoading(false);

        }
    };

    useEffect(() => {

        loadData();

    }, []);

    if (loading) {

        return (
            <h2>Loading Forecast Dashboard...</h2>
        );

    }

    return (

        <div className="forecast-page">

            <h2>
                Demand Forecast Dashboard
            </h2>

            <ForecastCards
                dashboard={dashboard}
            />

            <ForecastFilters />

            <ForecastCharts
                charts={charts}
            />

            <RecommendationTable
                recommendations={recommendations}
            />

            <CategoryForecastTable
                categories={categories}
            />

            <ForecastTable
                products={products}
            />

        </div>

    );

};

export default DemandForecast;