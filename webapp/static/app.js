// 数学自适应诊断答题站 —— 前端（无框架，单文件）
const $ = (s, r = document) => r.querySelector(s);
const el = (tag, cls, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html !== undefined) n.innerHTML = html;
  return n;
};
let curPaper = null;
let lastAttempt = null;

const show = (id) => {
  for (const v of ["view-pick", "view-paper", "view-report"]) $("#" + v).hidden = v !== id;
  window.scrollTo({ top: 0 });
};

window.addEventListener("DOMContentLoaded", async () => {
  $("#homeLink").addEventListener("click", (e) => { e.preventDefault(); show("view-pick"); });
  $("#submitBtn").addEventListener("click", submit);
  $("#resetBtn").addEventListener("click", () => { if (curPaper) renderPaper(curPaper); });
  $("#practiceBtn").addEventListener("click", loadPractice);
  $("#printBtn").addEventListener("click", () => window.print());
  $("#backBtn").addEventListener("click", () => show("view-pick"));
  await loadPapers();
});

async function loadPapers() {
  const res = await fetch("/api/papers");
  const list = await res.json();
  const box = $("#papers");
  box.innerHTML = "";
  if (!list.length) { box.append(el("p", "hint", "还没有试卷数据。")); return; }
  const byBook = {};
  for (const p of list) (byBook[p.book] ||= []).push(p);
  for (const [book, ps] of Object.entries(byBook)) {
    const wrap = el("div");
    wrap.append(el("div", "sec", book));
    const grid = el("div", "cards");
    for (const p of ps) {
      const c = el("div", "card");
      c.append(el("h3", null, p.paper));
      c.append(el("div", "sub",
        `<span class="badge">${kindName(p.kind)}</span>${p.itemCount} 题 · ${p.fullScore} 分 · ${p.duration} 分钟`));
      if (p.scope && p.scope.length) c.append(el("div", "sub", "范围：" + p.scope.join("、")));
      c.addEventListener("click", () => openPaper(p.examId));
      grid.append(c);
    }
    wrap.append(grid);
    box.append(wrap);
  }
}

const kindName = (k) => ({ unit: "单元卷", midterm: "期中卷", final: "期末卷" }[k] || k);

async function openPaper(examId) {
  const res = await fetch("/api/paper?examId=" + encodeURIComponent(examId));
  if (!res.ok) { alert("卷子读取失败"); return; }
  curPaper = await res.json();
  renderPaper(curPaper);
  show("view-paper");
}

function renderPaper(p) {
  $("#paperTitle").textContent = `数学（人教版）${p.book}　${p.paper}`;
  $("#paperMeta").textContent = `时间：${p.duration} 分钟　　满分：${p.fullScore} 分`;
  $("#paperScope").textContent = p.scope.length ? "范围：" + p.scope.join("、") : "";
  const form = $("#answerForm");
  form.innerHTML = "";
  for (const sec of p.sections) {
    form.append(el("div", "sec", `${sec.title}（${sec.rule}）`));
    for (const it of sec.items) {
      const q = el("div", "q");
      const needBlank = (it.type === "choice" || it.type === "multi") && !/[（(]\s*[）)]\s*$/.test(it.stem);
      q.append(el("p", "stem", `${it.no}．${escapeHtml(it.stem)}${needBlank ? "（　　）" : ""}（${it.score} 分）`));

      if (it.type === "choice" || it.type === "multi") {
        const opts = el("div", "opts");
        for (const o of it.options) {
          const lab = el("label", null,
            `<input type="${it.type === "multi" ? "checkbox" : "radio"}" name="q${it.no}" value="${o.label}"> ` +
            `<b>${o.label}．</b>${escapeHtml(o.text)}`);
          opts.append(lab);
        }
        q.append(opts);
        if (it.type === "multi") q.append(el("div", "selfscore", "多项选择：全对才得分，请勾选全部正确项。"));
      } else if (it.type === "solve") {
        const box = el("div", "solvebox");
        box.append(el("textarea", null, ""));
        box.querySelector("textarea").placeholder = "写解题过程（提交后请对照参考答案自评得分）";
        box.querySelector("textarea").name = "q" + it.no;
        const sel = el("div", "selfscore", "自评得分：");
        const inp = el("input");
        inp.type = "number"; inp.min = "0"; inp.max = String(it.score); inp.step = "1";
        inp.value = "0"; inp.id = "self" + it.no; inp.style.width = "70px";
        sel.append(inp, document.createTextNode(` / ${it.score} 分（按评分标准给分）`));
        box.append(sel);
        q.append(box);
      } else {
        const inp = el("input");
        inp.type = "text"; inp.name = "q" + it.no; inp.placeholder = "作答";
        q.append(inp);
      }
      form.append(q);
    }
  }
}

function collect() {
  const answers = {}, selfScores = {};
  for (const sec of curPaper.sections) {
    for (const it of sec.items) {
      if (it.type === "choice") {
        const picked = $(`input[name="q${it.no}"]:checked`);
        answers[it.no] = picked ? picked.value : "";
      } else if (it.type === "multi") {
        const picked = [...document.querySelectorAll(`input[name="q${it.no}"]:checked`)].map(x => x.value);
        answers[it.no] = picked.sort().join("");
      } else if (it.type === "solve") {
        const ta = document.querySelector(`textarea[name="q${it.no}"]`);
        answers[it.no] = ta ? ta.value : "";
        const sc = $("#self" + it.no);
        selfScores[it.no] = sc ? Number(sc.value || 0) : 0;
      } else {
        const inp = document.querySelector(`input[name="q${it.no}"]`);
        answers[it.no] = inp ? inp.value : "";
      }
    }
  }
  return { answers, selfScores };
}

async function submit() {
  const { answers, selfScores } = collect();
  $("#submitBtn").disabled = true;
  try {
    const res = await fetch("/api/submit", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ examId: curPaper.examId, answers, selfScores })
    });
    const rep = await res.json();
    if (!res.ok) { alert(rep.error || "提交失败"); return; }
    lastAttempt = rep.attempt;
    renderReport(rep);
    show("view-report");
  } finally {
    $("#submitBtn").disabled = false;
  }
}

function renderReport(rep) {
  $("#scoreBox").innerHTML =
    `<div><span class="big">${rep.earned}</span><span class="dim"> / ${rep.fullScore} 分</span></div>
     <div class="dim">得分率 ${(rep.rate * 100).toFixed(1)}%</div>
     <div class="dim">${rep.book} · ${rep.paper} · 记录 #${rep.attempt}</div>
     <div class="dim">判定口径：得分率 ≥80% 掌握；60–80% 待巩固；&lt;60% 未掌握；未掌握且前置课时得分率 &lt;50% 判前置缺口</div>`;

  const boxes = { "前置缺口": 0, "未掌握": 0, "待巩固": 0, "掌握": 0 };
  for (const d of rep.diagnosis) boxes[d.verdict] = (boxes[d.verdict] || 0) + 1;
  const sum = el("div", "scorebox");
  sum.innerHTML = Object.entries(boxes).map(([k, v]) =>
    `<div><span class="v v-${k}">${k}</span> <span class="dim">${v} 个知识点</span></div>`).join("");

  const tbl = el("table", "diag");
  tbl.innerHTML = `<colgroup><col style="width:26%"><col style="width:13%"><col style="width:13%"><col style="width:48%"></colgroup>
    <thead><tr><th>知识点</th><th class="num">得分/满分</th><th>结论</th><th>错因与建议</th></tr></thead>`;
  const tb = el("tbody");
  for (const d of rep.diagnosis) {
    const tr = el("tr");
    const L = [];
    if (d.prereqGap.length)
      L.push(`<div class="misline"><span class="tag">前置缺口</span>${d.prereqGap.map(g => `${escapeHtml(g.name)}（${(g.rate * 100).toFixed(0)}%）`).join("、")}</div>`);
    if ((d.prereqUnknown || []).length)
      L.push(`<div class="misline"><span class="tag">前置未考</span>${d.prereqUnknown.map(g => escapeHtml(g.name)).join("、")}（建议先做 1 道基础题探探）</div>`);
    if (d.misconceptions.length)
      L.push(`<div class="misline"><span class="tag">可能错因</span>${d.misconceptions.map(escapeHtml).join("；")}</div>`);
    if (d.wrongItems.length)
      L.push(`<div class="misline"><span class="tag">错题</span>第 ${d.wrongItems.join("、")} 题</div>`);
    // 副标题去掉与知识点名重复的部分，只留「册 · 章」
    const sub = (d.chapter || "").replace(d.name, "").replace(/\s*·\s*$/, "").trim();
    tr.innerHTML = `<td>${escapeHtml(d.name)}<div class="mis">${escapeHtml(sub)}</div></td>
      <td class="num">${d.earned} / ${d.total}</td>
      <td><span class="v v-${d.verdict}">${d.verdict}</span><div class="mis">${(d.rate * 100).toFixed(1)}%</div></td>
      <td>${L.join("")}</td>`;
    tb.append(tr);
  }
  tbl.append(tb);

  const box = $("#report");
  box.innerHTML = "";
  box.append(sum, tbl);
  $("#practiceBox").innerHTML = "";
}

async function loadPractice() {
  if (!lastAttempt) return;
  const res = await fetch("/api/practice?attempt=" + lastAttempt);
  const data = await res.json();
  const box = $("#practiceBox");
  box.innerHTML = "";
  const wrap = el("div", "practice");
  wrap.append(el("h2", null, "补练清单"));
  wrap.append(el("p", "hint", "按诊断结论排序：先补「前置缺口」，再补「未掌握」，最后「待巩固」。每题来自题库同知识点题。"));
  if (!data.practice.length) wrap.append(el("p", "hint", "本次全部知识点已达掌握水平，无需补练。"));
  for (const g of data.practice) {
    wrap.append(el("h3", null, `${escapeHtml(g.name)}　<span class="v v-${g.verdict}">${g.verdict}</span>`));
    if (g.misconceptions.length)
      wrap.append(el("div", "mis", "<b>重点盯：</b>" + g.misconceptions.map(escapeHtml).join("；")));
    for (const it of g.items) {
      const pi = el("div", "pi");
      pi.innerHTML = `<div>${escapeHtml(it.prompt)}</div>` +
        (it.options.length ? `<div class="mis">${it.options.map(o => `${o.label}．${escapeHtml(o.text)}`).join("　")}</div>` : "") +
        `<div class="ans">答案：${escapeHtml(String(it.answer))}</div>` +
        (it.analysis ? `<div class="mis">解析：${escapeHtml(it.analysis)}</div>` : "");
      pi.append(el("div", "selfscore", `<span class="badge">${it.type}</span>${it.difficulty || ""}`));
      pi.querySelector(".selfscore").innerHTML = `<span class="badge">${it.type}</span>${it.difficulty || ""}`;
      pi.querySelector(".selfscore").append(document.createTextNode("　" + it.qid));
      wrap.append(pi);
    }
  }
  box.append(wrap);
}

function escapeHtml(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
