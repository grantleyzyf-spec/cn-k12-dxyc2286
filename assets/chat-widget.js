/* chat-widget.js — xueketupu.com 站内客服挂件（零依赖）
 * 后端：POST /api/chat（SSE）；不可用时自动降级为内置 FAQ。
 */
(function () {
  if (window.__xktChatLoaded) return;
  window.__xktChatLoaded = true;

  var EMAIL = "grantleyzyf@gmail.com";
  var API = "/api/chat";
  var MAX_TURNS = 12;

  var FAQ = [
    ["这个网站是做什么的", "xueketupu.com 是中国 K-12 全学科知识图谱：把知识点、先修关系、诊断题和课标条目连成一张网，用来定位孩子「卡在哪一步」。全部免费，不用登录。"],
    ["怎么用", "三步：① 在 /explore/ 按学科找到当前知识点；② 到 /diagnose/ 选它，系统沿先修关系往回追，列出最可能拖后腿的「根因」并出题；③ 用 /learn/ 跟 /topics/ 补讲。"],
    ["收费吗/要注册吗", "不收费，也不需要注册登录，浏览器打开就能用。本站是个人维护的非经营性网站（渝ICP备2026027764号-1）。"],
    ["先修关系是什么", "先修关系=学 B 之前必须先掌握 A 的依赖关系。本站区分「硬先修」和「软先修」，诊断会优先追硬先修。"],
    ["有哪些学科", "覆盖小学到高中多个学科版本（人教、北师大、沪教、译林等），可按学科和年级在 /topics/ 里筛。"],
    ["数据从哪来", "知识点与课标条目按公开教材和课程标准整理，题目为自建；每条知识点附课标原文引用。"],
    ["怎么联系你们", "邮箱 " + EMAIL + "，或加 QQ 群 1045844951；合作请看 /sponsor/。"],
    ["能帮我解题吗", "站内不提供人工解题。建议用 /diagnose/ 定位薄弱点后自己做题，解析在知识点页里。"]
  ];

  var state = { msgs: [], turns: 0, mode: null, busy: false, pending: null, cfg: null };

  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }

  function linkify(text) {
    var frag = document.createDocumentFragment();
    var re = /(\/topics\/[A-Za-z0-9_\-]+\/|\/(explore|diagnose|learn|topics|teacher|sponsor|contact|novel)\/|https?:\/\/[^\s，。)]+|[\w.\-]+@[\w.\-]+\.\w+)/g;
    var last = 0, m;
    while ((m = re.exec(text))) {
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      var t = m[0], a = document.createElement("a");
      if (t.indexOf("@") > -1 && t.indexOf("http") !== 0) a.href = "mailto:" + t;
      else if (t.indexOf("http") === 0) a.href = t;
      else a.href = t;
      a.textContent = t;
      if (t.indexOf("http") === 0) { a.target = "_blank"; a.rel = "noopener"; }
      frag.appendChild(a);
      last = m.index + t.length;
    }
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    return frag;
  }

  // ---- UI ----
  var btn = el("button");
  btn.id = "xkt-chat-btn";
  btn.setAttribute("aria-label", "站内客服");
  btn.innerHTML =
    '<svg class="ico" viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">' +
    '<path d="M4 5.6A2.6 2.6 0 0 1 6.6 3h10.8A2.6 2.6 0 0 1 20 5.6v6.9a2.6 2.6 0 0 1-2.6 2.6H9.4l-4.1 3.3a.6.6 0 0 1-1.3-.5V5.6Z" fill="currentColor"/>' +
    '<circle cx="9" cy="9" r="1" fill="#0f766e"/><circle cx="12" cy="9" r="1" fill="#0f766e"/><circle cx="15" cy="9" r="1" fill="#0f766e"/></svg>' +
    "客服";

  var panel = el("div");
  panel.id = "xkt-chat-panel";
  panel.setAttribute("role", "dialog");
  panel.innerHTML =
    '<div class="xkt-hd"><div><b>知识图谱小助手</b><small>问用法 / 找知识点 / 看数据</small></div>' +
    '<button class="xkt-x" aria-label="关闭">×</button></div>' +
    '<div class="xkt-body"></div>' +
    '<div class="xkt-chips"></div>' +
    '<div class="xkt-ft"><textarea rows="1" placeholder="问用法 / 找知识点 / 看数据"></textarea>' +
    '<button>发送</button></div>' +
    '<div class="xkt-note">人工：' + EMAIL + " · 每日有条数上限</div>";

  var body = panel.querySelector(".xkt-body");
  var chips = panel.querySelector(".xkt-chips");
  var ta = panel.querySelector("textarea");
  var sendBtn = panel.querySelector(".xkt-ft button");

  document.addEventListener("DOMContentLoaded", mount);
  if (document.readyState !== "loading") mount();
  function mount() {
    if (document.getElementById("xkt-chat-btn")) return;
    document.body.appendChild(btn);
    document.body.appendChild(panel);
  }

  function addMsg(role, text) {
    var m = el("div", "xkt-msg " + role);
    if (role === "bot") m.appendChild(linkify(String(text).replace(/^\s+/, ""))); else m.textContent = text;
    body.appendChild(m);
    body.scrollTop = body.scrollHeight;
    return m;
  }

  function addTools(text) {
    var t = el("div", "xkt-tools");

    var r = el("button", null, "这个回答不对");
    r.onclick = function () {
      fetch(API + "/report", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: lastUser(), a: text })
      }).catch(function () {});
      r.textContent = "已记录，谢谢";
      r.disabled = true;
    };
    t.appendChild(r);

    var c = el("button", null, "复制对话");
    c.onclick = function () {
      var txt = state.msgs.map(function (x) {
        return (x.role === "user" ? "我：" : "助手：") + x.content;
      }).join("\n");
      var done = function () { c.textContent = "已复制"; setTimeout(function () { c.textContent = "复制对话"; }, 1500); };
      if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, done);
      else done();
    };
    t.appendChild(c);

    if (state.cfg && state.cfg.kf) {
      var a = el("a", null, "微信客服");
      a.href = state.cfg.kf;
      a.target = "_blank";
      a.rel = "noopener";
      t.appendChild(a);
    } else if (state.cfg && state.cfg.qq) {
      var q = el("button", null, "群号 " + state.cfg.qq);
      q.onclick = function () {
        if (navigator.clipboard) navigator.clipboard.writeText(state.cfg.qq);
        q.textContent = "已复制群号";
        setTimeout(function () { q.textContent = "群号 " + state.cfg.qq; }, 1500);
      };
      t.appendChild(q);
    }

    var m = el("a", null, "转人工");
    m.href = "mailto:" + ((state.cfg && state.cfg.email) || EMAIL) + "?subject=" + encodeURIComponent("站点咨询") +
      "&body=" + encodeURIComponent("我的问题：\n\n（对话）\n" + state.msgs.map(function (x) {
        return (x.role === "user" ? "我：" : "助手：") + x.content;
      }).join("\n"));
    t.appendChild(m);

    body.appendChild(t);
    body.scrollTop = body.scrollHeight;
  }

  function lastUser() {
    for (var i = state.msgs.length - 1; i >= 0; i--) if (state.msgs[i].role === "user") return state.msgs[i].content;
    return "";
  }

  function loadConfig() {
    fetch(API + "/config", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        if (!j || !j.ok) return;
        state.cfg = j;
        var note = panel.querySelector(".xkt-note");
        if (note) {
          note.innerHTML = j.kf
            ? '人工客服：<a href="' + j.kf + '" target="_blank" rel="noopener">微信</a> · ' +
              (j.email || EMAIL) + " · 每日有条数上限"
            : "人工：" + (j.email || EMAIL) + " · 每日有条数上限";
        }
      })
      .catch(function () {});
  }

  function renderChips() {
    chips.innerHTML = "";
    ["这个网站是做什么的", "孩子数学卡住了怎么用", "先修关系怎么理解", "收费吗"].forEach(function (q) {
      var b = el("button", null, q);
      b.onclick = function () { ask(q); };
      chips.appendChild(b);
    });
  }

  function openPanel() {
    panel.classList.add("open");
    btn.style.display = "none";
    if (!state.msgs.length) {
      addMsg("bot", "你好，我是本站的小助手。\n可以问我：网站怎么用、某个知识点在哪个学科/年级、数据从哪来、是否收费。");
      renderChips();
      checkHealth();
      loadConfig();
    }
    setTimeout(function () { ta.focus(); }, 60);
  }

  function closePanel() { panel.classList.remove("open"); btn.style.display = ""; }

  btn.onclick = function () { panel.classList.contains("open") ? closePanel() : openPanel(); };
  panel.querySelector(".xkt-x").onclick = closePanel;

  function checkHealth() {
    fetch(API + "/health", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { state.mode = j && j.ok ? (j.mode || "llm") : "offline"; })
      .catch(function () { state.mode = "offline"; });
  }

  // ---- 发送 ----
  function ask(q) {
    if (state.busy) return;
    q = (q || ta.value || "").trim();
    if (!q) return;
    ta.value = "";
    state.turns++;
    state.msgs.push({ role: "user", content: q });
    addMsg("user", q);

    if (state.turns > MAX_TURNS) {
      addMsg("bot", "这个会话的问题有点多了（上限 " + MAX_TURNS + " 条）。\n可以换个话题重开，或直接发邮件 " + EMAIL + "。");
      return;
    }

    var bubble = addMsg("bot", "");
    bubble.textContent = "…";

    if (state.mode === "offline") {
      bubble.textContent = "";
      bubble.appendChild(linkify(faqAnswer(q)));
      state.msgs.push({ role: "assistant", content: bubble.textContent });
      addTools(bubble.textContent);
      return;
    }

    state.busy = true;
    sendBtn.disabled = true;
    var acc = "";

    fetch(API, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: state.msgs })
    }).then(function (r) {
      if (!r.ok || !r.body) throw new Error("http " + r.status);
      var rd = r.body.getReader(), dec = new TextDecoder(), buf = "";
      function pump() {
        return rd.read().then(function (res) {
          if (res.done) return;
          buf += dec.decode(res.value, { stream: true });
          var parts = buf.split("\n\n");
          buf = parts.pop();
          parts.forEach(function (p) {
            if (p.indexOf("data:") !== 0) return;
            var raw = p.slice(5).trim();
            if (raw === "[DONE]") return;
            var j;
            try { j = JSON.parse(raw); } catch (e) { return; }
            if (j.d) {
              acc += j.d;
              acc = acc.replace(/\n{3,}$/, "\n");
              bubble.textContent = "";
              bubble.appendChild(linkify(acc));
              body.scrollTop = body.scrollHeight;
            }
            if (j.end) state.mode = j.mode || state.mode;
          });
          return pump();
        });
      }
      return pump();
    }).then(function () {
      state.msgs.push({ role: "assistant", content: acc });
      if (acc) addTools(acc);
    }).catch(function () {
      state.mode = "offline";
      bubble.textContent = "";
      bubble.appendChild(linkify(faqAnswer(q)));
      state.msgs.push({ role: "assistant", content: bubble.textContent });
    }).then(function () {
      state.busy = false;
      sendBtn.disabled = false;
    });
  }

  function faqAnswer(q) {
    var best = null, bestScore = 0;
    FAQ.forEach(function (pair) {
      var s = 0;
      for (var i = 0; i < q.length - 1; i++) if (pair[0].indexOf(q.substr(i, 2)) > -1) s++;
      if (s > bestScore) { bestScore = s; best = pair; }
    });
    if (best && bestScore >= 2) return best[1];
    return "当前是在线客服的离线模式（后端未启动）。\n常见问题可以看 /contact/，或发邮件 " + EMAIL + "。";
  }

  sendBtn.onclick = function () { ask(); };
  ta.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); }
  });
})();
