import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { getStats, getSales } from '../api';
import { useToast } from '../components/Toast';
import StatCard from '../components/StatCard';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function DashboardPage() {
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ total_sales: 0, total_profit: 0, total_orders: 0 });
  const [sales, setSales] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, salesRes] = await Promise.all([
        getStats(),
        getSales(100),
      ]);

      if (statsRes.ok) setStats(statsRes.data);
      else showToast('Failed to load dashboard metrics', 'error');

      if (salesRes.ok) setSales(salesRes.data);
      else showToast('Failed to load sales records', 'error');
    } catch {
      showToast('Connection error loading dashboard', 'error');
    }
  };

  // Build doughnut chart data from sales by category
  const categoryTotals = {};
  sales.forEach((s) => {
    categoryTotals[s.category] = (categoryTotals[s.category] || 0) + s.total;
  });

  const chartColors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4'];

  const chartData = {
    labels: Object.keys(categoryTotals),
    datasets: [
      {
        data: Object.values(categoryTotals),
        backgroundColor: chartColors.slice(0, Object.keys(categoryTotals).length),
        borderWidth: 2,
        borderColor: '#101626',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#94A3B8',
          font: { family: 'Outfit', size: 12 },
        },
      },
    },
  };

  const latestSales = [...sales].reverse().slice(0, 5);

  const formatCurrency = (val) =>
    `₹ ${val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <div className="content-section">
      {/* Stats Cards */}
      <div className="stats-grid">
        <StatCard
          title="Total Sales"
          value={formatCurrency(stats.total_sales)}
          icon="fa-indian-rupee-sign"
          colorClass="blue"
        />
        <StatCard
          title="Total Profit"
          value={formatCurrency(stats.total_profit)}
          icon="fa-wallet"
          colorClass="green"
        />
        <StatCard
          title="Total Orders"
          value={stats.total_orders}
          icon="fa-shopping-bag"
          colorClass="orange"
        />
      </div>

      {/* Dashboard Grid */}
      <div className="dashboard-grid">
        {/* Chart Card */}
        <div className="glass-card main-chart-preview">
          <div className="card-header">
            <h3>Sales Distribution</h3>
            <span className="badge">Live Preview</span>
          </div>
          <div className="canvas-container">
            {Object.keys(categoryTotals).length > 0 ? (
              <Doughnut data={chartData} options={chartOptions} />
            ) : (
              <div className="empty-state">No sales data to display</div>
            )}
          </div>
        </div>

        {/* Recent Orders */}
        <div className="glass-card latest-sales-preview">
          <div className="card-header">
            <h3>Recent Orders</h3>
            <button
              className="btn-text-action"
              onClick={() => navigate('/sales')}
              id="btn-view-all-sales"
            >
              View All
            </button>
          </div>
          <div className="recent-list-container">
            <table className="data-table-minimal">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {latestSales.length === 0 ? (
                  <tr>
                    <td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                      No sales recorded yet.
                    </td>
                  </tr>
                ) : (
                  latestSales.map((s) => (
                    <tr key={s.id}>
                      <td>{s.date}</td>
                      <td style={{ fontWeight: 500, color: 'white' }}>{s.product}</td>
                      <td><span className="badge">{s.category}</span></td>
                      <td style={{ fontWeight: 600, color: 'var(--accent-blue)' }}>
                        ₹ {s.total.toFixed(2)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
