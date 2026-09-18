import { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

import { getSalesByCategory } from "../../api/DashboardApi";

const COLORS = [
  "#6366F1",
  "#10B981",
  "#F59E0B",
  "#EF4444",
  "#06B6D4",
  "#8B5CF6",
  "#EC4899",
  "#14B8A6",
];

export default function DepartmentChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    loadCategorySales();
  }, []);

  const loadCategorySales = async () => {
    try {
      const response = await getSalesByCategory();

      const formattedData = response.map((item) => ({
        name: item.category_name,
        value: item.total_sales,
      }));

      setData(formattedData);
    } catch (error) {
      console.error("Error loading category sales:", error);
    }
  };

  return (
    <ResponsiveContainer width="100%" height={320}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          outerRadius={100}
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
  );
}