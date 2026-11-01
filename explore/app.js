/* 知识图谱浏览器 v2 —— 对照 cn-math-taxonomy 的 explore 逐项补齐
   学段 tabs / 年级 / 领域 / 搜索 / 按册分组折叠列表 / 聚焦子图（向上 N 层 + 向下 1 层）/
   分层布局 / 缩放平移 / 详情（教材位置·描述·掌握标准·课标原文·样题·先修·被依赖·诊断入口）
   数据：../data/<subject>/{topics,dependencies}.json */
(function () {
  'use strict';

  var CN_NUM = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
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
  // 册次标签：1–9 年级用「X年级」；10–14 是高中册次（必修一/二、选必一/二/三），一律按册名显示
  var SENIOR_BOOK = { 10: '必修一', 11: '必修二', 12: '选必一', 13: '选必二', 14: '选必三' };
  function gradeText(g) {
    g = Number(g);
    if (g >= 10) return (SENIOR_BOOK[g] || '高中');
    return (CN_NUM[g] || g) + '年级';
  }
  function isSeniorBook(g) { return Number(g) >= 10; }

  // 册名一律从 chapter 派生：物理/英语/语文的 grade 与册次并非一一对应
  function bookLabel(t) {
    var head = ((t && t.chapter) || '').split(' ')[0].replace('各单元', '');
    var m = head.match(/^(选择性必修|必修)(第?[一二三四五六七八九十]册|上册|下册|中册)$/);
    if (head.match(/^必修[一二三四五六]第[一二三四五]册$/)) return head;  // 西班牙语等「必修四第一册」分册
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

  function select(id, scroll, panel) {
    if (!byId.has(id)) return;
    selectedId = id;
    markActive();
    if (panel !== false) showInfo(byId.get(id));   // 首屏自动选中时不弹面板，图占满宽度更好读
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

  /* ---------- 分层图（像思维导图：方框 + 连线 + 严格分层）----------
     - 层：先修第 N 层 … 先修第 1 层 → 当前 → 下游 1 层，逐行排，行间画浅色层带
     - 方框：文字居中的圆角矩形，宽度随文字长度走
     - 连线：从父框底边到子框顶边的曲线，末端带箭头
     - 向上层数 1/2/3/全部；选「全部」且祖先 >40 时按年级折叠成聚合框 */
  var FOLD_AT = 40;
  var ancestorsOpen = false;

  // 让图区正好填满一屏（页面本身不滚动），否则最底层会被屏幕下沿切掉
  function fitHeight() {
    var m = document.querySelector('.main');
    if (!m) return;
    var top = m.getBoundingClientRect().top + (window.scrollY || 0);
    m.style.minHeight = '0';
    m.style.height = Math.max(340, window.innerHeight - top - 6) + 'px';
  }

  function initLegendToggle() {
    var legend = document.querySelector('.legend');
    var btn = document.getElementById('legend-btn');
    if (!legend || !btn) return;
    legend.classList.add('collapsed');            // 默认收起，别压住画布
    btn.addEventListener('click', function () {
      legend.classList.toggle('collapsed');
      btn.classList.toggle('active', !legend.classList.contains('collapsed'));
    });
  }

  function gradeTone(g) {
    g = Number(g) || 1;
    var hue = g <= 6 ? 172 : (g <= 9 ? 219 : 335);
    var step = g <= 6 ? (g - 1) : (g <= 9 ? (g - 7) : (g - 10));
    var light = Math.max(0.30, 0.58 - step * 0.05);
    return d3.color('hsl(' + hue + ',52%,' + Math.round(light * 100) + '%)').formatHex();
  }

  function nodeLabelW(label) {
    var n = String(label || '');
    var cjk = (n.match(/[\u4e00-\u9fff]/g) || []).length;
    var other = n.length - cjk;
    return Math.max(76, Math.min(228, cjk * 14 + other * 7.6 + 28));
  }
  function nodeH(d) { return d.role === 'center' ? 40 : 34; }

  function setFold(total, folded) {
    var box = $('graph-fold');
    if (!box) return;
    if (depth !== Infinity || total <= FOLD_AT) { box.hidden = true; box.innerHTML = ''; return; }
    box.hidden = false;
    box.innerHTML = folded
      ? '祖先较多，已按年级收起。' +
        '<button type="button" id="fold-toggle" data-open="1">共 ' + total + ' 个，点此展开全部</button>'
      : '已展开全部 ' + total + ' 个知识点。<button type="button" id="fold-toggle" data-open="0">按年级收起</button>';
  }

  // 严格按「层」排版：同一层的框排在同一行，行的中心对齐，父框尽量落在子框上方
  function layoutLayered(nodes, links) {
    var rows = new Map();
    nodes.forEach(function (d) {
      if (!rows.has(d.level)) rows.set(d.level, []);
      rows.get(d.level).push(d);
    });
    var levels = Array.from(rows.keys()).sort(function (a, b) { return a - b; });

    var nb = new Map();
    nodes.forEach(function (n) { nb.set(n.id, []); });
    links.forEach(function (l) {
      var a = l.source.id, b = l.target.id;
      if (nb.has(a) && nb.has(b)) { nb.get(a).push(b); nb.get(b).push(a); }
    });

    var pos = new Map();
    levels.forEach(function (lv) { rows.get(lv).forEach(function (n, i) { pos.set(n.id, i); }); });
    for (var pass = 0; pass < 4; pass++) {
      var seq = pass % 2 ? levels.slice().reverse() : levels;
      seq.forEach(function (lv) {
        var arr = rows.get(lv);
        arr.sort(function (a, b) {
          function bc(n) {
            var ns = nb.get(n.id).filter(function (id) { return pos.has(id); });
            if (!ns.length) return pos.get(n.id);
            return ns.reduce(function (s, id) { return s + pos.get(id); }, 0) / ns.length;
          }
          return bc(a) - bc(b);
        });
        arr.forEach(function (n, i) { pos.set(n.id, i); });
      });
    }

    // 一行放不下就折成多条子行（仍属同一层，层带会把它们框在一起），避免整体被缩小到看不清
    var gapX = 28, gapY = 56, rowGap = 92, maxRowW = 1e9, y = 0;   // 不折行：一折行连线会穿过上一排方框
    nodes.forEach(function (n) { n.w = nodeLabelW(n.name); });
    levels.forEach(function (lv) {
      var arr = rows.get(lv);
      var lines = [[]], lineW = 0;
      arr.forEach(function (n) {
        var add = (lines[lines.length - 1].length ? gapX : 0) + n.w;
        if (lineW + add > maxRowW && lines[lines.length - 1].length) {
          lines.push([]); lineW = 0; add = n.w;
        }
        lines[lines.length - 1].push(n); lineW += add;
      });
      var hMax = 0;
      lines.forEach(function (line, li) {
        var total = line.reduce(function (s, n) { return s + n.w; }, 0) + gapX * Math.max(0, line.length - 1);
        var x = -total / 2;
        var hh = Math.max.apply(null, line.map(nodeH));
        line.forEach(function (n) {
          n.x = x + n.w / 2;
          n.y = y + li * (hh + gapY) + nodeH(n) / 2;
          x += n.w + gapX;
        });
        hMax = Math.max(hMax, line.length ? hh + li * (hh + gapY) : 0);
      });
      y += hMax + rowGap;
    });
    return { levels: levels, rows: rows };
  }

  function renderGraph() {
    var svg = svgEl();
    svg.selectAll('*').remove();
    if (simulation) { simulation.stop(); simulation = null; }

    if (!selectedId || !byId.has(selectedId)) {
      emptyState(svg, '先在左侧选一个知识点', '可按学段、年级、领域筛选，或直接搜索名称 / 章节');
      $('graph-meta').textContent = '';
      setFold(0, false);
      return;
    }

    var up = bfs(selectedId, parentMap, depth);
    var down = bfs(selectedId, childMap, 1);
    var upIds = []; up.forEach(function (v, id) { upIds.push(id); });
    var downIds = []; down.forEach(function (v, id) { downIds.push(id); });
    var total = upIds.length + downIds.length + 1;
    var folded = depth === Infinity && total > FOLD_AT && !ancestorsOpen;

    var nodes = [], links = [], gradeOf = new Map();

    if (!folded) {
      var seen = {};
      [selectedId].concat(upIds).concat(downIds).forEach(function (id) {
        if (seen[id]) return; seen[id] = 1;
        var t = byId.get(id);
        nodes.push({
          id: id, name: t.name, grade: t.grade,
          role: id === selectedId ? 'center' : (up.has(id) ? 'up' : 'down'),
          level: id === selectedId ? 0 : (up.has(id) ? -(up.get(id)) : 1)
        });
      });
      var nodeIds = new Set(nodes.map(function (n) { return n.id; }));
      links = dependenciesData
        .filter(function (d) { return d && nodeIds.has(d.from) && nodeIds.has(d.to); })
        .map(function (d) { return { source: d.from, target: d.to, type: d.type }; });
    } else {
      var byGrade = new Map();
      upIds.forEach(function (id) {
        var g = byId.get(id).grade;
        if (!byGrade.has(g)) byGrade.set(g, []);
        byGrade.get(g).push(id);
      });
      byGrade.forEach(function (ids, g) {
        nodes.push({ id: 'grade:' + g, name: gradeText(g) + '·' + ids.length + '个', grade: g, role: 'agg', level: -1 });
        ids.forEach(function (id) { gradeOf.set(id, g); });
      });
      var ct = byId.get(selectedId);
      nodes.push({ id: selectedId, name: ct.name, grade: ct.grade, role: 'center', level: 0 });
      downIds.forEach(function (id) {
        var t = byId.get(id);
        nodes.push({ id: id, name: t.name, grade: t.grade, role: 'down', level: 1 });
      });
      var es = {};
      dependenciesData.forEach(function (d) {
        if (!d) return;
        var ga = gradeOf.get(d.from), gb = gradeOf.get(d.to);
        if (ga != null && gb != null) {
          if (ga === gb) return;
          es['gg:' + ga + '>' + gb] = { source: 'grade:' + ga, target: 'grade:' + gb, type: d.type };
        } else if (ga != null && d.to === selectedId) {
          es['as:' + ga] = { source: 'grade:' + ga, target: selectedId, type: d.type };
        } else if (gb != null && d.from === selectedId) {
          es['sa:' + gb] = { source: selectedId, target: 'grade:' + gb, type: d.type };
        } else if (d.from === selectedId && downIds.indexOf(d.to) >= 0) {
          es['sd:' + d.to] = { source: selectedId, target: d.to, type: d.type };
        }
      });
      links = Object.keys(es).map(function (k) { return es[k]; });
    }

    var nodeMap = new Map(nodes.map(function (n) { return [n.id, n]; }));
    links = links.filter(function (l) { return nodeMap.has(l.source) && nodeMap.has(l.target); });
    links.forEach(function (l) { l.source = nodeMap.get(l.source); l.target = nodeMap.get(l.target); });

    var lay = layoutLayered(nodes, links);
    var levels = lay.levels, rows = lay.rows;

    var g = svg.append('g').attr('class', 'viewport');
    var defs = svg.append('defs');
    [['arr-hard', '#0b5c53'], ['arr-soft', '#7b8b96']].forEach(function (pr) {
      defs.append('marker').attr('id', pr[0]).attr('viewBox', '0 -6 12 12')
        .attr('refX', 9).attr('refY', 0).attr('markerWidth', 9.5).attr('markerHeight', 9.5)
        .attr('orient', 'auto').append('path').attr('d', 'M0,-5L11,0L0,5Z').attr('fill', pr[1]);
    });

    // 层带：每条层一个横向色带，左侧写层名与个数
    var band = g.append('g').attr('class', 'layers');
    var minNodeX = Math.min.apply(null, nodes.map(function (d) { return d.x - nodeLabelW(d.name) / 2; }));
    var maxNodeX = Math.max.apply(null, nodes.map(function (d) { return d.x + nodeLabelW(d.name) / 2; }));
    var minX = minNodeX - 212, maxX = maxNodeX + 64;   // 左侧留出层名药丸的槽位，避免压住节点
    levels.forEach(function (lv, i) {
      var arr = rows.get(lv);
      var ys = arr.map(function (d) { return d.y; });
      var top = Math.min.apply(null, ys) - 34, bot = Math.max.apply(null, ys) + 34;
      var isNow = lv === 0;
      band.append('rect').attr('x', minX).attr('y', top).attr('width', maxX - minX)
        .attr('height', bot - top).attr('rx', 14)
        .attr('fill', isNow ? '#dff0ec' : (i % 2 ? '#eef5f6' : '#ffffff'))
        .attr('stroke', isNow ? '#a9d2c9' : '#cfe0e3').attr('stroke-width', isNow ? 2 : 1.2);
      var hasAgg = arr.some(function (d) { return d.role === 'agg'; });
      var label = isNow ? '当前'
        : (lv < 0 ? (hasAgg ? '先修（已按年级收起）' : '先修第 ' + (-lv) + ' 层') : '下游 1 层');
      var pillText = label + '（' + arr.length + '）';
      var pillW = pillText.length * 13.5 + 26;
      var pill = band.append('g').attr('class', 'layer-pill');
      pill.append('rect').attr('x', minX + 14).attr('y', top + 8).attr('width', pillW).attr('height', 26)
        .attr('rx', 13).attr('fill', isNow ? '#0b5c53' : '#4d6b74');
      pill.append('text').attr('x', minX + 14 + pillW / 2).attr('y', top + 26)
        .attr('class', 'layer-label').attr('text-anchor', 'middle')
        .attr('fill', '#ffffff').text(pillText);
    });

    // 连线：父框底边 → 子框顶边
    var sibIndex = new Map();
    links.forEach(function (l) { l._i = (sibIndex.get(l.source.id) || 0); sibIndex.set(l.source.id, l._i + 1); });
    links.forEach(function (l) {
      var n = sibIndex.get(l.source.id) || 1;
      var span = Math.min(nodeLabelW(l.source.name) * 0.62, 132);
      l._sx = l.source.x + (n > 1 ? (l._i - (n - 1) / 2) * (span / Math.max(1, n - 1)) : 0);
    });

    function edgePath(l) {
      var sx = l._sx == null ? l.source.x : l._sx;
      var sy = l.source.y + nodeH(l.source) / 2, ty = l.target.y - nodeH(l.target) / 2;
      var my = sy + (ty - sy) * 0.55;
      return 'M' + sx + ',' + sy + ' C' + sx + ',' + my + ' ' +
        l.target.x + ',' + my + ' ' + l.target.x + ',' + (ty - 3);
    }
    var link = g.append('g').attr('class', 'links').selectAll('path').data(links).join('path')
      .attr('class', function (d) { return 'link ' + (d.type === 'soft' ? 'soft' : 'hard'); })
      .attr('d', edgePath).attr('fill', 'none')
      .attr('marker-end', function (d) { return d.type === 'soft' ? 'url(#arr-soft)' : 'url(#arr-hard)'; });

    // 方框节点
    var node = g.append('g').attr('class', 'nodes').selectAll('g').data(nodes, function (d) { return d.id; }).join('g')
      .attr('class', function (d) { return 'node ' + d.role; })
      .attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; })
      .on('click', function (ev, d) {
        if (d.role === 'agg') { ancestorsOpen = true; renderGraph(); return; }
        if (d.id !== selectedId) select(d.id, true);
      })
      .call(d3.drag().on('drag', function (ev, d) {
        d.x = ev.x; d.y = ev.y;
        d3.select(this).attr('transform', 'translate(' + d.x + ',' + d.y + ')');
        link.attr('d', edgePath);
      }));

    node.append('rect')
      .attr('x', function (d) { return -nodeLabelW(d.name) / 2; })
      .attr('y', function (d) { return -nodeH(d) / 2; })
      .attr('width', function (d) { return nodeLabelW(d.name); })
      .attr('height', nodeH).attr('rx', 10)
      .attr('fill', function (d) { return d.role === 'agg' ? '#ffffff' : (d.role === 'center' ? '#0b5c53' : gradeTone(d.grade)); })
      .attr('stroke', function (d) { return d.role === 'center' ? '#08453e' : (d.role === 'agg' ? '#0f6e62' : '#ffffff'); })
      .attr('stroke-width', function (d) { return d.role === 'center' ? 3.4 : 1.2; })
      .attr('stroke-dasharray', function (d) { return d.role === 'agg' ? '6 3' : null; });

    node.append('text').attr('class', 'node-label')
      .attr('text-anchor', 'middle').attr('dy', '0.35em')
      .attr('fill', function (d) { return d.role === 'agg' ? '#0b5c53' : '#ffffff'; })
      .text(function (d) {
        var n = d.name || '', max = d.role === 'center' ? 20 : 12;
        return n.length > max ? n.slice(0, max) + '…' : n;
      });
    node.append('title').text(function (d) {
      if (d.role === 'agg') return d.name + '\n点击展开这一年级的全部知识点';
      var t = byId.get(d.id);
      return d.name + '\n' + gradeText(t.grade) + ' · ' + (t.domain || '') + '\n' + (t.chapter || '');
    });

    zoomTarget = g;
    zoomBehavior = d3.zoom().scaleExtent([0.2, 3]).on('zoom', function (ev) {
      g.attr('transform', ev.transform);
    });
    svg.call(zoomBehavior).on('dblclick.zoom', null);
    fitView();

    var t2 = byId.get(selectedId);
    var realUp = 0;
    up.forEach(function (v) { if (v > realUp) realUp = v; });
    var layerText = realUp ? ('向上 ' + realUp + ' 层') : '上方没有先修知识点';
    var head = folded
      ? '已按年级收起（全部 ' + total + ' 个知识点）'
      : '局部图 ' + nodes.length + ' 个知识点、' + links.length + ' 条先修';
    $('graph-meta').textContent = head + ' · ' + layerText + ' · 向下 ' + (downIds.length ? '1 层' : '0 层') + ' · ' +
      gradeText(t2.grade) + ' · ' + (t2.domain || '');
    setFold(total, folded);

    var btn = $('fold-toggle');
    if (btn) btn.addEventListener('click', function () {
      ancestorsOpen = btn.getAttribute('data-open') === '1';
      renderGraph();
    });
  }

  function fitView() {
    var svg = svgEl(), g = svg.select('g.viewport');
    if (g.empty() || !g.node()) return;
    var b = null;
    try { b = g.node().getBBox(); } catch (e) { return; }
    if (!b || !b.width || !b.height) return;
    var W = svg.node().clientWidth || 800, H = svg.node().clientHeight || 520, pad = 30;
    var panel = $('info-panel');
    if (panel && panel.classList.contains('show')) W -= (panel.offsetWidth + 26);   // 详情面板是浮层，别让图藏到它下面
    var foldBar = $('graph-fold');
    if (foldBar && !foldBar.hidden) H -= (foldBar.offsetHeight + 14);
    var k = Math.min(1, Math.max(0.18, Math.min((W - pad * 2) / b.width, (H - pad * 2) / b.height)));
    var tx = W / 2 - k * (b.x + b.width / 2);
    var ty = H / 2 - k * (b.y + b.height / 2);
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
        renderGraph();                      // 首屏不弹详情面板：图先占满宽度
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
      // 未登记册名（如西班牙语「必修四第一册」「选必第一册」grade≥13）按 grade 排在已登记册名之后
      function bookRank(x) {
        if (x.min >= 13 || RANK[x.label] === undefined) return 200 + x.min;
        return RANK[x.label];
      }
      return bookRank(a) - bookRank(b) || a.min - b.min;
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
      if (list.length) select(list[0].id, true, false);
    });

    $('depth-select').addEventListener('change', function (e) {
      depth = e.target.value === 'all' ? Infinity : parseInt(e.target.value, 10);
      ancestorsOpen = false;                       // 换层数先回到折叠态
      try { sessionStorage.setItem('cnmExplore.depth', e.target.value); } catch (err) {}
      renderGraph();
    });
    try {
      var savedDepth = sessionStorage.getItem('cnmExplore.depth');
      if (savedDepth) {
        var ds = $('depth-select');
        if ([].some.call(ds.options, function (o) { return o.value === savedDepth; })) {
          ds.value = savedDepth;
          depth = savedDepth === 'all' ? Infinity : parseInt(savedDepth, 10);
        }
      }
    } catch (err) {}
    $('fit-btn').addEventListener('click', fitView);
    $('zoom-in').addEventListener('click', function () { zoomBy(1.25); });
    $('zoom-out').addEventListener('click', function () { zoomBy(0.8); });
    $('reset-btn').addEventListener('click', function () {
      var list = filteredTopics();
      if (list.length) select(list[0].id, true, false);
    });
    $('info-close').addEventListener('click', closeInfo);

    var sel = $('subject-select');
    if (sel && [].some.call(sel.options, function (o) { return o.value === currentSubject; })) sel.value = currentSubject;
    document.querySelectorAll('#stage-tabs button').forEach(function (b) {
      b.classList.toggle('on', b.dataset.stage === stage);
    });
  }

  bind();
  initLegendToggle();
  fitHeight();
  window.addEventListener('resize', function () { fitHeight(); if (selectedId) renderGraph(); });
  loadData();
})();
