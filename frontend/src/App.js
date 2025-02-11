import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';

const API_URL = 'http://localhost:8000';

function App() {
  const [email, setEmail] = useState('');
  const [walletAddress, setWalletAddress] = useState('');
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState('');
  const [tradeDirection, setTradeDirection] = useState('long');
  const [tradeSize, setTradeSize] = useState('');
  const [tradingHistory, setTradingHistory] = useState([]);

  useEffect(() => {
    fetchAssets();
    if (walletAddress) {
      fetchTradingHistory();
    }
  }, [walletAddress]);

  const fetchAssets = async () => {
    try {
      const response = await axios.get(`${API_URL}/assets`);
      setAssets(response.data.assets);
    } catch (error) {
      console.error('Error fetching assets:', error);
    }
  };

  const fetchTradingHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/trading-history/${walletAddress}`);
      setTradingHistory(response.data.history);
    } catch (error) {
      console.error('Error fetching trading history:', error);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/register`, { email });
      setWalletAddress(response.data.wallet_address);
      alert('Registration successful!');
    } catch (error) {
      alert('Registration failed: ' + error.message);
    }
  };

  const handleTrade = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/trade`, {
        wallet_address: walletAddress,
        asset: selectedAsset,
        direction: tradeDirection,
        size: parseFloat(tradeSize),
      });
      alert(`Trade executed! Transaction hash: ${response.data.transaction_hash}`);
      fetchTradingHistory();
    } catch (error) {
      alert('Trade failed: ' + error.message);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Crypto Trading Platform
        </Typography>

        {!walletAddress ? (
          <Box component="form" onSubmit={handleRegister} sx={{ mt: 3 }}>
            <TextField
              fullWidth
              label="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              sx={{ mt: 2 }}
            >
              Register
            </Button>
          </Box>
        ) : (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Wallet Address: {walletAddress}
            </Typography>

            <Box component="form" onSubmit={handleTrade} sx={{ mt: 3 }}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Asset</InputLabel>
                <Select
                  value={selectedAsset}
                  onChange={(e) => setSelectedAsset(e.target.value)}
                >
                  {assets.map((asset) => (
                    <MenuItem key={asset} value={asset}>
                      {asset}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth margin="normal">
                <InputLabel>Direction</InputLabel>
                <Select
                  value={tradeDirection}
                  onChange={(e) => setTradeDirection(e.target.value)}
                >
                  <MenuItem value="long">Long</MenuItem>
                  <MenuItem value="short">Short</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Trade Size (USDC)"
                type="number"
                value={tradeSize}
                onChange={(e) => setTradeSize(e.target.value)}
                margin="normal"
              />

              <Button
                type="submit"
                variant="contained"
                color="primary"
                sx={{ mt: 2 }}
              >
                Execute Trade
              </Button>
            </Box>

            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                Trading History
              </Typography>
              {tradingHistory.map((trade) => (
                <Box key={trade.id} sx={{ mb: 2, p: 2, border: '1px solid #ccc' }}>
                  <Typography>Asset: {trade.asset}</Typography>
                  <Typography>Direction: {trade.direction}</Typography>
                  <Typography>Size: {trade.size} USDC</Typography>
                  <Typography>Status: {trade.status}</Typography>
                  <Typography>Time: {new Date(trade.timestamp).toLocaleString()}</Typography>
                </Box>
              ))}
            </Box>
          </Box>
        )}
      </Box>
    </Container>
  );
}

export default App; 