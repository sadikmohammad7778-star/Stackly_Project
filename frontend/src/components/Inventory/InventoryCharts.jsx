import { useEffect, useState } from "react";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts";

import {
  getCategoryChart,
  getStatusChart,
} from "../../api/inventoryApi";

export default function InventoryCharts() {
  const [categoryData, setCategoryData] = useState([]);
  const [statusData, setStatusData] = useState([]);

  useEffect(() => {
    loadCharts();
  }, []);

  const loadCharts = async () => {
    try {
      const category = await getCategoryChart(3);
      const status = await getStatusChart(3);

      setCategoryData(category);
      setStatusData(status);
    } catch (err) {
      console.error(err);
    }
  };

  const COLORS = [
    "#2563eb",
    "#16a34a",
    "#f59e0b",
    "#dc2626",
    "#9333ea",
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "20px",
        marginBottom: "30px",
      }}
    >
      <div
        style={{
          background: "#fff",
          padding: "20px",
          borderRadius: "10px",
          height: "350px",
        }}
      >
        <h3>Inventory by Category</h3>

        <ResponsiveContainer width="100%" height="90%">
          <BarChart data={categoryData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="total_stock" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div
        style={{
          background: "#fff",
          padding: "20px",
          borderRadius: "10px",
          height: "350px",
        }}
      >
        <h3>Stock Status</h3>

        <ResponsiveContainer width="100%" height="90%">
          <PieChart>
            <Pie
              data={statusData}
              dataKey="count"
              nameKey="status"
              outerRadius={100}
              label
            >
              {statusData.map((entry, index) => (
                <Cell
                  key={index}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>

            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}