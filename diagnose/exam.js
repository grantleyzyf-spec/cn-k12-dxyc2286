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
  // 根式：√3 / 2√6 / √(x+1) → 带横线的规范根号（与印刷体一致）
  const radify = (s) => String(s == null ? '' : s).replace(
    /√\s*(?:[\(（]([^()（）]{1,30})[\)）]|([0-9A-Za-z\u4e00-\u9fa5π·×°′″²³\/．.]{1,8}))/g,
    (m, g1, g2) => '<span class="rad"><span class="sq">√</span><span class="rd">' + esc((g1 || g2 || '').trim()) + '</span></span>');
  const rich = (s) => radify(s);
  // 渲染后统一把文本节点里的根式换成带横线的规范根号（不改 29 处 esc 调用点，也不误改属性）
  const RAD_RE = /√\s*(?:[\(（]([^()（）]{1,30})[\)）]|([0-9A-Za-z\u4e00-\u9fa5π·×°′″²³\/．.]{1,8}))/g;
  const FRAC_RE = /(^|[^\d\/√])((?:\d+(?:\.\d+)?[²³]?|π|[a-zA-Z]|\([^()（）]{1,14}\)))\s*\/\s*((?:\d+(?:\.\d+)?[²³]?|π|[a-zA-Z]|\([^()（）]{1,14}\)))(?![\d\/])/g;
  function radifyDom(root) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: (n) => (n.nodeValue && (n.nodeValue.indexOf('√') >= 0 || n.nodeValue.indexOf('/') >= 0) && !n.parentElement.closest('.rad,.frac'))
        ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      let html = node.nodeValue;
      html = html.replace(RAD_RE, (m, g1, g2) => '<span class="rad"><span class="sq">√</span><span class="rd">'
        + (g1 || g2 || '').trim() + '</span></span>');
      html = html.replace(FRAC_RE, (m, pre, a, b) => {
        const aNum = /^[\dπ]/.test(a), bNum = /^[\dπ]/.test(b);
        if (!aNum && !bNum) return m;
        if (a.length === 1 && b.length === 1 && /^[a-zA-Z]$/.test(a) && /^[a-zA-Z]$/.test(b)) return m;
        return pre + '<span class="frac"><span class="num">' + a + '</span><span class="den">' + b + '</span></span>';
      });
      if (html === node.nodeValue) return;
      const tmp = document.createElement('span');
      tmp.innerHTML = html;
      node.parentNode.replaceChild(tmp, node);
      while (tmp.firstChild) tmp.parentNode.insertBefore(tmp.firstChild, tmp);
      tmp.parentNode.removeChild(tmp);
    });
  }
  let radifyBusy = false;
  const MO = new MutationObserver((muts) => {
    if (radifyBusy) return;
    radifyBusy = true;
    try {
      muts.forEach((mu) => mu.addedNodes && mu.addedNodes.forEach((n) => {
        if (n.nodeType === 1) radifyDom(n);
        else if (n.nodeType === 3 && n.parentElement) radifyDom(n.parentElement);
      }));
    } finally { radifyBusy = false; }
  });
  MO.observe(document.body, { childList: true, subtree: true });
  window.addEventListener('load', () => radifyDom(document.body));

  window.examReset = resetExam;
})();
