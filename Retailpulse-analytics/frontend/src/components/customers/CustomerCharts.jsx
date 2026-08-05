import { useEffect, useState } from "react";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

import {
  customerGrowth,
  revenueByType,
  customerDistribution,
  topCustomers,
} from "../../api/customerApi";

import "./CustomerCharts.css";

const COLORS = [
  "#2563eb",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
];

export default function CustomerCharts() {
  const [growthData, setGrowthData] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [distributionData, setDistributionData] = useState([]);
  const [topCustomersData, setTopCustomersData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCharts();
  }, []);

  const loadCharts = async () => {
    try {
      const [
        growthResponse,
        revenueResponse,
        distributionResponse,
        topCustomersResponse,
      ] = await Promise.all([
        customerGrowth(),
        revenueByType(),
        customerDistribution(),
        topCustomers(),
      ]);

      console.log("Growth:", growthResponse.data);
      console.log("Revenue:", revenueResponse.data);
      console.log("Distribution:", distributionResponse.data);
      console.log("Top Customers:", topCustomersResponse.data);

      setGrowthData(growthResponse.data || []);
      setRevenueData(revenueResponse.data || []);
      setDistributionData(distributionResponse.data || []);
      setTopCustomersData(topCustomersResponse.data || []);
    } catch (error) {
      console.error("Error loading customer analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="chart-loading">
        Loading Customer Analytics...
      </div>
    );
  }

  return (
    <div className="chart-grid">

      {/* Customer Growth */}
      <div className="chart-card">
        <h3>📈 Customer Growth</h3>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={growthData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />

            <Line
              type="monotone"
              dataKey="customers"
              stroke="#2563eb"
              strokeWidth={3}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Revenue by Customer Type */}
      <div className="chart-card">
        <h3>💰 Revenue by Customer Type</h3>

        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={revenueData}
              dataKey="sum"
              nameKey="customer_type"
              outerRadius={100}
              label
            >
              {revenueData.map((item, index) => (
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

      {/* Customer Distribution */}
      <div className="chart-card">
        <h3>📊 Customer Distribution</h3>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={distributionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="city" />
            <YAxis />
            <Tooltip />
            <Legend />

            <Bar
              dataKey="count"
              fill="#10b981"
              radius={[6, 6, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Top Customers */}
      <div className="chart-card">
        <h3>🏆 Top Customers</h3>

        <table className="customer-table">
          <thead>
            <tr>
              <th>Customer Name</th>
              <th>Total Revenue</th>
            </tr>
          </thead>

          <tbody>
            {topCustomersData.length > 0 ? (
              topCustomersData.map((customer, index) => (
                <tr key={index}>
                  <td>{customer.name}</td>
                  <td>₹ {customer.revenue}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="2"
                  style={{ textAlign: "center" }}
                >
                  No customer data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}