/* 课时讲解页：点课时 → 看讲解。
 * 数据：learn/index.json（册→单元→课时）+ data/math/learn/<册>.json（正文 Markdown）
 * 深链：learn/?book=一年级上册#mat_p1000 或 /learn/#mat_p1000（自动定位册）
 */
(function () {
  'use strict';

  var selSubject = document.getElementById('sel-subject');
  var selEdition = document.getElementById('sel-edition');
  var selBook = document.getElementById('sel-book');
  var selUnit = document.getElementById('sel-unit');
  var listEl = document.getElementById('lesson-list');
  var reader = document.getElementById('reader');
  var hint = document.getElementById('hint');

  var INDEX = null;      // learn/index.json
  var REG = null;        // data/subject-groups.json：一级学科 → 二级教材版本
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
    // 被开方数内部：a^2 → a²，9/2 → 叠排分数（都画在根号横线之内）
    function innerMath(rad) {
      var out = esc(rad);
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
    // 根式：√3、2√6、√(x+1)、√a^2 → 规范根号（横线盖住整个被开方数，含幂与分数）
    function radify(t) {
      return t.replace(/√\s*(?:[\(（]([^()（）]{1,30})[\)）]|([0-9A-Za-z\u4e00-\u9fa5π·×°′″²³\/．.]{1,8})(\^[-]?\d{1,2})?)/g,
        function (m, g1, g2, g3) {
          var rad = (g1 || ((g2 || '') + (g3 || '')) || '').trim();
          return '<span class="rad"><span class="sq">√</span><span class="rd">' + innerMath(rad) + '</span></span>';
        });
    }
    // 分数：3/8、π/2、x/3、(a+b)/2 → 上下叠排 + 分数线（纯字母比 a/b、单位 km/h 不转）
    function fracify(t) {
      return t.replace(/(^|[^\d\/√])((?:\d+(?:\.\d+)?[²³]?|π|[a-zA-Z]|\([^()（）]{1,14}\)))\s*\/\s*((?:\d+(?:\.\d+)?[²³]?|π|[a-zA-Z]|\([^()（）]{1,14}\)))(?![\d\/])/g,
        function (m, pre, a, b) {
          var aNum = /^[\dπ]/.test(a), bNum = /^[\dπ]/.test(b);
          if (!aNum && !bNum) return m;
          if (a.length === 1 && b.length === 1 && /^[a-zA-Z]$/.test(a) && /^[a-zA-Z]$/.test(b)) return m;
          return pre + '<span class="frac"><span class="num">' + a + '</span><span class="den">' + b + '</span></span>';
        });
    }
    // 向量：向量OA / 向量AB / 向量a → 「向量」二字保留，字母上方加右箭头
    function vecify(t) {
      return t.replace(/(向量)\s*([A-Za-z][A-Za-z0-9]{0,3})/g,
        function (m, cn, lt) { return cn + '<span class="vec">' + lt + '</span>'; });
    }
    function inline(t) { return vecify(fracify(radify(esc(t)))).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>'); }
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

  // ⚠️ 同一册名在不同版本下都会出现（人教版/北京版/冀教版都有「一年级上册」），
  // 必须按 学科 + 版本 + 册 三者定位，否则会取到别的版本的书。
  function getBook(book, subject, edition) {
    var list = (INDEX && INDEX.books) || [];
    for (var i = 0; i < list.length; i++) {
      var b = list[i];
      if (b.book !== book) continue;
      if (subject && (b.subject || 'math') !== subject) continue;
      if (edition && (b.edition || '人教版') !== edition) continue;
      return b;
    }
    return null;
  }

  // 一级学科：优先读注册表（18 个），并标出该学科在本站有没有课时讲解数据
  function subjects() {
    var books = (INDEX && INDEX.books) || [];
    var hasData = function (subjId) {
      return books.some(function (b) { return (b.subject || 'math') === subjId; });
    };
    if (REG && REG.subjects && REG.subjects.length) {
      return REG.subjects.map(function (g) {
        return {
          id: g.id,
          name: g.name,
          editions: (g.editions || []).length,
          hasData: hasData(g.id),
          editionsWithData: books.filter(function (b) { return (b.subject || 'math') === g.id; })
            .map(function (b) { return b.edition || '人教版'; })
            .filter(function (v, i, a) { return a.indexOf(v) === i; })
        };
      });
    }
    var out = [];
    books.forEach(function (b) {
      if (!out.some(function (x) { return x.id === b.subject; })) {
        out.push({ id: b.subject || 'math', name: b.subjectName || '数学', editions: 1, hasData: true, editionsWithData: [] });
      }
    });
    return out;
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

  function fillSubjects(keep) {
    var ss = subjects();
    selSubject.innerHTML = ss.map(function (s) {
      var label = s.name + (s.hasData ? '' : '（暂无讲解）');
      return '<option value="' + esc(s.id) + '">' + esc(label) + '</option>';
    }).join('');
    if (keep && ss.some(function (s) { return s.id === keep; })) selSubject.value = keep;
  }

  function fillEditions(subject, keep) {
    var es = editions(subject);           // 只有真正有讲解数据的版本
    var g = groupOf(subject);
    if (!es.length) {
      selEdition.innerHTML = '<option value="">暂无</option>';
      hint.textContent = (g ? g.name : subject) + '：本学科暂无课时讲解数据。'
        + (g && (g.editions || []).length > 1 ? '（共 ' + g.editions.length + ' 个教材版本，均未生成讲解）' : '');
      if (typeof selBook !== 'undefined' && selBook) selBook.innerHTML = '<option value="">—</option>';
      if (typeof listEl !== 'undefined' && listEl) listEl.innerHTML = '';
      if (typeof reader !== 'undefined' && reader) reader.innerHTML = '<p class="empty">暂无讲解</p>';
      return;
    }
    selEdition.innerHTML = es.map(function (e) {
      return '<option value="' + esc(e) + '">' + esc(e) + '</option>';
    }).join('');
    if (keep && es.indexOf(keep) >= 0) selEdition.value = keep;
  }

  function groupOf(subjectId) {
    if (!REG || !REG.subjects) return null;
    return REG.subjects.filter(function (g) { return g.id === subjectId; })[0] || null;
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
        + '（' + b.lessonCount + ' 篇）</option>');
    });
    if (opened) html.push('</optgroup>');
    selBook.innerHTML = html.join('') || '<option value="">暂无</option>';
    if (keep && list.some(function (b) { return b.book === keep; })) selBook.value = keep;
    var cur = (subjects().filter(function (s) { return s.id === selSubject.value; })[0] || {});
    var subjName = cur.name || '';
    if (!list.length) {
      hint.textContent = subjName + '：本学科暂无课时讲解数据。';
      return;
    }
    var g2 = groupOf(selSubject.value);
    var more = (g2 && (g2.editions || []).length > editions(selSubject.value).length)
      ? '（另有 ' + (g2.editions.length - editions(selSubject.value).length) + ' 个教材版本暂无讲解）' : '';
    hint.textContent = subjName + '·' + selEdition.value + '：已收录 ' + list.length + ' 册 / '
      + list.reduce(function (n, b) { return n + b.lessonCount; }, 0) + ' 个课时' + more + '。'
      + ' 点课时名称，右侧（手机为下方）显示完整讲解。';
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
      history.replaceState(null, '', '?subject=' + encodeURIComponent(selSubject.value)
        + '&edition=' + encodeURIComponent(selEdition.value)
        + '&book=' + encodeURIComponent(BOOK.book) + '#' + topicId);
    }
    renderList();
    var act = listEl.querySelector('button.lesson.active');
    if (act) act.scrollIntoView({ block: 'nearest' });
    if (USER_SCROLLED) reader.scrollIntoView({ block: 'start', behavior: 'smooth' });
    document.title = L.title + ' · 课时讲解 · K-12 知识图谱';
  }

  function loadBook(book, then) {
    var b = getBook(book, selSubject.value, selEdition.value);
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
    // 索引（讲解数据）+ 注册表（学科→版本）并行取
    var pIndex = fetch('index.json').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
    var pReg = fetch('../data/subject-groups.json')
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });

    Promise.all([pIndex, pReg]).then(function (rs) {
      var idx = rs[0];
      REG = rs[1];
      INDEX = idx;
      INDEX.total = idx.count;
      fillSubjects();

      var q = new URLSearchParams(location.search);
      var hash = location.hash.slice(1);
      var wantBook = q.get('book'), wantSubj = q.get('subject'), wantEd = q.get('edition');

      // 深链（只有 #topicId）时反查它属于哪一册 / 哪一学科 / 哪个出版社
      var hitBook = null;
      if (hash) {
        (idx.books || []).forEach(function (b) {
          (b.lessons || []).forEach(function (L) { if (L.topicId === hash) hitBook = b; });
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
        wantBook = list.length ? list[0].book : '';   // 默认第一册（一年级上册），与试卷讲解一致
      }
      fillBooks(wantBook);
      if (!wantBook) {
        var gx = (typeof groupOf === 'function') ? groupOf(selSubject.value) : null;
        hint.textContent = (gx ? gx.name : '本学科') + '：暂无课时讲解数据。';
        if (selBook) selBook.innerHTML = '<option value="">—</option>';
        return;
      }
      selBook.value = wantBook;
      loadBook(wantBook, function () {
        var target = hash || (getBook(wantBook, selSubject.value, selEdition.value).lessons[0] || {}).topicId;
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
    var book = list[list.length - 1].book;
    fillBooks(book);
    history.replaceState(null, '', '?subject=' + encodeURIComponent(subj)
      + '&edition=' + encodeURIComponent(selEdition.value) + '&book=' + encodeURIComponent(book));
    loadBook(book, null);
  });

  selEdition.addEventListener('change', function () {
    var list = booksOf(selSubject.value, selEdition.value);
    if (!list.length) { selBook.innerHTML = '<option value="">暂无</option>'; return; }
    var prev = selBook.value;
    cur = null;
    // 换版本时尽量停在同一册（如都有一年级上册）；没有才退回第一册
    var book = list.some(function (b) { return b.book === prev; }) ? prev : list[0].book;
    fillBooks(book);
    history.replaceState(null, '', '?subject=' + encodeURIComponent(selSubject.value)
      + '&edition=' + encodeURIComponent(selEdition.value) + '&book=' + encodeURIComponent(book));
    loadBook(book, null);
  });

  selBook.addEventListener('change', function () {
    var b = selBook.value;
    if (!b) return;
    cur = null;
    history.replaceState(null, '', '?subject=' + encodeURIComponent(selSubject.value)
      + '&edition=' + encodeURIComponent(selEdition.value) + '&book=' + encodeURIComponent(b));
    loadBook(b, null);
  });
  selUnit.addEventListener('change', function () { USER_SCROLLED = true; renderList(); });
  listEl.addEventListener('click', function () { USER_SCROLLED = true; });
  boot();
})();
