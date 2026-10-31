/* 课时讲解页：点课时 → 看讲解。
 * 数据：learn/index.json（册→单元→课时）+ data/math/learn/<册>.json（正文 Markdown）
 * 深链：learn/?book=一年级上册#mat_p1000 或 /learn/#mat_p1000（自动定位册）
 */
(function () {
  'use strict';

  var selBook = document.getElementById('sel-book');
  var selUnit = document.getElementById('sel-unit');
  var listEl = document.getElementById('lesson-list');
  var reader = document.getElementById('reader');
  var hint = document.getElementById('hint');

  var INDEX = null;      // learn/index.json
  var BOOK = null;       // {index 条目, markdown map}
  var cur = null;        // 当前 topicId
  var USER_SCROLLED = false;  // 首屏不滚动，避免 sticky 顶栏把正文标题压出去

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /* 极简 Markdown → HTML：只支持本页用到的语法
   * # / ## / ### 标题；> 引用（❌✅ 转为对照块）；- [ ] 自查；- 列表；**粗体**；段落 */
  function md2html(md) {
    var lines = md.split('\n'), out = [], i = 0;
    function inline(t) { return esc(t).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>'); }
    while (i < lines.length) {
      var ln = lines[i].replace(/\s+$/, '');
      if (!ln.trim()) { i++; continue; }
      if (/^#\s/.test(ln)) { out.push('<h1>' + inline(ln.slice(2)) + '</h1>'); i++; continue; }
      if (/^###\s/.test(ln)) { out.push('<h3>' + inline(ln.slice(4)) + '</h3>'); i++; continue; }
      if (/^##\s/.test(ln)) { out.push('<h2>' + inline(ln.slice(3)) + '</h2>'); i++; continue; }
      if (/^-\s\[[ x]\]/.test(ln)) {
        var items = [];
        while (i < lines.length && /^-\s\[[ x]\]/.test(lines[i])) {
          items.push('<li>' + inline(lines[i].replace(/^-\s\[[ x]\]\s*/, '')) + '</li>'); i++;
        }
        out.push('<ul class="check">' + items.join('') + '</ul>'); continue;
      }
      if (/^-\s/.test(ln)) {
        var dots = [];
        while (i < lines.length && /^-\s/.test(lines[i]) && !/^-\s\[[ x]\]/.test(lines[i])) {
          dots.push('<li>' + inline(lines[i].slice(2)) + '</li>'); i++;
        }
        out.push('<ul class="dot">' + dots.join('') + '</ul>'); continue;
      }
      if (/^\d+\.\s/.test(ln)) {
        // 有序列表：数据里每步之间有空行，必须跨空行继续收集，否则会拆成 5 个各自从 1 开始的 <ol>
        var ols = [], k = i;
        while (k < lines.length) {
          if (/^\d+\.\s/.test(lines[k])) {
            ols.push('<li>' + inline(lines[k].replace(/^\d+\.\s*/, '')) + '</li>');
            k++;
            continue;
          }
          if (!lines[k].trim()) {                      // 空行：往后找下一条编号
            var j = k;
            while (j < lines.length && !lines[j].trim()) j++;
            if (j < lines.length && /^\d+\.\s/.test(lines[j])) { k = j; continue; }
          }
          break;
        }
        i = k;
        out.push('<ol class="steps-list">' + ols.join('') + '</ol>'); continue;
      }
      if (/^>\s?/.test(ln)) {
        var paras = [];
        while (i < lines.length && /^>\s?/.test(lines[i])) {
          var body = lines[i].replace(/^>\s?/, '').replace(/\s+$/, '');
          var cls = /^[❌✅]/.test(body) ? (/^❌/.test(body) ? 'cmp bad' : 'cmp good') : '';
          paras.push('<p' + (cls ? ' class="' + cls + '"' : '') + '>' + inline(body) + '</p>');
          i++;
        }
        out.push(clsWrap(paras));
        continue;
      }
      var buf = [];
      while (i < lines.length && lines[i].trim() && !/^(#{1,3}\s|-\s|>\s?|\d+\.\s)/.test(lines[i])) {
        buf.push(lines[i].replace(/^\s+/, '')); i++;
      }
      out.push('<p>' + inline(buf.join('')) + '</p>');
    }
    return out.join('\n');
  }
  function clsWrap(paras) {
    // 引用块内 ❌/✅ 是对照示例，不加灰底；纯原文引用才用 blockquote
    var pure = paras.every(function (p) { return /^<p>/.test(p); });
    return pure ? '<blockquote>' + paras.join('') + '</blockquote>' : paras.join('');
  }

  function getBook(book) {
    var list = (INDEX && INDEX.books) || [];
    for (var i = 0; i < list.length; i++) if (list[i].book === book) return list[i];
    return null;
  }

  function fillBooks() {
    var list = (INDEX && INDEX.books) || [];
    var html = [];
    var stageNow = '';
    list.forEach(function (b) {
      if (b.stage !== stageNow) {
        stageNow = b.stage;
        html.push('<optgroup label="' + esc(stageNow) + '">');
      }
      html.push('<option value="' + esc(b.book) + '">' + esc(b.book) + '（' + b.lessonCount + ' 篇）</option>');
    });
    // optgroup 需要成对闭合：简单收尾（浏览器容错，末组自动闭合）
    selBook.innerHTML = html.join('');
    if (INDEX && INDEX.total) {
      hint.textContent = '已收录 ' + list.length + ' 册 / ' + INDEX.total + ' 个课时。其余册次整理中。'
        + ' 点课时名称，右侧（手机为下方）显示完整讲解。';
    }
  }

  function fillUnits(book) {
    var b = getBook(book);
    if (!b) { selUnit.innerHTML = '<option value="">—</option>'; return; }
    var units = [];
    b.lessons.forEach(function (L) { if (units.indexOf(L.chapter) < 0) units.push(L.chapter); });
    selUnit.innerHTML = '<option value="">全部单元（' + b.lessonCount + ' 课时）</option>'
      + units.map(function (u) { return '<option value="' + esc(u) + '">' + esc(u) + '</option>'; }).join('');
  }

  function renderList() {
    if (!BOOK) { listEl.innerHTML = '<p class="empty">请选择册次</p>'; return; }
    var unitFilter = selUnit.value;
    var html = [], lastUnit = '';
    BOOK.lessons.forEach(function (L) {
      if (unitFilter && L.chapter !== unitFilter) return;
      if (L.chapter !== lastUnit) {
        html.push('<div class="unit">' + esc(L.chapter || '未分单元') + '</div>');
        lastUnit = L.chapter;
      }
      html.push('<button class="lesson' + (L.topicId === cur ? ' active' : '') + '" data-id="'
        + esc(L.topicId) + '">' + esc(L.title)
        + (L.words ? '<span class="w">' + L.words + ' 字</span>' : '') + '</button>');
    });
    listEl.innerHTML = html.join('') || '<p class="empty">本单元暂无讲解</p>';
    listEl.querySelectorAll('button.lesson').forEach(function (btn) {
      btn.addEventListener('click', function () { open(btn.getAttribute('data-id')); });
    });
  }

  function open(topicId) {
    if (!BOOK) return;
    var idx = -1;
    BOOK.lessons.forEach(function (L, i) { if (L.topicId === topicId) idx = i; });
    if (idx < 0) return;
    cur = topicId;
    var L = BOOK.lessons[idx];
    var md = (BOOK.md[topicId] || '').trim();
    var html = md ? md2html(md) : '<p>这篇讲解还没写。</p>';
    var prev = BOOK.lessons[idx - 1], next = BOOK.lessons[idx + 1];
    var nav = '<div class="navrow">'
      + '<button id="btn-prev"' + (prev ? ' data-id="' + esc(prev.topicId) + '"' : ' disabled') + '>'
      + (prev ? '← ' + esc(prev.title) : '已是第一篇') + '</button>'
      + '<button id="btn-next"' + (next ? ' data-id="' + esc(next.topicId) + '"' : ' disabled') + '>'
      + (next ? esc(next.title) + ' →' : '已是最后一篇') + '</button></div>'
      + '<p class="src">出处：' + esc(BOOK.book) + ' · 人教版数学 · 学生版精讲（'
      + (L.words || 0) + ' 字）· <a href="../diagnose/">去诊断这个课时</a></p>';
    reader.innerHTML = html + nav;
    ['btn-prev', 'btn-next'].forEach(function (id) {
      var b = document.getElementById(id);
      if (b && b.getAttribute('data-id')) {
        b.addEventListener('click', function () { open(b.getAttribute('data-id')); });
      }
    });
    if (location.hash.slice(1) !== topicId) {
      history.replaceState(null, '', '?book=' + encodeURIComponent(BOOK.book) + '#' + topicId);
    }
    renderList();
    var act = listEl.querySelector('button.lesson.active');
    if (act) act.scrollIntoView({ block: 'nearest' });
    if (USER_SCROLLED) reader.scrollIntoView({ block: 'start', behavior: 'smooth' });
    document.title = L.title + ' · 课时讲解 · K-12 知识图谱';
  }

  function loadBook(book, then) {
    var b = getBook(book);
    if (!b) return;
    fetch('../' + b.path).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (data) {
      var md = {};
      (data.lessons || []).forEach(function (L) { md[L.topicId] = L.markdown || ''; });
      BOOK = { book: book, lessons: b.lessons, md: md };
      fillUnits(book);
      renderList();
      if (then) then();
    }).catch(function (e) {
      reader.innerHTML = '<div class="reader-empty"><h2>这篇讲解加载失败</h2><p>'
        + esc(e.message) + '。检查网络后重试，或直接看 <code>' + esc(b.path) + '</code>。</p></div>';
    });
  }

  function boot() {
    fetch('index.json').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (idx) {
      INDEX = idx;
      INDEX.total = idx.count;
      fillBooks();
      var q = new URLSearchParams(location.search).get('book');
      var hash = location.hash.slice(1);
      var book = q;
      if (!book && hash) {
        idx.books.forEach(function (b) {
          b.lessons.forEach(function (L) { if (L.topicId === hash) book = b.book; });
        });
      }
      if (!book || !getBook(book)) {
        book = idx.books.length ? idx.books[idx.books.length - 1].book : '';
      }
      if (!book) { hint.textContent = '讲解数据还没生成（learn/index.json 为空）。'; return; }
      selBook.value = book;
      loadBook(book, function () {
        var target = hash || (getBook(book).lessons[0] || {}).topicId;
        if (target) open(target);
      });
    }).catch(function (e) {
      hint.textContent = '索引加载失败：' + e.message;
      selBook.innerHTML = '<option value="">加载失败</option>';
    });
  }

  selBook.addEventListener('change', function () {
    var b = selBook.value;
    if (!b) return;
    cur = null;
    history.replaceState(null, '', '?book=' + encodeURIComponent(b));
    loadBook(b, null);
  });
  selUnit.addEventListener('change', function () { USER_SCROLLED = true; renderList(); });
  listEl.addEventListener('click', function () { USER_SCROLLED = true; });
  boot();
})();
