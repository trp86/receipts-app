import { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  getAnalyticsSummary,
  getSpendingByCategory,
  getSpendingByMonth,
  getTopStores,
  getRecentReceipts
} from '../services/api';
import QuantityAnalytics from './QuantityAnalytics';
import './Analytics.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

function Analytics() {
  const [activeTab, setActiveTab] = useState('spending'); // 'spending' | 'quantity'
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [categoryData, setCategoryData] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);
  const [topStores, setTopStores] = useState([]);
  const [recentReceipts, setRecentReceipts] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [summaryRes, categoryRes, monthlyRes, storesRes, recentRes] = await Promise.all([
        getAnalyticsSummary(),
        getSpendingByCategory(),
        getSpendingByMonth(),
        getTopStores(),
        getRecentReceipts()
      ]);

      setSummary(summaryRes.data);
      setCategoryData(categoryRes.data);
      setMonthlyData(monthlyRes.data);
      setTopStores(storesRes.data);
      setRecentReceipts(recentRes.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
      setError('Failed to load analytics data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-error">
        <p>❌ {error}</p>
        <button onClick={loadAnalyticsData}>Retry</button>
      </div>
    );
  }

  // Render quantity analytics tab
  if (activeTab === 'quantity') {
    return (
      <div className="analytics-container">
        <div className="analytics-tabs">
          <button
            className={activeTab === 'spending' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('spending')}
          >
            💰 Spending
          </button>
          <button
            className={activeTab === 'quantity' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('quantity')}
          >
            📦 Quantity
          </button>
        </div>
        <QuantityAnalytics />
      </div>
    );
  }

  return (
    <div className="analytics-container">
      <div className="analytics-tabs">
        <button
          className={activeTab === 'spending' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('spending')}
        >
          💰 Spending
        </button>
        <button
          className={activeTab === 'quantity' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('quantity')}
        >
          📦 Quantity
        </button>
      </div>

      <h2>📊 Spending Analytics</h2>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-icon">💰</div>
          <div className="card-content">
            <p className="card-label">Total Spent</p>
            <p className="card-value">€{summary?.total_spent?.toFixed(2) || '0.00'}</p>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">🧾</div>
          <div className="card-content">
            <p className="card-label">Receipts</p>
            <p className="card-value">{summary?.receipt_count || 0}</p>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">📊</div>
          <div className="card-content">
            <p className="card-label">Avg Receipt</p>
            <p className="card-value">€{summary?.avg_receipt?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
      </div>

      {/* Monthly Spending Trend */}
      {monthlyData.length > 0 && (
        <div className="chart-section">
          <h3>📈 Monthly Spending Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `€${value.toFixed(2)}`} />
              <Legend />
              <Line
                type="monotone"
                dataKey="total_spent"
                stroke="#8884d8"
                strokeWidth={2}
                name="Total Spent"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Category Breakdown */}
      {categoryData.length > 0 && (
        <div className="chart-section">
          <h3>🏷️ Spending by Category</h3>
          <div className="chart-row">
            <ResponsiveContainer width="50%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  dataKey="total_spent"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => `${entry.category}: €${entry.total_spent.toFixed(2)}`}
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-€{index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `€${value.toFixed(2)}`} />
              </PieChart>
            </ResponsiveContainer>

            <ResponsiveContainer width="50%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip formatter={(value) => `€${value.toFixed(2)}`} />
                <Bar dataKey="total_spent" fill="#82ca9d" name="Total Spent" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Top Stores */}
      {topStores.length > 0 && (
        <div className="chart-section">
          <h3>🏪 Top Stores</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topStores} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="store_name" type="category" width={150} />
              <Tooltip formatter={(value) => `€${value.toFixed(2)}`} />
              <Bar dataKey="total_spent" fill="#0088FE" name="Total Spent" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recent Receipts */}
      {recentReceipts.length > 0 && (
        <div className="chart-section">
          <h3>📋 Recent Receipts</h3>
          <div className="receipts-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Store</th>
                  <th>Items</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {recentReceipts.map((receipt) => (
                  <tr key={receipt.receipt_id}>
                    <td>{receipt.date}</td>
                    <td>{receipt.store_name}</td>
                    <td>{receipt.item_count}</td>
                    <td>€{receipt.total_amount.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {summary?.receipt_count === 0 && (
        <div className="empty-state">
          <p>📭 No receipts yet!</p>
          <p>Start scanning receipts to see your spending analytics.</p>
        </div>
      )}
    </div>
  );
}

export default Analytics;
