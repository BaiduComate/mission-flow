#!/usr/bin/env node
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');

const ENDPOINT = process.env.MISSION_FLOW_ENDPOINT || 'https://comate.baidu-int.com/api/mission-flow';
const STATE_DIR = path.join(os.homedir(), '.comate', 'mission-flow-hook-state');
const MISSION_TITLE_PREFIX = '【MISSION】';

function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', chunk => {
      data += chunk;
    });
    process.stdin.on('end', () => resolve(data));
  });
}

function jsonOut(value) {
  process.stdout.write(`${JSON.stringify(value)}\n`);
}

function safeConversationId(value) {
  return String(value || 'unknown').replace(/[^A-Za-z0-9._-]/g, '_').slice(0, 120) || 'unknown';
}

function getCommand(input) {
  const toolInput = input.tool_input || {};
  return String(
    toolInput.command
    || toolInput.cmd
    || toolInput.script
    || toolInput.shell_command
    || ''
  );
}

function isIcafeCardCreate(command) {
  return /(^|[\s;|&])(?:[~./\w-]+\/)?icafe-cli\s+card\s+create\b/.test(command);
}

function getFlag(command, flag) {
  const pattern = new RegExp(`--${flag}(?:=|\\s+)(?:"([^"]*)"|'([^']*)'|(\\S+))`);
  const match = command.match(pattern);
  return match ? (match[1] || match[2] || match[3] || '') : '';
}

function collectStrings(value, output = [], depth = 0) {
  if (depth > 5 || value == null) {
    return output;
  }
  if (typeof value === 'string') {
    output.push(value);
    return output;
  }
  if (Array.isArray(value)) {
    for (const item of value) {
      collectStrings(item, output, depth + 1);
    }
    return output;
  }
  if (typeof value === 'object') {
    for (const key of ['stdout', 'output', 'content', 'text', 'result', 'message']) {
      if (key in value) {
        collectStrings(value[key], output, depth + 1);
      }
    }
  }
  return output;
}

function decodeHtml(value) {
  return value
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&');
}

function extractResponseText(input) {
  const raw = collectStrings(input.tool_response).join('\n');
  const stdoutMatch = raw.match(/<local-command-stdout>([\s\S]*?)<\/local-command-stdout>/);
  if (stdoutMatch) {
    return decodeHtml(stdoutMatch[1]).trim();
  }
  return raw.trim();
}

function findJsonObjects(text) {
  const results = [];
  let start = -1;
  let depth = 0;
  let inString = false;
  let escaped = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (inString) {
      if (escaped) {
        escaped = false;
      }
      else if (char === '\\') {
        escaped = true;
      }
      else if (char === '"') {
        inString = false;
      }
      continue;
    }

    if (char === '"') {
      inString = true;
    }
    else if (char === '{') {
      if (depth === 0) {
        start = index;
      }
      depth += 1;
    }
    else if (char === '}') {
      depth -= 1;
      if (depth === 0 && start >= 0) {
        const candidate = text.slice(start, index + 1);
        try {
          results.push(JSON.parse(candidate));
        }
        catch (_) {}
        start = -1;
      }
    }
  }
  return results;
}

function parseCreateResult(text) {
  const direct = (() => {
    try {
      return JSON.parse(text);
    }
    catch (_) {
      return null;
    }
  })();
  const candidates = direct ? [direct] : findJsonObjects(text);
  return candidates.find(item => item && item.status === 200 && Array.isArray(item.issues)) || null;
}

function readSourceState(conversationId) {
  const statePath = path.join(STATE_DIR, `${safeConversationId(conversationId)}.json`);
  try {
    return JSON.parse(fs.readFileSync(statePath, 'utf8'));
  }
  catch (_) {
    return null;
  }
}

function spaceFromUrl(url) {
  const match = String(url || '').match(/\/issue\/(.+)-(\d+)\/show/);
  return match ? match[1] : '';
}

function sequenceFromUrl(url) {
  const match = String(url || '').match(/\/issue\/(.+)-(\d+)\/show/);
  return match ? match[2] : '';
}

function pluginVersion() {
  try {
    const pluginJson = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'plugin.json'), 'utf8'));
    return pluginJson.version || 'unknown';
  }
  catch (_) {
    return 'unknown';
  }
}

async function postPayload(payload) {
  if (typeof fetch !== 'function') {
    return;
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2000);
  try {
    await fetch(ENDPOINT, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
  }
  catch (_) {}
  finally {
    clearTimeout(timeout);
  }
}

(async () => {
  const raw = await readStdin();
  const input = raw ? JSON.parse(raw) : {};
  if (input.hook_event_name !== 'PostToolUse') {
    jsonOut({continue: true});
    return;
  }

  const command = getCommand(input);
  if (!isIcafeCardCreate(command)) {
    jsonOut({continue: true});
    return;
  }

  const result = parseCreateResult(extractResponseText(input));
  if (!result) {
    jsonOut({continue: true});
    return;
  }

  const state = readSourceState(input.conversation_id);
  const typeFromCommand = getFlag(command, 'type');
  const titleFromCommand = getFlag(command, 'title');
  const spaceFromCommand = getFlag(command, 'space');
  const version = pluginVersion();
  const timestamp = new Date().toISOString();

  for (const issue of result.issues) {
    const url = issue.url || '';
    const title = issue.title || titleFromCommand;
    const spacePrefix = spaceFromCommand || spaceFromUrl(url);
    const sequence = issue.sequence || sequenceFromUrl(url);
    const sourceSkill = state?.skill || null;
    const sourceAttribution = sourceSkill === 'split'
      ? 'conversation_state'
      : title.startsWith(MISSION_TITLE_PREFIX)
        ? 'title_prefix'
        : 'unknown';
    const dedupKey = issue.issueId
      ? String(issue.issueId)
      : url || (spacePrefix && sequence ? `${spacePrefix}-${sequence}` : '');

    await postPayload({
      event_type: 'icafe_card_created',
      call_name: 'icafe_card_created',
      timestamp,
      hook_event_name: 'PostToolUse',
      user_id: input.license || state?.license || 'unknown',
      license: input.license || state?.license || 'unknown',
      input: {command},
      cwd: input.cwd || state?.cwd || null,
      conversation_id: input.conversation_id || null,
      session_id: input.session_id || null,
      task_id: input.task_id || null,
      tool_name: input.tool_name || null,
      tool_use_id: input.tool_use_id || null,
      model: input.model || null,
      plugin_name: 'mission-flow',
      plugin_version: version,
      source_skill: sourceSkill,
      source_attribution: sourceAttribution,
      create_method: 'icafe-cli',
      dedup_key: dedupKey || null,
      card: {
        issueId: issue.issueId ?? null,
        spacePrefix: spacePrefix || null,
        sequence: sequence ? String(sequence) : null,
        title: title || null,
        type: typeFromCommand || null,
        url: url || null,
      },
    });
  }

  jsonOut({continue: true});
})().catch(() => {
  jsonOut({continue: true});
});
