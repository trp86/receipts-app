import { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  getQuantitySummary,
  getTopBulkItems,
  getQuantityByCategory,
  getUnitPriceInsights,
  getQuantityTrends
} from '../services/api';
import './QuantityAnalytics.css';

function QuantityAnalytics() {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [bulkItems, setBulkItems] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [priceInsights, setPriceInsights] = useState([]);
  const [trendsData, setTrendsData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadQuantityData();
  }, []);

  const loadQuantityData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [summaryRes, bulkRes, categoryRes, priceRes, trendsRes] = await Promise.all([
        getQuantitySummary(),
        getTopBulkItems(null, 10),
        getQuantityByCategory(),
        getUnitPriceInsights(null, 10),
        getQuantityTrends(null, 6)
      ]);

      setSummary(summaryRes.data);
      setBulkItems(bulkRes.data);
      setCategoryData(categoryRes.data);
      setPriceInsights(priceRes.data);
      setTrendsData(trendsRes.data);
    } catch (err) {
      console.error('Failed to load quantity analytics:', err);
      setError('Failed to load quantity data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="spinner"></div>
        <p>Loading quantity analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-error">
        <p>❌ {error}</p>
        <button onClick={loadQuantityData}>Retry</button>
      </div>
    );
  }

  // Process trends data for visualization
  const processedTrends = () => {
    if (!trendsData || trendsData.length === 0) return [];

    // Group by month
    const monthMap = {};
    trendsData.forEach(item => {
      if (!monthMap[item.month]) {
        monthMap[item.month] = { month: item.month };
      }
      monthMap[item.month][item.category] = item.avg_quantity;
    });

    return Object.values(monthMap);
  };

  // Get unique categories for trend chart
  const trendCategories = [...new Set(trendsData.map(item => item.category))].slice(0, 5);

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088fe'];

  return (
    <div className="quantity-analytics-container">
      <h2>📦 Quantity Analytics</h2>
      <p className="subtitle">Bulk buying patterns and unit price insights</p>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-icon">📦</div>
          <div className="card-content">
            <p className="card-label">Items in Bulk</p>
            <p className="card-value">{summary?.items_in_bulk || 0}</p>
            <p className="card-subtext">{summary?.bulk_percentage || 0}% of all items</p>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">📊</div>
          <div className="card-content">
            <p className="card-label">Total Units</p>
            <p className="card-value">{Math.round(summary?.total_units || 0)}</p>
            <p className="card-subtext">items purchased</p>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">🔢</div>
          <div className="card-content">
            <p className="card-label">Avg Quantity</p>
            <p className="card-value">{summary?.avg_quantity || 0}×</p>
            <p className="card-subtext">per purchase</p>
          </div>
        </div>
      </div>

      {/* Top Bulk Items */}
      {bulkItems.length > 0 && (
        <div className="chart-section">
          <h3>🏆 Top Bulk Items</h3>
          <div className="bulk-items-list">
            {bulkItems.map((item, index) => (
              <div key={index} className="bulk-item-card">
                <div className="bulk-item-rank">#{index + 1}</div>
                <div className="bulk-item-details">
                  <h4>{item.item_name}</h4>
                  <p className="bulk-item-category">{item.category}</p>
                  <div className="bulk-item-stats">
                    <span className="stat">
                      <strong>{item.avg_quantity}×</strong> avg quantity
                    </span>
                    <span className="stat">
                      <strong>{item.times_purchased}</strong> purchases
                    </span>
                    <span className="stat">
                      <strong>{Math.round(item.total_units)}</strong> total units
                    </span>
                  </div>
                  <p className="bulk-item-spent">
                    Total spent: <strong>€{item.total_spent.toFixed(2)}</strong>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Average Quantity by Category */}
      {categoryData.length > 0 && (
        <div className="chart-section">
          <h3>📊 Average Quantity by Category</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" angle={-45} textAnchor="end" height={120} />
              <YAxis label={{ value: 'Avg Quantity', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                formatter={(value, name) => {
                  if (name === 'avg_quantity') return [`${value}×`, 'Avg Quantity'];
                  return [value, name];
                }}
              />
              <Bar dataKey="avg_quantity" fill="#82ca9d" name="Avg Quantity" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Unit Price Insights */}
      {priceInsights.length > 0 && (
        <div className="chart-section">
          <h3>💰 Unit Price Insights</h3>
          <div className="price-insights-table">
            <table>
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Category</th>
                  <th>Best Price</th>
                  <th>Avg Price</th>
                  <th>Highest</th>
                  <th>Variation</th>
                  <th>Potential Savings</th>
                </tr>
              </thead>
              <tbody>
                {priceInsights.map((item, index) => (
                  <tr key={index}>
                    <td className="item-name">{item.item_name}</td>
                    <td>{item.category}</td>
                    <td className="price-best">€{item.best_price.toFixed(2)}</td>
                    <td>€{item.avg_unit_price.toFixed(2)}</td>
                    <td className="price-high">€{item.highest_price.toFixed(2)}</td>
                    <td>
                      <span className="price-variation">
                        €{item.price_variation.toFixed(2)}
                      </span>
                    </td>
                    <td className="savings">
                      €{item.potential_savings.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="insights-note">
            💡 <strong>Tip:</strong> Potential savings show how much you could save by always buying at the best price.
          </p>
        </div>
      )}

      {/* Quantity Trends Over Time */}
      {trendsData.length > 0 && (
        <div className="chart-section">
          <h3>📈 Quantity Trends (Last 6 Months)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={processedTrends()}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis label={{ value: 'Avg Quantity', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              {trendCategories.map((category, index) => (
                <Line
                  key={category}
                  type="monotone"
                  dataKey={category}
                  stroke={COLORS[index % COLORS.length]}
                  strokeWidth={2}
                  name={category}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Empty State */}
      {summary?.items_in_bulk === 0 && (
        <div className="empty-state">
          <p>📦 No bulk purchases yet!</p>
          <p>Start buying items in quantity to see your bulk buying patterns.</p>
        </div>
      )}
    </div>
  );
}

export default QuantityAnalytics;
