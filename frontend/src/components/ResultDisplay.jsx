function ResultDisplay({ data, onReset }) {
  return (
    <div className="result-container">
      <div className="result-card">
        <h2>✓ Receipt Processed</h2>

        <div className="result-section">
          <div className="result-row">
            <span className="label">Store:</span>
            <span className="value">{data.store_name || 'N/A'}</span>
          </div>

          <div className="result-row">
            <span className="label">Date:</span>
            <span className="value">{data.date || 'N/A'}</span>
          </div>

          <div className="result-row total">
            <span className="label">Total:</span>
            <span className="value">€{data.total_amount || '0.00'}</span>
          </div>
        </div>

        {data.items && data.items.length > 0 && (
          <div className="result-section">
            <h3>Items</h3>
            <ul className="items-list">
              {data.items.map((item, index) => (
                <li key={index} className="item-row">
                  <span className="item-name">{item.name}</span>
                  <span className="item-price">€{item.price}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <button onClick={onReset} className="btn-primary">
          📸 Scan New Receipt
        </button>
      </div>
    </div>
  );
}

export default ResultDisplay;
