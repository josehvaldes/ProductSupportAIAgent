type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const enabled =
  typeof import.meta !== 'undefined' &&
  typeof import.meta.env !== 'undefined' &&
  (import.meta.env.MODE === 'development' || import.meta.env.VITE_DEBUG === 'true');

function format(module: string, level: LogLevel, args: unknown[]) {
  const ts = new Date().toISOString();
  return [`[%c${level.toUpperCase()}%c][${ts}][${module}]`, 'color:#555', 'color:inherit', ...args];
}

export function createLogger(module: string) {
  return {
    debug: (...args: unknown[]) => enabled && console.debug(...format(module, 'debug', args)),
    info: (...args: unknown[]) => enabled && console.info(...format(module, 'info', args)),
    warn: (...args: unknown[]) => enabled && console.warn(...format(module, 'warn', args)),
    error: (...args: unknown[]) => enabled && console.error(...format(module, 'error', args)),
    group: (label: string) => enabled && console.groupCollapsed(label),
    groupEnd: () => enabled && console.groupEnd(),
    time: (label: string) => enabled && console.time(label),
    timeEnd: (label: string) => enabled && console.timeEnd(label),
  };
}