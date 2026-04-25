/**
 * Smart Factory — Human-readable dashboard
 * Fetches same data as API and renders tables/GUI.
 */
(function () {
'use strict';

// Base path for API (empty when served at /; set when behind a path prefix e.g. /factory)
const API_BASE = (function () {
  var p = window.location.pathname.replace(/\/$/, '');
  return p || '';
})();

const COLUMN_LABELS = {
  id: 'ID',
  project_id: 'Project ID',
  project_name: 'Project',
  name: 'Name',
  title: 'Title',
  description: 'Description',
  type: 'Type',
  status: 'Status',
  priority: 'Priority',
  step: 'Step',
  progress_percent: 'Progress %',
  assigned_to: 'Assigned to',
  assigned_team: 'Team',
  assigned_agent: 'Agent',
  taken_at: 'Taken at',
  created_at: 'Created',
  updated_at: 'Updated',
  repo_url: 'Repo URL',
  gdd_path: 'GDD path',
  req_id: 'Req ID',
  executor: 'Executor',
  output_path: 'Output',
  completed_at: 'Completed',
  team: 'Team',
  reported_at: 'Reported at',
  reporter_agent: 'Reporter',
  payload: 'Payload',
  active: 'Active',
  run_number: 'Run',
  last_run_at: 'Last run',
  trigger_type: 'Trigger',
  stages: 'Stages',
  source: 'Source',
  path: 'Path',
  config: 'Config',
  last_seen: 'Last seen',
  requirement_id: 'Requirement ID',
  task_id: 'Task ID',
  reason: 'Reason',
  options: 'Options',
  decision: 'Decision',
  reported_at: 'Reported at',
  resolved_at: 'Resolved at',
  pipeline_name: 'Pipeline',
  pipeline_id: 'Pipeline ID',
  started_at: 'Started at',
  finished_at: 'Finished at',
  trigger_reason: 'Trigger reason',
  date: 'Date',
  api_count: 'API count',
  success_count: 'Success',
  failed_count: 'Failed',
  timestamp: 'Time',
  chat_type: 'Chat type',
  api_endpoint: 'Endpoint',
  detail_type: 'Type',
  content: 'Content',
};

function el(id) {
  return document.getElementById(id);
}

function showToast(msg, isError = false) {
  const t = el('toast');
  t.textContent = msg;
  t.className = 'toast show' + (isError ? ' error' : '');
  clearTimeout(window._toastT);
  window._toastT = setTimeout(() => { t.classList.remove('show'); }, 3000);
}

function humanKey(key) {
  return COLUMN_LABELS[key] || key.replace(/_/g, ' ');
}

function formatCell(key, value) {
  if (value == null || value === '') return '—';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if ((key === 'payload' || key === 'options') && typeof value === 'string') {
    try {
      const o = JSON.parse(value);
      value = JSON.stringify(o, null, 2);
    } catch (_) {}
    return '<pre class="payload-pre">' + escapeHtml(value) + '</pre>';
  }
  if ((key.includes('_at') || key === 'taken_at' || key === 'last_seen') && typeof value === 'string') {
    const d = value.replace('Z', '').slice(0, 19);
    return d || value;
  }
  if (key === 'content' && typeof value === 'string' && value.length > 120) {
    return '<pre class="payload-pre">' + escapeHtml(value) + '</pre>';
  }
  return escapeHtml(String(value));
}

function escapeHtml(s) {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

/** Sort array of objects by id (numeric ascending). Rows without id go last. */
function sortById(arr) {
  if (!Array.isArray(arr) || arr.length === 0) return arr;
  return arr.slice().sort(function (a, b) {
    var ia = a != null && a.hasOwnProperty('id') ? Number(a.id) : NaN;
    var ib = b != null && b.hasOwnProperty('id') ? Number(b.id) : NaN;
    if (isNaN(ia) && isNaN(ib)) return 0;
    if (isNaN(ia)) return 1;
    if (isNaN(ib)) return -1;
    return ia - ib;
  });
}

function buildTable(data, options = {}) {
  if (!Array.isArray(data) || data.length === 0) {
    return '<p class="empty">No rows.</p>';
  }
  const keys = options.columns || Object.keys(data[0]).filter(k => options.skipKeys && !options.skipKeys.includes(k));
  const skipKeys = options.skipKeys || [];
  const cols = (options.columns || Object.keys(data[0])).filter(k => !skipKeys.includes(k));
  let html = '<table class="data-table"><thead><tr>';
  cols.forEach(k => { html += '<th>' + escapeHtml(humanKey(k)) + '</th>'; });
  html += '</tr></thead><tbody>';
  data.forEach(row => {
    html += '<tr>';
    cols.forEach(k => {
      const v = row[k];
      const cell = formatCell(k, v);
      const cls = typeof v === 'number' && k !== 'id' && k !== 'project_id' && k !== 'req_id' ? ' num' : '';
      const truncate = (k === 'description' || k === 'title') && typeof v === 'string' && v.length > 60 ? ' truncate' : '';
      html += '<td class="mono' + cls + truncate + '" title="' + (v != null ? escapeHtml(String(v)) : '') + '">' + cell + '</td>';
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  return html;
}

function addStatusBadge(el, status) {
  if (!status) return;
  const c = status === 'new' ? 'badge-new' : status === 'in_progress' ? 'badge-in_progress' : status === 'done' ? 'badge-done' : status === 'online' ? 'badge-online' : 'badge-offline';
  el.classList.add('badge', c);
}

// ----- Dashboard stats -----
function renderDashboardStats(json) {
  const html = [];
  if (json.projects && json.projects.length) {
    html.push('<div class="stat-card"><h3>Projects by status</h3><table>');
    json.projects.forEach(r => { html.push('<tr><td>' + escapeHtml(r.status || '—') + '</td><td>' + r.count + '</td></tr>'); });
    html.push('</table></div>');
  }
  if (json.requirements && json.requirements.length) {
    html.push('<div class="stat-card"><h3>Requirements by status</h3><table>');
    json.requirements.forEach(r => { html.push('<tr><td>' + escapeHtml(r.status || '—') + '</td><td>' + r.count + '</td></tr>'); });
    html.push('</table></div>');
  }
  if (json.tasks && json.tasks.length) {
    html.push('<div class="stat-card"><h3>Tasks by status</h3><table>');
    json.tasks.forEach(r => { html.push('<tr><td>' + escapeHtml(r.status || '—') + '</td><td>' + r.count + '</td></tr>'); });
    html.push('</table></div>');
  }
  if (json.machines && json.machines.length) {
    html.push('<div class="stat-card"><h3>Machines by status</h3><table>');
    json.machines.forEach(r => { html.push('<tr><td>' + escapeHtml(r.status || '—') + '</td><td>' + r.count + '</td></tr>'); });
    html.push('</table></div>');
  }
  return html.length ? '<div class="stats-grid">' + html.join('') + '</div>' : '<p class="empty">No stats.</p>';
}

// ----- Risk report -----
function renderRiskReport(json) {
  const risks = json.risks || [];
  if (risks.length === 0) return '<p class="empty">No risks.</p>';
  let html = '<p><strong>Count: ' + (json.count || risks.length) + '</strong></p><ul class="risk-list">';
  risks.forEach(r => {
    const typeClass = (r.type || '').includes('stuck') ? 'stuck' : (r.type || '').includes('slow') ? 'slow' : 'blocked';
    html += '<li><span class="risk-type ' + typeClass + '">' + escapeHtml(r.type || '') + '</span>';
    if (r.req_id) html += ' Req #' + r.req_id;
    if (r.team) html += ' Team: ' + escapeHtml(r.team);
    if (r.title) html += ' — ' + escapeHtml(r.title);
    if (r.progress != null) html += ' Progress: ' + r.progress + '%';
    if (r.count != null) html += ' Blocked tasks: ' + r.count;
    html += '</li>';
  });
  html += '</ul>';
  return html;
}

// ----- Teams online (list) -----
function renderTeamsOnline(json) {
  const teams = json.teams || [];
  if (teams.length === 0) return '<p class="empty">No online teams.</p>';
  return '<p><strong>Online: </strong>' + teams.map(t => '<span class="badge badge-active">' + escapeHtml(t) + '</span>').join(' ') + '</p>';
}

// ----- Requirements table -----
function renderRequirementsTable(data, options = {}) {
  if (!Array.isArray(data) || data.length === 0) return '<p class="empty">No requirements.</p>';

  const projectScoped = options.projectScoped === true;
  const cols = options.columns || (
    projectScoped
      ? ['id', 'title', 'type', 'status', 'priority', 'assigned_team', 'assigned_agent', 'step', 'progress_percent', 'taken_at', 'updated_at']
      : ['id', 'project_name', 'title', 'type', 'status', 'priority', 'assigned_team', 'assigned_agent', 'step', 'progress_percent', 'taken_at', 'updated_at']
  );

  let html = '<table class="data-table"><thead><tr>';
  cols.forEach(k => { html += '<th>' + escapeHtml(humanKey(k)) + '</th>'; });
  html += '</tr></thead><tbody>';

  data.forEach(row => {
    html += '<tr>';
    cols.forEach(k => {
      let v = row[k];
      if (k === 'status') {
        v = '<span class="badge badge-' + (v === 'new' ? 'new' : v === 'in_progress' ? 'in_progress' : 'done') + '">' + escapeHtml(String(v || '')) + '</span>';
      } else {
        v = formatCell(k, v);
      }
      const cls = typeof row[k] === 'number' && !['id', 'project_id'].includes(k) ? ' num' : '';
      html += '<td class="mono' + cls + '">' + v + '</td>';
    });
    html += '</tr>';
  });

  html += '</tbody></table>';
  return html;
}

function renderTasksTable(data) {
  if (!Array.isArray(data) || data.length === 0) return '<p class="empty">No tasks for this requirement.</p>';
  return buildTable(data, { skipKeys: [] });
}

// ----- Blockages -----
function renderBlockagesTable(data) {
  if (!Array.isArray(data) || data.length === 0) return '<p class="empty">No blockages.</p>';
  return buildTable(data, { skipKeys: [] });
}

// ----- CI/CD Builds (with status badges) -----
function renderCicdBuildsTable(data) {
  if (!Array.isArray(data) || data.length === 0) return '<p class="empty">No builds.</p>';
  const cols = ['id', 'pipeline_name', 'pipeline_id', 'status', 'started_at', 'finished_at', 'build_log', 'artifacts'];
  let html = '<table class="data-table"><thead><tr>';
  cols.forEach(k => { html += '<th>' + escapeHtml(humanKey(k)) + '</th>'; });
  html += '</tr></thead><tbody>';
  data.forEach(row => {
    html += '<tr>';
    cols.forEach(k => {
      let v = row[k];
      if (k === 'status') {
        const c = v === 'success' ? 'badge-done' : v === 'failed' || v === 'cancelled' ? 'badge-offline' : 'badge-in_progress';
        v = '<span class="badge ' + c + '">' + escapeHtml(String(v || '')) + '</span>';
      } else {
        v = formatCell(k, v);
      }
      const truncate = (k === 'build_log' || k === 'artifacts') && typeof row[k] === 'string' && row[k].length > 80 ? ' truncate' : '';
      html += '<td class="mono' + truncate + '" title="' + (row[k] != null ? escapeHtml(String(row[k])) : '') + '">' + v + '</td>';
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  return html;
}

// ----- Feishu stats (two tables) -----
function renderFeishuStats(json) {
  if (json.error) return '<p class="empty">' + escapeHtml(json.error) + '</p>';
  let html = '';
  if (json.daily_stats && json.daily_stats.length) {
    html += '<h3 class="subsection-title">Daily stats</h3>' + buildTable(json.daily_stats, { skipKeys: [] });
  } else {
    html += '<p class="empty">No daily stats.</p>';
  }
  if (json.recent_calls && json.recent_calls.length) {
    html += '<h3 class="subsection-title">Recent calls</h3>' + buildTable(json.recent_calls, { skipKeys: [] });
  } else {
    html += '<p class="empty">No recent calls.</p>';
  }
  return html || '<p class="empty">No data.</p>';
}

// ----- Pipeline runs -----
function renderPipelineRunsTable(data) {
  if (!Array.isArray(data) || data.length === 0) return '<p class="empty">No runs for this pipeline.</p>';
  return buildTable(data, { skipKeys: [] });
}

// ----- Development details -----
function renderDevDetailsSummary(data) {
  if (!Array.isArray(data) || data.length === 0) return '<p class="empty">No development details.</p>';
  let html = '';
  data.forEach(({ team, details }) => {
    if (!details || details.length === 0) return;
    html += '<h3 class="subsection-title">' + escapeHtml(team) + '</h3>';
    html += buildTable(details, { skipKeys: [] });
  });
  return html || '<p class="empty">No development details.</p>';
}

function renderDevDetailsTeamTable(data) {
  if (!Array.isArray(data) || data.length === 0) return '<p class="empty">No task details for this team.</p>';
  return buildTable(data, { skipKeys: [] });
}

// ----- Loaders -----
async function fetchApi(path) {
  var url = API_BASE + path;
  var res = await fetch(url);
  if (!res.ok) throw new Error(res.status + ' ' + res.statusText + ': ' + path);
  var text = await res.text();
  try {
    return text ? JSON.parse(text) : null;
  } catch (e) {
    throw new Error('Invalid JSON from ' + path);
  }
}

/** Fetch raw response text for Raw API view (pretty-print JSON if possible). */
async function fetchRaw(path) {
  var url = API_BASE + path;
  var res = await fetch(url);
  var text = await res.text();
  if (!res.ok) return { error: res.status + ' ' + res.statusText, body: text };
  try {
    var data = text ? JSON.parse(text) : null;
    return { ok: true, text: JSON.stringify(data, null, 2) };
  } catch (e) {
    return { ok: true, text: text };
  }
}

// ----- Dashboard modules (tabs) -----
var currentDashboardTab = 'overview';

function normalizeProjectName(name) {
  return String(name || '')
    .trim()
    .toLowerCase()
    .replace(/_/g, ' ')
    .replace(/-/g, ' ')
    .replace(/\s+/g, ' ');
}

function computeProjectPriorityRanks(projects) {
  var ranksById = {};
  var pinned = {
    'stock analyze': 1,
    'pinball experience': 2,
    'pinball-experience': 2
    , 'smart factory': 3
  };

  var remaining = [];
  (projects || []).forEach(function (p) {
    if (!p || p.id == null) return;
    var pid = Number(p.id);
    var pname = normalizeProjectName(p.name);
    if (pinned.hasOwnProperty(pname)) {
      ranksById[pid] = pinned[pname];
    } else {
      remaining.push(p);
    }
  });

  remaining.sort(function (a, b) { return Number(a.id || 0) - Number(b.id || 0); });
  var nextRank = 4;
  remaining.forEach(function (p) {
    var pid = Number(p.id || 0);
    if (ranksById[pid] == null) {
      ranksById[pid] = nextRank;
      nextRank += 1;
    }
  });
  return ranksById;
}

function requirementPriorityRank(priority) {
  if (!priority) return 2;
  var s = String(priority).toUpperCase().trim();
  if (s[0] === 'P') {
    var n = Number(s.slice(1));
    if (!isNaN(n)) return n;
  }
  return 2;
}

function renderRequirementsByProject(projects, requirements) {
  var projArr = Array.isArray(projects) ? projects : [];
  var reqArr = Array.isArray(requirements) ? requirements : [];
  if (!projArr.length) return renderRequirementsTable(reqArr, { projectScoped: false });
  if (!reqArr.length) return '<p class="empty">No requirements.</p>';

  var ranksById = computeProjectPriorityRanks(projArr);

  var reqsByPid = {};
  reqArr.forEach(function (r) {
    var pid = r && r.project_id != null ? Number(r.project_id) : null;
    if (pid == null) return;
    if (!reqsByPid[pid]) reqsByPid[pid] = [];
    reqsByPid[pid].push(r);
  });

  var projectsSorted = projArr.slice().sort(function (a, b) {
    var ra = ranksById[Number(a.id || 0)];
    var rb = ranksById[Number(b.id || 0)];
    if (ra == null && rb == null) return Number(a.id || 0) - Number(b.id || 0);
    if (ra == null) return 1;
    if (rb == null) return -1;
    if (ra !== rb) return ra - rb;
    return Number(a.id || 0) - Number(b.id || 0);
  });

  var html = '';
  projectsSorted.forEach(function (p) {
    var pid = Number(p.id || 0);
    var rows = reqsByPid[pid] || [];
    if (!rows.length) return;

    var rank = ranksById[pid];
    html += '<h3 class="subsection-title">' + escapeHtml(p.name || 'Unknown') + ' (Priority ' + escapeHtml(rank == null ? '—' : String(rank)) + ')</h3>';

    rows.sort(function (a, b) {
      var bugA = (String(a.type || '').toLowerCase() === 'bug') ? 0 : 1;
      var bugB = (String(b.type || '').toLowerCase() === 'bug') ? 0 : 1;
      if (bugA !== bugB) return bugA - bugB;
      var pa = requirementPriorityRank(a.priority);
      var pb = requirementPriorityRank(b.priority);
      if (pa !== pb) return pa - pb;
      var ca = String(a.created_at || '');
      var cb = String(b.created_at || '');
      if (ca !== cb) return ca < cb ? -1 : 1;
      return Number(a.id || 0) - Number(b.id || 0);
    });

    html += renderRequirementsTable(rows, { projectScoped: true });
  });

  return html || '<p class="empty">No requirements.</p>';
}

function renderMeetingsTable(meetings) {
  if (!Array.isArray(meetings) || meetings.length === 0) return '<p class="empty">No running meetings.</p>';
  var cols = ['id', 'topic', 'host_agent', 'status', 'current_round', 'participants_total', 'created_at'];
  var html = '<table class="data-table"><thead><tr>';
  cols.forEach(function (k) { html += '<th>' + escapeHtml(humanKey(k)) + '</th>'; });
  html += '<th>Action</th></tr></thead><tbody>';
  meetings.forEach(function (m) {
    html += '<tr>';
    cols.forEach(function (k) {
      var v = m[k];
      if (v == null || v === '') v = '—';
      var cls = typeof m[k] === 'number' && !['id', 'project_id'].includes(k) ? ' num' : '';
      html += '<td class="mono' + cls + '">' + escapeHtml(String(v)) + '</td>';
    });
    html += '<td><button type="button" class="btn-refresh btn-view-meeting" data-mid="' + escapeHtml(String(m.id)) + '">View</button></td>';
    html += '</tr>';
  });
  html += '</tbody></table>';
  return html;
}

function renderMeetingDetails(json) {
  if (!json) return '<p class="empty">No meeting data.</p>';
  var meeting = json.meeting || json;
  var participants = json.participants || [];
  if (json.error) return '<p class="error">' + escapeHtml(json.error) + '</p>';

  var html = '';
  if (meeting) {
    html += '<h3 class="subsection-title">Meeting #' + escapeHtml(String(meeting.id || '—')) + '</h3>';
    html += '<div class="stat-card" style="margin-bottom: 1rem;">' +
      '<div><strong>Topic:</strong> ' + escapeHtml(meeting.topic || '—') + '</div>' +
      '<div><strong>Host:</strong> ' + escapeHtml(meeting.host_agent || '—') + '</div>' +
      '<div><strong>Status:</strong> ' + escapeHtml(meeting.status || '—') + '</div>' +
      '<div><strong>Round:</strong> ' + escapeHtml(String(meeting.current_round || 1)) + '</div>' +
      (meeting.problem_to_solve ? '<div><strong>Problem:</strong> ' + escapeHtml(meeting.problem_to_solve) + '</div>' : '') +
      '</div>';
  }
  html += '<h3 class="subsection-title">Participants</h3>';
  html += buildTable(participants, { skipKeys: [] });
  return html || '<p class="empty">No details.</p>';
}

async function loadOverviewTab() {
  var stats = await fetchApi('/api/dashboard/stats');
  var teamsOnline = await fetchApi('/api/teams/online');
  var teamsStatus = await fetchApi('/api/teams/status-report/summary');

  var html = '';
  html += '<h3 class="subsection-title">Stats</h3>' + renderDashboardStats(stats);
  html += '<h3 class="subsection-title">Teams online</h3>' + renderTeamsOnline(teamsOnline);

  var arr = Array.isArray(teamsStatus) ? sortById(teamsStatus) : [teamsStatus];
  html += '<h3 class="subsection-title">Teams status summary</h3>' + (arr.length ? buildTable(arr, { skipKeys: [] }) : '<p class="empty">No team status reports.</p>');
  return html;
}

async function loadRequirementsTab() {
  var projects = await fetchApi('/api/projects');
  var requirements = await fetchApi('/api/requirements');
  return renderRequirementsByProject(projects, requirements);
}

async function loadRiskTab() {
  var risk = await fetchApi('/api/dashboard/risk-report');
  var blockages = await fetchApi('/api/discussion/blockages?status=pending');

  var html = '';
  html += '<h3 class="subsection-title">Risk report</h3>' + renderRiskReport(risk);
  html += '<h3 class="subsection-title">Pending blockages</h3>' + renderBlockagesTable(blockages);
  return html;
}

async function loadMeetingsTab() {
  var meetings = await fetchApi('/api/meetings?status=running');
  var html = '';
  html += '<h3 class="subsection-title">Running meetings</h3>' + renderMeetingsTable(meetings);
  html += '<h3 class="subsection-title">Meeting details</h3>' +
    '<div id="meeting-details" class="content" style="padding: 1rem;">' +
    '<p class="empty">Select a meeting from above.</p>' +
    '</div>';
  return html;
}

async function loadDashboardModule(tabId) {
  var t = tabId || 'overview';
  if (t === 'overview') return loadOverviewTab();
  if (t === 'requirements') return loadRequirementsTab();
  if (t === 'risk') return loadRiskTab();
  if (t === 'meetings') return loadMeetingsTab();
  return '<p class="empty">Unknown dashboard tab.</p>';
}

// ----- Raw API: valid GET APIs by category (task/category, path, description) -----
var RAW_API_LIST = [
  { category: 'Discovery', path: '/api/', desc: 'API index – list all available endpoints' },
  { category: 'Dashboard', path: '/api/dashboard/stats', desc: 'Dashboard stats – projects/requirements/tasks/machines counts by status' },
  { category: 'Dashboard', path: '/api/dashboard/risk-report', desc: 'Risk report – stuck, slow, blocked items' },
  { category: 'Projects', path: '/api/projects', desc: 'List all projects' },
  { category: 'Requirements', path: '/api/requirements', desc: 'List requirements (optional ?status=, ?assigned_team=)' },
  { category: 'Machines', path: '/api/machines', desc: 'List all machines' },
  { category: 'Tools', path: '/api/tools', desc: 'List registered tools' },
  { category: 'Teams', path: '/api/teams/online', desc: 'List online teams' },
  { category: 'Teams', path: '/api/teams/status-report/summary', desc: 'Latest status report per team (active/offline)' },
  { category: 'Teams', path: '/api/teams/machine-status/summary', desc: 'Latest machine status per team' },
  { category: 'Pipelines', path: '/api/pipelines', desc: 'List pipelines' },
  { category: 'Discussion', path: '/api/discussion/blockages', desc: 'List blockages (?status=pending|resolved| or empty for all)' },
  { category: 'CI/CD', path: '/api/cicd/builds', desc: 'List CI/CD builds (?pipeline_id=, ?status=)' },
  { category: 'Feishu', path: '/api/feishu/stats', desc: 'Feishu API call stats (daily + recent)' },
  { category: 'Development details', path: '/api/teams/development-details/summary', desc: 'Task dev details summary per team (?per_team=30)' },
];

function renderRawApiList() {
  var byCat = {};
  RAW_API_LIST.forEach(function (item) {
    if (!byCat[item.category]) byCat[item.category] = [];
    byCat[item.category].push(item);
  });
  var html = '';
  Object.keys(byCat).sort().forEach(function (cat) {
    html += '<h3 class="subsection-title">' + escapeHtml(cat) + '</h3>';
    html += '<table class="data-table"><thead><tr><th>Path</th><th>Purpose</th><th></th></tr></thead><tbody>';
    byCat[cat].forEach(function (item) {
      html += '<tr><td class="mono">GET ' + escapeHtml(item.path) + '</td><td>' + escapeHtml(item.desc) + '</td><td><button type="button" class="btn-refresh btn-view-raw" data-path="' + escapeHtml(item.path) + '">View raw</button></td></tr>';
    });
    html += '</tbody></table>';
  });
  return html;
}

// ----- UI: only Dashboard and Raw API -----
function showSection(sectionId) {
  document.querySelectorAll('.panel').forEach(function (p) { p.classList.remove('active'); });
  document.querySelectorAll('.nav-btn').forEach(function (b) { b.classList.remove('active'); });
  var panel = document.getElementById('section-' + sectionId);
  var btn = document.querySelector('.nav-btn[data-section="' + sectionId + '"]');
  if (panel) panel.classList.add('active');
  if (btn) btn.classList.add('active');
}

async function refreshDashboard() {
  var container = document.getElementById('content-dashboard');
  if (!container) return;
  container.innerHTML = '<p class="loading">Loading…</p>';
  try {
    var html = await loadDashboardModule(currentDashboardTab);
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = '<p class="error">' + escapeHtml(e.message) + '</p>';
    showToast(e.message, true);
  }
}

// ----- Init -----
document.querySelectorAll('.nav-btn').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var section = btn.getAttribute('data-section');
    showSection(section);
    if (section === 'raw-api') {
      var listEl = document.getElementById('raw-api-list');
      if (listEl && !listEl.innerHTML.trim()) listEl.innerHTML = renderRawApiList();
    }
    if (window.SFMgmt && typeof window.SFMgmt.onNavSection === 'function') {
      window.SFMgmt.onNavSection(section);
    }
  });
});

document.querySelectorAll('.btn-refresh').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var r = btn.getAttribute('data-refresh');
    if (r === 'dashboard') refreshDashboard();
    if (window.SFMgmt && typeof window.SFMgmt.onRefreshClick === 'function') {
      window.SFMgmt.onRefreshClick(r);
    }
  });
});

// Dashboard tabs
document.querySelectorAll('.dashboard-tab-btn').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var tabId = btn.getAttribute('data-dashboard-tab');
    if (!tabId) return;
    currentDashboardTab = tabId;
    document.querySelectorAll('.dashboard-tab-btn').forEach(function (b) { b.classList.remove('active'); });
    btn.classList.add('active');
    refreshDashboard();
  });
});

// Raw API: View raw – delegate on content-raw-api
document.getElementById('content-raw-api').addEventListener('click', function (e) {
  var btn = e.target.closest('.btn-view-raw');
  if (!btn) return;
  var path = btn.getAttribute('data-path');
  if (!path) return;
  var outputEl = document.getElementById('raw-api-output');
  if (!outputEl) return;
  outputEl.innerHTML = '<p class="loading">Loading…</p>';
  fetchRaw(path).then(function (result) {
    if (result.error) {
      outputEl.innerHTML = '<p class="error">' + escapeHtml(result.error) + '</p>' +
        (result.body ? '<pre class="raw-api-pre">' + escapeHtml(result.body) + '</pre>' : '');
      showToast(result.error, true);
      return;
    }
    outputEl.innerHTML = '<pre class="raw-api-pre">' + escapeHtml(result.text) + '</pre>';
  }).catch(function (err) {
    outputEl.innerHTML = '<p class="error">' + escapeHtml(err.message) + '</p>';
    showToast(err.message, true);
  });
});

// Load dashboard on first open; prefill Raw API list
function initDashboard() {
  showSection('dashboard');
  var activeBtn = document.querySelector('.dashboard-tab-btn.active');
  if (activeBtn) {
    currentDashboardTab = activeBtn.getAttribute('data-dashboard-tab') || 'overview';
  }

  // Meeting "View" handler (event delegation on container)
  var container = document.getElementById('content-dashboard');
  if (container && !container._meetingViewBound) {
    container._meetingViewBound = true;
    container.addEventListener('click', function (e) {
      var btn = e.target.closest('.btn-view-meeting');
      if (!btn) return;
      var mid = btn.getAttribute('data-mid');
      if (!mid) return;

      var detailsEl = document.getElementById('meeting-details');
      if (!detailsEl) return;
      detailsEl.innerHTML = '<p class="loading">Loading…</p>';

      fetchApi('/api/meetings/' + encodeURIComponent(mid)).then(function (json) {
        detailsEl.innerHTML = renderMeetingDetails(json);
      }).catch(function (err) {
        detailsEl.innerHTML = '<p class="error">' + escapeHtml(err.message) + '</p>';
        showToast(err.message, true);
      });
    });
  }

  refreshDashboard();
  var listEl = document.getElementById('raw-api-list');
  if (listEl) listEl.innerHTML = renderRawApiList();
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDashboard);
} else {
  initDashboard();
}
})();
