import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Dice state management
let diceState = {
  dice: Array(6).fill(null).map((_, i) => ({
    id: i,
    value: 1,
    isSpinning: false,
    targetValue: 1
  })),
  total: 6,
  lastUpdated: Date.now()
};

// Get current dice state
app.get('/api/dice/state', (req, res) => {
  res.json(diceState);
});

// Spin all dice to a specific number
app.post('/api/dice/spin-all', (req, res) => {
  const { targetValue } = req.body;
  
  if (!targetValue || targetValue < 1 || targetValue > 6) {
    return res.status(400).json({ error: 'Invalid target value. Must be between 1 and 6.' });
  }

  // Set all dice to spinning state with target value
  diceState.dice = diceState.dice.map(dice => ({
    ...dice,
    isSpinning: true,
    targetValue: targetValue
  }));
  diceState.lastUpdated = Date.now();

  res.json({
    success: true,
    message: `All 6 dice spinning to ${targetValue}`,
    state: diceState
  });

  // Broadcast initial state
  broadcastState();

  // Simulate dice animation completion after 8 seconds
  setTimeout(() => {
    diceState.dice = diceState.dice.map(dice => ({
      ...dice,
      value: targetValue,
      isSpinning: false
    }));
    updateState({});
    console.log(`All dice completed spinning to ${targetValue}. Total: ${diceState.total}`);
  }, 8000);
});

// Spin all dice to random values
app.post('/api/dice/spin-random', (req, res) => {
  // Generate random values for each dice
  const randomValues = diceState.dice.map(() => Math.floor(Math.random() * 6) + 1);

  // Set all dice to spinning state with random target values
  diceState.dice = diceState.dice.map((dice, index) => ({
    ...dice,
    isSpinning: true,
    targetValue: randomValues[index]
  }));
  diceState.lastUpdated = Date.now();

  res.json({
    success: true,
    message: 'All 6 dice spinning to random values',
    targetValues: randomValues,
    state: diceState
  });

  // Broadcast initial state
  broadcastState();

  // Simulate dice animation completion after 8 seconds
  setTimeout(() => {
    diceState.dice = diceState.dice.map((dice, index) => ({
      ...dice,
      value: randomValues[index],
      isSpinning: false
    }));
    updateState({});
    console.log(`All dice completed spinning to random values. Total: ${diceState.total}`);
  }, 8000);
});

// Spin a specific dice
app.post('/api/dice/spin/:diceId', (req, res) => {
  const diceId = parseInt(req.params.diceId);
  const { targetValue } = req.body;

  if (diceId < 0 || diceId > 5) {
    return res.status(400).json({ error: 'Invalid dice ID. Must be between 0 and 5.' });
  }

  if (!targetValue || targetValue < 1 || targetValue > 6) {
    return res.status(400).json({ error: 'Invalid target value. Must be between 1 and 6.' });
  }

  // Update specific dice
  diceState.dice[diceId] = {
    ...diceState.dice[diceId],
    isSpinning: true,
    targetValue: targetValue
  };
  diceState.lastUpdated = Date.now();

  res.json({
    success: true,
    message: `Dice ${diceId + 1} spinning to ${targetValue}`,
    state: diceState
  });

  // Broadcast initial state
  broadcastState();

  // Simulate dice animation completion after 8 seconds
  setTimeout(() => {
    diceState.dice[diceId] = {
      ...diceState.dice[diceId],
      value: targetValue,
      isSpinning: false
    };
    updateState({});
    console.log(`Dice ${diceId + 1} completed spinning to ${targetValue}`);
  }, 8000);
});

// Reset all dice
app.post('/api/dice/reset', (req, res) => {
  diceState = {
    dice: Array(6).fill(null).map((_, i) => ({
      id: i,
      value: 1,
      isSpinning: false,
      targetValue: 1
    })),
    total: 6,
    lastUpdated: Date.now()
  };

  updateState({});

  res.json({
    success: true,
    message: 'All dice reset to 1',
    state: diceState
  });
});

// WebSocket server instance (will be initialized after HTTP server)
let wss = null;

// Broadcast state updates to all connected clients
function broadcastState() {
  if (!wss) return;
  const message = JSON.stringify({ type: 'state', data: diceState });
  wss.clients.forEach((client) => {
    if (client.readyState === 1) { // WebSocket.OPEN
      client.send(message);
    }
  });
}

// Update state and broadcast
function updateState(updates) {
  Object.assign(diceState, updates);
  diceState.lastUpdated = Date.now();
  diceState.total = diceState.dice.reduce((sum, dice) => sum + dice.value, 0);
  broadcastState();
}

const server = app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`API endpoints:`);
  console.log(`  GET  /api/dice/state - Get current dice state`);
  console.log(`  POST /api/dice/spin-all - Spin all dice to a number`);
  console.log(`  POST /api/dice/spin-random - Spin all dice to random values`);
  console.log(`  POST /api/dice/spin/:diceId - Spin a specific dice`);
  console.log(`  POST /api/dice/reset - Reset all dice`);
});

// WebSocket server for real-time updates
wss = new WebSocketServer({ server });

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Send current state to new client
  ws.send(JSON.stringify({ type: 'state', data: diceState }));

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log('Received:', data);
    } catch (error) {
      console.error('Error parsing message:', error);
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

