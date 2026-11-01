/* 学科 → 教材版本 级联选择器（诊断页用）
 *
 * 为什么单独成文件：
 * 1) 诊断页的学科下拉原来是写死的 18 个学科，同一学科的不同教材版本（人教版/北师大版/苏教版…）
 *    根本进不来；版本应当是学科下的二级分支，而不是独立的学科。
 * 2) 这段逻辑放在 index.html 的内联 <script> 里时，某些环境（如代理/净化层）会把内联脚本里的
 *    形如 <option …> 的标签串剥掉，导致下拉永远空白；放到外部 js 里就不受影响。
 * 3) 选项一律用 DOM API（new Option）构造，不拼 HTML 字符串，从根上避免同类问题。
 *
 * 对外接口（挂在 window.DiagSelector）：
 *   ready                     Promise，注册表加载完（失败也会 resolve）
 *   activeSubject()           当前真正取数的目录（版本目录优先，如 math-bsd）
 *   syncFromUrl(editionId)    按 URL 里的 ?subject= 把两个下拉设好，返回是否命中
 *   onSubjectChange()         学科下拉变化时调用：重填版本下拉
 *   bind(onReload)            绑定两个下拉的 change 事件，变化后回调 onReload
 */
(function () {
  'use strict';

  // 诊断页排障用：把后续内联脚本里的异常记到 window.__errs（生产无害）
  window.addEventListener('error', function (e) {
    window.__errs = window.__errs || [];
    window.__errs.push((e.message || 'error') + ' @' + (e.filename || '').split('/').pop() + ':' + e.lineno);
  });

  var REG = null;

  function $(id) { return document.getElementById(id); }

  function groupOf(editionId) {
    if (!REG) return null;
    var list = REG.subjects || [];
    for (var i = 0; i < list.length; i++) {
      var eds = list[i].editions || [];
      for (var j = 0; j < eds.length; j++) {
        if (eds[j].id === editionId) return list[i];
      }
    }
    return null;
  }

  function clear(sel) {
    while (sel.options.length) sel.remove(0);
  }

  function fillSubjects() {
    var sel = $('subject-select');
    if (!sel || !REG) return;
    var keep = sel.value;
    clear(sel);
    sel.add(new Option('请选择学科', ''));
    (REG.subjects || []).forEach(function (g) {
      var eds = g.editions || [];
      if (!eds.length) return;
      var label = g.name + (eds.length > 1 ? '（' + eds.length + ' 版）' : '');
      sel.add(new Option(label, eds[0].id));
    });
    if (keep) sel.value = keep;
  }

  function fillEditions(group, want) {
    var row = $('edition-row');
    var sel = $('edition-select');
    if (!row || !sel) return;
    var eds = (group && group.editions) || [];
    if (eds.length <= 1) {
      row.style.display = 'none';
      clear(sel);
      return;
    }
    row.style.display = '';
    clear(sel);
    eds.forEach(function (e) {
      sel.add(new Option((e.name || e.id) + '（' + e.topics + ' 点）', e.id));
    });
    sel.value = want || eds[0].id;
  }

  function activeSubject() {
    var ed = $('edition-select');
    var sub = $('subject-select');
    if (ed && ed.options.length && ed.value) return ed.value;
    return sub ? sub.value : '';
  }

  function onSubjectChange() {
    var sub = $('subject-select');
    if (!sub) return;
    var g = groupOf(sub.value);
    fillEditions(g, g && g.editions && g.editions[0] ? g.editions[0].id : null);
  }

  function syncFromUrl(editionId) {
    if (!editionId) return false;
    var sub = $('subject-select');
    if (!sub) return false;
    var g = groupOf(editionId);
    if (g && g.editions && g.editions.length) {
      var hit = false;
      for (var i = 0; i < sub.options.length; i++) {
        if (sub.options[i].value === g.editions[0].id) { sub.value = g.editions[0].id; hit = true; break; }
      }
      if (!hit) sub.value = g.editions[0].id;
      fillEditions(g, editionId);
      return true;
    }
    // 注册表里没有（老链接可能写的是学科 id）：退回老逻辑
    for (var k = 0; k < sub.options.length; k++) {
      if (sub.options[k].value === editionId) { sub.value = editionId; break; }
    }
    fillEditions(groupOf(editionId), null);
    return false;
  }

  function bind(onReload) {
    var sub = $('subject-select');
    var ed = $('edition-select');
    if (sub) sub.addEventListener('change', function () { onSubjectChange(); if (onReload) onReload(); });
    if (ed) ed.addEventListener('change', function () { if (onReload) onReload(); });
  }

  var ready = fetch('../data/subject-groups.json')
    .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function (reg) { REG = reg; fillSubjects(); return reg; })
    .catch(function () { return null; });

  window.DiagSelector = {
    ready: ready,
    activeSubject: activeSubject,
    syncFromUrl: syncFromUrl,
    onSubjectChange: onSubjectChange,
    bind: bind,
    groupOf: groupOf
  };
})();
