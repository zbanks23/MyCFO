const { spawn } = require('child_process');
const path = require('path');

// Determine the correct python executable based on the OS
const isWindows = process.platform === 'win32';
const pythonExecutable = isWindows ? 'python.exe' : 'python';
const venvPath = isWindows 
  ? path.join('venv', 'Scripts', pythonExecutable)
  : path.join('venv', 'bin', pythonExecutable);

console.log(`[API] Starting Python server using: ${venvPath}`);

// Spawn the python process
const pythonProcess = spawn(venvPath, ['app.py'], {
  stdio: 'inherit', // This shows the Python output in your terminal
  shell: true
});

pythonProcess.on('error', (err) => {
  console.error('[API] Failed to start Python process:', err);
});

pythonProcess.on('close', (code) => {
  console.log(`[API] Python process exited with code ${code}`);
});