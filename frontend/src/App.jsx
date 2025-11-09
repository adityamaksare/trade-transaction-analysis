import React, { useState, useEffect, useRef } from 'react';
import Counters from './components/Counters';
import RecentTable from './components/RecentTable';
import { connectSocket, disconnectSocket, onSummaryCounts, onTransactionStream, onTransactionUpdate } from './api/socket';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function App() {
  const [stats, setStats] = useState({ total: 0, legit: 0, fraud: 0 });
  const [transactions, setTransactions] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(false);

  // Fetch initial stats from API
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/summary`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Log when transactions state changes
  useEffect(() => {
    console.log('🔄 Transactions state updated. Count:', transactions.length);
    if (transactions.length > 0) {
      console.log('  Most recent:', transactions[0]?.trade_id);
    }
  }, [transactions]);

  useEffect(() => {
    console.log('🚀 App mounting - setting up WebSocket');

    // Load initial data from database on mount
    fetchStats();
    fetchTransactions();

    // Connect to WebSocket
    connectSocket();

    // Set up listeners IMMEDIATELY (not waiting for connect event)
    // Listen for summary counts
    onSummaryCounts((data) => {
      console.log('📊 Received summary_counts:', data);
      setStats(data);
    });

    // Listen for transaction stream (prepend to existing list)
    onTransactionStream((data) => {
      console.log('💳 Received transaction_stream event:', data.trade_id);
      setTransactions(prev => {
        // Check for duplicates to prevent React key warnings
        const existsAtIndex = prev.findIndex(tx => tx.trade_id === data.trade_id);

        if (existsAtIndex >= 0) {
          console.log('🔄 Updating existing transaction:', data.trade_id, 'at index', existsAtIndex);
          // Replace the existing transaction with the new data (might have updated fields)
          const updated = [...prev];
          updated[existsAtIndex] = data;
          return updated;
        }

        console.log('✅ Adding new transaction to state:', data.trade_id);
        console.log('  Current state has', prev.length, 'transactions');

        // Add new transaction at the beginning
        const newTransactions = [data, ...prev];
        console.log('  New state will have', newTransactions.length, 'transactions');

        // Keep only last 1000 transactions in memory
        return newTransactions.slice(0, 1000);
      });
    });

    // Listen for combined transaction update (atomic update of both stats and transaction)
    onTransactionUpdate((data) => {
      console.log('🔄 Received transaction_update (atomic):', data.transaction.trade_id, '| Stats:', data.stats);

      // Update stats and transaction atomically in the same handler
      setStats(data.stats);

      setTransactions(prev => {
        const existsAtIndex = prev.findIndex(tx => tx.trade_id === data.transaction.trade_id);

        if (existsAtIndex >= 0) {
          const updated = [...prev];
          updated[existsAtIndex] = data.transaction;
          return updated;
        }

        const newTransactions = [data.transaction, ...prev];
        return newTransactions.slice(0, 1000);
      });
    });

    console.log('✅ WebSocket listeners registered');

    // Cleanup on unmount
    return () => {
      console.log('🔴 App unmounting - disconnecting WebSocket');
      disconnectSocket();
    };
  }, []);

  // Fetch ALL transactions from API (filtering done client-side)
  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: '10000' }); // Fetch all transactions
      const response = await fetch(`${API_BASE_URL}/api/transactions?${params.toString()}`);
      const data = await response.json();

      // Transform API response to match Transaction interface
      const transformedTransactions = data.transactions.map((tx) => ({
        trade_id: tx.trade_id,
        trader_id: tx.trader_id,
        symbol: tx.symbol,
        quantity: tx.quantity,
        price: tx.price,
        timestamp: tx.timestamp,
        order_type: tx.order_type,
        label: tx.llama_result?.label || 'legit',
        confidence: tx.llama_result?.confidence || 0.5,
        reason: tx.llama_result?.reason || 'No reason provided',
        processed_at: tx.processed_at
      }));

      // Sort by processed_at descending (newest first)
      transformedTransactions.sort((a, b) => {
        return new Date(b.processed_at).getTime() - new Date(a.processed_at).getTime();
      });

      setTransactions(transformedTransactions);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTotalClick = () => {
    setFilter('all');
  };

  const handleLegitClick = () => {
    setFilter('legit');
  };

  const handleFraudClick = () => {
    setFilter('fraud');
  };

  // Apply filter at display time (client-side filtering)
  const filteredTransactions = filter === 'all'
    ? transactions
    : transactions.filter(tx => tx.label === filter);

  return (
    <div
      className="min-vh-100"
      style={{
        background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
        minHeight: '100vh'
      }}
    >
      {/* Modern Header */}
      <header
        style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 4px 30px rgba(0, 0, 0, 0.3)'
        }}
        className="sticky-top"
      >
        <div className="container py-4">
          <div className="d-flex align-items-center justify-content-between">
            <div>
              <h1 className="text-white fw-bold mb-1" style={{ fontSize: '1.75rem', letterSpacing: '0.5px' }}>
                🔍 AI Fraud Detection System
              </h1>
              <p className="text-white-50 mb-0 small">Real-Time Stock Market Transaction Analysis</p>
            </div>
            <div className="text-end">
              <div className="d-flex align-items-center gap-2">
                <span className="badge bg-success bg-opacity-25 text-white border border-success">
                  ● Live
                </span>
                <span className="text-white-50 small">
                  {filter === 'all'
                    ? `${transactions.length} Transactions`
                    : `${filteredTransactions.length} of ${transactions.length} Transactions`}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container py-4">
        {/* Statistics Cards */}
        <Counters
          stats={stats}
          onTotalClick={handleTotalClick}
          onLegitClick={handleLegitClick}
          onFraudClick={handleFraudClick}
        />

        {/* Filter Section */}
        <div
          className="card mb-4 border-0"
          style={{
            background: 'rgba(255, 255, 255, 0.08)',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}
        >
          <div className="card-body">
            <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
              <div className="d-flex align-items-center gap-2">
                <i className="bi bi-funnel text-white-50"></i>
                <label className="text-white fw-semibold mb-0">Filter Transactions:</label>
              </div>
              <select
                className="form-select form-select-md"
                style={{
                  width: 'auto',
                  minWidth: '200px',
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  color: 'white'
                }}
                value={filter}
                onChange={(e) => {
                  const newFilter = e.target.value;
                  if (newFilter === 'all') {
                    handleTotalClick();
                  } else if (newFilter === 'legit') {
                    handleLegitClick();
                  } else {
                    handleFraudClick();
                  }
                }}
              >
                <option value="all" style={{ background: '#1a1a2e' }}>🔹 All Transactions</option>
                <option value="legit" style={{ background: '#1a1a2e' }}>✅ Legitimate Only</option>
                <option value="fraud" style={{ background: '#1a1a2e' }}>⚠️ Fraudulent Only</option>
              </select>
            </div>
          </div>
        </div>

        {/* Transactions Table */}
        {loading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-white" role="status" style={{ width: '3rem', height: '3rem' }}>
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-3 text-white">Loading transactions...</p>
          </div>
        ) : (
          <RecentTable transactions={filteredTransactions} />
        )}
      </main>

      {/* Modern Footer */}
      <footer
        className="text-white text-center py-4 mt-5"
        style={{
          background: 'rgba(255, 255, 255, 0.03)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)'
        }}
      >
        <div className="container">
          <p className="mb-2 text-white-50 small">
            Powered by <span className="text-white fw-semibold">Kafka • Ollama Llama3 • MongoDB • React</span>
          </p>
          <p className="mb-0 text-white-50" style={{ fontSize: '0.75rem' }}>
            © 2025 Fraud Detection System | Real-Time AI-Powered Analytics | Aditya Maksare
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
