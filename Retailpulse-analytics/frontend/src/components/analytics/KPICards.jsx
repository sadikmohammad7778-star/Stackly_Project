import {
  FiDollarSign,
  FiShoppingCart,
  FiPackage,
  FiAlertTriangle,
  FiLayers,
  FiTrendingUp,
  FiBox,
  FiArchive,
} from "react-icons/fi";

import "./AnalyticsComponents.css";

export default function KPICards({ data }) {
 const cards = [
  {
    title: "Total Revenue",
    value: `₹${(data.total_revenue || 0).toLocaleString()}`,
    icon: <FiDollarSign />,
  },
  {
    title: "Total Orders",
    value: (data.total_orders || 0).toLocaleString(),
    icon: <FiShoppingCart />,
  },
  {
    title: "Products Sold",
    value: (data.total_products_sold || 0).toLocaleString(),
    icon: <FiPackage />,
  },
  {
    title: "Average Order",
    value: `₹${(data.average_order_value || 0).toLocaleString()}`,
    icon: <FiDollarSign />,
  },
  {
    title: "Inventory Value",
    value: `₹${(data.total_inventory_value || 0).toLocaleString()}`,
    icon: <FiPackage />,
  },
  {
    title: "Low Stock",
    value: (data.low_stock_products || 0).toLocaleString(),
    icon: <FiAlertTriangle />,
  },
  {
    title: "Out of Stock",
    value: (data.out_of_stock_products || 0).toLocaleString(),
    icon: <FiAlertTriangle />,
  },
  {
    title: "Categories",
    value: (data.total_categories || 0).toLocaleString(),
    icon: <FiPackage />,
  },
];

  return (
    <div className="kpi-grid">
      {cards.map((card) => (
        <div className="kpi-card" key={card.title}>
          <div className="kpi-icon">
            {card.icon}
          </div>

          <div className="kpi-content">
            <h4>{card.title}</h4>
            <h2>{card.value}</h2>
          </div>
        </div>
      ))}
    </div>
  );
}