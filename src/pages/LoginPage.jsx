import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';

export default function LoginPage() {
  const { login } = useAuth();
  const { showToast } = useToast();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username || !password) {
      setError('Username and password are required');
      return;
    }

    try {
      const result = await login(username, password);
      if (result.ok) {
        showToast('Welcome back, admin!', 'success');
      } else {
        const serverError = result.data?.message || result.data?.error || 'Login failed';
        setError(serverError);
      }
    } catch (err) {
      console.error("Login fetch error:", err);
      setError('Cannot connect to API backend. Please check network connectivity and backend deployment.');
    }
  };

  return (
    <div className="overlay">
      <div className="login-card">
        <div className="login-header">
          <div className="logo-icon">
            <i className="fa-solid fa-chart-line" />
          </div>
          <h1>AI Sales Forecasting</h1>
          <p>Enter credentials to access dashboard</p>
        </div>

        <form onSubmit={handleSubmit} id="login-form">
          <div className="input-group">
            <label htmlFor="username">
              <i className="fa-solid fa-user" /> Username
            </label>
            <input
              type="text"
              id="username"
              placeholder="e.g., admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">
              <i className="fa-solid fa-lock" /> Password
            </label>
            <div className="password-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                placeholder="e.g., admin123"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="btn-toggle"
                onClick={() => setShowPassword(!showPassword)}
                id="toggle-password"
              >
                <i className={`fa-regular ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`} />
              </button>
            </div>
          </div>

          {error && <div className="error-msg">{error}</div>}

          <button type="submit" className="btn-login" id="btn-login-submit">
            Login <i className="fa-solid fa-arrow-right-to-bracket" />
          </button>
        </form>

        <div className="login-footer">
          Developed Using Python + AI/ML
        </div>
      </div>
    </div>
  );
}
