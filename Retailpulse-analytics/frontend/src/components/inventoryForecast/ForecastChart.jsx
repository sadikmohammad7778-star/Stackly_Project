import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
} from "recharts";

import "./ForecastChart.css";

export default function ForecastChart({ recommendation }) {

    if (!recommendation) {
        return null;
    }

    const data = [
        {
            name: "Daily Demand",
            value: Number(
                recommendation.average_daily_sales || 0
            ),
        },
        {
            name: "Forecast Demand",
            value: Number(
                recommendation.forecasted_demand || 0
            ),
        },
    ];

    return (
        <div className="forecast-chart-card">

            <h2>Demand Forecast</h2>

            <p>
                Historical average demand compared with
                forecasted demand.
            </p>

            <div className="forecast-chart">

                <ResponsiveContainer
                    width="100%"
                    height={280}
                >

                    <BarChart data={data}>

                        <CartesianGrid strokeDasharray="3 3" />

                        <XAxis dataKey="name" />

                        <YAxis />

                        <Tooltip />

                        <Legend />

                        <Bar
                            dataKey="value"
                            name="Demand"
                        />

                    </BarChart>

                </ResponsiveContainer>

            </div>

        </div>
    );
}