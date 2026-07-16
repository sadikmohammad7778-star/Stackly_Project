import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

import { getCategories } from "../../services/categoryService";
import { getProducts } from "../../services/productService";

function Reports() {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    loadReportData();
  }, []);

  const loadReportData = async () => {
    try {
      const categoryRes = await getCategories();
      const productRes = await getProducts();

      setChartData([
        {
          name: "Categories",
          value: categoryRes.data.length,
        },
        {
          name: "Products",
          value: productRes.data.length,
        },
      ]);
    } catch (error) {
      console.error(error);
    }
  };

  const COLORS = ["#7c3aed", "#2563eb"];

  return (
    <div style={{ padding: "20px" }}>
      <h1 style={{ marginBottom: "20px" }}>
        Reports & Analytics
      </h1>

      <div
        style={{
          background: "#fff",
          borderRadius: "12px",
          padding: "20px",
          boxShadow: "0 2px 10px rgba(0,0,0,.1)",
          height: "450px",
        }}
      >
        <h3 style={{ textAlign: "center", marginBottom: "20px" }}>
          Products vs Categories
        </h3>

        <ResponsiveContainer width="100%" height="90%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              outerRadius={140}
              innerRadius={70}
              label
            >
              {chartData.map((entry, index) => (
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
    </div>
  );
}

export default Reports;