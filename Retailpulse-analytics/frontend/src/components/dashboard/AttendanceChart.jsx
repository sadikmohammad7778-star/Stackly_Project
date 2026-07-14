import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const data = [
  { day: "Mon", attendance: 95 },
  { day: "Tue", attendance: 91 },
  { day: "Wed", attendance: 97 },
  { day: "Thu", attendance: 89 },
  { day: "Fri", attendance: 98 },
];

export default function AttendanceChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="day" />
        <YAxis />
        <Tooltip />
        <Bar
          dataKey="attendance"
          fill="#10B981"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}