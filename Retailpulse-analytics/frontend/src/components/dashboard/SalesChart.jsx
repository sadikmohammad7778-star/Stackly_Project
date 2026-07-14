import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { month: "Jan", sales: 4000 },
  { month: "Feb", sales: 5200 },
  { month: "Mar", sales: 6100 },
  { month: "Apr", sales: 5800 },
  { month: "May", sales: 7600 },
  { month: "Jun", sales: 9100 },
];

export default function SalesChart() {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="sales"
          stroke="#6366F1"
          strokeWidth={3}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}