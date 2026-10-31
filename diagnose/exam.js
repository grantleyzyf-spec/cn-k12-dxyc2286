/* 整卷模式（单元卷 / 期中 / 期末）—— 与自适应诊断共用同一套知识点与课标数据
   数据源：diagnose/exam-index.json（卷索引）+ exams/<册>/<卷名>.json（卷面）
   判分：choice/multi/numeric/fill 自动；solve 与多空答案给三档自评 */
(function () {
  const S = {
    index: null,
    paper: null,
    meta: null,
    answers: {},      // itemId -> string / label / array
    judge: {},        // itemId -> {ok:bool|null, factor:number, self:bool}
    topics: null,     // topicId -> topic
    startedAt: 0,
    timerId: null,
    leftSec: 0
  };

  const TYPE_NAME = { choice: '选择', multi: '多选', numeric: '计算', fill: '填空', solve: '解答' };
  const SUBJECT_NAME = {
    math: '数学', chinese: '语文', english: '英语', physics: '物理', chemistry: '化学', biology: '生物',
    history: '历史', geography: '地理', science: '科学', 'information-technology': '信息科技',
    japanese: '日语', russian: '俄语', german: '德语', french: '法语', spanish: '西班牙语',
    music: '音乐', art: '美术'
  };
  const SELF_TIERS = [['full', '全对', 1], ['half', '部分对', 0.5], ['zero', '没得分', 0]];

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  /* ---------- 基础判分工具（与自适应诊断同口径） ---------- */
  function normAns(v) {
    return (v || '').replace(/[\uFF01-\uFF5E]/g, c => String.fromCharCode(c.charCodeAt(0) - 0xFEE0))
      .replace(/[，、]/g, ',').replace(/。/g, '.').replace(/\s+/g, '').toLowerCase();
  }
  function parseNum(v) {
    const t = normAns(v).replace(/[%％]/g, '').replace(/[（）()]/g, '');
    if (/^-?\d+(\.\d+)?$/.test(t)) return parseFloat(t);
    const m = t.match(/^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/);
    if (m && parseFloat(m[2]) !== 0) return parseFloat(m[1]) / parseFloat(m[2]);
    return NaN;
  }
  function near(a, b) { return Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(b)); }

  // 把「（1）100；（2）6 个」拆成 [["1","100"],["2","6个"]] 形式
  function splitParts(ans) {
    const s = String(ans || '').trim();
    if (!/[；;]/.test(s)) return [{ tag: '', body: s }];
    return s.split(/[；;]/).map(x => x.trim()).filter(Boolean).map(seg => {
      const m = seg.match(/^[（(]\s*(\d+)\s*[）)]\s*(.+)$/);
      return m ? { tag: m[1], body: m[2] } : { tag: '', body: seg };
    });
  }
  function partMatch(userPart, keyPart) {
    const u = normAns(userPart), k = normAns(keyPart);
    if (!u) return false;
    if (u === k) return true;
    const nu = parseNum(u), nk = parseNum(k);
    if (!isNaN(nu) && !isNaN(nk) && near(nu, nk)) return true;
    // 允许「100」对「100个」这类带单位差异
    const strip = (t) => t.replace(/[个只有米厘米分米元角分人本辆只支张天时分秒千克克吨]/g, '');
    const su = strip(u), sk = strip(k);
    const nu2 = parseNum(su), nk2 = parseNum(sk);
    if (!isNaN(nu2) && !isNaN(nk2) && near(nu2, nk2)) return true;
    return su === sk && su.length > 0;
  }

  function judgeAuto(item) {
    const u = S.answers[item.itemId];
    if (item.type === 'choice') {
      const ans = normAns(item.answer).toUpperCase();
      if (!u) return { ok: null, factor: 0, self: false, empty: true };
      return { ok: normAns(u).toUpperCase() === ans, factor: normAns(u).toUpperCase() === ans ? 1 : 0, self: false };
    }
    if (item.type === 'multi') {
      if (!u || !u.length) return { ok: null, factor: 0, self: false, empty: true };
      const pick = (Array.isArray(u) ? u : String(u).split('')).map(x => normAns(x).toUpperCase()).sort().join('');
      const key = normAns(item.answer).replace(/[,，、]/g, '').toUpperCase().split('').sort().join('');
      return { ok: pick === key, factor: pick === key ? 1 : 0, self: false };
    }
    if (item.type === 'numeric' || item.type === 'fill') {
      if (!normAns(u)) return { ok: null, factor: 0, self: false, empty: true };
      const keys = splitParts(item.answer);
      const users = splitParts(u);
      // 多空答案：学生也按分号写了才比；否则交给自评
      if (keys.length > 1) {
        if (users.length !== keys.length) return { ok: false, factor: 0, self: true };
        const all = keys.every((k, i) => partMatch(users[i].body, k.body));
        return { ok: all, factor: all ? 1 : 0, self: true };
      }
      const ok = partMatch(u, item.answer);
      return { ok, factor: ok ? 1 : 0, self: false };
    }
    return { ok: null, factor: 0, self: true }; // solve：交给自评
  }

  /* ---------- 索引与选卷 ---------- */
  async function loadIndex() {
    const r = await fetch('../diagnose/exam-index.json', { cache: 'no-cache' });
    if (!r.ok) throw new Error('exam-index.json ' + r.status);
    S.index = await r.json();
  }

  function cnNum(s) {
    const m = String(s).match(/第([一二三四五六七八九十百]+)单元/);
    if (!m) return 99;
    const map = { 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9, 十: 10 };
    const t = m[1];
    if (t.length === 1) return map[t] || 99;
    if (t[0] === '十') return 10 + (map[t[1]] || 0);
    if (t[1] === '十') return (map[t[0]] || 0) * 10 + (map[t[2]] || 0);
    return 99;
  }

  function booksOf(subject, edition) {
    const m = new Map();
    Object.entries(S.index.exams).forEach(([id, e]) => {
      if (subject && (e.subject || 'math') !== subject) return;
      if (edition && (e.edition || '人教版') !== edition) return;
      const k = e.book;
      const cur = m.get(k) || { book: k, grade: e.grade, stage: e.stage, papers: [] };
      cur.papers.push(Object.assign({ examId: id }, e));
      m.set(k, cur);
    });
    const arr = [...m.values()];
    arr.sort((a, b) => a.grade - b.grade || String(a.book).localeCompare(String(b.book), 'zh'));
    arr.forEach(x => x.papers.sort((p, q) => {
      const order = { unit: 0, midterm: 1, final: 2 };
      const ko = (order[p.kind] - order[q.kind]);
      if (ko) return ko;
      const kn = cnNum(p.paper) - cnNum(q.paper);
      if (kn) return kn;
      return String(p.paper).localeCompare(String(q.paper), 'zh');
    }));
    return arr;
  }

  function paperLabel(e) {
    const kind = { unit: '单元卷', midterm: '期中', final: '期末' }[e.kind] || '卷';
    return `[${kind}] ${e.paper} · ${e.itemCount} 题 / ${e.fullScore} 分 / ${e.duration} 分钟`;
  }

  function editionOf(meta) { return (meta && meta.edition) || (S.index && S.index.edition) || '人教版'; }

  /* ---------- 试卷渲染 ---------- */
  async function loadTopics(subject) {
    if (S.topics) return S.topics;
    const r = await fetch(`../data/${subject}/topics.json`, { cache: 'force-cache' });
    const d = await r.json();
    S.topics = {};
    (Array.isArray(d) ? d : []).forEach(t => { S.topics[t.id] = t; });
    return S.topics;
  }

  async function openPaper(examId) {
    const meta = S.index.exams[examId];
    if (!meta) return;
    const shown = $('exam-paper');
    shown.style.display = 'block';
    shown.innerHTML = '<div class="ex-tip">正在载入试卷…</div>';
    $('exam-setup').style.display = 'none';
    $('exam-report').style.display = 'none';
    let r;
    try {
      const subj = meta.subject || 'math';
      r = await fetch(`../data/${subj}/` + meta.path.split('/').map(encodeURIComponent).join('/'), { cache: 'no-cache' });
    } catch (e) {
      shown.innerHTML = '<div class="ex-tip">试卷载入失败（网络）：' + esc(e.message) + '</div>';
      return;
    }
    if (!r.ok) { shown.innerHTML = '<div class="ex-tip">试卷载入失败：HTTP ' + r.status + '</div>'; return; }
    S.paper = await r.json();
    S.meta = meta;
    S.answers = {}; S.judge = {}; S.startedAt = Date.now();
    renderPaper();               // 先用卷面把页面立起来，不等 1.8MB 的 topics.json
    startTimer(meta.duration);
    loadTopics(meta.subject || 'math').catch(() => {});   // 报告/先修名称用，后台补
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function renderPaper() {
    const p = S.paper, m = S.meta;
    const kindName = { unit: '单元测试卷', midterm: '期中测试卷', final: '期末测试卷' }[p.kind] || '测试卷';
    const ed = editionOf(m);
    const subjName = SUBJECT_NAME[m.subject || 'math'] || (m.subject || '数学');
    let head = `
      <div class="ex-head">
        <div class="ex-title"><span class="ex-edition">${esc(ed)}</span>${esc(p.book)} · ${esc(p.paper)}</div>
        <div class="ex-sub">${esc(subjName)} · ${esc(ed)}教材 ｜ ${esc(kindName)} ｜ 满分 ${p.fullScore} 分 ｜ 建议用时 ${p.duration} 分钟 ｜ 共 ${m.itemCount} 题</div>
        ${(p.scope && p.scope.length) ? `<div class="ex-scope">考查范围：${p.scope.map(esc).join('；')}</div>` : ''}
        <div class="ex-timer" id="ex-timer">剩余 00:00</div>
      </div>`;
    let body = '';
    p.sections.forEach((sec, si) => {
      body += `<div class="ex-section"><div class="ex-sec-title">${esc(sec.title)}</div>
        <div class="ex-sec-rule">${esc(sec.rule || '')}</div>`;
      sec.items.forEach(it => { body += renderItem(it); });
      body += '</div>';
    });
    body += `<div class="ex-actions">
        <button class="btn" id="ex-submit">交卷并批改</button>
        <button class="ex-btn-ghost" id="ex-quit">退出本卷</button>
      </div>`;
    $('exam-paper').innerHTML = head + body;

    // 事件绑定
    $('exam-paper').addEventListener('input', onInput);
    $('exam-paper').addEventListener('click', onClickItem);
    $('ex-submit').onclick = submitPaper;
    $('ex-quit').onclick = () => { stopTimer(); if (confirm('退出后本次作答不保存，确定退出？')) resetExam(); };
  }

  function renderItem(it) {
    const badge = `<span class="ex-badge">${TYPE_NAME[it.type] || it.type}</span><span class="ex-score">${it.score} 分</span>`;
    let ctrl = '';
    if (it.type === 'choice' && Array.isArray(it.options)) {
      ctrl = `<div class="options" data-item="${esc(it.itemId)}">` +
        it.options.map(o => `<div class="option" data-label="${esc(o.label)}">${esc(o.label)}. ${esc(o.text)}</div>`).join('') + '</div>';
    } else if (it.type === 'multi' && Array.isArray(it.options)) {
      ctrl = `<div class="options multi" data-item="${esc(it.itemId)}">` +
        it.options.map(o => `<div class="option" data-label="${esc(o.label)}">${esc(o.label)}. ${esc(o.text)}</div>`).join('') +
        `</div><div class="ex-tip">多选题：点选全部正确项</div>`;
    } else if (it.type === 'solve') {
      ctrl = `<div class="answer-input"><textarea rows="4" data-item="${esc(it.itemId)}" placeholder="写出解答过程（可分行）"></textarea></div>` +
        (it.scoreRule && it.scoreRule.length ? `<div class="ex-tip">评分要点：${it.scoreRule.map(esc).join('；')}</div>` : '');
    } else {
      const ph = it.type === 'numeric' ? '只填数字或算式结果；多空用分号分隔' : '多个空用分号分隔';
      ctrl = `<div class="answer-input"><input type="text" autocomplete="off" data-item="${esc(it.itemId)}" placeholder="${ph}"></div>`;
    }
    return `<div class="ex-item" data-item="${esc(it.itemId)}">
        <div class="ex-item-head"><span class="ex-no">${it.no}.</span>${badge}</div>
        <div class="ex-stem">${esc(it.stem)}</div>
        ${ctrl}
      </div>`;
  }

  function onInput(e) {
    const el = e.target;
    const id = el.getAttribute('data-item');
    if (!id) return;
    S.answers[id] = el.value;
  }

  function onClickItem(e) {
    const op = e.target.closest('.option');
    if (!op) return;
    const wrap = op.parentElement;
    const id = wrap.getAttribute('data-item');
    const label = op.getAttribute('data-label');
    if (wrap.classList.contains('multi')) {
      op.classList.toggle('selected');
      const picked = [...wrap.querySelectorAll('.option.selected')].map(x => x.getAttribute('data-label'));
      S.answers[id] = picked;
    } else {
      [...wrap.querySelectorAll('.option')].forEach(x => x.classList.remove('selected'));
      op.classList.add('selected');
      S.answers[id] = label;
    }
  }

  /* ---------- 计时 ---------- */
  function startTimer(minutes) {
    stopTimer();
    S.leftSec = Math.round(minutes * 60);
    paintTimer();
    S.timerId = setInterval(() => {
      S.leftSec--;
      paintTimer();
      if (S.leftSec <= 0) { stopTimer(); alert('时间到，自动交卷。'); submitPaper(); }
    }, 1000);
  }
  function paintTimer() {
    const el = $('ex-timer');
    if (!el) return;
    const m = Math.max(0, Math.floor(S.leftSec / 60)), s = Math.max(0, S.leftSec % 60);
    el.textContent = `剩余 ${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    el.classList.toggle('warn', S.leftSec <= 300);
  }
  function stopTimer() { if (S.timerId) { clearInterval(S.timerId); S.timerId = null; } }

  /* ---------- 批改 ---------- */
  function submitPaper() {
    stopTimer();
    const items = allItems();
    let autoScore = 0, selfScore = 0, selfCount = 0, blank = 0;
    items.forEach(it => {
      const j = judgeAuto(it);
      S.judge[it.itemId] = j;
      if (j.empty) blank++;
      if (j.self) { selfCount++; }
      else autoScore += (it.score || 0) * (j.factor || 0);
    });
    renderReport(items, autoScore, selfScore, selfCount, blank);
    $('exam-paper').style.display = 'none';
    $('exam-report').style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function allItems() {
    const out = [];
    S.paper.sections.forEach(sec => sec.items.forEach(it => out.push(it)));
    return out;
  }

  function renderReport(items, autoScore, selfScore, selfCount, blank) {
    const total = S.paper.fullScore;
    const usedSec = Math.round((Date.now() - S.startedAt) / 1000);
    const usedMin = Math.floor(usedSec / 60), usedS = usedSec % 60;

    // 分题型
    const byType = {};
    items.forEach(it => {
      const t = it.type; byType[t] = byType[t] || { got: 0, full: 0, n: 0 };
      byType[t].full += it.score || 0; byType[t].n++;
      const j = S.judge[it.itemId] || { factor: 0 };
      byType[t].got += (it.score || 0) * (j.self ? 0 : (j.factor || 0));
    });

    // 知识点得分率
    const byTopic = {};
    items.forEach(it => {
      const j = S.judge[it.itemId] || {};
      (it.topicIds || []).forEach(tid => {
        const b = byTopic[tid] = byTopic[tid] || { got: 0, full: 0, n: 0, wrong: [] };
        b.full += it.score || 0; b.n++;
        if (!j.self) b.got += (it.score || 0) * (j.factor || 0);
        if (j.ok === false) b.wrong.push(it);
      });
    });
    const weak = Object.entries(byTopic)
      .map(([tid, b]) => ({ tid, ...b, rate: b.full ? b.got / b.full : 0, name: (S.topics[tid] || {}).name || tid, chapter: (S.topics[tid] || {}).chapter || '' }))
      .filter(x => x.rate < 0.6)
      .sort((a, b) => a.rate - b.rate);

    const typeRows = Object.entries(byType).map(([t, v]) =>
      `<tr><td>${TYPE_NAME[t] || t}</td><td>${v.n}</td><td>${v.full}</td><td>${Math.round(v.got * 10) / 10}</td></tr>`).join('');

    const selfItems = items.filter(it => (S.judge[it.itemId] || {}).self);

    const html = `
      <div class="result-card">
        <div class="result-title">📊 卷面报告 · ${esc(S.paper.paper)}</div>
        <div class="ex-kpi">
          <div><b>${Math.round(autoScore * 10) / 10}</b><span>自动判分得分 / ${total}</span></div>
          <div><b>${usedMin}′${String(usedS).padStart(2, '0')}″</b><span>用时（限 ${S.paper.duration} 分钟）</span></div>
          <div><b>${blank}</b><span>未作答</span></div>
          <div><b>${selfCount}</b><span>待自评（解答/多空）</span></div>
        </div>
        <div class="ex-tip">未作答的题按 0 分计；解答题与多空答案在下方自评后计入总分。</div>
        <h4 style="margin:18px 0 8px">分题型</h4>
        <table class="ex-table"><thead><tr><th>题型</th><th>题数</th><th>满分</th><th>已得分</th></tr></thead><tbody>${typeRows}</tbody></table>

        <h4 style="margin:20px 0 8px">薄弱知识点（得分率 &lt; 60%）</h4>
        ${weak.length ? `<ul class="result-list">${weak.map(w => `
          <li>
            <div class="topic-name">${esc(w.name)} <span class="ex-rate">${Math.round(w.rate * 100)}%</span></div>
            <div class="topic-desc">${esc(w.chapter)} ｜ 得分 ${Math.round(w.got * 10) / 10}/${w.full}</div>
            <div class="ex-fix">
              <a class="ex-link" href="../learn/#${encodeURIComponent(w.tid)}">看讲解 →</a>
              <a class="ex-link" href="../diagnose/?topic=${encodeURIComponent(w.tid)}">沿先修链诊断这个点 →</a>
            </div>
          </li>`).join('')}</ul>` : `<p class="ex-ok">本次没有得分率低于 60% 的知识点。</p>`}

        ${selfItems.length ? `<h4 style="margin:20px 0 8px">需要你自评的题（${selfItems.length}）</h4>
        <div id="ex-self">${selfItems.map(it => `
          <div class="ex-self-row" data-item="${esc(it.itemId)}">
            <div class="ex-self-stem"><b>第 ${it.no} 题</b>（${it.score} 分）：${esc(it.stem)}</div>
            <div class="ex-self-key"><b>参考答案：</b>${esc(it.answer)}</div>
            ${it.scoreRule && it.scoreRule.length ? `<div class="ex-self-key"><b>评分要点：</b>${it.scoreRule.map(esc).join('；')}</div>` : ''}
            <div class="self-check">${SELF_TIERS.map(([k, label]) => `<button data-tier="${k}" data-score="${it.score}">${label}</button>`).join('')}</div>
          </div>`).join('')}</div>
        <div class="ex-tip">自评会实时改总分；未点按的题按 0 分计。</div>` : ''}

        <h4 style="margin:20px 0 8px">逐题明细</h4>
        <div class="ex-items">${items.map(it => {
          const j = S.judge[it.itemId] || {};
          const state = j.self ? '<span class="ex-tag wait">待自评</span>'
            : (j.empty ? '<span class="ex-tag blank">未答</span>'
            : (j.ok ? '<span class="ex-tag ok">✓</span>' : '<span class="ex-tag no">✗</span>'));
          const ua = S.answers[it.itemId];
          const uaText = Array.isArray(ua) ? ua.join('') : (ua || '（未作答）');
          return `<div class="ex-line">${state}<b>${it.no}.</b> ${esc(it.stem).slice(0, 60)}${it.stem.length > 60 ? '…' : ''}
            <div class="ex-line-detail">你的答案：${esc(uaText)} ｜ 答案：${esc(it.answer)}</div>
            ${it.analysis ? `<div class="ex-line-detail">解析：${esc(it.analysis)}</div>` : ''}
            ${(it.prereq && it.prereq.length) ? `<div class="ex-line-detail">先修：${it.prereq.map(p => esc((S.topics[p] || {}).name || p)).join('、')}</div>` : ''}
          </div>`;
        }).join('')}</div>

        <div class="ex-actions">
          <button class="btn" id="ex-again">再做一遍本卷</button>
          <button class="ex-btn-ghost" id="ex-export">导出成绩 JSON</button>
          <button class="ex-btn-ghost" onclick="window.print()">打印</button>
          <button class="ex-btn-ghost" id="ex-back">换一张卷</button>
        </div>
      </div>`;

    $('exam-report').innerHTML = html;
    $('ex-again').onclick = () => openPaper(S.meta.examId);
    $('ex-back').onclick = resetExam;
    $('ex-export').onclick = () => exportJSON(items);
    const selfBox = document.getElementById('ex-self');
    if (selfBox) selfBox.addEventListener('click', e => {
      const b = e.target.closest('button[data-tier]');
      if (!b) return;
      const row = b.closest('.ex-self-row');
      const id = row.getAttribute('data-item');
      const tier = SELF_TIERS.find(t => t[0] === b.dataset.tier);
      const it = items.find(x => x.itemId === id);
      const got = (it.score || 0) * tier[2];
      S.judge[id] = { ok: tier[0] === 'full', factor: tier[2], self: false, selfDone: true };
      row.querySelectorAll('button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      // 重算总分
      let sc = 0;
      items.forEach(x => { const jj = S.judge[x.itemId] || { factor: 0 }; sc += (x.score || 0) * (jj.factor || 0); });
      $('exam-report').querySelector('.ex-kpi b').textContent = Math.round(sc * 10) / 10;
    });
  }

  function exportJSON(items) {
    const data = {
      paper: S.meta.examId, title: S.paper.book + ' ' + S.paper.paper, kind: S.paper.kind,
      generated: new Date().toISOString(),
      total: S.paper.fullScore,
      items: items.map(it => ({
        no: it.no, itemId: it.itemId, type: it.type, score: it.score,
        topicIds: it.topicIds, userAnswer: S.answers[it.itemId] || '',
        correctAnswer: it.answer, ok: (S.judge[it.itemId] || {}).ok
      }))
    };
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
    a.download = `${S.meta.examId}-result.json`;
    a.click();
  }

  function resetExam() {
    stopTimer();
    S.paper = null; S.answers = {}; S.judge = {};
    $('exam-paper').style.display = 'none';
    $('exam-report').style.display = 'none';
    $('exam-setup').style.display = 'block';
  }

  /* ---------- 初始化 ---------- */
  let inited = false;
  window.initExamMode = async function () {
    if (inited) return;
    try {
      await loadIndex();
    } catch (e) {
      $('exam-setup').innerHTML = '<p class="ex-tip">试卷索引加载失败：' + esc(e.message) + '</p>';
      return;
    }
    inited = true;
    const subjSel = $('exam-subject'), edSel = $('exam-edition');
    const bk = $('exam-book'), pp = $('exam-paper-select');
    const subjects = S.index.subjects || { math: { count: S.index.count || 0, editions: S.index.editions || ['人教版'] } };
    let books = [];

    const fillPapers = () => {
      const b = books.find(x => x.book === bk.value);
      pp.innerHTML = (b ? b.papers : []).map(p => `<option value="${esc(p.examId)}">${esc(paperLabel(p))}</option>`).join('');
      $('exam-start').disabled = !pp.options.length;
    };
    const fillBooks = () => {
      const subj = subjSel ? subjSel.value : 'math';
      const ed = edSel ? edSel.value : null;
      books = booksOf(subj, ed);
      bk.innerHTML = books.map(b => `<option value="${esc(b.book)}">${esc(b.book)}（${b.papers.length} 卷）</option>`).join('');
      fillPapers();
    };
    const fillEditions = () => {
      const subj = subjSel ? subjSel.value : 'math';
      const info = subjects[subj] || { editions: ['人教版'] };
      edSel.innerHTML = info.editions.map(e => `<option value="${esc(e)}">${esc(e)}</option>`).join('');
      edSel.disabled = info.editions.length <= 1;
      fillBooks();
    };

    if (subjSel) {
      subjSel.innerHTML = Object.keys(subjects)
        .map(s => `<option value="${esc(s)}">${esc(SUBJECT_NAME[s] || s)}（${subjects[s].count} 卷）</option>`).join('');
      subjSel.disabled = Object.keys(subjects).length <= 1;
      subjSel.onchange = fillEditions;
    }
    if (edSel) edSel.onchange = fillBooks;
    bk.onchange = fillPapers;
    fillEditions();
    $('exam-start').onclick = () => openPaper(pp.value);
  };

  window.examReset = resetExam;
})();
