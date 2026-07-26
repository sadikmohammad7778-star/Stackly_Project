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

export default function TopCategoryChart({ data }) {
  return (
    <div className="chart-card">
      <h3>Top Categories</h3>

      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="category_name" />

          <YAxis />

          <Tooltip />

          <Bar
            dataKey="revenue"
            fill="#16a34a"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}