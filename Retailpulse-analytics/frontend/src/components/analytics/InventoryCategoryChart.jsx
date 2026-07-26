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

export default function InventoryCategoryChart({ data }) {
  return (
    <div className="chart-card">
      <h3>Inventory by Category</h3>

      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="category_name" />

          <YAxis />

          <Tooltip />

          <Bar
            dataKey="available_stock"
            fill="#2563eb"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}