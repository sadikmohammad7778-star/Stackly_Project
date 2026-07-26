import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Tooltip,
  Legend,
  Cell,
} from "recharts";

import "./AnalyticsComponents.css";

const COLORS = [
  "#0ea5e9",
  "#16a34a",
  "#f59e0b",
  "#dc2626",
  "#8b5cf6",
];

export default function SalesChannelChart({ data }) {
  return (
    <div className="chart-card">
      <h3>Sales Channels</h3>

      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            dataKey="total_sales"
            nameKey="sales_channel"
            outerRadius={110}
            label
          >
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>

          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}