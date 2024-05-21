const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { exec } = require('child_process');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', (socket) => {
  socket.on('run code', (code, expectedOutput) => {
    exec(`node -e "${code.replace(/"/g, '\\"')}"`, (error, stdout, stderr) => {
      if (error) {
        io.emit('code output', `Error: ${stderr}`);
        io.emit('test result', 'Test failed: Code execution error');
      } else {
        const cleanOutput = stdout.trim();
        io.emit('code output', `Output: ${cleanOutput}`);
        io.emit('test result', `Expected Output: ${expectedOutput}`);
        if (cleanOutput === expectedOutput) {
          io.emit('test result', 'Test passed: Correct output!');
        } else {
          io.emit('test result', `Test failed: Expected ${expectedOutput}, but got ${cleanOutput}`);
        }
      }
    });
  });
});

server.listen(3000, () => {
  console.log('Server is running on http://localhost:3000');
});
