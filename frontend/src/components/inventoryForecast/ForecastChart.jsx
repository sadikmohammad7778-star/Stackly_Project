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

export default function ForecastChart({ forecast = [] }) {

    const chartData = forecast.map((item) => ({
        product: item.product_name,
        dailyDemand: Number(item.average_daily_sales || 0),
        forecastDemand: Number(item.forecasted_demand || 0),
    }));

    if (chartData.length === 0) {
        return (
            <div className="forecast-chart-card">
                <h2>Demand Forecast</h2>

                <div className="forecast-chart-empty">
                    No forecast data available.
                </div>
            </div>
        );
    }

    return (
        <div className="forecast-chart-card">

            <div className="forecast-chart-header">
                <div>
                    <h2>Demand Forecast</h2>

                    <p>
                        Daily demand compared with forecasted demand.
                    </p>
                </div>
            </div>

            <div className="forecast-chart">

                <ResponsiveContainer
                    width="100%"
                    height={350}
                >

                    <BarChart
                        data={chartData}
                        margin={{
                            top: 10,
                            right: 20,
                            left: 0,
                            bottom: 10,
                        }}
                    >

                        <CartesianGrid
                            strokeDasharray="3 3"
                        />

                        <XAxis
                            dataKey="product"
                            tick={{ fontSize: 12 }}
                            interval={0}
                        />

                        <YAxis
                            allowDecimals
                        />

                        <Tooltip
                            formatter={(value) =>
                                Number(value).toFixed(2)
                            }
                        />

                        <Legend />

                        <Bar
                            dataKey="dailyDemand"
                            name="Daily Demand"
                            fill="#6366F1"
                            radius={[6, 6, 0, 0]}
                        />

                        <Bar
                            dataKey="forecastDemand"
                            name="Forecast Demand"
                            fill="#22C55E"
                            radius={[6, 6, 0, 0]}
                        />

                    </BarChart>

                </ResponsiveContainer>

            </div>

        </div>
    );
}