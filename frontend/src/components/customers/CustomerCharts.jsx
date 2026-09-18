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
  revenueBySegment,
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
        revenueBySegment(),
        customerDistribution(),
        topCustomers(),
      ]);

      console.log("Customer Growth:", growthResponse);
      console.log(
          "REVENUE BY SEGMENT FULL:",
          JSON.stringify(revenueResponse, null, 2)
      );
      console.log("Customer Distribution:", distributionResponse);
      console.log("Top Customers:", topCustomersResponse);

      setGrowthData(
        Array.isArray(growthResponse)
          ? growthResponse
          : []
      );

      /*
       * Normalize Revenue Data
       *
       * Backend might return:
       *
       * { segment: "New", sum: 450000 }
       *
       * OR
       *
       * { segment: "New", revenue: 450000 }
       *
       * OR
       *
       * { segment: "New", total_revenue: 450000 }
       */

      const normalizedRevenue = Array.isArray(
        revenueResponse
      )
        ? revenueResponse.map((item) => ({
            segment:
              item.segment ||
              item.customer_segment ||
              "Unknown",

            revenue: Number(
              item.revenue ??
              item.sum ??
              item.total_revenue ??
              item.total ??
              0
            ),
          }))
        : [];

      console.log(
        "NORMALIZED REVENUE FULL:",
        JSON.stringify(normalizedRevenue, null, 2)
      );
      setRevenueData(normalizedRevenue);

      setDistributionData(
        Array.isArray(distributionResponse)
          ? distributionResponse
          : []
      );

      setTopCustomersData(
        Array.isArray(topCustomersResponse)
          ? topCustomersResponse
          : []
      );
    } catch (error) {
      console.error(
        "Error loading customer charts:",
        error
      );

      setGrowthData([]);
      setRevenueData([]);
      setDistributionData([]);
      setTopCustomersData([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="no-chart-data">
        Loading customer analytics...
      </div>
    );
  }

  return (
    <div className="customer-charts">

      {/* ================= Customer Growth ================= */}

      <div className="chart-card">
        <h3>📈 Customer Growth</h3>

        {growthData.length > 0 ? (
          <ResponsiveContainer
            width="100%"
            height={300}
          >
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
        ) : (
          <div className="no-chart-data">
            No customer growth data available
          </div>
        )}
      </div>


      {/* ================= Revenue By Segment ================= */}

      <div className="chart-card">
        <h3>💰 Revenue by Customer Segment</h3>

        {revenueData.length > 0 ? (
          <ResponsiveContainer
            width="100%"
            height={300}
          >
            <PieChart>

              <Pie
                data={revenueData}
                dataKey="revenue"
                nameKey="segment"
                outerRadius={100}
                label
              >
                {revenueData.map(
                  (entry, index) => (
                    <Cell
                      key={index}
                      fill={
                        COLORS[
                          index % COLORS.length
                        ]
                      }
                    />
                  )
                )}
              </Pie>

              <Tooltip
                formatter={(value) =>
                  `₹${Number(
                    value || 0
                  ).toLocaleString("en-IN")}`
                }
              />

              <Legend />

            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="no-chart-data">
            No revenue segment data available
          </div>
        )}
      </div>


      {/* ================= Customer Distribution ================= */}

      <div className="chart-card">
        <h3>📍 Customer Distribution</h3>

        {distributionData.length > 0 ? (
          <ResponsiveContainer
            width="100%"
            height={300}
          >
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
        ) : (
          <div className="no-chart-data">
            No customer distribution data available
          </div>
        )}
      </div>


      {/* ================= Top Customers ================= */}

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
              topCustomersData.map(
                (customer, index) => (
                  <tr
                    key={
                      customer.id || index
                    }
                  >

                    <td>
                      {customer.name || "-"}
                    </td>

                    <td>
                      ₹
                      {Number(
                        customer.revenue || 0
                      ).toLocaleString(
                        "en-IN",
                        {
                          minimumFractionDigits: 2,
                        }
                      )}
                    </td>

                  </tr>
                )
              )
            ) : (
              <tr>
                <td
                  colSpan="2"
                  style={{
                    textAlign: "center",
                  }}
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