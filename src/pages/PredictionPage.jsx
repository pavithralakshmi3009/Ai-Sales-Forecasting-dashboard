import { useState } from 'react';
import { predictSales } from '../api';
import { useToast } from '../components/Toast';

export default function PredictionPage() {
  const { showToast } = useToast();
  const [month, setMonth] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [predMonth, setPredMonth] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!month || parseInt(month) <= 0) {
      showToast('Please enter a valid month', 'error');
      return;
    }

    setLoading(true);

    try {
      const result = await predictSales(month);

      if (result.ok) {
        setPrediction(result.data.predicted_sales);
        setPredMonth(result.data.month);
        showToast(`Predicted sales for Month ${month} computed`, 'success');
      } else {
        showToast(result.data?.error || 'Prediction failed', 'error');
        setPrediction(null);
      }
    } catch {
      showToast('Prediction service unavailable', 'error');
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (val) =>
    `₹ ${val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <div className="content-section">
      <div className="prediction-grid">
        {/* Forecast Setup Card */}
        <div className="glass-card prediction-config-card">
          <div className="card-header">
            <h3>Forecast Setup</h3>
          </div>
          <form onSubmit={handleSubmit} id="prediction-form">
            <div className="input-group">
              <label htmlFor="predict-month">Enter Future Month</label>
              <input
                type="number"
                id="predict-month"
                min="1"
                placeholder="e.g. 13"
                value={month}
                onChange={(e) => setMonth(e.target.value)}
                required
              />
              <span className="input-hint">
                Month 1–12 are historical, 13+ are future projections.
              </span>
            </div>

            <button
              type="submit"
              className="btn-success btn-block"
              disabled={loading}
            >
              <i className="fa-solid fa-bolt" />
              {loading ? 'Calculating...' : 'Generate Forecast'}
            </button>
          </form>
        </div>

        {/* Forecast Results Card */}
        <div className="glass-card prediction-result-card">
          <div className="card-header">
            <h3>Sales Forecast Results</h3>
          </div>
          <div className="prediction-display">
            <div className={`predict-icon-wrapper ${loading ? '' : 'animate-pulse'}`}>
              <i className="fa-solid fa-brain" />
            </div>
            <div className="predict-details">
              <p className="label">Predicted Sales Amount</p>
              <h2 id="prediction-result-val">
                {loading
                  ? 'Calculating...'
                  : prediction !== null
                  ? formatCurrency(prediction)
                  : '₹ 0.00'}
              </h2>
              <span className="badge badge-purple" id="prediction-month-badge">
                Month {predMonth || '-'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
