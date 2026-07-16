import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

import "./DashboardChart.css";

function DashboardChart() {

  const data = [
    { month: "Jan", products: 45 },
    { month: "Feb", products: 60 },
    { month: "Mar", products: 55 },
    { month: "Apr", products: 75 },
    { month: "May", products: 68 },
    { month: "Jun", products: 90 },
  ];

  return (
    <div className="chart-card">

      <h3>Inventory Overview</h3>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="products" fill="#7c3aed" radius={[6, 2, 0, 0]}   barSize={50}/>
        </BarChart>
      </ResponsiveContainer>

    </div>
  );
}

export default DashboardChart;