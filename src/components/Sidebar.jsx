import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const menuItems = [
  { to: '/', icon: 'fa-house', label: 'Dashboard' },
  { to: '/sales', icon: 'fa-boxes-stacked', label: 'Sales Management' },
  { to: '/prediction', icon: 'fa-brain', label: 'AI Prediction' },
  { to: '/analytics', icon: 'fa-chart-simple', label: 'Sales Graph' },
];

export default function Sidebar() {
  const { logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <i className="fa-solid fa-chart-pie logo-icon-sm" />
        <h2>AI Forecast</h2>
      </div>

      <nav className="sidebar-menu">
        {menuItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `menu-item ${isActive ? 'active' : ''}`
            }
          >
            <i className={`fa-solid ${item.icon}`} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="avatar">
            <i className="fa-solid fa-user-tie" />
          </div>
          <div className="user-info">
            <span className="user-name">Administrator</span>
            <span className="user-role">Super User</span>
          </div>
        </div>
        <button className="btn-logout" onClick={logout} id="btn-logout">
          <i className="fa-solid fa-arrow-right-from-bracket" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}
