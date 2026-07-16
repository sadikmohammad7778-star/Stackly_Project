import { useEffect, useState } from "react";
import {
  FaBoxes,
  FaCheckCircle,
  FaTimesCircle,
  FaTags,
} from "react-icons/fa";

import { getDashboardSummary } from "../../services/dashboardService";
import "./DashboardCards.css";

function DashboardCards() {
  const [summary, setSummary] = useState({
    total_products: 0,
    active_products: 0,
    inactive_products: 0,
    total_categories: 0,
  });

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (error) {
      console.error("Error loading dashboard:", error);
    }
  };

  const cards = [
    {
      title: "Total Products",
      value: summary.total_products,
      icon: <FaBoxes />,
    },
    {
      title: "Active Products",
      value: summary.active_products,
      icon: <FaCheckCircle />,
    },
    {
      title: "Inactive Products",
      value: summary.inactive_products,
      icon: <FaTimesCircle />,
    },
    {
      title: "Total Categories",
      value: summary.total_categories,
      icon: <FaTags />,
    },
  ];

  return (
    <div className="cards">
      {cards.map((card, index) => (
        <div className="card" key={index}>
          <div className="card-icon">{card.icon}</div>

          <div>
            <h4>{card.title}</h4>
            <h2>{card.value}</h2>
          </div>
        </div>
      ))}
    </div>
  );
}

export default DashboardCards;