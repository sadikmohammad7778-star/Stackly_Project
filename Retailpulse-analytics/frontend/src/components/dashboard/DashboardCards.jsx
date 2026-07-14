import {
  FiBriefcase,
  FiUsers,
  FiGrid,
  FiCalendar,
} from "react-icons/fi";

import StatCard from "./StatCard";

export default function DashboardCards({ data }) {

  const cards = [

    {
      title: "Companies",
      value: data?.companies ?? 0,
      color: "#6366F1",
      icon: <FiBriefcase />,
    },

    {
      title: "Employees",
      value: data?.employees ?? 0,
      color: "#10B981",
      icon: <FiUsers />,
    },

    {
      title: "Departments",
      value: data?.departments ?? 0,
      color: "#F59E0B",
      icon: <FiGrid />,
    },

    {
      title: "Attendance",
      value: data?.attendance ?? 0,
      color: "#EF4444",
      icon: <FiCalendar />,
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