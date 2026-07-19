import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { getMonthlySales } from "../../api/DashboardApi";

export default function SalesChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    loadMonthlySales();
  }, []);

  const loadMonthlySales = async () => {
    try {
      const response = await getMonthlySales();
      setData(response);
    } catch (error) {
      console.error("Error loading monthly sales:", error);
    }
  };

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="revenue"
          stroke="#6366F1"
          strokeWidth={3}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}