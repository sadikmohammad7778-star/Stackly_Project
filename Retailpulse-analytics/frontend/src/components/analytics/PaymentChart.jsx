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
  "#4f46e5",
  "#16a34a",
  "#f59e0b",
  "#dc2626",
  "#0ea5e9",
];

export default function PaymentChart({ data }) {
  return (
    <div className="chart-card">
      <h3>Payment Methods</h3>

      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            dataKey="total_sales"
            nameKey="payment_method"
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