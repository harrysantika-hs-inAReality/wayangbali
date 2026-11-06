// Runs the PHP backend (tutor + queue) and the Vite dev server together.
// Vite proxies /tutor.php and /queue.php to PHP (see vite.config.ts). Ctrl+C stops both.
import { spawn, spawnSync } from 'node:child_process';

const phpPort = process.env.PHP_PORT ?? '8124';
const children = [
  spawn(process.env.PHP ?? 'php', ['-S', `127.0.0.1:${phpPort}`, '-t', 'public'], { stdio: 'inherit' }),
  spawn('npm', ['run', 'dev'], { stdio: 'inherit', shell: true, env: { ...process.env, PHP_PORT: phpPort } }),
];

let stopping = false;
function stopAll(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) {
    if (child.exitCode !== null || !child.pid) continue;
    // Windows: kill the whole tree, otherwise the npm shell leaves Vite running.
    if (process.platform === 'win32') spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' });
    else child.kill('SIGTERM');
  }
  process.exit(code);
}

for (const child of children) {
  child.on('error', (error) => { console.error(`[serve-all] ${error.message}`); stopAll(1); });
  child.on('exit', (code) => stopAll(code ?? 0));
}
process.on('SIGINT', () => stopAll(0));
process.on('SIGTERM', () => stopAll(0));
