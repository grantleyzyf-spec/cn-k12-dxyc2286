/* 知识图谱浏览器 v2 —— 对照 cn-math-taxonomy 的 explore 逐项补齐
   学段 tabs / 年级 / 领域 / 搜索 / 按册分组折叠列表 / 聚焦子图（向上 N 层 + 向下 1 层）/
   分层布局 / 缩放平移 / 详情（教材位置·描述·掌握标准·课标原文·样题·先修·被依赖·诊断入口）
   数据：../data/<subject>/{topics,dependencies}.json */
(function () {
  'use strict';

  var CN_NUM = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
    '十一', '十二', '十三', '十四'];
  var SUBJECT_NAME = {
    math: '数学', chinese: '语文', english: '英语', physics: '物理', chemistry: '化学',
    biology: '生物', history: '历史', geography: '地理', science: '科学',
    'information-technology': '信息科技', japanese: '日语', russian: '俄语',
    german: '德语', french: '法语', spanish: '西班牙语', music: '音乐', art: '美术'
  };

  var topicsData = [], dependenciesData = [];
  var parentMap = new Map(), childMap = new Map(), byId = new Map();
  var domains = [];

  var params = new URLSearchParams(location.search);
  var currentSubject = params.get('subject') || 'math';
  var stage = params.get('stage') || 'all';
  var currentGrade = params.get('grade') || 'all';
  var currentDomain = params.get('domain') || 'all';
  var currentBook = params.get('book') || 'all';   // 高中按册筛（必修一/选必二…）
  var query = '';
  var depth = 2;
  var selectedId = null;
  var simulation = null, zoomBehavior = null, zoomTarget = null;

  function $(id) { return document.getElementById(id); }
  function svgEl() { return d3.select('#graph-canvas'); }
  // 册次标签：1–9 年级用「X年级」，10–14 是高中册次（必修一/二、选必一/二/三），绝不写「十三年级」
  var SENIOR_BOOK = { 10: '必修一', 11: '必修二', 12: '选必一', 13: '选必二', 14: '选必三' };
  function gradeText(g) {
    g = Number(g);
    if (SENIOR_BOOK[g]) return SENIOR_BOOK[g];
    return (CN_NUM[g] || g) + '年级';
  }
  function isSeniorBook(g) { return Number(g) >= 10; }

  // 册名一律从 chapter 派生：物理/英语/语文的 grade 与册次不是一一对应
  function bookLabel(t) {
    var head = ((t && t.chapter) || '').split(' ')[0].replace('各单元', '');
    var m = head.match(/^(选择性必修|必修)(第?[一二三四五六七八九十]册|上册|下册|中册)$/);
    if (m) {
      var tail = m[2].replace('册', '')
        .replace('第一', '一').replace('第二', '二').replace('第三', '三')
        .replace('第四', '四').replace('第五', '五').replace('第六', '六');
      return (m[1] === '选择性必修' ? '选必' : '必修') + tail;
    }
    return head || ((CN_NUM[Number(t && t.grade)] || (t || {}).grade || '') + '年级');
  }
  function stageOf(g) { return g <= 6 ? 'primary' : (g <= 9 ? 'junior' : 'senior'); }
  function stageName(g) { return { primary: '小学', junior: '初中', senior: '高中' }[stageOf(g)]; }
  function colorOf(g) { return g <= 6 ? '#0f9d8a' : (g <= 9 ? '#2f6fd0' : '#b5446e'); }
  function bookKey(t) {
    return isSeniorBook(t.grade)
      ? bookLabel(t)
      : gradeText(t.grade) + (t.semester === '下' ? '下册' : '上册');
  }

  async function fetchJSON(path) {
    var r = await fetch(path, { cache: 'no-cache' });
    if (!r.ok) throw new Error(path + ' HTTP ' + r.status);
    return r.json();
  }

  function indexGraph() {
    parentMap = new Map(); childMap = new Map();
    byId = new Map(topicsData.map(function (t) { return [t.id, t]; }));
    dependenciesData.forEach(function (d) {
      if (!d || !byId.has(d.from) || !byId.has(d.to)) return;
      if (!parentMap.has(d.to)) parentMap.set(d.to, []);
      parentMap.get(d.to).push({ id: d.from, type: d.type });
      if (!childMap.has(d.from)) childMap.set(d.from, []);
      childMap.get(d.from).push({ id: d.to, type: d.type });
    });
    var cnt = {};
    topicsData.forEach(function (t) {
      var k = t.domain || '未分类';
      cnt[k] = (cnt[k] || 0) + 1;
    });
    domains = Object.keys(cnt).sort(function (a, b) { return cnt[b] - cnt[a]; });
  }

  function bfs(startId, adj, limit) {
    var seen = new Map(), frontier = [startId], level = 0;
    while (frontier.length && level < limit) {
      level += 1;
      var next = [];
      frontier.forEach(function (cur) {
        (adj.get(cur) || []).forEach(function (e) {
          if (e.id === startId || seen.has(e.id)) return;
          seen.set(e.id, level); next.push(e.id);
        });
      });
      frontier = next;
    }
    return seen;
  }

  function filteredTopics() {
    var q = query.trim().toLowerCase();
    return topicsData.filter(function (t) {
      if (stage !== 'all' && stageOf(t.grade) !== stage) return false;
      if (currentBook !== 'all') {
        if (!isSeniorBook(t.grade) || bookLabel(t) !== currentBook) return false;
      } else if (currentGrade !== 'all' && String(t.grade) !== String(currentGrade)) return false;
      if (currentDomain !== 'all' && (t.domain || '未分类') !== currentDomain) return false;
      if (!q) return true;
      return (t.name || '').toLowerCase().indexOf(q) >= 0 ||
        (t.chapter || '').toLowerCase().indexOf(q) >= 0 ||
        (t.domain || '').toLowerCase().indexOf(q) >= 0;
    }).sort(function (a, b) { return a.grade - b.grade || String(a.id).localeCompare(String(b.id)); });
  }

  /* ---------- 列表（按册分组、可折叠） ---------- */
  function renderList() {
    var host = $('topic-list');
    var list = filteredTopics();
    $('list-count').textContent = list.length + ' 个';
    host.innerHTML = '';
    var groups = {};
    list.forEach(function (t) {
      var k = bookKey(t);
      (groups[k] = groups[k] || []).push(t);
    });
    Object.keys(groups).forEach(function (k, gi) {
      var d = document.createElement('details');
      d.className = 'book-group';
      d.open = gi < 3 || groups[k].some(function (t) { return t.id === selectedId; });
      var s = document.createElement('summary');
      s.innerHTML = '<span>' + k + '</span><em>' + groups[k].length + '</em>';
      d.appendChild(s);
      groups[k].forEach(function (t) {
        var li = document.createElement('li');
        li.dataset.id = t.id;
        li.className = 'topic-item' + (t.id === selectedId ? ' active' : '');
        li.innerHTML = '<span class="t-name">' + t.name + '</span>' +
          '<span class="grade">' + (isSeniorBook(t.grade) ? bookLabel(t) : gradeText(t.grade)) + '</span>';
        li.onclick = function () { select(t.id, true); };
        d.appendChild(li);
      });
      host.appendChild(d);
    });
    if (!list.length) host.innerHTML = '<p class="list-empty">没有匹配的知识点：换个关键词，或把学段/年级/领域切回「全部」。</p>';
  }

  function markActive() {
    var sb = document.querySelector('.sidebar');
    var items = document.querySelectorAll('#topic-list .topic-item');
    for (var i = 0; i < items.length; i++) {
      var on = items[i].dataset.id === selectedId;
      items[i].classList.toggle('active', on);
      if (!on) continue;
      var det = items[i].closest('details');
      if (det) det.open = true;
      if (sb) {
        var delta = items[i].getBoundingClientRect().top - sb.getBoundingClientRect().top;
        sb.scrollTop = sb.scrollTop + delta - sb.clientHeight / 2;
      }
    }
  }

  function urlFor(hashId) {
    var q = new URLSearchParams();
    q.set('subject', currentSubject);
    if (stage !== 'all') q.set('stage', stage);
    if (currentBook !== 'all') q.set('book', currentBook);
    else if (currentGrade !== 'all') q.set('grade', currentGrade);
    if (currentDomain !== 'all') q.set('domain', currentDomain);
    return '?' + q.toString() + (hashId ? '#' + encodeURIComponent(hashId) : '');
  }

  function select(id, scroll) {
    if (!byId.has(id)) return;
    selectedId = id;
    markActive();
    showInfo(byId.get(id));
    renderGraph();
    if (scroll) markActive();
    history.replaceState(null, '', urlFor(id));
  }

  /* ---------- 详情 ---------- */
  function names(entries, limit) {
    if (!entries || !entries.length) return '<span class="muted">无</span>';
    return entries.slice(0, limit).map(function (e) {
      var t = byId.get(e.id);
      return '<a href="#" data-jump="' + e.id + '">' + (t ? t.name : e.id) + '</a>' +
        (e.type === 'soft' ? '<span class="soft-tag">（建议）</span>' : '');
    }).join('、') + (entries.length > limit ? ' 等 ' + entries.length + ' 个' : '');
  }

  function showInfo(t) {
    $('info-title').textContent = t.name;
    $('info-meta').textContent = [SUBJECT_NAME[t.subject] || t.subject, stageName(t.grade),
      isSeniorBook(t.grade) ? bookLabel(t) : gradeText(t.grade),
      isSeniorBook(t.grade) ? '' : (t.semester || ''), t.domain || '']
      .filter(Boolean).join(' · ');

    var h = '<div class="kv"><b>教材位置</b>' + (t.chapter || '—') + '</div>';
    if (t.description) h += '<p class="desc-p">' + t.description + '</p>';

    if (t.mastery_criteria && t.mastery_criteria.length) {
      h += '<h4>掌握标准</h4><ul>' + t.mastery_criteria.map(function (s) {
        return '<li>' + s + '</li>';
      }).join('') + '</ul>';
    }

    var stds = t.standards || [];
    h += '<h4>课标条目（' + stds.length + '）</h4>';
    if (stds.length) {
      h += '<ul class="std-list">' + stds.map(function (s) {
        var conf = { exact: '直接对应', partial: '部分对应', inferred: '推断' }[s.confidence] || s.confidence;
        var quote = s.quote
          ? '<details class="quote"><summary>查看课标原文</summary><blockquote>' + s.quote + '</blockquote>' +
            (s.sourceLine ? '<div class="src">' + s.sourceLine + '</div>' : '') + '</details>'
          : '<div class="src">（该条目暂无原文引文）</div>';
        return '<li><code>' + s.id + '</code> <span class="conf ' + s.confidence + '">' + conf + '</span>' + quote + '</li>';
      }).join('') + '</ul>';
    } else {
      h += '<p class="muted">课标原文里没有对应表述，留空不编造。</p>';
    }

    var dq = t.diagnostic_question;
    if (dq && dq.question) {
      h += '<h4>样题</h4><div class="sample"><div class="q">' + dq.question + '</div>' +
        '<details><summary>看答案</summary><div class="a">' + (dq.answer || '—') + '</div></details></div>';
    }

    h += '<h4>直接先修（上游 ' + ((parentMap.get(t.id) || []).length) + '）</h4><div class="kv">' +
      names(parentMap.get(t.id), 8) + '</div>';
    h += '<h4>被依赖（下游 ' + ((childMap.get(t.id) || []).length) + '）</h4><div class="kv">' +
      names(childMap.get(t.id), 8) + '</div>';

    h += '<a class="btn-diag" href="../diagnose/?subject=' + encodeURIComponent(currentSubject) +
      '&topic=' + encodeURIComponent(t.id) + '">诊断这个知识点</a>';

    var box = $('info-desc');
    box.innerHTML = h;
    box.querySelectorAll('[data-jump]').forEach(function (a) {
      a.addEventListener('click', function (ev) { ev.preventDefault(); select(a.getAttribute('data-jump'), true); });
    });
    $('info-panel').classList.add('show');
  }

  function closeInfo() { $('info-panel').classList.remove('show'); }

  /* ---------- 图 ---------- */
  function emptyState(svg, title, sub) {
    var w = svg.node().clientWidth || 600, h = svg.node().clientHeight || 400;
    svg.append('text').attr('x', w / 2).attr('y', h / 2 - 10).attr('text-anchor', 'middle')
      .attr('class', 'empty-title').text(title);
    if (sub) svg.append('text').attr('x', w / 2).attr('y', h / 2 + 18)
      .attr('text-anchor', 'middle').attr('class', 'empty-sub').text(sub);
  }

  function renderGraph() {
    var svg = svgEl();
    svg.selectAll('*').remove();
    if (simulation) { simulation.stop(); simulation = null; }

    var w = svg.node().clientWidth || 800, h = svg.node().clientHeight || 520;
    if (!selectedId || !byId.has(selectedId)) {
      emptyState(svg, '先在左侧选一个知识点', '可按学段、年级、领域筛选，或直接搜索名称 / 章节');
      $('graph-meta').textContent = '';
      return;
    }

    var up = bfs(selectedId, parentMap, depth);
    var down = bfs(selectedId, childMap, 1);

    var ids = [selectedId];
    up.forEach(function (v, id) { ids.push(id); });
    down.forEach(function (v, id) { if (ids.indexOf(id) < 0) ids.push(id); });

    var nodes = ids.map(function (id) {
      var t = byId.get(id);
      return {
        id: id, name: t.name, grade: t.grade,
        role: id === selectedId ? 'center' : (up.has(id) ? 'up' : 'down'),
        level: id === selectedId ? 0 : (up.has(id) ? -up.get(id) : down.get(id))
      };
    });
    var nodeIds = new Set(ids);
    var links = dependenciesData
      .filter(function (d) { return d && nodeIds.has(d.from) && nodeIds.has(d.to); })
      .map(function (d) { return { source: d.from, target: d.to, type: d.type }; });

    var radius = function (d) { return d.role === 'center' ? 14 : (d.role === 'up' ? 9 : 7); };
    var rowGap = Math.max(96, Math.min(150, h / Math.max(2, up.size + 0.8)));

    var g = svg.append('g').attr('class', 'viewport');

    var defs = svg.append('defs');
    [['arr-hard', '#0f6e62'], ['arr-soft', '#8b9aa7']].forEach(function (p) {
      defs.append('marker').attr('id', p[0]).attr('viewBox', '0 -5 10 10')
        .attr('refX', 20).attr('refY', 0).attr('markerWidth', 5.5).attr('markerHeight', 5.5)
        .attr('orient', 'auto').append('path').attr('d', 'M0,-4L9,0L0,4').attr('fill', p[1]);
    });

    simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(function (d) { return d.id; })
        .distance(function (l) { return l.type === 'soft' ? 165 : 125; }).strength(0.5))
      .force('charge', d3.forceManyBody().strength(function (d) { return d.role === 'center' ? -420 : -240; }))
      .force('collide', d3.forceCollide().radius(function (d) { return radius(d) + 34; }))
      .force('y', d3.forceY(function (d) { return h / 2 + d.level * rowGap; }).strength(0.92))
      .force('x', d3.forceX(function (d) { return d.role === 'down' ? w * 0.6 : w * 0.46; }).strength(0.1));

    var link = g.append('g').attr('class', 'links').selectAll('line').data(links).join('line')
      .attr('class', function (d) { return 'link ' + (d.type === 'soft' ? 'soft' : 'hard'); })
      .attr('marker-end', function (d) { return d.type === 'soft' ? 'url(#arr-soft)' : 'url(#arr-hard)'; });

    var node = g.append('g').attr('class', 'nodes').selectAll('g').data(nodes).join('g')
      .attr('class', function (d) { return 'node ' + d.role; })
      .on('click', function (ev, d) { if (d.id !== selectedId) select(d.id, true); })
      .call(d3.drag()
        .on('start', function (ev, d) { if (!ev.active) simulation.alphaTarget(0.2).restart(); d.fx = d.x; d.fy = d.y; })
        .on('drag', function (ev, d) { d.fx = ev.x; d.fy = ev.y; })
        .on('end', function (ev, d) { if (!ev.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));

    node.append('circle')
      .attr('r', radius)
      .attr('fill', function (d) { return colorOf(d.grade); })
      .attr('stroke', function (d) { return d.role === 'center' ? '#0f6e62' : null; })
      .attr('stroke-width', function (d) { return d.role === 'center' ? 4 : null; });

    node.append('text').attr('class', 'node-label')
      .attr('dx', function (d) { return radius(d) + 6; }).attr('dy', 4)
      .text(function (d) {
        var n = d.name || '', max = d.role === 'center' ? 22 : 14;
        return n.length > max ? n.slice(0, max) + '…' : n;
      });
    node.append('title').text(function (d) {
      var t = byId.get(d.id);
      return d.name + '\n' + (isSeniorBook(t.grade) ? bookLabel(t) : gradeText(t.grade)) +
        ' · ' + (t.domain || '') + '\n' + (t.chapter || '');
    });

    simulation.on('tick', function () {
      link.attr('x1', function (d) { return d.source.x; }).attr('y1', function (d) { return d.source.y; })
        .attr('x2', function (d) { return d.target.x; }).attr('y2', function (d) { return d.target.y; });
      node.attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });
    });
    simulation.on('end', function () { fitView(); });

    zoomTarget = g;
    zoomBehavior = d3.zoom().scaleExtent([0.25, 3]).on('zoom', function (ev) {
      g.attr('transform', ev.transform);
    });
    svg.call(zoomBehavior).on('dblclick.zoom', null);

    var t = byId.get(selectedId);
    $('graph-meta').textContent = stageName(t.grade) + ' · ' +
      (isSeniorBook(t.grade) ? bookLabel(t) : gradeText(t.grade)) + ' · ' + (t.domain || '') +
      ' · 先修 ' + up.size + ' · 下游 ' + down.size;
  }

  function fitView() {
    var svg = svgEl(), g = svg.select('g.viewport');
    if (g.empty()) return;
    var box = null;
    g.selectAll('g.node').each(function (d) {
      var r = d.role === 'center' ? 22 : 16;
      var b = { x0: d.x - r - 100, x1: d.x + r + 100, y0: d.y - r - 18, y1: d.y + r + 18 };
      box = box ? {
        x0: Math.min(box.x0, b.x0), x1: Math.max(box.x1, b.x1),
        y0: Math.min(box.y0, b.y0), y1: Math.max(box.y1, b.y1)
      } : b;
    });
    if (!box) return;
    var W = svg.node().clientWidth || 800, H = svg.node().clientHeight || 520, pad = 26;
    var bw = Math.max(140, box.x1 - box.x0), bh = Math.max(100, box.y1 - box.y0);
    var k = Math.min(3, Math.max(0.25, Math.min((W - pad * 2) / bw, (H - pad * 2) / bh)));
    var tx = W / 2 - k * ((box.x0 + box.x1) / 2);
    var ty = H / 2 - k * ((box.y0 + box.y1) / 2);
    svg.transition().duration(240).call(zoomBehavior.transform, d3.zoomIdentity.translate(tx, ty).scale(k));
  }

  function zoomBy(f) {
    if (!zoomBehavior) return;
    svgEl().transition().duration(160).call(zoomBehavior.scaleBy, f);
  }

  /* ---------- 载入 ---------- */
  async function loadData() {
    $('graph-meta').textContent = '加载中…';
    try {
      var res = await Promise.all([
        fetchJSON('../data/' + currentSubject + '/topics.json'),
        fetchJSON('../data/' + currentSubject + '/dependencies.json')
      ]);
      topicsData = res[0]; dependenciesData = res[1];
      indexGraph();
      fillDomainOptions();
      fillGradeOptions();

      var hashId = decodeURIComponent((location.hash || '').replace(/^#/, ''));
      if (!(hashId && byId.has(hashId))) {
        var list = filteredTopics(), best = null, bestScore = -1;
        list.forEach(function (t) {
          var sc = (parentMap.get(t.id) || []).length * 2 + (childMap.get(t.id) || []).length;
          if (sc > bestScore) { bestScore = sc; best = t; }
        });
        selectedId = best ? best.id : (list[0] ? list[0].id : null);
      } else {
        selectedId = hashId;
      }
      renderList();
      if (selectedId) {
        showInfo(byId.get(selectedId));
        renderGraph();
        history.replaceState(null, '', urlFor(selectedId));
      } else { renderGraph(); }
    } catch (e) {
      $('graph-meta').textContent = '';
      var svg = svgEl(); svg.selectAll('*').remove();
      emptyState(svg, '数据加载失败', e.message + '（本地请用 python3 -m http.server 打开）');
    }
  }

  function fillGradeOptions() {
    var sel = $('grade-select');
    var html = '<option value="all">全部册次</option>';
    for (var g = 1; g <= 9; g++) html += '<option value="g:' + g + '">' + gradeText(g) + '</option>';
    var books = [], seen = {};
    topicsData.forEach(function (t) {
      if (!isSeniorBook(t.grade)) return;
      var b = bookLabel(t);
      if (!seen[b]) { seen[b] = true; books.push({ label: b, min: t.grade }); }
    });
    var RANK = { '必修一': 11, '必修二': 12, '必修三': 13, '必修四': 14, '必修五': 15, '必修六': 16,
                 '选必一': 21, '选必二': 22, '选必三': 23, '选必四': 24 };
    books.sort(function (a, b) {
      return (RANK[a.label] || 99) - (RANK[b.label] || 99) || a.min - b.min;
    });
    books.forEach(function (b) { html += '<option value="b:' + b.label + '">' + b.label + '</option>'; });
    sel.innerHTML = html;
    var want = currentBook !== 'all' ? ('b:' + currentBook) : (currentGrade !== 'all' ? ('g:' + currentGrade) : 'all');
    if ([].some.call(sel.options, function (o) { return o.value === want; })) sel.value = want;
    else { currentBook = 'all'; currentGrade = 'all'; sel.value = 'all'; }
  }

  function fillDomainOptions() {
    var sel = $('domain-select');
    sel.innerHTML = '<option value="all">全部领域</option>' + domains.map(function (d) {
      return '<option value="' + d.replace(/"/g, '&quot;') + '">' + d + '</option>';
    }).join('');
    if ([].some.call(sel.options, function (o) { return o.value === currentDomain; })) sel.value = currentDomain;
    else { currentDomain = 'all'; sel.value = 'all'; }
  }

  function refreshSelection() {
    var list = filteredTopics();
    if (!list.some(function (t) { return t.id === selectedId; })) selectedId = list.length ? list[0].id : null;
    renderList();
    if (selectedId) { showInfo(byId.get(selectedId)); renderGraph(); } else { closeInfo(); renderGraph(); }
  }

  function bind() {
    $('subject-select').addEventListener('change', function (e) {
      currentSubject = e.target.value;
      stage = 'all'; currentGrade = 'all'; currentDomain = 'all'; currentBook = 'all';
      selectedId = null; closeInfo();
      history.replaceState(null, '', urlFor());
      loadData();
    });

    document.querySelectorAll('#stage-tabs button').forEach(function (b) {
      b.addEventListener('click', function () {
        stage = b.dataset.stage;
        document.querySelectorAll('#stage-tabs button').forEach(function (x) { x.classList.toggle('on', x === b); });
        history.replaceState(null, '', urlFor());
        refreshSelection();
      });
    });

    $('grade-select').addEventListener('change', function (e) {
      var v = e.target.value;
      if (v === 'all') { currentGrade = 'all'; currentBook = 'all'; }
      else if (v.indexOf('b:') === 0) { currentBook = v.slice(2); currentGrade = 'all'; }
      else { currentGrade = v.slice(2); currentBook = 'all'; }
      history.replaceState(null, '', urlFor());
      refreshSelection();
    });

    $('domain-select').addEventListener('change', function (e) {
      currentDomain = e.target.value;
      history.replaceState(null, '', urlFor());
      refreshSelection();
    });

    var s = $('topic-search');
    s.addEventListener('input', function (e) { query = e.target.value; renderList(); });
    s.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') return;
      var list = filteredTopics();
      if (list.length) select(list[0].id, true);
    });

    $('depth-select').addEventListener('change', function (e) {
      depth = e.target.value === 'all' ? Infinity : parseInt(e.target.value, 10);
      renderGraph();
    });
    $('fit-btn').addEventListener('click', fitView);
    $('zoom-in').addEventListener('click', function () { zoomBy(1.25); });
    $('zoom-out').addEventListener('click', function () { zoomBy(0.8); });
    $('reset-btn').addEventListener('click', function () {
      var list = filteredTopics();
      if (list.length) select(list[0].id, true);
    });
    $('info-close').addEventListener('click', closeInfo);

    var sel = $('subject-select');
    if (sel && [].some.call(sel.options, function (o) { return o.value === currentSubject; })) sel.value = currentSubject;
    document.querySelectorAll('#stage-tabs button').forEach(function (b) {
      b.classList.toggle('on', b.dataset.stage === stage);
    });
  }

  bind();
  loadData();
})();
