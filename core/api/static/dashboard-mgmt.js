/**
 * Smart Factory — Management UI (1:1 with HTTP API for humans)
 * Loaded after dashboard.js; uses same API_BASE convention.
 */
(function () {
  'use strict';

  var API_BASE = (function () {
    var p = window.location.pathname.replace(/\/$/, '');
    return p || '';
  })();

  function toast(msg, isError) {
    var t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.className = 'toast show' + (isError ? ' error' : '');
    clearTimeout(window._toastMgmt);
    window._toastMgmt = setTimeout(function () { t.classList.remove('show'); }, 3500);
  }

  function esc(s) {
    if (s == null) return '';
    var d = document.createElement('div');
    d.textContent = String(s);
    return d.innerHTML;
  }

  async function apiJson(method, path, bodyObj) {
    var opts = { method: method, headers: {} };
    if (bodyObj !== undefined && bodyObj !== null) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(bodyObj);
    }
    var res = await fetch(API_BASE + path, opts);
    var text = await res.text();
    var data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch (e) {
      data = { _raw: text };
    }
    return { ok: res.ok, status: res.status, data: data, text: text };
  }

  // ----- Projects -----
  var selectedProjectId = null;

  function projectFormFields(values, prefix) {
    prefix = prefix || 'pf_';
    values = values || {};
    var fields = [
      ['name', 'text', '名称 name *'],
      ['description', 'textarea', '描述 description'],
      ['type', 'text', '类型 type（默认 game）'],
      ['status', 'text', '状态 status'],
      ['gdd_path', 'text', 'GDD 路径 gdd_path'],
      ['repo_url', 'text', '仓库 URL repo_url'],
      ['repo_default_branch', 'text', '默认分支 repo_default_branch'],
      ['repo_last_sync_at', 'text', '同步时间 repo_last_sync_at (ISO)'],
      ['repo_head_commit', 'text', 'HEAD 提交 repo_head_commit'],
      ['repo_remote_notes', 'textarea', '仓库备注 repo_remote_notes'],
      ['category', 'text', 'category'],
      ['purpose', 'textarea', 'purpose'],
      ['benefits', 'textarea', 'benefits'],
      ['outcome', 'textarea', 'outcome'],
      ['priority', 'text', '优先级 priority (P0–P3)'],
    ];
    var html = '<div class="form-stack">';
    fields.forEach(function (f) {
      var key = f[0];
      var typ = f[1];
      var label = f[2];
      var id = prefix + key;
      var v = values[key] != null ? values[key] : '';
      html += '<label for="' + esc(id) + '">' + esc(label) + '</label>';
      if (typ === 'textarea') {
        html += '<textarea id="' + esc(id) + '" name="' + esc(key) + '">' + esc(v) + '</textarea>';
      } else {
        html += '<input type="text" id="' + esc(id) + '" name="' + esc(key) + '" value="' + esc(v) + '">';
      }
    });
    html += '</div>';
    return html;
  }

  function readProjectForm(prefix) {
    prefix = prefix || 'pf_';
    var keys = ['name', 'description', 'type', 'status', 'gdd_path', 'repo_url', 'repo_default_branch',
      'repo_last_sync_at', 'repo_head_commit', 'repo_remote_notes', 'category', 'purpose', 'benefits', 'outcome', 'priority'];
    var out = {};
    keys.forEach(function (k) {
      var el = document.getElementById(prefix + k);
      if (!el) return;
      var v = el.value.trim();
      if (v !== '') out[k] = v;
    });
    return out;
  }

  async function refreshProjectsPanel() {
    var container = document.getElementById('content-projects');
    if (!container) return;
    container.innerHTML = '<p class="loading">Loading…</p>';
    try {
      var r = await apiJson('GET', '/api/projects');
      if (!r.ok) throw new Error(r.status + ' ' + (r.data && r.data.error ? r.data.error : 'projects'));
      var projects = Array.isArray(r.data) ? r.data : [];
      var html = '<div class="mgmt-grid"><div class="mgmt-panel"><h3>新建项目 POST /api/projects</h3>';
      html += projectFormFields({}, 'newpf_');
      html += '<div class="form-actions"><button type="button" class="btn-primary" id="btn-project-create">创建</button></div>';
      html += '</div><div class="mgmt-panel"><h3>项目列表</h3>';
      if (!projects.length) {
        html += '<p class="empty">无项目</p>';
      } else {
        html += '<table class="data-table"><thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Status</th><th>Priority</th><th class="cell-actions">操作</th></tr></thead><tbody>';
        projects.forEach(function (p) {
          html += '<tr><td class="mono">' + esc(p.id) + '</td><td>' + esc(p.name) + '</td><td>' + esc(p.type) + '</td><td>' + esc(p.status) + '</td><td>' + esc(p.priority) + '</td>';
          html += '<td class="cell-actions"><button type="button" class="btn-refresh btn-small btn-proj-edit" data-id="' + esc(p.id) + '">编辑</button> ';
          html += '<button type="button" class="btn-refresh btn-small btn-proj-reqs" data-id="' + esc(p.id) + '">需求</button></td></tr>';
        });
        html += '</tbody></table>';
      }
      html += '</div></div>';
      html += '<div id="project-editor-wrap" class="mgmt-panel" style="margin: 1rem; display:none;"><h3>编辑 PATCH /api/projects/&lt;id&gt; · DELETE</h3><div id="project-editor-inner"></div></div>';
      container.innerHTML = html;

      document.getElementById('btn-project-create').addEventListener('click', async function () {
        var body = readProjectForm('newpf_');
        if (!body.name) {
          toast('name 必填', true);
          return;
        }
        if (!body.type) body.type = 'game';
        if (!body.status) body.status = 'active';
        if (!body.priority) body.priority = 'P2';
        var cr = await apiJson('POST', '/api/projects', body);
        if (!cr.ok) {
          toast((cr.data && cr.data.error) || cr.text || '创建失败', true);
          return;
        }
        toast('已创建 id=' + (cr.data && cr.data.id));
        refreshProjectsPanel();
      });

      container.querySelectorAll('.btn-proj-edit').forEach(function (b) {
        b.addEventListener('click', async function () {
          var pid = b.getAttribute('data-id');
          selectedProjectId = pid;
          var wr = document.getElementById('project-editor-wrap');
          var inner = document.getElementById('project-editor-inner');
          wr.style.display = 'block';
          inner.innerHTML = '<p class="loading">Loading…</p>';
          var gr = await apiJson('GET', '/api/projects/' + encodeURIComponent(pid));
          if (!gr.ok) {
            inner.innerHTML = '<p class="error">加载失败</p>';
            return;
          }
          var pv = gr.data;
          inner.innerHTML = '<p class="hint mono">ID ' + esc(pv.id) + '</p>' + projectFormFields(pv, 'pf_');
          inner.innerHTML += '<div class="form-actions">' +
            '<button type="button" class="btn-primary" id="btn-project-save">保存 PATCH</button> ' +
            '<button type="button" class="btn-danger" id="btn-project-del">删除 DELETE（无需求时）</button></div>' +
            '<div id="project-reqs-preview" style="margin-top:1rem;"></div>';

          document.getElementById('btn-project-save').addEventListener('click', async function () {
            var patch = readProjectForm('pf_');
            var pr = await apiJson('PATCH', '/api/projects/' + encodeURIComponent(pid), patch);
            if (!pr.ok) {
              toast((pr.data && pr.data.error) || 'PATCH 失败', true);
              return;
            }
            toast('项目已更新');
            refreshProjectsPanel();
          });
          document.getElementById('btn-project-del').addEventListener('click', async function () {
            if (!confirm('确认删除项目 #' + pid + '？（存在需求时会 409）')) return;
            var dr = await apiJson('DELETE', '/api/projects/' + encodeURIComponent(pid));
            if (!dr.ok) {
              toast((dr.data && dr.data.error) || dr.text, true);
              return;
            }
            toast('已删除');
            wr.style.display = 'none';
            refreshProjectsPanel();
          });
        });
      });

      container.querySelectorAll('.btn-proj-reqs').forEach(function (b) {
        b.addEventListener('click', async function () {
          var pid = b.getAttribute('data-id');
          var wr = document.getElementById('project-editor-wrap');
          var inner = document.getElementById('project-editor-inner');
          if (!wr || !inner) return;
          wr.style.display = 'block';
          inner.innerHTML = '<h3>项目 #' + esc(pid) + ' — GET /api/projects/' + esc(pid) + '/requirements</h3><div id="project-reqs-preview"></div>';
          var prev = document.getElementById('project-reqs-preview');
          prev.innerHTML = '<p class="loading">Loading…</p>';
          var rr = await apiJson('GET', '/api/projects/' + encodeURIComponent(pid) + '/requirements');
          if (rr.ok && Array.isArray(rr.data)) {
            prev.innerHTML = rr.data.length
              ? '<table class="data-table"><thead><tr><th>id</th><th>title</th><th>status</th><th>team</th></tr></thead><tbody>' +
                rr.data.map(function (x) {
                  return '<tr><td>' + esc(x.id) + '</td><td>' + esc(x.title) + '</td><td>' + esc(x.status) + '</td><td>' + esc(x.assigned_team) + '</td></tr>';
                }).join('') + '</tbody></table>'
              : '<p class="empty">无需求</p>';
          } else prev.innerHTML = '<p class="error">加载失败</p>';
        });
      });
    } catch (e) {
      container.innerHTML = '<p class="error">' + esc(e.message) + '</p>';
      toast(e.message, true);
    }
  }

  // ----- Requirements -----
  var selectedReqId = null;
  var reqFilterState = { status: '', priority: '', assigned_team: '' };

  function requirementEditForm(row) {
    row = row || {};
    var fields = [
      ['title', 'text', 'title'],
      ['description', 'textarea', 'description'],
      ['priority', 'text', 'priority'],
      ['status', 'text', 'status'],
      ['type', 'text', 'type'],
      ['assigned_to', 'text', 'assigned_to'],
      ['assigned_team', 'text', 'assigned_team'],
      ['assigned_agent', 'text', 'assigned_agent'],
      ['taken_at', 'text', 'taken_at'],
      ['plan_step_id', 'text', 'plan_step_id'],
      ['plan_phase', 'text', 'plan_phase'],
      ['step', 'text', 'step'],
      ['progress_percent', 'text', 'progress_percent'],
      ['depends_on', 'textarea', 'depends_on (JSON 数组，如 [1,2])'],
      ['parent_requirement_id', 'text', 'parent_requirement_id'],
      ['design_doc_path', 'text', 'design_doc_path'],
      ['acceptance_criteria', 'editable-textarea', 'acceptance_criteria'],
      ['note', 'textarea', 'note'],
    ];
    var html = '<div class="form-stack">';
    fields.forEach(function (f) {
      var key = f[0];
      var typ = f[1];
      var label = f[2];
      var id = 'rq_' + key;
      var v = row[key] != null ? row[key] : '';
      if (key === 'depends_on' && typeof v === 'string' && v.startsWith('[')) { /* keep */ }
      else if (key === 'depends_on' && v && typeof v === 'object') v = JSON.stringify(v);
      html += '<label for="' + esc(id) + '">' + esc(label) + '</label>';
      if (typ === 'textarea' || typ === 'editable-textarea') {
        html += '<textarea id="' + esc(id) + '" name="' + esc(key) + '" class="' + (typ === 'editable-textarea' ? '' : '') + '">' + esc(v) + '</textarea>';
      } else {
        html += '<input type="text" id="' + esc(id) + '" name="' + esc(key) + '" value="' + esc(v) + '">';
      }
    });
    html += '</div>';
    return html;
  }

  function readReqPatchForm() {
    var keys = ['title', 'description', 'priority', 'status', 'type', 'assigned_to', 'assigned_team', 'assigned_agent',
      'taken_at', 'plan_step_id', 'plan_phase', 'step', 'progress_percent', 'design_doc_path', 'acceptance_criteria', 'note', 'parent_requirement_id'];
    var out = {};
    keys.forEach(function (k) {
      var el = document.getElementById('rq_' + k);
      if (!el) return;
      var v = el.value.trim();
      if (v !== '') {
        if (k === 'progress_percent') out[k] = Number(v);
        else if (k === 'parent_requirement_id') out[k] = v === '' ? null : Number(v);
        else out[k] = v;
      }
    });
    var depEl = document.getElementById('rq_depends_on');
    if (depEl && depEl.value.trim()) {
      try {
        out.depends_on = JSON.parse(depEl.value.trim());
      } catch (e) {
        out.depends_on = depEl.value.trim();
      }
    }
    return out;
  }

  async function loadRequirementDetail(reqId) {
    var wrap = document.getElementById('req-detail-panel');
    if (!wrap) return;
    wrap.innerHTML = '<p class="loading">Loading…</p>';
    var gr = await apiJson('GET', '/api/requirements/' + encodeURIComponent(reqId));
    if (!gr.ok) {
      wrap.innerHTML = '<p class="error">无法加载需求</p>';
      return;
    }
    var row = gr.data;
    var html = '<p class="hint mono">code: ' + esc(row.code || '') + ' · GET /api/requirements/' + esc(reqId) + '</p>';
    html += requirementEditForm(row);
    html += '<div class="form-actions">' +
      '<button type="button" class="btn-primary" id="btn-req-patch">保存 PATCH</button>' +
      '<button type="button" class="btn-refresh" id="btn-req-autosplit">自动拆分 POST auto-split</button></div>';
    html += '<h4 class="subsection-title">领取 POST take</h4><div class="form-stack">' +
      '<label>assigned_team</label><input type="text" id="take_team" placeholder="jarvis">' +
      '<label>assigned_agent</label><input type="text" id="take_agent" placeholder="agent id"></div>' +
      '<button type="button" class="btn-primary btn-small" id="btn-req-take">Take</button>';
    html += '<h4 class="subsection-title">分配 POST assign（Vanguard）</h4><div class="form-stack">' +
      '<label>assigned_team</label><input type="text" id="assign_team" placeholder="tesla"></div>' +
      '<button type="button" class="btn-primary btn-small" id="btn-req-assign">Assign</button>';

    html += '<h4 class="subsection-title">新建任务 POST /api/tasks</h4><div class="form-stack">' +
      '<label>title</label><input type="text" id="new_task_title">' +
      '<label>description</label><textarea id="new_task_desc"></textarea>' +
      '<label>executor</label><input type="text" id="new_task_exec"></div>' +
      '<button type="button" class="btn-primary btn-small" id="btn-task-create">创建任务</button>';

    html += '<h4 class="subsection-title">任务列表 GET /api/requirements/' + esc(reqId) + '/tasks</h4><div id="req-tasks-area"></div>';

    html += '<h4 class="subsection-title">测试用例</h4><div id="req-tc-area"></div>';

    wrap.innerHTML = html;

    document.getElementById('btn-req-patch').addEventListener('click', async function () {
      var body = readReqPatchForm();
      var pr = await apiJson('PATCH', '/api/requirements/' + encodeURIComponent(reqId), body);
      if (!pr.ok) {
        toast((pr.data && pr.data.error) || 'PATCH 失败', true);
        return;
      }
      toast('需求已更新');
      refreshRequirementsPanel();
    });
    document.getElementById('btn-req-autosplit').addEventListener('click', async function () {
      var ar = await apiJson('POST', '/api/requirements/' + encodeURIComponent(reqId) + '/auto-split', {});
      if (!ar.ok) {
        toast((ar.data && ar.data.error) || 'auto-split 失败', true);
        return;
      }
      toast('已触发 auto-split');
      loadRequirementDetail(reqId);
    });
    document.getElementById('btn-req-take').addEventListener('click', async function () {
      var body = { assigned_team: document.getElementById('take_team').value.trim(), assigned_agent: document.getElementById('take_agent').value.trim() };
      var tr = await apiJson('POST', '/api/requirements/' + encodeURIComponent(reqId) + '/take', body);
      if (!tr.ok) {
        toast((tr.data && tr.data.error) || 'take 失败', true);
        return;
      }
      toast('已领取');
      loadRequirementDetail(reqId);
    });
    document.getElementById('btn-req-assign').addEventListener('click', async function () {
      var body = { assigned_team: document.getElementById('assign_team').value.trim() };
      var tr = await apiJson('POST', '/api/requirements/' + encodeURIComponent(reqId) + '/assign', body);
      if (!tr.ok) {
        toast((tr.data && tr.data.error) || 'assign 失败', true);
        return;
      }
      toast('已分配');
      loadRequirementDetail(reqId);
    });
    document.getElementById('btn-task-create').addEventListener('click', async function () {
      var body = {
        req_id: Number(reqId),
        title: document.getElementById('new_task_title').value.trim(),
        description: document.getElementById('new_task_desc').value.trim(),
        executor: document.getElementById('new_task_exec').value.trim(),
      };
      if (!body.title) {
        toast('任务 title 必填', true);
        return;
      }
      var cr = await apiJson('POST', '/api/tasks', body);
      if (!cr.ok) {
        toast((cr.data && cr.data.error) || '创建任务失败', true);
        return;
      }
      toast('任务已创建');
      loadRequirementDetail(reqId);
    });

    await loadTasksBlock(reqId);
    await loadTestCasesBlock(reqId);
  }

  async function loadTasksBlock(reqId) {
    var area = document.getElementById('req-tasks-area');
    if (!area) return;
    var r = await apiJson('GET', '/api/requirements/' + encodeURIComponent(reqId) + '/tasks');
    if (!r.ok || !Array.isArray(r.data)) {
      area.innerHTML = '<p class="error">加载任务失败</p>';
      return;
    }
    if (!r.data.length) {
      area.innerHTML = '<p class="empty">无任务</p>';
      return;
    }
    var html = '<table class="data-table"><thead><tr><th>id</th><th>code</th><th>title</th><th>status</th><th>executor</th><th>操作</th></tr></thead><tbody>';
    r.data.forEach(function (t) {
      html += '<tr><td>' + esc(t.id) + '</td><td class="mono">' + esc(t.code || '') + '</td><td>' + esc(t.title) + '</td><td>' + esc(t.status) + '</td><td>' + esc(t.executor) + '</td>';
      html += '<td><button type="button" class="btn-refresh btn-small btn-task-patch" data-tid="' + esc(t.id) + '">PATCH</button></td></tr>';
    });
    html += '</tbody></table>';
    html += '<div id="task-patch-panel" class="mgmt-panel" style="margin-top:0.75rem;display:none;"><h4>PATCH /api/tasks/&lt;id&gt;</h4>' +
      '<div class="form-stack"><label>title</label><input id="tp_title"><label>status</label><input id="tp_status" placeholder="todo|in_progress|done|blocked">' +
      '<label>executor</label><input id="tp_executor"><label>output_path</label><input id="tp_output_path"><label>step</label><input id="tp_step">' +
      '<label>next_step_task_id</label><input id="tp_next" placeholder="空表示清除"><label>risk</label><input id="tp_risk"><label>blocker</label><input id="tp_blocker">' +
      '<label>note</label><textarea id="tp_note"></textarea></div>' +
      '<div class="form-actions"><button type="button" class="btn-primary" id="btn-task-patch-save">提交 PATCH</button></div></div>';
    area.innerHTML = html;

    var patchPanel = document.getElementById('task-patch-panel');
    var currentTid = null;
    area.querySelectorAll('.btn-task-patch').forEach(function (b) {
      b.addEventListener('click', async function () {
        currentTid = b.getAttribute('data-tid');
        patchPanel.style.display = 'block';
        var gt = await apiJson('GET', '/api/tasks/' + encodeURIComponent(currentTid));
        if (gt.ok && gt.data) {
          var d = gt.data;
          document.getElementById('tp_title').value = d.title || '';
          document.getElementById('tp_status').value = d.status || '';
          document.getElementById('tp_executor').value = d.executor || '';
          document.getElementById('tp_output_path').value = d.output_path || '';
          document.getElementById('tp_step').value = d.step || '';
          document.getElementById('tp_next').value = d.next_step_task_id != null ? String(d.next_step_task_id) : '';
          document.getElementById('tp_risk').value = d.risk || '';
          document.getElementById('tp_blocker').value = d.blocker || '';
          document.getElementById('tp_note').value = d.note || '';
        }
      });
    });
    document.getElementById('btn-task-patch-save').addEventListener('click', async function () {
      if (!currentTid) return;
      var body = {};
      var pairs = [['title', 'tp_title'], ['status', 'tp_status'], ['executor', 'tp_executor'], ['output_path', 'tp_output_path'], ['step', 'tp_step'], ['risk', 'tp_risk'], ['blocker', 'tp_blocker'], ['note', 'tp_note']];
      pairs.forEach(function (p) {
        var v = document.getElementById(p[1]).value.trim();
        if (v !== '') body[p[0]] = v;
      });
      var nx = document.getElementById('tp_next').value.trim();
      if (nx !== '') body.next_step_task_id = Number(nx);
      else body.next_step_task_id = null;
      var pr = await apiJson('PATCH', '/api/tasks/' + encodeURIComponent(currentTid), body);
      if (!pr.ok) {
        toast((pr.data && pr.data.error) || '任务 PATCH 失败', true);
        return;
      }
      toast('任务已更新');
      loadRequirementDetail(reqId);
    });
  }

  async function loadTestCasesBlock(reqId) {
    var area = document.getElementById('req-tc-area');
    if (!area) return;
    var r = await apiJson('GET', '/api/requirements/' + encodeURIComponent(reqId) + '/test-cases');
    if (!r.ok) {
      area.innerHTML = '<p class="error">' + esc((r.data && r.data.error) || '加载测试用例失败') + '</p>';
      return;
    }
    var rows = Array.isArray(r.data) ? r.data : [];
    var html = '<div class="form-stack" style="margin-bottom:1rem;"><h4>新建 POST test-cases</h4>' +
      '<label>title *</label><input id="tc_new_title">' +
      '<label>layer</label><input id="tc_new_layer" placeholder="unit|component|...">' +
      '<label>task_id</label><input id="tc_new_task_id">' +
      '<label>description</label><textarea id="tc_new_desc"></textarea>' +
      '<label>status</label><input id="tc_new_status" placeholder="planned">' +
      '<label>result_notes</label><textarea id="tc_new_notes"></textarea>' +
      '<button type="button" class="btn-primary btn-small" id="btn-tc-create">创建测试用例</button></div>';

    if (rows.length) {
      html += '<table class="data-table"><thead><tr><th>id</th><th>layer</th><th>title</th><th>status</th><th>操作</th></tr></thead><tbody>';
      rows.forEach(function (tc) {
        html += '<tr><td>' + esc(tc.id) + '</td><td>' + esc(tc.layer) + '</td><td>' + esc(tc.title) + '</td><td>' + esc(tc.status) + '</td>';
        html += '<td><button type="button" class="btn-refresh btn-small btn-tc-edit" data-tcid="' + esc(tc.id) + '">PATCH</button> ';
        html += '<button type="button" class="btn-danger btn-small btn-tc-del" data-tcid="' + esc(tc.id) + '">DELETE</button></td></tr>';
      });
      html += '</tbody></table>';
    } else html += '<p class="empty">暂无测试用例</p>';

    html += '<div id="tc-patch-panel" class="mgmt-panel" style="margin-top:0.75rem;display:none;"><h4>PATCH /api/test-cases/&lt;id&gt;</h4>' +
      '<div class="form-stack"><label>task_id</label><input id="tcp_task_id"><label>layer</label><input id="tcp_layer"><label>title</label><input id="tcp_title">' +
      '<label>description</label><textarea id="tcp_desc"></textarea><label>status</label><input id="tcp_status"><label>result_notes</label><textarea id="tcp_notes"></textarea></div>' +
      '<button type="button" class="btn-primary btn-small" id="btn-tc-patch-save">保存</button></div>';

    area.innerHTML = html;

    document.getElementById('btn-tc-create').addEventListener('click', async function () {
      var body = {
        title: document.getElementById('tc_new_title').value.trim(),
        layer: document.getElementById('tc_new_layer').value.trim() || 'unit',
        description: document.getElementById('tc_new_desc').value.trim() || null,
        status: document.getElementById('tc_new_status').value.trim() || 'planned',
        result_notes: document.getElementById('tc_new_notes').value.trim() || null,
      };
      var tid = document.getElementById('tc_new_task_id').value.trim();
      if (tid) body.task_id = Number(tid);
      if (!body.title) {
        toast('测试用例 title 必填', true);
        return;
      }
      var cr = await apiJson('POST', '/api/requirements/' + encodeURIComponent(reqId) + '/test-cases', body);
      if (!cr.ok) {
        toast((cr.data && cr.data.error) || '创建失败', true);
        return;
      }
      toast('测试用例已创建');
      loadRequirementDetail(reqId);
    });

    var tcPatchId = null;
    var tcp = document.getElementById('tc-patch-panel');
    area.querySelectorAll('.btn-tc-edit').forEach(function (b) {
      b.addEventListener('click', async function () {
        tcPatchId = b.getAttribute('data-tcid');
        tcp.style.display = 'block';
        var gr = await apiJson('GET', '/api/test-cases/' + encodeURIComponent(tcPatchId));
        if (gr.ok && gr.data) {
          var d = gr.data;
          document.getElementById('tcp_task_id').value = d.task_id != null ? String(d.task_id) : '';
          document.getElementById('tcp_layer').value = d.layer || '';
          document.getElementById('tcp_title').value = d.title || '';
          document.getElementById('tcp_desc').value = d.description || '';
          document.getElementById('tcp_status').value = d.status || '';
          document.getElementById('tcp_notes').value = d.result_notes || '';
        }
      });
    });
    area.querySelectorAll('.btn-tc-del').forEach(function (b) {
      b.addEventListener('click', async function () {
        var id = b.getAttribute('data-tcid');
        if (!confirm('删除测试用例 #' + id + '?')) return;
        var dr = await apiJson('DELETE', '/api/test-cases/' + encodeURIComponent(id));
        if (!dr.ok) {
          toast((dr.data && dr.data.error) || '删除失败', true);
          return;
        }
        toast('已删除');
        loadRequirementDetail(reqId);
      });
    });
    document.getElementById('btn-tc-patch-save').addEventListener('click', async function () {
      if (!tcPatchId) return;
      var body = {};
      [['task_id', 'tcp_task_id'], ['layer', 'tcp_layer'], ['title', 'tcp_title'], ['description', 'tcp_desc'], ['status', 'tcp_status'], ['result_notes', 'tcp_notes']].forEach(function (p) {
        var v = document.getElementById(p[1]).value.trim();
        if (v !== '') {
          if (p[0] === 'task_id') body.task_id = Number(v);
          else body[p[0]] = v;
        }
      });
      var pr = await apiJson('PATCH', '/api/test-cases/' + encodeURIComponent(tcPatchId), body);
      if (!pr.ok) {
        toast((pr.data && pr.data.error) || 'PATCH 失败', true);
        return;
      }
      toast('测试用例已更新');
      loadRequirementDetail(reqId);
    });
  }

  async function refreshRequirementsPanel() {
    var container = document.getElementById('content-requirements');
    var filters = document.getElementById('req-filters');
    if (!container || !filters) return;

    filters.innerHTML = '<label>status <input type="text" id="flt_status" placeholder="new" value="' + esc(reqFilterState.status) + '"></label>' +
      '<label>priority <input type="text" id="flt_priority" placeholder="P0" value="' + esc(reqFilterState.priority) + '"></label>' +
      '<label>assigned_team <input type="text" id="flt_team" value="' + esc(reqFilterState.assigned_team) + '"></label>' +
      '<button type="button" class="btn-refresh" id="btn-req-filter">应用筛选</button>';

    container.innerHTML = '<p class="loading">Loading…</p>';

    document.getElementById('btn-req-filter').addEventListener('click', function () {
      reqFilterState.status = document.getElementById('flt_status').value.trim();
      reqFilterState.priority = document.getElementById('flt_priority').value.trim();
      reqFilterState.assigned_team = document.getElementById('flt_team').value.trim();
      refreshRequirementsPanel();
    });

    var qs = [];
    if (reqFilterState.status) qs.push('status=' + encodeURIComponent(reqFilterState.status));
    if (reqFilterState.priority) qs.push('priority=' + encodeURIComponent(reqFilterState.priority));
    if (reqFilterState.assigned_team) qs.push('assigned_team=' + encodeURIComponent(reqFilterState.assigned_team));
    var path = '/api/requirements' + (qs.length ? '?' + qs.join('&') : '');

    try {
      var lr = await apiJson('GET', path);
      if (!lr.ok) throw new Error('requirements');
      var list = Array.isArray(lr.data) ? lr.data : [];

      var html = '<div class="mgmt-grid"><div class="mgmt-panel"><h3>新建需求 POST /api/requirements</h3>' +
        '<div class="form-stack"><label>project_id *</label><input id="cr_project_id" type="number">' +
        '<label>title *</label><input id="cr_title"><label>description</label><textarea id="cr_desc"></textarea>' +
        '<label>priority</label><input id="cr_priority" value="P2"><label>type</label><input id="cr_type" value="feature">' +
        '<label>plan_step_id</label><input id="cr_plan_step"><label>plan_phase</label><input id="cr_plan_phase">' +
        '<label>parent_requirement_id</label><input id="cr_parent"><label>depends_on JSON</label><textarea id="cr_dep" placeholder="[]"></textarea>' +
        '<label>note</label><textarea id="cr_note"></textarea></div>' +
        '<button type="button" class="btn-primary" id="btn-req-create">创建</button></div>';

      html += '<div class="mgmt-panel"><h3>列表 ' + esc(path) + '</h3>';
      if (!list.length) html += '<p class="empty">无数据</p>';
      else {
        html += '<table class="data-table"><thead><tr><th>id</th><th>code</th><th>title</th><th>status</th><th>team</th><th>操作</th></tr></thead><tbody>';
        list.forEach(function (r) {
          html += '<tr><td>' + esc(r.id) + '</td><td class="mono">' + esc(r.code || '') + '</td><td>' + esc(r.title) + '</td><td>' + esc(r.status) + '</td><td>' + esc(r.assigned_team) + '</td>';
          html += '<td><button type="button" class="btn-refresh btn-small btn-req-open" data-rid="' + esc(r.id) + '">打开编辑</button></td></tr>';
        });
        html += '</tbody></table>';
      }
      html += '</div></div>';
      html += '<div id="req-detail-panel" class="mgmt-panel" style="margin:1rem;"></div>';
      container.innerHTML = html;

      document.getElementById('btn-req-create').addEventListener('click', async function () {
        var pid = document.getElementById('cr_project_id').value.trim();
        var title = document.getElementById('cr_title').value.trim();
        if (!pid) {
          toast('project_id 必填', true);
          return;
        }
        if (!title) {
          toast('title 必填', true);
          return;
        }
        var body = {
          project_id: Number(pid),
          title: title,
          description: document.getElementById('cr_desc').value.trim() || undefined,
          priority: document.getElementById('cr_priority').value.trim() || 'P2',
          type: document.getElementById('cr_type').value.trim() || 'feature',
          plan_step_id: document.getElementById('cr_plan_step').value.trim() || undefined,
          plan_phase: document.getElementById('cr_plan_phase').value.trim() || undefined,
          note: document.getElementById('cr_note').value.trim() || undefined,
        };
        var par = document.getElementById('cr_parent').value.trim();
        if (par) body.parent_requirement_id = Number(par);
        var dep = document.getElementById('cr_dep').value.trim();
        if (dep) {
          try {
            body.depends_on = JSON.parse(dep);
          } catch (e) {
            toast('depends_on 需为合法 JSON', true);
            return;
          }
        }
        var cr = await apiJson('POST', '/api/requirements', body);
        if (!cr.ok) {
          toast((cr.data && cr.data.error) || '创建失败', true);
          return;
        }
        toast('需求已创建 id=' + (cr.data && cr.data.id));
        refreshRequirementsPanel();
      });

      container.querySelectorAll('.btn-req-open').forEach(function (b) {
        b.addEventListener('click', function () {
          selectedReqId = b.getAttribute('data-rid');
          loadRequirementDetail(selectedReqId);
        });
      });

      if (selectedReqId) {
        loadRequirementDetail(selectedReqId);
      }
    } catch (e) {
      container.innerHTML = '<p class="error">' + esc(e.message) + '</p>';
      toast(e.message, true);
    }
  }

  // ----- Teams -----
  async function refreshTeamsPanel() {
    var container = document.getElementById('content-teams');
    if (!container) return;
    container.innerHTML = '<p class="loading">Loading…</p>';
    try {
      var online = await apiJson('GET', '/api/teams/online');
      var sumRep = await apiJson('GET', '/api/teams/status-report/summary');
      var sumMach = await apiJson('GET', '/api/teams/machine-status/summary');
      var risk = await apiJson('GET', '/api/dashboard/risk-report');
      var block = await apiJson('GET', '/api/discussion/blockages?status=pending');

      var teamsSet = {};
      if (online.ok && online.data && online.data.teams) online.data.teams.forEach(function (t) { teamsSet[t] = true; });
      if (sumRep.ok && Array.isArray(sumRep.data)) sumRep.data.forEach(function (r) { if (r.team) teamsSet[r.team] = true; });

      var html = '<h3 class="subsection-title">GET /api/teams/online</h3>';
      if (online.ok && online.data && online.data.teams && online.data.teams.length) {
        html += '<p>' + online.data.teams.map(function (t) { return '<span class="badge badge-active">' + esc(t) + '</span>'; }).join(' ') + '</p>';
      } else html += '<p class="empty">无在线团队或请求失败</p>';

      html += '<h3 class="subsection-title">GET /api/teams/status-report/summary</h3>';
      html += sumRep.ok && Array.isArray(sumRep.data) && sumRep.data.length
        ? '<div class="table-scroll">' + buildSimpleTable(sumRep.data) + '</div>' : '<p class="empty">无数据</p>';

      html += '<h3 class="subsection-title">GET /api/teams/machine-status/summary</h3>';
      html += sumMach.ok && Array.isArray(sumMach.data) && sumMach.data.length
        ? '<div class="table-scroll">' + buildSimpleTable(sumMach.data) + '</div>' : '<p class="empty">无数据</p>';

      html += '<h3 class="subsection-title">GET /api/dashboard/risk-report</h3>';
      if (risk.ok && risk.data) {
        var risks = risk.data.risks || [];
        html += '<p>count: ' + esc(risk.data.count != null ? risk.data.count : risks.length) + '</p><ul class="risk-list">';
        risks.forEach(function (r) {
          html += '<li><span class="mono">' + esc(r.type) + '</span> req ' + esc(r.req_id) + ' ' + esc(r.title || '') + '</li>';
        });
        html += '</ul>';
      } else html += '<p class="empty">无风险数据</p>';

      var devSum = await apiJson('GET', '/api/teams/development-details/summary');
      html += '<h3 class="subsection-title">GET /api/teams/development-details/summary</h3>';
      if (devSum.ok && devSum.data != null) {
        html += '<pre class="payload-pre" style="max-height:240px;">' + esc(JSON.stringify(devSum.data, null, 2)) + '</pre>';
      } else html += '<p class="empty">无数据或失败</p>';

      html += '<h3 class="subsection-title">GET /api/discussion/blockages?status=pending</h3>';
      html += block.ok && Array.isArray(block.data) && block.data.length
        ? buildSimpleTable(block.data) : '<p class="empty">无待处理阻塞</p>';

      html += '<div class="mgmt-panel" style="margin-top:1rem;"><h3>按团队查看 · 上报</h3>' +
        '<label>team</label><input type="text" id="team_pick" list="team-list" placeholder="jarvis">' +
        '<datalist id="team-list">' + Object.keys(teamsSet).sort().map(function (t) { return '<option value="' + esc(t) + '">'; }).join('') + '</datalist>' +
        '<div class="form-actions"><button type="button" class="btn-refresh" id="btn-team-load">加载分配与报告</button></div>' +
        '<div id="team-detail-out" style="margin-top:1rem;"></div></div>';

      html += '<div class="mgmt-grid"><div class="mgmt-panel"><h3>POST /api/discussion/blockage</h3>' +
        '<div class="form-stack"><label>team</label><input id="bl_team"><label>requirement_id</label><input id="bl_req" type="number">' +
        '<label>task_id (optional)</label><input id="bl_task" type="number"><label>reason</label><textarea id="bl_reason"></textarea>' +
        '<label>options JSON</label><textarea id="bl_opts" class="code"></textarea></div>' +
        '<button type="button" class="btn-primary" id="btn-block-post">上报阻塞</button></div>';

      html += '<div class="mgmt-panel"><h3>PATCH /api/discussion/blockage/&lt;id&gt;</h3>' +
        '<label>blockage id</label><input id="bl_res_id" type="number">' +
        '<label>status</label><input id="bl_res_status" placeholder="resolved">' +
        '<label>decision</label><textarea id="bl_res_decision"></textarea>' +
        '<button type="button" class="btn-primary" id="btn-block-patch">更新</button></div></div>';

      html += '<div class="mgmt-grid"><div class="mgmt-panel"><h3>POST /api/teams/&lt;team&gt;/machine-status</h3>' +
        '<label>reporter_agent</label><input id="ms_agent"><label>payload JSON</label><textarea id="ms_payload" class="code">{}</textarea>' +
        '<button type="button" class="btn-primary" id="btn-ms-post">提交</button></div>';

      html += '<div class="mgmt-panel"><h3>POST /api/teams/&lt;team&gt;/status-report</h3>' +
        '<label>reporter_agent</label><input id="sr_agent"><label>payload JSON</label><textarea id="sr_payload" class="code">{}</textarea>' +
        '<button type="button" class="btn-primary" id="btn-sr-post">提交</button></div></div>';

      html += '<div class="mgmt-panel"><h3>POST /api/teams/&lt;team&gt;/task-detail</h3>' +
        '<div class="form-stack"><label>requirement_id</label><input id="td_req" type="number"><label>task_id</label><input id="td_task" type="number">' +
        '<label>detail_type</label><input id="td_type" placeholder="analysis|assignment|development">' +
        '<label>content</label><textarea id="td_content"></textarea></div>' +
        '<button type="button" class="btn-primary" id="btn-td-post">提交</button>' +
        '<button type="button" class="btn-refresh" id="btn-td-list">GET task-details</button>' +
        '<div id="td-list-out" style="margin-top:0.75rem;"></div></div>';

      container.innerHTML = html;

      document.getElementById('btn-team-load').addEventListener('click', async function () {
        var team = document.getElementById('team_pick').value.trim();
        var out = document.getElementById('team-detail-out');
        if (!team) {
          toast('填写 team', true);
          return;
        }
        out.innerHTML = '<p class="loading">Loading…</p>';
        var ar = await apiJson('GET', '/api/teams/' + encodeURIComponent(team) + '/assigned-requirements');
        var mr = await apiJson('GET', '/api/teams/' + encodeURIComponent(team) + '/machine-status');
        var sr = await apiJson('GET', '/api/teams/' + encodeURIComponent(team) + '/status-report');
        var h = '<h4>assigned-requirements</h4><pre class="payload-pre">' + esc(JSON.stringify(ar.data, null, 2)) + '</pre>';
        h += '<h4>machine-status</h4><pre class="payload-pre">' + esc(JSON.stringify(mr.data, null, 2)) + '</pre>';
        h += '<h4>status-report</h4><pre class="payload-pre">' + esc(JSON.stringify(sr.data, null, 2)) + '</pre>';
        out.innerHTML = h;
      });

      document.getElementById('btn-block-post').addEventListener('click', async function () {
        var body = {
          team: document.getElementById('bl_team').value.trim(),
          requirement_id: Number(document.getElementById('bl_req').value.trim()),
          reason: document.getElementById('bl_reason').value.trim(),
        };
        var tid = document.getElementById('bl_task').value.trim();
        if (tid) body.task_id = Number(tid);
        var opts = document.getElementById('bl_opts').value.trim();
        if (opts) {
          try {
            body.options = JSON.parse(opts);
          } catch (e) {
            toast('options 需为 JSON', true);
            return;
          }
        }
        if (!body.team || !body.requirement_id || !body.reason) {
          toast('team, requirement_id, reason 必填', true);
          return;
        }
        var pr = await apiJson('POST', '/api/discussion/blockage', body);
        if (!pr.ok) {
          toast((pr.data && pr.data.error) || '失败', true);
          return;
        }
        toast('已上报阻塞');
        refreshTeamsPanel();
      });

      document.getElementById('btn-block-patch').addEventListener('click', async function () {
        var id = document.getElementById('bl_res_id').value.trim();
        if (!id) {
          toast('blockage id 必填', true);
          return;
        }
        var body = {
          status: document.getElementById('bl_res_status').value.trim(),
          decision: document.getElementById('bl_res_decision').value.trim(),
        };
        var pr = await apiJson('PATCH', '/api/discussion/blockage/' + encodeURIComponent(id), body);
        if (!pr.ok) {
          toast((pr.data && pr.data.error) || 'PATCH 失败', true);
          return;
        }
        toast('已更新阻塞');
        refreshTeamsPanel();
      });

      function teamFromPick() {
        var t = document.getElementById('team_pick').value.trim();
        if (!t) {
          toast('请先在上方填写 team', true);
          return null;
        }
        return t;
      }

      document.getElementById('btn-ms-post').addEventListener('click', async function () {
        var team = teamFromPick();
        if (!team) return;
        var agent = document.getElementById('ms_agent').value.trim();
        var raw = document.getElementById('ms_payload').value.trim() || '{}';
        var payload;
        try {
          payload = JSON.parse(raw);
        } catch (e) {
          toast('payload 需为 JSON', true);
          return;
        }
        var pr = await apiJson('POST', '/api/teams/' + encodeURIComponent(team) + '/machine-status', { reporter_agent: agent, payload: payload });
        if (!pr.ok) {
          toast((pr.data && pr.data.error) || '失败', true);
          return;
        }
        toast('machine-status 已提交');
      });

      document.getElementById('btn-sr-post').addEventListener('click', async function () {
        var team = teamFromPick();
        if (!team) return;
        var agent = document.getElementById('sr_agent').value.trim();
        var raw = document.getElementById('sr_payload').value.trim() || '{}';
        var payload;
        try {
          payload = JSON.parse(raw);
        } catch (e) {
          toast('payload 需为 JSON', true);
          return;
        }
        var pr = await apiJson('POST', '/api/teams/' + encodeURIComponent(team) + '/status-report', { reporter_agent: agent, payload: payload });
        if (!pr.ok) {
          toast((pr.data && pr.data.error) || '失败', true);
          return;
        }
        toast('status-report 已提交');
      });

      document.getElementById('btn-td-post').addEventListener('click', async function () {
        var team = teamFromPick();
        if (!team) return;
        var body = {
          requirement_id: Number(document.getElementById('td_req').value.trim()),
          task_id: Number(document.getElementById('td_task').value.trim()),
          detail_type: document.getElementById('td_type').value.trim(),
          content: document.getElementById('td_content').value.trim(),
        };
        if (!body.requirement_id || !body.task_id || !body.detail_type || !body.content) {
          toast('四项均必填', true);
          return;
        }
        var pr = await apiJson('POST', '/api/teams/' + encodeURIComponent(team) + '/task-detail', body);
        if (!pr.ok) {
          toast((pr.data && pr.data.error) || '失败', true);
          return;
        }
        toast('task-detail 已提交');
      });

      document.getElementById('btn-td-list').addEventListener('click', async function () {
        var team = teamFromPick();
        if (!team) return;
        var out = document.getElementById('td-list-out');
        out.innerHTML = '<p class="loading">Loading…</p>';
        var gr = await apiJson('GET', '/api/teams/' + encodeURIComponent(team) + '/task-details');
        out.innerHTML = '<pre class="payload-pre">' + esc(JSON.stringify(gr.data, null, 2)) + '</pre>';
      });
    } catch (e) {
      container.innerHTML = '<p class="error">' + esc(e.message) + '</p>';
      toast(e.message, true);
    }
  }

  function buildSimpleTable(rows) {
    if (!rows || !rows.length) return '<p class="empty">—</p>';
    var keys = Object.keys(rows[0]);
    var html = '<table class="data-table"><thead><tr>';
    keys.forEach(function (k) { html += '<th>' + esc(k) + '</th>'; });
    html += '</tr></thead><tbody>';
    rows.forEach(function (row) {
      html += '<tr>';
      keys.forEach(function (k) {
        var v = row[k];
        var cell = v != null && typeof v === 'object' ? JSON.stringify(v) : String(v);
        html += '<td class="mono truncate" title="' + esc(cell) + '">' + esc(cell.length > 80 ? cell.slice(0, 80) + '…' : cell) + '</td>';
      });
      html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
  }

  // ----- Hook -----
  window.SFMgmt = {
    onNavSection: function (section) {
      if (section === 'projects') refreshProjectsPanel();
      if (section === 'requirements') refreshRequirementsPanel();
      if (section === 'teams') refreshTeamsPanel();
    },
    onRefreshClick: function (r) {
      if (r === 'projects') refreshProjectsPanel();
      if (r === 'teams') refreshTeamsPanel();
    },
  };
})();
