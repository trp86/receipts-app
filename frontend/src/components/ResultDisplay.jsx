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
            <h3>Items ({data.items.length})</h3>
            <ul className="items-list">
              {data.items.map((item, index) => (
                <li key={index} className="item-row">
                  <div className="item-info">
                    <div className="item-name-qty">
                      <span className="item-name">{item.name}</span>
                      {item.quantity && item.quantity > 1 && (
                        <span className="item-quantity">×{item.quantity}</span>
                      )}
                    </div>
                    {item.category && (
                      <span className="item-category">
                        {item.category}
                        {item.subcategory && ` / ${item.subcategory}`}
                      </span>
                    )}
                    {item.quantity && item.quantity > 1 && item.unit_price && (
                      <span className="item-unit-price">
                        €{item.unit_price} each
                      </span>
                    )}
                  </div>
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
