export default function StatCard({ title, value, icon, colorClass }) {
  return (
    <div className={`stat-card ${colorClass}`}>
      <div className="stat-icon">
        <i className={`fa-solid ${icon}`} />
      </div>
      <div className="stat-content">
        <h3>{title}</h3>
        <p>{value}</p>
      </div>
    </div>
  );
}
