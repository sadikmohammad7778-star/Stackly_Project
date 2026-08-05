import { useState } from "react";

import {
    refreshForecast,
    exportForecastCSV,
    exportForecastPDF,
} from "../../api/demandForecastApi";
import "./ForecastFilters.css";
const ForecastFilters = () => {

    const [search, setSearch] = useState("");

    const [category, setCategory] = useState("");

    const [brand, setBrand] = useState("");

    const [forecastPeriod, setForecastPeriod] = useState("30_days");

    const handleRefresh = async () => {

        try {

            await refreshForecast({
                forecast_period: forecastPeriod,
            });

            alert("Forecast refreshed successfully.");

            window.location.reload();

        } catch (error) {

            console.error(error);

        }

    };

    const downloadFile = (blob, filename) => {

        const url = window.URL.createObjectURL(blob);

        const link = document.createElement("a");

        link.href = url;

        link.download = filename;

        link.click();

        window.URL.revokeObjectURL(url);

    };

    const handleCSV = async () => {

        const response = await exportForecastCSV();

        downloadFile(
            response.data,
            "Demand_Forecast_Report.csv",
        );

    };

    const handlePDF = async () => {

        const response = await exportForecastPDF();

        downloadFile(
            response.data,
            "Demand_Forecast_Report.pdf",
        );

    };

    return (

        <div className="forecast-filter">

            <input
                type="text"
                placeholder="Search Product"
                value={search}
                onChange={(e) =>
                    setSearch(e.target.value)
                }
            />

            <input
                type="text"
                placeholder="Category"
                value={category}
                onChange={(e) =>
                    setCategory(e.target.value)
                }
            />

            <input
                type="text"
                placeholder="Brand"
                value={brand}
                onChange={(e) =>
                    setBrand(e.target.value)
                }
            />

            <select
                value={forecastPeriod}
                onChange={(e) =>
                    setForecastPeriod(e.target.value)
                }
            >
                <option value="7_days">
                    Next 7 Days
                </option>

                <option value="30_days">
                    Next 30 Days
                </option>

                <option value="90_days">
                    Next 90 Days
                </option>

            </select>

            <button onClick={handleRefresh}>
                Refresh Forecast
            </button>

            <button onClick={handleCSV}>
                Export CSV
            </button>

            <button onClick={handlePDF}>
                Export PDF
            </button>

        </div>

    );

};

export default ForecastFilters;