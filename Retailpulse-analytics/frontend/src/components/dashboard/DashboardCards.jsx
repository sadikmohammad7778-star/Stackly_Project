import {
  FiBriefcase,
  FiUsers,
  FiGrid,
  FiShoppingBag,
  FiShoppingCart,
  FiDollarSign,
  FiAlertTriangle,
  FiPackage,
} from "react-icons/fi";

import StatCard from "./StatCard";

export default function DashboardCards({ data }) {
  const cards = [
    {
      title: "Companies",
      value: data?.total_companies ?? 0,
      color: "#6366F1",
      icon: <FiBriefcase />,
    },
    {
      title: "Users",
      value: data?.total_users ?? 0,
      color: "#10B981",
      icon: <FiUsers />,
    },
    {
      title: "Categories",
      value: data?.total_categories ?? 0,
      color: "#F59E0B",
      icon: <FiGrid />,
    },
    {
      title: "Products",
      value: data?.total_products ?? 0,
      color: "#3B82F6",
      icon: <FiShoppingBag />,
    },
    {
      title: "Sales",
      value: data?.total_sales ?? 0,
      color: "#8B5CF6",
      icon: <FiShoppingCart />,
    },
    {
      title: "Revenue",
      value: `₹${Number(data?.total_revenue ?? 0).toLocaleString()}`,
      color: "#22C55E",
      icon: <FiDollarSign />,
    },
    {
      title: "Low Stock",
      value: data?.low_stock_products ?? 0,
      color: "#F97316",
      icon: <FiAlertTriangle />,
    },
    {
      title: "Out of Stock",
      value: data?.out_of_stock_products ?? 0,
      color: "#EF4444",
      icon: <FiPackage />,
    },
  ];

  return (
    <div className="cards-grid">
      {cards.map((card, index) => (
        <StatCard key={index} {...card} />
      ))}
    </div>
  );
}