import { io } from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5001';

let socket = null;

export const connectSocket = () => {
  if (socket?.connected) {
    console.log('Socket already connected');
    return;
  }

  socket = io(SOCKET_URL, {
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: Infinity,
  });

  socket.on('connect', () => {
    console.log('WebSocket connected');
  });

  socket.on('disconnect', (reason) => {
    console.log('WebSocket disconnected:', reason);
  });

  socket.on('connect_error', (error) => {
    console.error('WebSocket connection error:', error);
  });

  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
    console.log('WebSocket disconnected manually');
  }
};

export const onSummaryCounts = (callback) => {
  if (!socket) return;
  // Remove all previous listeners before adding new one
  socket.off('summary_counts');
  socket.on('summary_counts', callback);
};

export const onTransactionStream = (callback) => {
  if (!socket) return;
  // Remove all previous listeners before adding new one
  socket.off('transaction_stream');
  socket.on('transaction_stream', callback);
};
