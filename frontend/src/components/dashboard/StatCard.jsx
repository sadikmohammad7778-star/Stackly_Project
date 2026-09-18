import "./StatCard.css";

export default function StatCard({
  title,
  value,
  icon,
  color,
}) {
  return (
    <div
      className="stat-card"
      style={{
        borderTop: `5px solid ${color}`,
      }}
    >
      <div className="stat-content">
        <h4>{title}</h4>
        <h2>{value}</h2>
      </div>

      <div
        className="stat-icon"
        style={{
          backgroundColor: color,
        }}
      >
        {icon}
      </div>
    </div>
  );
}