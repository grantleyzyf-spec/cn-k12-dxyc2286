/* 知识图谱浏览器（聚焦子图版）
   - 以「当前知识点」为中心：向上 N 层先修 + 向下 1 层依赖
   - 搜索、层级切换、适配画面；点图中任意节点即以它为中心重画
   - 颜色：小学青绿 / 初中蓝 / 高中品红；实线 = hard 先修，虚线 = soft
   数据：../data/<subject>/{topics,dependencies}.json */
(function () {
  'use strict';

  var CN_NUM = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
    '十一', '十二', '十三', '十四'];

  var topicsData = [];
  var dependenciesData = [];
  var parentMap = new Map();   // id -> [{id, type}]  先修（上游）
  var childMap = new Map();    // id -> [{id, type}]  后继（下游）
  var byId = new Map();

  var currentSubject = new URLSearchParams(location.search).get('subject') || 'math';
  var currentGrade = 'all';
  var selectedId = null;
  var depth = 2;               // 2 / 1 / 3 / Infinity
  var query = '';
  var simulation = null;

  var SUBJECT_NAME = {
    math: '数学', chinese: '语文', english: '英语', physics: '物理', chemistry: '化学',
    biology: '生物', history: '历史', geography: '地理', science: '科学',
    'information-technology': '信息科技', japanese: '日语', russian: '俄语',
    german: '德语', french: '法语', spanish: '西班牙语', music: '音乐', art: '美术'
  };

  function svgEl() { return d3.select('#graph-canvas'); }
  function gradeText(g) { return (CN_NUM[g] || g) + '年级'; }
  function isPrimary(g) { return g <= 6; }
  function isJunior(g) { return g >= 7 && g <= 9; }
  function colorOf(g) {
    if (isPrimary(g)) return '#0f9d8a';
    if (isJunior(g)) return '#2f6fd0';
    return '#b5446e';
  }

  // ---------- 数据 ----------
  async function fetchJSON(path) {
    var r = await fetch(path, { cache: 'no-cache' });
    if (!r.ok) throw new Error(path + ' HTTP ' + r.status);
    return r.json();
  }

  function indexGraph() {
    parentMap = new Map();
    childMap = new Map();
    byId = new Map(topicsData.map(function (t) { return [t.id, t]; }));
    dependenciesData.forEach(function (d) {
      if (!d || !byId.has(d.from) || !byId.has(d.to)) return;
      if (!parentMap.has(d.to)) parentMap.set(d.to, []);
      parentMap.get(d.to).push({ id: d.from, type: d.type });
      if (!childMap.has(d.from)) childMap.set(d.from, []);
      childMap.get(d.from).push({ id: d.to, type: d.type });
    });
  }

  // 向上（先修）BFS，limit = 层数或 Infinity
  function ancestorsOf(id, limit) {
    var seen = new Map();      // id -> 层数
    var frontier = [id];
    var level = 0;
    while (frontier.length && level < limit) {
      level += 1;
      var next = [];
      frontier.forEach(function (cur) {
        (parentMap.get(cur) || []).forEach(function (e) {
          if (e.id === id || seen.has(e.id)) return;
          seen.set(e.id, level);
          next.push(e.id);
        });
      });
      frontier = next;
    }
    return seen;
  }

  function descendantsOf(id, limit) {
    var seen = new Map();
    var frontier = [id];
    var level = 0;
    while (frontier.length && level < limit) {
      level += 1;
      var next = [];
      frontier.forEach(function (cur) {
        (childMap.get(cur) || []).forEach(function (e) {
          if (e.id === id || seen.has(e.id)) return;
          seen.set(e.id, level);
          next.push(e.id);
        });
      });
      frontier = next;
    }
    return seen;
  }

  // ---------- 侧栏列表 ----------
  function visibleTopics() {
    var list = topicsData;
    if (currentGrade !== 'all') {
      list = list.filter(function (t) { return String(t.grade) === String(currentGrade); });
    }
    if (query) {
      var q = query.trim().toLowerCase();
      list = list.filter(function (t) {
        return (t.name || '').toLowerCase().indexOf(q) >= 0 ||
          (t.chapter || '').toLowerCase().indexOf(q) >= 0 ||
          (t.domain || '').toLowerCase().indexOf(q) >= 0;
      });
    }
    return list.slice().sort(function (a, b) {
      return a.grade - b.grade || String(a.id).localeCompare(String(b.id));
    });
  }

  function updateTopicList() {
    var host = document.getElementById('topic-list');
    var list = visibleTopics();
    host.innerHTML = '';
    document.getElementById('list-count').textContent = list.length + ' 个';
    list.forEach(function (t) {
      var li = document.createElement('li');
      li.dataset.id = t.id;
      if (t.id === selectedId) li.className = 'active';
      li.innerHTML = '<span class="t-name">' + t.name + '</span>' +
        '<span class="grade">' + gradeText(t.grade) + '</span>';
      li.onclick = function () { select(t.id); };
      host.appendChild(li);
    });
  }

  function select(id, scrollList) {
    if (!byId.has(id)) return;
    selectedId = id;
    var lis = document.querySelectorAll('#topic-list li');
    var sb = document.querySelector('.sidebar');
    for (var i = 0; i < lis.length; i++) {
      var on = lis[i].dataset.id === id;
      lis[i].classList.toggle('active', on);
      if (on && scrollList && sb) {
        var delta = lis[i].getBoundingClientRect().top - sb.getBoundingClientRect().top;
        sb.scrollTop = sb.scrollTop + delta - sb.clientHeight / 2;
      }
    }
    showInfo(byId.get(id));
    renderGraph();
  }

  // ---------- 信息面板 ----------
  function nameList(entries, limit) {
    if (!entries || !entries.length) return '无';
    return entries.slice(0, limit).map(function (e) {
      var t = byId.get(e.id);
      return '<a href="#" data-jump="' + e.id + '">' + (t ? t.name : e.id) + '</a>' +
        (e.type === 'soft' ? '<span class="soft-tag">（建议）</span>' : '');
    }).join('、') + (entries.length > limit ? ' 等 ' + entries.length + ' 个' : '');
  }

  function showInfo(topic) {
    document.getElementById('info-title').textContent = topic.name;
    document.getElementById('info-meta').textContent =
      [SUBJECT_NAME[topic.subject] || topic.subject, gradeText(topic.grade),
        topic.semester || '', topic.domain || ''].filter(Boolean).join(' · ');
    var html = '';
    if (topic.chapter) html += '<div class="kv"><b>教材位置</b>' + topic.chapter + '</div>';
    if (topic.description) html += '<p class="desc-p">' + topic.description + '</p>';
    if (topic.mastery_criteria && topic.mastery_criteria.length) {
      html += '<h4>掌握标准</h4><ul>' + topic.mastery_criteria.map(function (s) {
        return '<li>' + s + '</li>';
      }).join('') + '</ul>';
    }
    var ups = parentMap.get(topic.id) || [];
    var downs = childMap.get(topic.id) || [];
    html += '<h4>直接先修（上游 ' + ups.length + ' 个）</h4><div class="kv">' + nameList(ups, 8) + '</div>';
    html += '<h4>被依赖（下游 ' + downs.length + ' 个）</h4><div class="kv">' + nameList(downs, 8) + '</div>';
    var desc = document.getElementById('info-desc');
    desc.innerHTML = html;
    desc.querySelectorAll('[data-jump]').forEach(function (a) {
      a.addEventListener('click', function (ev) {
        ev.preventDefault();
        select(a.getAttribute('data-jump'), true);
      });
    });
    document.getElementById('info-panel').classList.add('show');
  }

  function closeInfo() {
    document.getElementById('info-panel').classList.remove('show');
  }

  // ---------- 画图 ----------
  function emptyState(svg, text, sub) {
    var w = svg.node().clientWidth || 600;
    var h = svg.node().clientHeight || 400;
    svg.append('text').attr('x', w / 2).attr('y', h / 2 - 8)
      .attr('text-anchor', 'middle').attr('class', 'empty-title').text(text);
    if (sub) {
      svg.append('text').attr('x', w / 2).attr('y', h / 2 + 20)
        .attr('text-anchor', 'middle').attr('class', 'empty-sub').text(sub);
    }
  }

  function renderGraph() {
    var svg = svgEl();
    svg.selectAll('*').remove();
    if (simulation) { simulation.stop(); simulation = null; }
    svg.attr('viewBox', null);

    var w = svg.node().clientWidth || 800;
    var h = svg.node().clientHeight || 520;

    if (!selectedId || !byId.has(selectedId)) {
      emptyState(svg, '先在左侧选一个知识点', '也可以用上方搜索框按名称、章节、领域检索');
      return;
    }

    var center = byId.get(selectedId);
    var up = ancestorsOf(selectedId, depth);
    var down = descendantsOf(selectedId, 1);

    var ids = [selectedId];
    up.forEach(function (lvl, id) { ids.push(id); });
    down.forEach(function (lvl, id) { if (ids.indexOf(id) < 0) ids.push(id); });

    var nodes = ids.map(function (id) {
      var t = byId.get(id);
      return {
        id: id, name: t.name, grade: t.grade, type: t.type,
        role: id === selectedId ? 'center' : (up.has(id) ? 'up' : 'down'),
        level: id === selectedId ? 0 : (up.has(id) ? up.get(id) : -down.get(id))
      };
    });
    var nodeIds = new Set(ids);

    // forceLink 认 source/target；每次重绘重建对象，避免被上一次 simulation 改写
    var links = dependenciesData
      .filter(function (d) { return d && nodeIds.has(d.from) && nodeIds.has(d.to); })
      .map(function (d) { return { source: d.from, target: d.to, type: d.type }; });

    var radius = function (d) { return d.role === 'center' ? 13 : (d.role === 'up' ? 9 : 7); };

    simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(function (d) { return d.id; }).distance(function (l) {
        return l.type === 'hard' ? 110 : 150;
      }).strength(0.7))
      .force('charge', d3.forceManyBody().strength(function (d) { return d.role === 'center' ? -900 : -420; }))
      .force('collide', d3.forceCollide().radius(function (d) { return radius(d) + 26; }))
      .force('x', d3.forceX(function (d) { return d.role === 'down' ? w * 0.66 : w * 0.42; }).strength(0.12))
      .force('y', d3.forceY(h / 2).strength(0.06))
      .force('center', d3.forceCenter(w / 2, h / 2).strength(0.05));

    var link = svg.append('g').attr('class', 'links')
      .selectAll('line').data(links).join('line')
      .attr('class', function (d) { return 'link ' + (d.type === 'soft' ? 'soft' : 'hard'); });

    var node = svg.append('g').attr('class', 'nodes')
      .selectAll('g').data(nodes).join('g')
      .attr('class', function (d) { return 'node ' + d.role; })
      .style('cursor', 'pointer')
      .on('click', function (ev, d) { if (d.id !== selectedId) select(d.id, true); })
      .call(d3.drag()
        .on('start', function (ev, d) {
          if (!ev.active) simulation.alphaTarget(0.25).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on('drag', function (ev, d) { d.fx = ev.x; d.fy = ev.y; })
        .on('end', function (ev, d) {
          if (!ev.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        }));

    node.append('circle')
      .attr('r', radius)
      .attr('fill', function (d) { return colorOf(d.grade); })
      .attr('stroke', function (d) { return d.role === 'center' ? '#0f6e62' : null; })
      .attr('stroke-width', function (d) { return d.role === 'center' ? 4 : null; });

    node.append('text')
      .attr('class', 'node-label')
      .attr('dx', function (d) { return radius(d) + 6; })
      .attr('dy', 4)
      .text(function (d) {
        var n = d.name || '';
        var max = d.role === 'center' ? 22 : 14;
        return n.length > max ? n.slice(0, max) + '…' : n;
      });

    node.append('title').text(function (d) { return d.name; });

    simulation.on('tick', function () {
      link
        .attr('x1', function (d) { return d.source.x; })
        .attr('y1', function (d) { return d.source.y; })
        .attr('x2', function (d) { return d.target.x; })
        .attr('y2', function (d) { return d.target.y; });
      node.attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });
      node.each(function (d) {
        d.x = Math.max(30, Math.min(w - 30, d.x));
        d.y = Math.max(24, Math.min(h - 24, d.y));
      });
    });

    simulation.on('end', function () { fitView(); });

    document.getElementById('graph-hint').textContent =
      (depth === Infinity ? '全部先修 ' : depth + ' 层内先修 ') + up.size + ' 个 · 下游 ' + down.size + ' 个';
  }

  function fitView() {
    var svg = svgEl();
    var g = svg.select('g.nodes');
    if (g.empty()) return;
    var box = null;
    g.selectAll('g.node').each(function (d) {
      var r = d.role === 'center' ? 20 : 14;
      var b = { x0: d.x - r - 90, x1: d.x + r + 90, y0: d.y - r - 16, y1: d.y + r + 16 };
      box = box ? {
        x0: Math.min(box.x0, b.x0), x1: Math.max(box.x1, b.x1),
        y0: Math.min(box.y0, b.y0), y1: Math.max(box.y1, b.y1)
      } : b;
    });
    if (!box) return;
    var pad = 18;
    var vw = Math.max(240, box.x1 - box.x0 + pad * 2);
    var vh = Math.max(180, box.y1 - box.y0 + pad * 2);
    svg.attr('viewBox', [box.x0 - pad, box.y0 - pad, vw, vh].join(' '));
  }

  // ---------- 载入 ----------
  async function loadData() {
    var hint = document.getElementById('graph-hint');
    hint.textContent = '加载中…';
    try {
      var res = await Promise.all([
        fetchJSON('../data/' + currentSubject + '/topics.json'),
        fetchJSON('../data/' + currentSubject + '/dependencies.json')
      ]);
      topicsData = res[0];
      dependenciesData = res[1];
      indexGraph();
      var hashId = decodeURIComponent((location.hash || '').replace(/^#/, ''));
      var list = visibleTopics();
      // 默认选「关系最密」的知识点，首屏就能看到先修与下游；同分取靠前的
      var firstWithUp = null, bestScore = -1;
      list.forEach(function (t) {
        var up = (parentMap.get(t.id) || []).length;
        var down = (childMap.get(t.id) || []).length;
        var score = up * 2 + down;
        if (score > bestScore) { bestScore = score; firstWithUp = t; }
      });
      var first = (bestScore > 0 ? firstWithUp : list[0]);
      selectedId = (hashId && byId.has(hashId)) ? hashId : (first ? first.id : null);
      updateTopicList();
      if (selectedId) { select(selectedId, true); } else { renderGraph(); }
    } catch (e) {
      hint.textContent = '';
      var svg = svgEl();
      svg.selectAll('*').remove();
      emptyState(svg, '数据加载失败', e.message + '（本地请用 python3 -m http.server 打开）');
    }
  }

  // ---------- 交互 ----------
  function bind() {
    document.getElementById('subject-select').addEventListener('change', function (e) {
      currentSubject = e.target.value;
      selectedId = null;
      closeInfo();
      history.replaceState(null, '', '?subject=' + encodeURIComponent(currentSubject));
      loadData();
    });

    document.getElementById('grade-select').addEventListener('change', function (e) {
      currentGrade = e.target.value;
      var list = visibleTopics();
      if (!list.some(function (t) { return t.id === selectedId; })) {
        selectedId = list.length ? list[0].id : null;
      }
      updateTopicList();
      if (selectedId) showInfo(byId.get(selectedId));
      renderGraph();
    });

    document.getElementById('depth-select').addEventListener('change', function (e) {
      depth = e.target.value === 'all' ? Infinity : parseInt(e.target.value, 10);
      renderGraph();
    });

    var search = document.getElementById('topic-search');
    search.addEventListener('input', function (e) {
      query = e.target.value;
      updateTopicList();
    });
    search.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') return;
      var list = visibleTopics();
      if (list.length) select(list[0].id, true);
    });

    document.getElementById('fit-btn').addEventListener('click', fitView);
    document.getElementById('reset-btn').addEventListener('click', function () {
      var list = visibleTopics();
      if (list.length) select(list[0].id, true);
    });
    document.getElementById('info-close').addEventListener('click', closeInfo);

    var sel = document.getElementById('subject-select');
    if (sel && Array.prototype.some.call(sel.options, function (o) { return o.value === currentSubject; })) {
      sel.value = currentSubject;
    }
  }

  bind();
  loadData();
})();
