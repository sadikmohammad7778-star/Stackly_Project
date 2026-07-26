import { useEffect, useState } from "react";

import {
  getDashboardKPIs,
  getRevenueTrend,
  getTopProducts,
  getTopCategories,
  getPaymentMethods,
  getSalesChannels,
  getInventoryCategory,
  getStockStatus,
  getInventoryValue,
} from "../api/analyticsApi";

import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

import KPICards from "../components/analytics/KPICards";
import RevenueChart from "../components/analytics/RevenueChart";
import ProductChart from "../components/analytics/ProductChart";
import TopCategoryChart from "../components/analytics/TopCategoryChart";
import PaymentChart from "../components/analytics/PaymentChart";
import SalesChannelChart from "../components/analytics/SalesChannelChart";
import InventoryCategoryChart from "../components/analytics/InventoryCategoryChart";
import StockStatusChart from "../components/analytics/StockStatusChart";
import InventoryValueChart from "../components/analytics/InventoryValueChart";
import "./Analytics.css";

export default function Analytics() {
  const companyId = 3;

  const [kpis, setKpis] = useState({});
  const [revenueTrend, setRevenueTrend] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [topCategories, setTopCategories] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [salesChannels, setSalesChannels] = useState([]);
  const [inventoryCategory, setInventoryCategory] = useState([]);
  const [stockStatus, setStockStatus] = useState([]);
  const [inventoryValue, setInventoryValue] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("month");

  useEffect(() => {
    loadAnalytics();
  }, [filter]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        dashboard,
        revenue,
        products,
        categories,
        payments,
        channels,
        inventoryCategoryData,
        stock,
        inventoryValueData,
      ] = await Promise.all([
       getDashboardKPIs(companyId, filter),
       getRevenueTrend(companyId, filter),
       getTopProducts(companyId, filter),
       getTopCategories(companyId, filter),
       getPaymentMethods(companyId, filter),
       getSalesChannels(companyId, filter),
       getInventoryCategory(companyId, filter),
       getStockStatus(companyId, filter),
       getInventoryValue(companyId, filter),
      ]);

      setKpis(dashboard);
      setRevenueTrend(revenue);
      setTopProducts(products);
      setTopCategories(categories);
      setPaymentMethods(payments);
      setSalesChannels(channels);
      setInventoryCategory(inventoryCategoryData);
      setStockStatus(stock);
      setInventoryValue(inventoryValueData);
    } catch (err) {
      console.error(err);
      setError("Unable to load analytics.");
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = () => {
    const rows = [];

    rows.push(["Retail Analytics Dashboard"]);
    rows.push(["Generated On", new Date().toLocaleString()]);
    rows.push([]);

    rows.push(["Dashboard KPIs"]);
    rows.push(["Metric", "Value"]);
    rows.push(["Total Revenue", kpis.total_revenue]);
    rows.push(["Total Orders", kpis.total_orders]);
    rows.push(["Products Sold", kpis.total_products_sold]);
    rows.push(["Average Order Value", kpis.average_order_value]);
    rows.push(["Inventory Value", kpis.total_inventory_value]);
    rows.push(["Low Stock", kpis.low_stock_products]);
    rows.push(["Out Of Stock", kpis.out_of_stock_products]);
    rows.push(["Categories", kpis.total_categories]);

    rows.push([]);
    rows.push(["Revenue Trend"]);
    rows.push(["Date", "Revenue"]);
    revenueTrend.forEach((item) =>
      rows.push([item.date, item.revenue])
    );

    rows.push([]);
    rows.push(["Top Products"]);
    rows.push(["Product", "Quantity Sold"]);
    topProducts.forEach((item) =>
      rows.push([item.product_name, item.quantity_sold])
    );

    rows.push([]);
    rows.push(["Top Categories"]);
    rows.push(["Category", "Revenue"]);
    topCategories.forEach((item) =>
      rows.push([item.category_name, item.revenue])
    );

    rows.push([]);
    rows.push(["Payment Methods"]);
    rows.push(["Method", "Sales"]);
    paymentMethods.forEach((item) =>
      rows.push([item.payment_method, item.total_sales])
    );

    rows.push([]);
    rows.push(["Sales Channels"]);
    rows.push(["Channel", "Sales"]);
    salesChannels.forEach((item) =>
      rows.push([item.sales_channel, item.total_sales])
    );

    rows.push([]);
    rows.push(["Inventory"]);
    rows.push(["Category", "Available Stock"]);
    inventoryCategory.forEach((item) =>
      rows.push([item.category_name, item.available_stock])
    );

    rows.push([]);
    rows.push(["Stock Status"]);
    rows.push(["Status", "Count"]);
    stockStatus.forEach((item) =>
      rows.push([item.stock_status, item.count])
    );

    rows.push([]);
    rows.push(["Inventory Value"]);
    rows.push(["Category", "Value"]);
    inventoryValue.forEach((item) =>
      rows.push([item.category_name, item.inventory_value])
    );

    const csv = rows.map((row) => row.join(",")).join("\n");

    const blob = new Blob([csv], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "Retail_Analytics_Report.csv";
    link.click();

    URL.revokeObjectURL(url);
  };

  const exportPDF = () => {
  const doc = new jsPDF();

  // Title
  doc.setFontSize(20);
  doc.text("Retail Analytics Dashboard", 14, 20);

  doc.setFontSize(11);
  doc.text(
    `Generated On: ${new Date().toLocaleString()}`,
    14,
    30
  );

  // KPI Table
  autoTable(doc, {
    startY: 40,
    head: [["Metric", "Value"]],
    body: [
      ["Total Revenue", `₹${kpis.total_revenue || 0}`],
      ["Total Orders", kpis.total_orders || 0],
      ["Products Sold", kpis.total_products_sold || 0],
      ["Average Order Value", `₹${kpis.average_order_value || 0}`],
      ["Inventory Value", `₹${kpis.total_inventory_value || 0}`],
      ["Low Stock", kpis.low_stock_products || 0],
      ["Out Of Stock", kpis.out_of_stock_products || 0],
      ["Categories", kpis.total_categories || 0],
    ],
  });

  // Top Products
  autoTable(doc, {
    startY: doc.lastAutoTable.finalY + 15,
    head: [["Product", "Quantity Sold"]],
    body: topProducts.map((item) => [
      item.product_name,
      item.quantity_sold,
    ]),
  });

  // Top Categories
  autoTable(doc, {
    startY: doc.lastAutoTable.finalY + 15,
    head: [["Category", "Revenue"]],
    body: topCategories.map((item) => [
      item.category_name,
      item.revenue,
    ]),
  });

  doc.save("Retail_Analytics_Report.pdf");
};

  if (loading) {
    return (
      <div className="analytics-loading">
        <h2>Loading Analytics...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-error">
        <h2>{error}</h2>
        <button onClick={loadAnalytics}>Retry</button>
      </div>
    );
  }

  return (
    <div className="analytics-page">

      {/* Dashboard Header */}
      <div className="dashboard-header">

        <div>
          <h2>Retail Analytics Dashboard</h2>
          <p>Business insights and performance overview</p>
        </div>

        <div className="dashboard-actions">

          <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
            </select>
          <button
            className="refresh-btn"
            onClick={loadAnalytics}
          >
            Refresh
          </button>

          <div className="export-buttons">

              <button
                className="export-btn"
                onClick={exportCSV}
              >
                Export CSV
              </button>

              <button
                className="pdf-btn"
                onClick={exportPDF}
              >
                Export PDF
              </button>

            </div>

        </div>

      </div>

      {/* KPI Cards */}
      <KPICards data={kpis} />

      {/* Charts */}
      <div className="chart-grid">

        <RevenueChart data={revenueTrend} />

        <ProductChart data={topProducts} />

        <TopCategoryChart data={topCategories} />

        <PaymentChart data={paymentMethods} />

        <SalesChannelChart data={salesChannels} />

        <InventoryCategoryChart data={inventoryCategory} />

        <StockStatusChart data={stockStatus} />

        <InventoryValueChart data={inventoryValue} />

      </div>

    </div>
  );
}