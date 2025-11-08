import React from 'react';

const Counters = ({ stats, onTotalClick, onLegitClick, onFraudClick }) => {
  const fraudPercentage = stats.total > 0
    ? ((stats.fraud / stats.total) * 100).toFixed(1)
    : '0.0';

  const legitPercentage = stats.total > 0
    ? ((stats.legit / stats.total) * 100).toFixed(1)
    : '0.0';

  const cardStyle = (gradient) => ({
    background: `linear-gradient(135deg, ${gradient})`,
    border: 'none',
    borderRadius: '16px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
    backdropFilter: 'blur(10px)'
  });

  const hoverStyle = {
    transform: 'translateY(-8px) scale(1.02)',
    boxShadow: '0 15px 40px rgba(0, 0, 0, 0.4)'
  };

  return (
    <div className="row g-4 mb-4">
      {/* Total Transactions Card */}
      <div className="col-md-4">
        <div
          className="card h-100 text-center text-white"
          style={cardStyle('rgba(67, 97, 238, 0.3), rgba(64, 224, 208, 0.3)')}
          onClick={onTotalClick}
          onMouseEnter={(e) => {
            Object.assign(e.currentTarget.style, hoverStyle);
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0) scale(1)';
            e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.3)';
          }}
        >
          <div className="card-body p-4">
            <div className="mb-3" style={{ fontSize: '2.5rem' }}>📊</div>
            <h5 className="text-white-50 text-uppercase fw-bold mb-3" style={{ fontSize: '0.9rem', letterSpacing: '1px' }}>
              Total Transactions
            </h5>
            <h2 className="display-4 fw-bold mb-3">{stats.total.toLocaleString()}</h2>
            {onTotalClick && (
              <div className="mt-3 pt-3 border-top border-white border-opacity-25">
                <p className="mb-0 text-white-50 small">👆 Click to view all</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Legitimate Transactions Card */}
      <div className="col-md-4">
        <div
          className="card h-100 text-center text-white"
          style={cardStyle('rgba(46, 213, 115, 0.3), rgba(0, 184, 148, 0.3)')}
          onClick={onLegitClick}
          onMouseEnter={(e) => {
            Object.assign(e.currentTarget.style, hoverStyle);
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0) scale(1)';
            e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.3)';
          }}
        >
          <div className="card-body p-4">
            <div className="mb-3" style={{ fontSize: '2.5rem' }}>✅</div>
            <h5 className="text-white-50 text-uppercase fw-bold mb-3" style={{ fontSize: '0.9rem', letterSpacing: '1px' }}>
              Legitimate
            </h5>
            <h2 className="display-4 fw-bold mb-2 text-white">{stats.legit.toLocaleString()}</h2>
            <p className="h4 mb-3 text-white-50">{legitPercentage}%</p>
            {onLegitClick && (
              <div className="mt-3 pt-3 border-top border-white border-opacity-25">
                <p className="mb-0 text-white-50 small">👆 Click to view legit only</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Fraudulent Transactions Card */}
      <div className="col-md-4">
        <div
          className="card h-100 text-center text-white"
          style={cardStyle('rgba(255, 71, 87, 0.3), rgba(255, 99, 132, 0.3)')}
          onClick={onFraudClick}
          onMouseEnter={(e) => {
            Object.assign(e.currentTarget.style, hoverStyle);
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0) scale(1)';
            e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.3)';
          }}
        >
          <div className="card-body p-4">
            <div className="mb-3" style={{ fontSize: '2.5rem' }}>⚠️</div>
            <h5 className="text-white-50 text-uppercase fw-bold mb-3" style={{ fontSize: '0.9rem', letterSpacing: '1px' }}>
              Fraudulent
            </h5>
            <h2 className="display-4 fw-bold mb-2 text-white">{stats.fraud.toLocaleString()}</h2>
            <p className="h4 mb-3 text-white-50">{fraudPercentage}%</p>
            {onFraudClick && (
              <div className="mt-3 pt-3 border-top border-white border-opacity-25">
                <p className="mb-0 text-white-50 small">👆 Click to view fraud only</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Counters;
