/* 试卷讲解页：点卷名 → 看整卷讲解。
 * 数据：lectures/index.json（册→卷清单）+ lectures/data/<册>.json（正文 Markdown）
 * 深链：lectures/?book=八年级下册#mat_exam_g8b_u19
 */
(function () {
  'use strict';

  var selBook = document.getElementById('sel-book');
  var selKind = document.getElementById('sel-kind');
  var listEl = document.getElementById('paper-list');
  var reader = document.getElementById('reader');
  var hint = document.getElementById('hint');

  var INDEX = null, BOOK = null, cur = null, USER_SCROLLED = false;

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /* 与课时讲解页同一套行内排版：根式 / 分数 / 向量 / 粗体 */
  // 被开方数内部：a^2 → a²，9/2 → 叠排分数（都画在根号横线之内）
  function innerMath(s) {
    var out = esc(s);
    out = out.replace(/([0-9A-Za-z\u4e00-\u9fa5π²³])\^(-?\d{1,2})/g, function (m, b, e) {
      return b + '<sup>' + e.replace('-', '−') + '</sup>';
    });
    out = out.replace(/(^|[^\d\/])((?:\d+(?:\.\d+)?[²³]?|π|[a-zA-Z]))\s*\/\s*((?:\d+(?:\.\d+)?[²³]?|π|[a-zA-Z]))(?![\d\/])/g,
      function (m, pre, a, b) {
        if (!/^[\dπ]/.test(a) && !/^[\dπ]/.test(b)) return m;
        if (/^[a-zA-Z]$/.test(a) && /^[a-zA-Z]$/.test(b)) return m;
        return pre + '<span class="frac"><span class="num">' + a + '</span><span class="den">' + b + '</span></span>';
      });
    return out;
  }

  function radify(t) {
    // 根号：√3、2√6、√(x+1)、√a^2 → 规范根号；被开方数里的幂与分数画在根号里面
    return t.replace(/√\s*(?:[\(（]([^()（）]{1,30})[\)）]|([0-9A-Za-z\u4e00-\u9fa5π·×°′″²³\/．.]{1,8})(\^[-]?\d{1,2})?)/g,
      function (m, g1, g2, g3) {
        var rad = (g1 || ((g2 || '') + (g3 || '')) || '').trim();
        return '<span class="rad"><span class="sq">√</span><span class="rd">' + innerMath(rad) + '</span></span>';
      });
  }
  function fracify(t) {
    return t.replace(/(^|[^\d\/√])((?:\d+(?:\.\d+)?[²³]?|π|[a-zA-Z]|\([^()（）]{1,14}\)))\s*\/\s*((?:\d+(?:\.\d+)?[²³]?|π|[a-zA-Z]|\([^()（）]{1,14}\)))(?![\d\/])/g,
      function (m, pre, a, b) {
        var aNum = /^[\dπ]/.test(a), bNum = /^[\dπ]/.test(b);
        if (!aNum && !bNum) return m;
        if (a.length === 1 && b.length === 1 && /^[a-zA-Z]$/.test(a) && /^[a-zA-Z]$/.test(b)) return m;
        return pre + '<span class="frac"><span class="num">' + a + '</span><span class="den">' + b + '</span></span>';
      });
  }
  function vecify(t) {
    return t.replace(/(向量)\s*([A-Za-z][A-Za-z0-9]{0,3})/g,
      function (m, cn, lt) { return cn + '<span class="vec">' + lt + '</span>'; });
  }
  function inline(t) {
    return vecify(fracify(radify(esc(t)))).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  }

  function md2html(md) {
    var lines = md.split('\n'), out = [], i = 0;
    while (i < lines.length) {
      var ln = lines[i].replace(/\s+$/, '');
      if (!ln.trim()) { i++; continue; }
      if (/^#\s/.test(ln)) { out.push('<h1>' + inline(ln.slice(2)) + '</h1>'); i++; continue; }
      if (/^###\s/.test(ln)) { out.push('<h3>' + inline(ln.slice(4)) + '</h3>'); i++; continue; }
      if (/^##\s/.test(ln)) { out.push('<h2>' + inline(ln.slice(3)) + '</h2>'); i++; continue; }
      if (/^-\s\[[ x]\]/.test(ln)) {
        var boxes = [];
        while (i < lines.length && /^-\s\[[ x]\]/.test(lines[i])) {
          boxes.push('<li>' + inline(lines[i].replace(/^-\s\[[ x]\]\s*/, '')) + '</li>'); i++;
        }
        out.push('<ul class="check">' + boxes.join('') + '</ul>');
        continue;
      }
      if (/^-\s/.test(ln)) {
        var dots = [];
        while (i < lines.length && /^-\s/.test(lines[i]) && !/^-\s\[[ x]\]/.test(lines[i])) {
          dots.push('<li>' + inline(lines[i].slice(2)) + '</li>'); i++;
        }
        out.push('<ul class="dot">' + dots.join('') + '</ul>');
        continue;
      }
      if (/^\d+\.\s/.test(ln)) {
        var ols = [], k = i;
        while (k < lines.length) {
          if (/^\d+\.\s/.test(lines[k])) {
            ols.push('<li>' + inline(lines[k].replace(/^\d+\.\s*/, '')) + '</li>');
            k++; continue;
          }
          if (!lines[k].trim()) {
            var j = k;
            while (j < lines.length && !lines[j].trim()) j++;
            if (j < lines.length && /^\d+\.\s/.test(lines[j])) { k = j; continue; }
          }
          break;
        }
        i = k;
        out.push('<ol class="steps-list">' + ols.join('') + '</ol>');
        continue;
      }
      if (/^>\s?/.test(ln)) {
        var ps = [];
        while (i < lines.length && /^>\s?/.test(lines[i])) {
          var body = lines[i].replace(/^>\s?/, '').replace(/\s+$/, '');
          var cls = /^[❌✅]/.test(body) ? (/^❌/.test(body) ? 'cmp bad' : 'cmp good') : '';
          ps.push('<p' + (cls ? ' class="' + cls + '"' : '') + '>' + inline(body) + '</p>');
          i++;
        }
        out.push('<blockquote>' + ps.join('') + '</blockquote>');
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

  var KIND_LABEL = { unit: '单元卷', mid: '期中', fin: '期末' };

  function getBook(name) {
    var list = (INDEX && INDEX.books) || [];
    for (var i = 0; i < list.length; i++) if (list[i].book === name) return list[i];
    return null;
  }

  function fillBooks() {
    var list = (INDEX && INDEX.books) || [];
    var html = [], stageNow = '';
    list.forEach(function (b) {
      if (b.stage !== stageNow) {
        stageNow = b.stage;
        html.push('<optgroup label="' + esc(stageNow) + '">');
      }
      html.push('<option value="' + esc(b.book) + '">' + esc(b.book) + '（' + b.paperCount + ' 份）</option>');
    });
    selBook.innerHTML = html.join('');
    if (INDEX) {
      hint.textContent = '已收录 ' + list.length + ' 册 / ' + INDEX.count
        + ' 份试卷讲解。点卷名，右侧（手机为下方）显示整卷讲解。';
    }
  }

  function renderList() {
    if (!BOOK) { listEl.innerHTML = '<p class="empty">请选择册次</p>'; return; }
    var kind = selKind.value;
    var html = [], lastKind = '';
    BOOK.papers.forEach(function (p) {
      if (kind && p.kind !== kind) return;
      if (p.kind !== lastKind) {
        html.push('<div class="unit">' + esc(KIND_LABEL[p.kind] || '试卷') + '</div>');
        lastKind = p.kind;
      }
      html.push('<button class="lesson' + (p.examId === cur ? ' active' : '') + '" data-id="'
        + esc(p.examId) + '">' + esc(p.paper)
        + (p.words ? '<span class="w">' + p.words + ' 字</span>' : '') + '</button>');
    });
    listEl.innerHTML = html.join('') || '<p class="empty">这一类暂无讲解</p>';
    listEl.querySelectorAll('button.lesson').forEach(function (btn) {
      btn.addEventListener('click', function () { open(btn.getAttribute('data-id')); });
    });
  }

  function open(examId) {
    if (!BOOK) return;
    var idx = -1;
    BOOK.papers.forEach(function (p, i) { if (p.examId === examId) idx = i; });
    if (idx < 0) return;
    cur = examId;
    var p = BOOK.papers[idx];
    var md = (p.markdown || '').trim();
    var html = md ? md2html(md) : '<p>这份讲解还没写。</p>';
    var meta = BOOK.meta[examId] || {};
    var prev = BOOK.papers[idx - 1], next = BOOK.papers[idx + 1];
    var nav = '<div class="navrow">'
      + '<button id="btn-prev"' + (prev ? ' data-id="' + esc(prev.examId) + '"' : ' disabled') + '>'
      + (prev ? '← ' + esc(prev.paper) : '已是第一份') + '</button>'
      + '<button id="btn-next"' + (next ? ' data-id="' + esc(next.examId) + '"' : ' disabled') + '>'
      + (next ? esc(next.paper) + ' →' : '已是最后一份') + '</button></div>'
      + '<p class="src">' + esc(BOOK.book) + ' · ' + esc(p.paper)
      + (meta.fullScore ? ' · 满分 ' + meta.fullScore + ' 分' : '')
      + (meta.duration ? ' · ' + meta.duration + ' 分钟' : '')
      + (meta.items ? ' · ' + meta.items + ' 题' : '')
      + ' · ' + (p.words || 0) + ' 字 · <a href="../diagnose/">去整卷测试</a></p>';
    reader.innerHTML = html + nav;
    ['btn-prev', 'btn-next'].forEach(function (id) {
      var b = document.getElementById(id);
      if (b && b.getAttribute('data-id')) {
        b.addEventListener('click', function () { open(b.getAttribute('data-id')); });
      }
    });
    if (location.hash.slice(1) !== examId) {
      history.replaceState(null, '', '?book=' + encodeURIComponent(BOOK.book) + '#' + examId);
    }
    renderList();
    var act = listEl.querySelector('button.lesson.active');
    if (act) act.scrollIntoView({ block: 'nearest' });
    if (USER_SCROLLED) reader.scrollIntoView({ block: 'start', behavior: 'smooth' });
    document.title = p.paper + ' · 试卷讲解 · K-12 知识图谱';
  }

  function loadBook(name, then) {
    var b = getBook(name);
    if (!b) return;
    fetch(b.path + '?v=1').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (data) {
      var meta = {};
      b.papers.forEach(function (p) { meta[p.examId] = p; });
      BOOK = { book: name, papers: data.papers || [], meta: meta };
      renderList();
      if (then) then();
    }).catch(function (e) {
      reader.innerHTML = '<div class="reader-empty"><h2>讲解加载失败</h2><p>'
        + esc(e.message) + '。检查网络后重试，或直接看 <code>' + esc(b.path) + '</code>。</p></div>';
    });
  }

  function boot() {
    fetch('index.json').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (idx) {
      INDEX = idx;
      fillBooks();
      var q = new URLSearchParams(location.search).get('book');
      var hash = location.hash.slice(1);
      var book = q;
      if (!book && hash) {
        idx.books.forEach(function (b) {
          b.papers.forEach(function (p) { if (p.examId === hash) book = b.book; });
        });
      }
      if (!book || !getBook(book)) {
        book = idx.books.length ? idx.books[0].book : '';
      }
      if (!book) { hint.textContent = '讲解数据还没生成（lectures/index.json 为空）。'; return; }
      selBook.value = book;
      loadBook(book, function () {
        var target = hash || ((getBook(book).papers[0] || {}).examId);
        if (target) open(target);
      });
    }).catch(function (e) {
      hint.textContent = '索引加载失败：' + e.message;
      selBook.innerHTML = '<option value="">加载失败</option>';
    });
  }

  selBook.addEventListener('change', function () {
    if (!selBook.value) return;
    cur = null;
    history.replaceState(null, '', '?book=' + encodeURIComponent(selBook.value));
    loadBook(selBook.value, null);
  });
  selKind.addEventListener('change', function () { USER_SCROLLED = true; renderList(); });
  listEl.addEventListener('click', function () { USER_SCROLLED = true; });
  boot();
})();
