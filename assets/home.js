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

  // 学科图标（与 explore 页一致）
  var SUBJECT_ICON = {
    math: '📐', chinese: '📖', english: '🔤', physics: '⚡', chemistry: '🧪', biology: '🧬',
    history: '📜', geography: '🌍', science: '🔬', 'information-technology': '💻', japanese: '🇯🇵',
    russian: '🇷🇺', german: '🇩🇪', french: '🇫🇷', spanish: '🇪🇸', music: '🎵', art: '🎨',
    'mental-health': '🧠'
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

  // 一级=学科卡，二级=版本 chips：同一学科的不同教材版本不单列成学科
  function renderSubjects(s, reg) {
    var host = document.getElementById('subjects');
    if (!host) return;

    if (reg && reg.subjects && reg.subjects.length) {
      host.innerHTML = '';
      reg.subjects.slice().sort(function (a, b) { return b.topics - a.topics; }).forEach(function (sub) {
        var block = document.createElement('div');
        block.className = 'subject-block';

        var eds = (sub.editions || []).slice();
        var main = eds[0] || { id: sub.id, name: '', topics: sub.topics };

        var a = document.createElement('a');
        a.className = 'subject-card';
        a.href = 'explore/?subject=' + encodeURIComponent(main.id);

        var wrap = document.createElement('span');
        var name = document.createElement('span');
        name.className = 'sc-name';
        name.textContent = (SUBJECT_ICON[sub.id] ? SUBJECT_ICON[sub.id] + ' ' : '') + sub.name;
        var meta = document.createElement('span');
        meta.className = 'sc-meta';
        meta.textContent = (sub.label || SUBJECT_LABEL[sub.id] || '') + (eds.length > 1 ? ' · ' + eds.length + ' 个版本' : '');
        wrap.appendChild(name);
        wrap.appendChild(document.createElement('br'));
        wrap.appendChild(meta);

        var count = document.createElement('span');
        count.className = 'sc-count';
        count.textContent = fmt(sub.topics);
        a.appendChild(wrap);
        a.appendChild(count);
        block.appendChild(a);

        if (eds.length > 1) {
          var chips = document.createElement('div');
          chips.className = 'sc-editions';
          eds.forEach(function (e) {
            var c = document.createElement('a');
            c.className = 'sc-chip';
            c.href = 'explore/?subject=' + encodeURIComponent(e.id);
            c.textContent = (e.name || e.id) + ' ' + fmt(e.topics);
            c.title = sub.name + ' · ' + (e.name || e.id) + ' · ' + fmt(e.topics) + ' 个知识点';
            chips.appendChild(c);
          });
          block.appendChild(chips);
        }
        host.appendChild(block);
      });
      host.setAttribute('aria-busy', 'false');
      var ns = document.getElementById('n-subjects');
      if (ns) ns.textContent = String(reg.subjects.length);
      return;
    }

    // 回退：没有注册表时按 stats.json 的 per_subject 平铺（旧行为）
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

  // 把页面里 <span data-stat="topics"> 之类的占位改成 stats.json 的实时数字
  function fillStatTexts(s) {
    if (!s) return;
    document.querySelectorAll('[data-stat]').forEach(function (el) {
      var k = el.getAttribute('data-stat');
      if (s[k] !== undefined && s[k] !== null) el.textContent = s[k];
    });
  }

  var pStats = fetch('data/stats.json', { cache: 'no-cache' }).then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  });
  var pReg = fetch('data/subject-groups.json', { cache: 'no-cache' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .catch(function () { return null; });

  Promise.all([pStats, pReg])
    .then(function (rs) {
      var s = rs[0], reg = rs[1];
      renderStats(s);
      renderSubjects(s, reg);
      fillStatTexts(s);
    })
    .catch(function (e) {
      renderStats(FALLBACK);
      renderSubjects(FALLBACK, null);
      fillStatTexts(FALLBACK);
      showError('统计文件读取失败（' + e.message + '），已回退到内置基线数字。请用本地静态服务器打开页面，或稍后重试。');
    });
})();
