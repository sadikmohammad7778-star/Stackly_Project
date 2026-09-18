import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
} from "recharts";
import "./ForecastCharts.css";

const COLORS = [
    "#1976d2",
    "#43a047",
    "#f57c00",
    "#d32f2f",
    "#7b1fa2",
    "#0097a7",
];

const ForecastCharts = ({ charts }) => {

    return (

        <div className="forecast-charts">

            {/* Historical vs Forecast */}

            <div className="chart-card">

                <h3>Historical Sales vs Forecast</h3>

                <ResponsiveContainer width="100%" height={350}>

                    <LineChart
                        data={charts.historical_vs_forecast || []}
                    >

                        <CartesianGrid strokeDasharray="3 3" />

                        <XAxis dataKey="product" />

                        <YAxis />

                        <Tooltip />

                        <Legend />

                        <Line
                            type="monotone"
                            dataKey="historical_sales"
                            stroke="#1976d2"
                        />

                        <Line
                            type="monotone"
                            dataKey="forecast"
                            stroke="#43a047"
                        />

                    </LineChart>

                </ResponsiveContainer>

            </div>

            {/* Product Demand */}

            <div className="chart-card">

                <h3>Product Demand Trend</h3>

                <ResponsiveContainer width="100%" height={350}>

                    <BarChart
                        data={charts.product_trend || []}
                    >

                        <CartesianGrid strokeDasharray="3 3" />

                        <XAxis dataKey="product" />

                        <YAxis />

                        <Tooltip />

                        <Legend />

                        <Bar
                            dataKey="predicted"
                            fill="#1976d2"
                        />

                    </BarChart>

                </ResponsiveContainer>

            </div>

            {/* Category Trend */}

            <div className="chart-card">

                <h3>Category Demand Trend</h3>

                <ResponsiveContainer width="100%" height={350}>

                    <PieChart>

                        <Pie
                            data={charts.category_trend || []}
                            dataKey="predicted"
                            nameKey="category"
                            outerRadius={120}
                            label
                        >

                            {(charts.category_trend || []).map(
                                (_, index) => (
                                    <Cell
                                        key={index}
                                        fill={
                                            COLORS[
                                                index %
                                                COLORS.length
                                            ]
                                        }
                                    />
                                )
                            )}

                        </Pie>

                        <Tooltip />

                    </PieChart>

                </ResponsiveContainer>

            </div>

            {/* Top Products */}

            <div className="chart-card">

                <h3>Top Predicted Products</h3>

                <ResponsiveContainer width="100%" height={350}>

                    <BarChart
                        data={charts.top_products || []}
                    >

                        <CartesianGrid strokeDasharray="3 3" />

                        <XAxis dataKey="product" />

                        <YAxis />

                        <Tooltip />

                        <Bar
                            dataKey="predicted"
                            fill="#43a047"
                        />

                    </BarChart>

                </ResponsiveContainer>

            </div>

            {/* Seasonal Pattern */}

            <div className="chart-card">

                <h3>Seasonal Sales Pattern</h3>

                <ResponsiveContainer width="100%" height={350}>

                    <LineChart
                        data={charts.seasonal_pattern || []}
                    >

                        <CartesianGrid strokeDasharray="3 3" />

                        <XAxis dataKey="month" />

                        <YAxis />

                        <Tooltip />

                        <Legend />

                        <Line
                            dataKey="sales"
                            stroke="#f57c00"
                        />

                    </LineChart>

                </ResponsiveContainer>

            </div>

        </div>

    );

};

export default ForecastCharts;