/* 首页数据渲染：读 data/stats.json，填统计卡与 17 个学科卡。
   失败时给出可读提示并回退到内置基线数字（不静默显示破折号）。 */
(function () {
  'use strict';

  var FALLBACK = {
    subjects: 17, topics: 1924, dependencies: 2199, questions: 1924, standards_entries: 972,
    per_subject: [
      { id: 'math', name: '数学', topics: 479 }, { id: 'chinese', name: '语文', topics: 205 },
      { id: 'english', name: '英语', topics: 204 }, { id: 'physics', name: '物理', topics: 177 },
      { id: 'biology', name: '生物', topics: 140 }, { id: 'history', name: '历史', topics: 138 },
      { id: 'german', name: '德语', topics: 100 }, { id: 'russian', name: '俄语', topics: 96 },
      { id: 'geography', name: '地理', topics: 85 }, { id: 'chemistry', name: '化学', topics: 62 },
      { id: 'information-technology', name: '信息科技', topics: 51 }, { id: 'french', name: '法语', topics: 46 },
      { id: 'japanese', name: '日语', topics: 39 }, { id: 'spanish', name: '西班牙语', topics: 29 },
      { id: 'art', name: '美术', topics: 26 }, { id: 'music', name: '音乐', topics: 24 },
      { id: 'science', name: '科学', topics: 23 }
    ]
  };

  var SUBJECT_LABEL = {
    math: '小·初·高', chinese: '小·初·高', english: '小·初·高', physics: '初·高',
    biology: '高', history: '初·高', german: '高', russian: '小·初·高', geography: '初·高',
    chemistry: '初·高', 'information-technology': '小·初', french: '高', japanese: '高',
    spanish: '小·初·高', art: '小·初·高', music: '小·初·高', science: '小'
  };

  function fmt(n) {
    if (typeof n !== 'number' || !isFinite(n)) return '—';
    return n.toLocaleString('zh-CN');
  }

  function setText(id, v) {
    var el = document.getElementById(id);
    if (el) el.textContent = fmt(v);
  }

  function renderStats(s) {
    setText('n-subjects', s.subjects);
    setText('n-topics', s.topics);
    setText('n-edges', s.dependencies);
    setText('n-questions', s.questions);
    setText('n-standards', s.standards_entries);
    var box = document.getElementById('stats');
    if (box) box.setAttribute('aria-busy', 'false');
  }

  function renderSubjects(s) {
    var host = document.getElementById('subjects');
    if (!host) return;
    var rows = (s.per_subject || []).slice().sort(function (a, b) { return b.topics - a.topics; });
    host.innerHTML = '';
    rows.forEach(function (r) {
      var a = document.createElement('a');
      a.className = 'subject-card';
      a.href = 'explore/?subject=' + encodeURIComponent(r.id);
      var wrap = document.createElement('span');
      var name = document.createElement('span');
      name.className = 'sc-name';
      name.textContent = r.name;
      var meta = document.createElement('span');
      meta.className = 'sc-meta';
      meta.textContent = (SUBJECT_LABEL[r.id] || '') + (r.with_quote ? ' · 已补引文' : '');
      wrap.appendChild(name);
      wrap.appendChild(document.createElement('br'));
      wrap.appendChild(meta);
      var count = document.createElement('span');
      count.className = 'sc-count';
      count.textContent = fmt(r.topics);
      a.appendChild(wrap);
      a.appendChild(count);
      host.appendChild(a);
    });
    host.setAttribute('aria-busy', 'false');
  }

  function showError(msg) {
    var box = document.getElementById('load-error');
    if (!box) return;
    box.hidden = false;
    box.textContent = msg;
  }

  fetch('data/stats.json', { cache: 'no-cache' })
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function (s) {
      renderStats(s);
      renderSubjects(s);
    })
    .catch(function (e) {
      renderStats(FALLBACK);
      renderSubjects(FALLBACK);
      showError('统计文件读取失败（' + e.message + '），已回退到内置基线数字。请用本地静态服务器打开页面，或稍后重试。');
    });
})();
