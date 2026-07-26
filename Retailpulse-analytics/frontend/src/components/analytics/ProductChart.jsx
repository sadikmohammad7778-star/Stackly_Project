import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import "./AnalyticsComponents.css";

export default function ProductChart({ data }) {
  return (
    <div className="chart-card">
      <h3>Top Selling Products</h3>

      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="product_name" />

          <YAxis />

          <Tooltip />

          <Bar
            dataKey="quantity_sold"
            fill="#4f46e5"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}