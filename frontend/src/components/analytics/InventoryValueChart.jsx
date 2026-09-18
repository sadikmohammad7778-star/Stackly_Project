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

export default function InventoryValueChart({ data }) {
  return (
    <div className="chart-card">
      <h3>Inventory Value</h3>

      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="category_name" />

          <YAxis />

          <Tooltip />

          <Bar
            dataKey="inventory_value"
            fill="#7c3aed"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}