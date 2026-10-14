#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import Mobilerun from '@mobilerun/sdk';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const evidenceDir = path.join(__dirname, 'evidence');

const PASSIVE_RULES = [
  'Do not submit forms.',
  'Do not send messages.',
  'Do not buy anything or enter payment details.',
  'Do not enter passwords or one-time codes.',
  'Do not change account, privacy, billing, or device settings.',
  'Stop if a screen asks for credentials, payment, legal consent, KYC, or destructive confirmation.'
].join(' ');

const usage = `Mobilerun ops helper

Usage:
  node droidrun_mobilerun_ops.mjs <command> [options]

Commands:
  health                         Check SDK import and API authentication.
  devices [--page-size N]         List cloud devices.
  apps [--query TEXT]             Search available apps.
  open-app --app PACKAGE          Run a task to open an app on a cloud device.
  ui-summary                      Run a passive UI summary task.
  screenshot                      Run a passive screenshot capture task.
  warmup                         Run a passive low step device warmup task.

Options:
  --device-id ID                  Overrides MOBILERUN_CLOUD_DEVICE_ID.
  --app PACKAGE                   Android package or app identifier.
  --query TEXT                    App search query.
  --page-size N                   Page size, default 10.
  --model NAME                    LLM model for task APIs.
  --base-url URL                  Overrides MOBILERUN_BASE_URL.
  --help                         Show this help.

Environment:
  MOBILERUN_CLOUD_API_KEY         Required for cloud calls.
  MOBILERUN_BASE_URL              Optional SDK base URL.
  MOBILERUN_CLOUD_DEVICE_ID       Default device id for task commands.
`;

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const item = argv[i];
    if (!item.startsWith('--')) {
      args._.push(item);
      continue;
    }
    const key = item.slice(2);
    if (key === 'help') {
      args.help = true;
      continue;
    }
    const value = argv[i + 1];
    if (!value || value.startsWith('--')) {
      throw new Error(`Missing value for --${key}`);
    }
    args[key] = value;
    i += 1;
  }
  return args;
}

function toInt(value, fallback) {
  if (value === undefined) return fallback;
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed) || parsed < 1 || parsed > 100) {
    throw new Error(`Invalid positive integer: ${value}`);
  }
  return parsed;
}

function client(args) {
  const apiKey = process.env.MOBILERUN_CLOUD_API_KEY;
  if (!apiKey) {
    const err = new Error('MOBILERUN_CLOUD_API_KEY is required for Mobilerun Cloud calls.');
    err.exitCode = 2;
    throw err;
  }
  return new Mobilerun({
    apiKey,
    baseURL: args['base-url'] || process.env.MOBILERUN_BASE_URL || undefined,
    maxRetries: 1,
    timeout: 30000
  });
}

function sanitizeError(error) {
  return {
    name: error?.name || 'Error',
    message: String(error?.message || error || 'unknown error').replace(/Bearer\s+\S+/gi, 'Bearer [redacted]'),
    status: error?.status || error?.code || undefined
  };
}

function pickDevice(args) {
  const deviceId = args['device-id'] || process.env.MOBILERUN_CLOUD_DEVICE_ID;
  if (!deviceId) {
    const err = new Error('A device id is required. Set MOBILERUN_CLOUD_DEVICE_ID or pass --device-id.');
    err.exitCode = 2;
    throw err;
  }
  return deviceId;
}

function model(args) {
  return args.model || process.env.MOBILERUN_LLM_MODEL || 'google/gemini-3.1-flash-lite-preview';
}

function compactDevice(device) {
  return {
    id: device.id,
    name: device.name || null,
    status: device.status || null,
    type: device.type || null,
    osVersion: device.osVersion || device.os_version || null,
    updatedAt: device.updatedAt || null
  };
}

function compactApp(app) {
  return {
    id: app.id,
    displayName: app.displayName,
    packageName: app.packageName,
    type: app.type,
    source: app.source,
    status: app.status,
    versionName: app.versionName
  };
}

async function writeEvidence(prefix, data) {
  await fs.mkdir(evidenceDir, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const file = path.join(evidenceDir, `${stamp}-${prefix}.json`);
  await fs.writeFile(file, `${JSON.stringify(data, null, 2)}\n`, { mode: 0o600 });
  return file;
}

async function runTask(api, args, task, extra = {}) {
  const body = {
    deviceId: pickDevice(args),
    task,
    llmModel: model(args),
    maxSteps: Number.parseInt(args['max-steps'] || extra.maxSteps || '8', 10),
    vision: true,
    reasoning: false,
    continueOnFailure: false,
    ...extra.body
  };
  const response = await api.tasks.run(body);
  const taskId = response.id || response.taskId || response.task?.id;
  const evidence = { command: args._[0], taskId, response };
  const evidencePath = await writeEvidence(args._[0], evidence);
  return { taskId, evidencePath, response };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0];
  if (args.help || !command) {
    process.stdout.write(usage);
    return;
  }

  if (!['health', 'devices', 'apps', 'open-app', 'ui-summary', 'screenshot', 'warmup'].includes(command)) {
    throw new Error(`Unknown command: ${command}`);
  }

  const api = client(args);
  if (command === 'health') {
    const devices = await api.devices.list({ pageSize: 1 });
    console.log(JSON.stringify({ ok: true, sdk: '@mobilerun/sdk', devicesVisible: Boolean(devices) }, null, 2));
    return;
  }

  if (command === 'devices') {
    const pageSize = toInt(args['page-size'], 10);
    const response = await api.devices.list({ pageSize });
    const items = response.items || [];
    console.log(JSON.stringify({ items: items.map(compactDevice), pagination: response.pagination || null }, null, 2));
    return;
  }

  if (command === 'apps') {
    const pageSize = toInt(args['page-size'], 10);
    const response = await api.apps.list({ pageSize, query: args.query, source: 'all' });
    const items = response.items || [];
    console.log(JSON.stringify({ count: response.count || null, items: items.map(compactApp), pagination: response.pagination || null }, null, 2));
    return;
  }

  if (command === 'open-app') {
    if (!args.app) throw new Error('--app is required for open-app');
    const result = await runTask(api, args, `Open app ${args.app}. ${PASSIVE_RULES}`, { maxSteps: 10, body: { apps: [args.app] } });
    console.log(JSON.stringify({ ok: true, ...result }, null, 2));
    return;
  }

  if (command === 'ui-summary') {
    const result = await runTask(api, args, `Passively inspect the current screen and summarize visible UI state. ${PASSIVE_RULES}`, { maxSteps: 6 });
    console.log(JSON.stringify({ ok: true, ...result }, null, 2));
    return;
  }

  if (command === 'screenshot') {
    const result = await runTask(api, args, `Capture or expose a screenshot artifact for the current screen, then stop. ${PASSIVE_RULES}`, { maxSteps: 4 });
    if (result.taskId) {
      try {
        const screenshots = await api.tasks.screenshots.list(result.taskId);
        result.screenshots = screenshots.urls || [];
      } catch (error) {
        result.screenshotLookupError = sanitizeError(error);
      }
    }
    console.log(JSON.stringify({ ok: true, ...result }, null, 2));
    return;
  }

  if (command === 'warmup') {
    const result = await runTask(api, args, `Passive device warmup only. Confirm device is responsive and report the foreground app or visible safe state. ${PASSIVE_RULES}`, { maxSteps: 5 });
    console.log(JSON.stringify({ ok: true, ...result }, null, 2));
  }
}

main().catch((error) => {
  console.error(JSON.stringify({ ok: false, error: sanitizeError(error) }, null, 2));
  process.exit(error.exitCode || 1);
});
