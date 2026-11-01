/* 试卷讲解页：点卷名 → 看整卷讲解。
 * 数据：learn/exam/index.json（册→卷清单）+ learn/exam/data/<册>.json（正文 Markdown）
 * 深链：learn/exam/?book=八年级下册#mat_exam_g8b_u19
 */
(function () {
  'use strict';

  var selSubject = document.getElementById('sel-subject');
  var selEdition = document.getElementById('sel-edition');
  var selBook = document.getElementById('sel-book');
  var selKind = document.getElementById('sel-kind');
  var listEl = document.getElementById('paper-list');
  var reader = document.getElementById('reader');
  var hint = document.getElementById('hint');

  var INDEX = null, BOOK = null, cur = null, USER_SCROLLED = false;
  var REG = null;   // ../data/subject-groups.json：一级学科 → 二级教材版本

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

  // 初中/高中教材按「章」，小学按「单元」：标题跟着教材走
  function unitWord(bookName) {
    var b = getBook(bookName);
    var papers = (b && b.papers) || [];
    for (var i = 0; i < papers.length; i++) {
      if (papers[i].kind === 'unit' && /章/.test(papers[i].paper || '')) return '章';
    }
    return '单元';
  }
  function kindLabels() {
    var w = unitWord((BOOK && BOOK.book) || (selBook && selBook.value));
    return { unit: w + '测试卷', mid: '期中测试卷', fin: '期末测试卷' };
  }
  var KIND_LABEL = { unit: '单元卷', mid: '期中', fin: '期末' };

  function getBook(name) {
    var list = (INDEX && INDEX.books) || [];
    for (var i = 0; i < list.length; i++) if (list[i].book === name) return list[i];
    return null;
  }

  // 一级学科：优先读注册表（18 个），标出该学科在本站有没有试卷讲解数据
  function subjects() {
    var books = (INDEX && INDEX.books) || [];
    var hasData = function (subjId) {
      return books.some(function (b) { return (b.subject || 'math') === subjId; });
    };
    if (REG && REG.subjects && REG.subjects.length) {
      return REG.subjects.map(function (g) {
        return { id: g.id, name: g.name, editions: (g.editions || []).length, hasData: hasData(g.id) };
      });
    }
    var out = [];
    books.forEach(function (b) {
      if (!out.some(function (x) { return x.id === b.subject; })) {
        out.push({ id: b.subject || 'math', name: b.subjectName || '数学', editions: 1, hasData: true });
      }
    });
    return out;
  }

  function groupOf(subjectId) {
    if (!REG || !REG.subjects) return null;
    return REG.subjects.filter(function (g) { return g.id === subjectId; })[0] || null;
  }

  function editions(subject) {
    var list = (INDEX && INDEX.books) || [], out = [];
    list.forEach(function (b) {
      if ((b.subject || 'math') !== subject) return;
      var e = b.edition || '人教版';
      if (out.indexOf(e) < 0) out.push(e);
    });
    return out;
  }

  function booksOf(subject, edition) {
    return ((INDEX && INDEX.books) || []).filter(function (b) {
      return (b.subject || 'math') === subject && (b.edition || '人教版') === edition;
    });
  }

  function fillSubjects() {
    selSubject.innerHTML = subjects().map(function (x) {
      return '<option value="' + esc(x.id) + '">' + esc(x.name + (x.hasData ? '' : '（暂无讲解）')) + '</option>';
    }).join('');
  }

  function fillEditions(subject, keep) {
    var es = editions(subject);
    var g = groupOf(subject);
    if (!es.length) {
      selEdition.innerHTML = '<option value="">暂无</option>';
      hint.textContent = (g ? g.name : subject) + '：本学科暂无试卷讲解数据。';
      if (typeof listEl !== 'undefined' && listEl) listEl.innerHTML = '';
      if (typeof reader !== 'undefined' && reader) reader.innerHTML = '<p class="empty">暂无讲解</p>';
      if (typeof selBook !== 'undefined' && selBook) selBook.innerHTML = '<option value="">—</option>';
      return;
    }
    selEdition.innerHTML = es.map(function (e) {
      return '<option value="' + esc(e) + '">' + esc(e) + '</option>';
    }).join('');
    if (keep && es.indexOf(keep) >= 0) selEdition.value = keep;
  }

  // 册次：只列当前 学科+出版社 的册，按学段分组
  function fillBooks(keep) {
    var list = booksOf(selSubject.value, selEdition.value);
    var html = [], stageNow = '', opened = false;
    list.forEach(function (b) {
      if (b.stage !== stageNow) {
        if (opened) html.push('</optgroup>');   // ⚠️ 必须成对闭合：不闭合时浏览器会把后一个 optgroup 嵌进前一个，初中/高中整组选不到
        stageNow = b.stage;
        html.push('<optgroup label="' + esc(stageNow) + '">');
        opened = true;
      }
      html.push('<option value="' + esc(b.book) + '">' + esc(b.book)
        + '（' + b.paperCount + ' 份）</option>');
    });
    if (opened) html.push('</optgroup>');
    selBook.innerHTML = html.join('') || '<option value="">暂无</option>';
    if (keep && list.some(function (b) { return b.book === keep; })) selBook.value = keep;
    var subjName = (subjects().filter(function (x) { return x.id === selSubject.value; })[0] || {}).name || '';
    hint.textContent = subjName + '·' + selEdition.value + '：已收录 ' + list.length + ' 册 / '
      + list.reduce(function (n, b) { return n + b.paperCount; }, 0) + ' 份试卷讲解。'
      + ' 点卷名，右侧（手机为下方）显示整卷讲解。';
  }

  function renderList() {
    if (!BOOK) { listEl.innerHTML = '<p class="empty">请选择册次</p>'; return; }
    // 下拉里的「单元/章」也跟着教材走
    var w0 = unitWord(BOOK.book);
    var oUnit = document.querySelector('#sel-kind option[value="unit"]');
    if (oUnit) oUnit.textContent = w0 + '测试卷';
    var oAll = document.querySelector('#sel-kind option[value=""]');
    if (oAll) oAll.textContent = '全部（' + w0 + ' / 期中 / 期末）';
    var kind = selKind.value;
    var html = [], lastKind = '';
    BOOK.papers.forEach(function (p) {
      if (kind && p.kind !== kind) return;
      if (p.kind !== lastKind) {
        html.push('<div class="unit">' + esc(kindLabels()[p.kind] || '试卷') + '</div>');
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
      + ' · ' + (p.words || 0) + ' 字 · <a href="../../diagnose/?mode=exam">去整卷测试</a></p>';
    reader.innerHTML = html + nav;
    ['btn-prev', 'btn-next'].forEach(function (id) {
      var b = document.getElementById(id);
      if (b && b.getAttribute('data-id')) {
        b.addEventListener('click', function () { open(b.getAttribute('data-id')); });
      }
    });
    if (location.hash.slice(1) !== examId) {
      history.replaceState(null, '', '?subject=' + encodeURIComponent(selSubject.value)
        + '&edition=' + encodeURIComponent(selEdition.value)
        + '&book=' + encodeURIComponent(BOOK.book) + '#' + examId);
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
    fetch(b.path + '?v=2').then(function (r) {
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
    var pIndex = fetch('index.json').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
    var pReg = fetch('../../data/subject-groups.json')
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });

    Promise.all([pIndex, pReg]).then(function (rs) {
      var idx = rs[0];
      REG = rs[1];
      INDEX = idx;
      fillSubjects();

      var q = new URLSearchParams(location.search);
      var hash = location.hash.slice(1);
      var wantBook = q.get('book'), wantSubj = q.get('subject'), wantEd = q.get('edition');

      // 深链只有 #examId 时反查它属于哪一册 / 哪一学科 / 哪个出版社
      var hitBook = null;
      if (hash) {
        (idx.books || []).forEach(function (b) {
          (b.papers || []).forEach(function (p) { if (p.examId === hash) hitBook = b; });
        });
      }
      if (hitBook) {
        wantBook = wantBook || hitBook.book;
        wantSubj = wantSubj || hitBook.subject || 'math';
        wantEd = wantEd || hitBook.edition || '人教版';
      }
      if (!wantSubj || !subjects().some(function (x) { return x.id === wantSubj; })) {
        wantSubj = (subjects()[0] || {}).id || 'math';
      }
      selSubject.value = wantSubj;
      fillEditions(wantSubj, wantEd);
      var list = booksOf(wantSubj, selEdition.value);
      if (!wantBook || !list.some(function (b) { return b.book === wantBook; })) {
        wantBook = list.length ? list[0].book : '';
      }
      fillBooks(wantBook);
      if (!wantBook) { hint.textContent = '讲解数据还没生成（learn/exam/index.json 为空）。'; return; }
      selBook.value = wantBook;
      loadBook(wantBook, function () {
        var target = hash || ((getBook(wantBook).papers[0] || {}).examId);
        if (target) open(target);
      });
    }).catch(function (e) {
      hint.textContent = '索引加载失败：' + e.message;
      selBook.innerHTML = '<option value="">加载失败</option>';
    });
  }

  selSubject.addEventListener('change', function () {
    var subj = selSubject.value;
    if (!subj) return;
    cur = null;
    fillEditions(subj, null);
    var list = booksOf(subj, selEdition.value);
    if (!list.length) { selBook.innerHTML = '<option value="">暂无</option>'; return; }
    var book = list[0].book;
    fillBooks(book);
    history.replaceState(null, '', '?subject=' + encodeURIComponent(subj)
      + '&edition=' + encodeURIComponent(selEdition.value) + '&book=' + encodeURIComponent(book));
    loadBook(book, null);
  });

  selEdition.addEventListener('change', function () {
    var list = booksOf(selSubject.value, selEdition.value);
    if (!list.length) { selBook.innerHTML = '<option value="">暂无</option>'; return; }
    cur = null;
    var book = list[0].book;
    fillBooks(book);
    history.replaceState(null, '', '?subject=' + encodeURIComponent(selSubject.value)
      + '&edition=' + encodeURIComponent(selEdition.value) + '&book=' + encodeURIComponent(book));
    loadBook(book, null);
  });

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
