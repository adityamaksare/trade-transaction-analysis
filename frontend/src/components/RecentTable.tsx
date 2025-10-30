import React from 'react';

interface Transaction {
  trade_id: string;
  trader_id: string;
  symbol: string;
  quantity: number;
  price: number;
  timestamp: string;
  order_type: string;
  label: string;
  confidence: number;
  reason: string;
  processed_at: string;
}

interface RecentTableProps {
  transactions: Transaction[];
}

const RecentTable: React.FC<RecentTableProps> = ({ transactions }) => {
  return (
    <div 
      className="card border-0" 
      style={{ 
        background: '#ffffff',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        borderRadius: '16px',
        overflow: 'hidden',
        border: '2px solid #e0e0e0'
      }}
    >
      <div 
        className="card-header border-0"
        style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderBottom: '2px solid #667eea',
          padding: '1.25rem'
        }}
      >
        <div className="d-flex align-items-center justify-content-between">
          <h3 className="mb-0 text-white fw-bold" style={{ fontSize: '1.5rem' }}>
            <span className="me-2">📋</span>
            Transaction History
          </h3>
          <span className="badge" style={{
            background: 'rgba(255, 255, 255, 0.2)',
            color: 'white',
            border: '2px solid rgba(255, 255, 255, 0.3)',
            padding: '0.5rem 1rem',
            fontSize: '0.95rem'
          }}>
            {transactions.length} records
          </span>
        </div>
      </div>
      <div className="card-body p-0">
        <div className="table-responsive" style={{ maxHeight: '600px', overflowY: 'auto' }}>
          <table className="table table-hover mb-0">
            <thead style={{ 
              background: '#f8f9fa',
              position: 'sticky',
              top: 0,
              zIndex: 10,
              borderBottom: '2px solid #dee2e6',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <tr>
                <th className="text-dark fw-bold border-0" style={{ padding: '1rem 0.75rem' }}>Trade ID</th>
                <th className="text-dark fw-bold border-0" style={{ padding: '1rem 0.75rem' }}>Trader</th>
                <th className="text-dark fw-bold border-0" style={{ padding: '1rem 0.75rem' }}>Symbol</th>
                <th className="text-dark fw-bold border-0 text-end" style={{ padding: '1rem 0.75rem' }}>Quantity</th>
                <th className="text-dark fw-bold border-0 text-end" style={{ padding: '1rem 0.75rem' }}>Price</th>
                <th className="text-dark fw-bold border-0 text-center" style={{ padding: '1rem 0.75rem' }}>Type</th>
                <th className="text-dark fw-bold border-0 text-center" style={{ padding: '1rem 0.75rem' }}>Label</th>
                <th className="text-dark fw-bold border-0 text-center" style={{ padding: '1rem 0.75rem' }}>Confidence</th>
                <th className="text-dark fw-bold border-0" style={{ padding: '1rem 0.75rem' }}>Reason</th>
                <th className="text-dark fw-bold border-0" style={{ padding: '1rem 0.75rem' }}>Time</th>
              </tr>
            </thead>
            <tbody>
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan={10} className="text-center text-muted py-5">
                    <div className="py-4">
                      <div style={{ fontSize: '3rem', opacity: 0.3 }}>⏳</div>
                      <p className="mt-3 mb-0 text-dark">Waiting for transactions...</p>
                      <p className="small text-muted mt-2">Transactions will appear here in real-time</p>
                    </div>
                  </td>
                </tr>
              ) : (
                transactions.map((tx, index) => (
                  <tr 
                    key={tx.trade_id} 
                    style={{
                      borderLeft: tx.label === 'fraud' ? '5px solid #ff4757' : '5px solid #2ed573',
                      background: index % 2 === 0 ? '#ffffff' : '#f8f9fa',
                      borderBottom: '1px solid #dee2e6'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = tx.label === 'fraud' 
                        ? '#ffe6e6' 
                        : '#e6f9e6';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = index % 2 === 0 ? '#ffffff' : '#f8f9fa';
                    }}
                  >
                    <td className="text-dark fw-bold" style={{ padding: '1rem 0.75rem' }}>{tx.trade_id}</td>
                    <td className="text-dark" style={{ padding: '1rem 0.75rem' }}>{tx.trader_id}</td>
                    <td className="text-dark fw-bold" style={{ padding: '1rem 0.75rem' }}>
                      <span className="badge" style={{
                        background: '#667eea',
                        color: 'white',
                        border: 'none',
                        padding: '0.4rem 0.8rem',
                        fontSize: '0.9rem'
                      }}>
                        {tx.symbol}
                      </span>
                    </td>
                    <td className="text-dark text-end fw-semibold" style={{ padding: '1rem 0.75rem' }}>
                      {tx.quantity.toLocaleString()}
                    </td>
                    <td className="text-dark fw-bold text-end" style={{ padding: '1rem 0.75rem', fontSize: '1.05rem', color: '#667eea' }}>
                      ₹{tx.price.toFixed(2)}
                    </td>
                    <td className="text-center" style={{ padding: '1rem 0.75rem' }}>
                      <span 
                        className="badge" 
                        style={{
                          background: tx.order_type === 'buy' ? '#2ed573' : '#ff4757',
                          color: 'white',
                          border: 'none',
                          fontWeight: 700,
                          fontSize: '0.85rem',
                          padding: '0.45rem 0.85rem'
                        }}
                      >
                        {tx.order_type === 'buy' ? '🔼 BUY' : '🔽 SELL'}
                      </span>
                    </td>
                    <td className="text-center" style={{ padding: '1rem 0.75rem' }}>
                      <span 
                        className="badge"
                        style={{
                          background: tx.label === 'fraud' ? '#ff4757' : '#2ed573',
                          color: 'white',
                          border: 'none',
                          fontWeight: 700,
                          fontSize: '0.85rem',
                          padding: '0.45rem 0.85rem'
                        }}
                      >
                        {tx.label === 'fraud' ? '⚠️ FRAUD' : '✅ LEGIT'}
                      </span>
                    </td>
                    <td className="text-center" style={{ padding: '1rem 0.75rem' }}>
                      <span style={{ 
                        fontWeight: 700,
                        fontSize: '1rem',
                        color: tx.confidence > 0.8 ? '#2ed573' : tx.confidence > 0.5 ? '#ffa502' : '#ff4757'
                      }}>
                        {(tx.confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="text-dark" style={{ padding: '1rem 0.75rem', maxWidth: '250px', fontSize: '0.9rem' }}>
                      {tx.reason}
                    </td>
                    <td className="text-muted small text-nowrap" style={{ padding: '1rem 0.75rem' }}>
                      {new Date(tx.timestamp).toLocaleTimeString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RecentTable;
