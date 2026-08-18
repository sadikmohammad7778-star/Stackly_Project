import { useEffect, useState } from "react";

import {
    getInventoryForecast,
    getInventoryForecastSummary,
    getProductInventoryRecommendation,
} from "../api/inventoryForecastApi";

import "./InventoryForecast.css";

import ForecastSummary from "../components/inventoryForecast/ForecastSummary";
import RecommendationPanel from "../components/inventoryForecast/RecommendationPanel";
import ForecastChart from "../components/inventoryForecast/ForecastChart";

export default function InventoryForecast() {

    // ============================
    // State
    // ============================

    const [forecast, setForecast] = useState([]);
    const [summary, setSummary] = useState(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Filters
    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("");
    const [risk, setRisk] = useState("");
    const [reorderOnly, setReorderOnly] = useState(false);

    // Sorting
    const [sortBy, setSortBy] = useState("");
    const [sortOrder, setSortOrder] = useState("asc");

    const [selectedProduct, setSelectedProduct] = useState(null);
    const [recommendation, setRecommendation] = useState(null);
    const [recommendationLoading, setRecommendationLoading] = useState(false);


    // ============================
    // Load Forecast
    // ============================

    useEffect(() => {
        loadForecast();
    }, []);


    const loadForecast = async () => {

        try {

            setLoading(true);
            setError("");

            const [
                forecastResponse,
                summaryResponse,
            ] = await Promise.all([
                getInventoryForecast(30),
                getInventoryForecastSummary(),
            ]);

            setForecast(forecastResponse.data);
            setSummary(summaryResponse.data);

        } catch (err) {

            console.error(
                "Inventory forecast error:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to load inventory forecast."
            );

        } finally {

            setLoading(false);

        }
    };


    // ============================
    // Filter Forecast
    // ============================

    const filteredForecast = forecast.filter((item) => {

        const searchValue =
            search.toLowerCase().trim();

        const productName =
            item.product_name?.toLowerCase() || "";

        const sku =
            item.sku?.toLowerCase() || "";

        const matchesSearch =
            !searchValue ||
            productName.includes(searchValue) ||
            sku.includes(searchValue);

        const matchesCategory =
            !category ||
            String(item.category_id) === category;

        const matchesRisk =
            !risk ||
            item.stock_risk === risk;

        const matchesReorder =
            !reorderOnly ||
            Number(
                item.recommended_reorder_quantity
            ) > 0;

        return (
            matchesSearch &&
            matchesCategory &&
            matchesRisk &&
            matchesReorder
        );
    });


    // ============================
    // Sort Forecast
    // ============================

    const sortedForecast = [...filteredForecast];

    if (sortBy) {

        sortedForecast.sort((a, b) => {

            const valueA =
                Number(a[sortBy]) || 0;

            const valueB =
                Number(b[sortBy]) || 0;

            if (sortOrder === "asc") {
                return valueA - valueB;
            }

            return valueB - valueA;
        });
    }


    const handleProductSelect = async (productId) => {
        try {
            setRecommendationLoading(true);
            setRecommendation(null);
            setSelectedProduct(productId);

            const response =
                await getProductInventoryRecommendation(productId);

            setRecommendation(response.data);

        } catch (err) {
            console.error(
                "Recommendation error:",
                err
            );

            setRecommendation(null);

        } finally {
            setRecommendationLoading(false);
        }
    };
    // ============================
    // Loading
    // ============================

    if (loading) {

        return (
            <div className="inventory-forecast-page">

                <div className="forecast-loading">
                    Loading inventory forecast...
                </div>

            </div>
        );
    }


    // ============================
    // Error
    // ============================

    if (error) {

        return (
            <div className="inventory-forecast-page">

                <div className="forecast-error">

                    {error}

                    <button onClick={loadForecast}>
                        Retry
                    </button>

                </div>

            </div>
        );
    }


    // ============================
    // Page
    // ============================

    return (

        <div className="inventory-forecast-page">

            {/* ============================
                Header
            ============================ */}

            <div className="inventory-forecast-header">

                <div>

                    <h1>
                        Inventory Forecasting
                    </h1>

                    <p>
                        Forecast demand and smart
                        replenishment recommendations.
                    </p>

                </div>

            </div>


            {/* ============================
                Summary
            ============================ */}

            <ForecastSummary
                summary={summary}
            />


            {/* ============================
                Filters
            ============================ */}

            <div className="forecast-filters">

                {/* Search */}

                <input
                    type="text"
                    placeholder="Search Product or SKU..."
                    value={search}
                    onChange={(e) =>
                        setSearch(e.target.value)
                    }
                />


                {/* Category */}

                <select
                    value={category}
                    onChange={(e) =>
                        setCategory(e.target.value)
                    }
                >

                    <option value="">
                        All Categories
                    </option>

                    {[
                        ...new Set(
                            forecast.map(
                                (item) =>
                                    item.category_id
                            )
                        ),
                    ].map((categoryId) => (

                        <option
                            key={categoryId}
                            value={categoryId}
                        >
                            Category {categoryId}
                        </option>

                    ))}

                </select>


                {/* Risk */}

                <select
                    value={risk}
                    onChange={(e) =>
                        setRisk(e.target.value)
                    }
                >

                    <option value="">
                        All Risks
                    </option>

                    <option value="Healthy">
                        Healthy
                    </option>

                    <option value="Low Stock">
                        Low Stock
                    </option>

                    <option value="Stockout Risk">
                        Stockout Risk
                    </option>

                    <option value="Out of Stock">
                        Out of Stock
                    </option>

                    <option value="Overstock">
                        Overstock
                    </option>

                </select>


                {/* Reorder */}

                <label className="reorder-filter">

                    <input
                        type="checkbox"
                        checked={reorderOnly}
                        onChange={(e) =>
                            setReorderOnly(
                                e.target.checked
                            )
                        }
                    />

                    Reorder Required

                </label>


                {/* Sort By */}

                <select
                    value={sortBy}
                    onChange={(e) => {

                        setSortBy(
                            e.target.value
                        );

                        setSortOrder("asc");

                    }}
                >

                    <option value="">
                        Sort By
                    </option>

                    <option value="current_stock">
                        Current Stock
                    </option>

                    <option value="average_daily_sales">
                        Daily Demand
                    </option>

                    <option value="forecasted_demand">
                        Forecast Demand
                    </option>

                    <option value="days_of_stock_remaining">
                        Days Remaining
                    </option>

                    <option value="reorder_point">
                        Reorder Point
                    </option>

                    <option value="recommended_reorder_quantity">
                        Recommended Qty
                    </option>

                </select>


                {/* Sort Order */}

                <select
                    value={sortOrder}
                    onChange={(e) =>
                        setSortOrder(
                            e.target.value
                        )
                    }
                    disabled={!sortBy}
                >

                    <option value="asc">
                        Low to High
                    </option>

                    <option value="desc">
                        High to Low
                    </option>

                </select>

            </div>

           {/* ============================
                Forecast Table
            ============================ */}

            <div className="forecast-table-container">

                <h2>
                    Inventory Forecast
                </h2>

                {sortedForecast.length === 0 ? (

                    <div className="forecast-empty">
                        No inventory forecast data available.
                    </div>

                ) : (

                    <div className="forecast-table-wrapper">

                        <table>

                            <thead>

                                <tr>
                                    <th>Product</th>
                                    <th>SKU</th>
                                    <th>Current Stock</th>
                                    <th>Daily Demand</th>
                                    <th>Forecast Demand</th>
                                    <th>Days Remaining</th>
                                    <th>Reorder Point</th>
                                    <th>Recommended Qty</th>
                                    <th>Risk</th>
                                    <th>Recommendation</th>
                                </tr>

                            </thead>

                            <tbody>

                                {sortedForecast.map((item) => (

                                    <tr key={item.product_id}>

                                        <td>
                                            <button
                                                className="forecast-product-button"
                                                onClick={() =>
                                                    handleProductSelect(
                                                        item.product_id
                                                    )
                                                }
                                            >
                                                {item.product_name}
                                            </button>
                                        </td>

                                        <td>
                                            {item.sku}
                                        </td>

                                        <td>
                                            {item.current_stock}
                                        </td>

                                        <td>
                                            {item.average_daily_sales}
                                        </td>

                                        <td>
                                            {item.forecasted_demand}
                                        </td>

                                        <td>
                                            {item.days_of_stock_remaining ?? "—"}
                                        </td>

                                        <td>
                                            {item.reorder_point}
                                        </td>

                                        <td>
                                            {item.recommended_reorder_quantity}
                                        </td>

                                        <td>
                                            <span
                                                className={`risk-badge risk-${item.stock_risk
                                                    ?.toLowerCase()
                                                    .replace(/\s+/g, "-")}`}
                                            >
                                                {item.stock_risk}
                                            </span>
                                        </td>

                                        <td>
                                            {item.recommendation}
                                        </td>

                                    </tr>

                                ))}

                            </tbody>

                        </table>

                    </div>

                )}

                {recommendationLoading && (
                    <div className="forecast-loading">
                        Loading recommendation...
                    </div>
                )}

                {recommendation && (
                    <RecommendationPanel
                        recommendation={recommendation}
                    />
                )}

                {recommendation && (
                    <ForecastChart
                        recommendation={recommendation}
                    />
                )}

            </div>



        </div>
    );
}