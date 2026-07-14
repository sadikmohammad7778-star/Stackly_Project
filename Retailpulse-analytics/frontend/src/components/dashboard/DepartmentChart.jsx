import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { name: "Sales", value: 25 },
  { name: "HR", value: 10 },
  { name: "IT", value: 35 },
  { name: "Finance", value: 15 },
  { name: "Support", value: 15 },
];

const COLORS = [
  "#6366F1",
  "#10B981",
  "#F59E0B",
  "#EF4444",
  "#06B6D4",
];

export default function DepartmentChart() {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <PieChart>
        <Pie
          data={data}
          outerRadius={100}
          dataKey="value"
          label
        >
          {data.map((entry, index) => (
            <Cell
              key={index}
              fill={COLORS[index]}
            />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}