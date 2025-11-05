import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

function Popup() {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check connection status
    chrome.storage.local.get(['gmailConnected'], (result) => {
      setIsConnected(!!result.gmailConnected);
    });
  }, []);

  const handleConnect = async () => {
    setLoading(true);
    try {
      // Request Gmail API access
      const response = await chrome.runtime.sendMessage({
        type: 'GET_AUTH_TOKEN'
      });

      if (response.token) {
        chrome.storage.local.set({ gmailConnected: true });
        setIsConnected(true);
      } else {
        alert('Failed to connect: ' + (response.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Connection error:', error);
      alert('Failed to connect to Gmail');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '16px', width: '300px' }}>
      <div style={{ marginBottom: '16px' }}>
        <h2 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>
          AI Email Grouping
        </h2>
        <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
          Automatically organize emails by project
        </p>
      </div>
      
      <div
        style={{
          padding: '12px',
          borderRadius: '8px',
          marginBottom: '16px',
          backgroundColor: isConnected ? '#e8f5e9' : '#ffebee',
          color: isConnected ? '#2e7d32' : '#c62828',
        }}
      >
        {isConnected ? '✓ Connected to Gmail' : 'Not connected'}
      </div>

      {!isConnected && (
        <button
          onClick={handleConnect}
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#1976d2',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: 500,
          }}
        >
          {loading ? 'Connecting...' : 'Connect to Gmail'}
        </button>
      )}
    </div>
  );
}

// Initialize React app
const container = document.getElementById('root') || document.body;
const root = createRoot(container);
root.render(<Popup />);

