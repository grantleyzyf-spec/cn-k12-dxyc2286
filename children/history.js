/* 记录页：按孩子（或全部）汇总反复未掌握的知识点 + 诊断明细 */
(function () {
  'use strict';
  var K = window.CnmKids;
  var qs = new URLSearchParams(location.search);
  var childParam = qs.get('child');
  var kids = K.list();
  var cur = K.current();
  var childId = childParam || (cur ? cur.id : null);
  var child = kids.filter(function (k) { return k.id === childId; })[0] || null;

  var SUBJECTS = { math: '数学', english: '英语', chinese: '语文', physics: '物理', chemistry: '化学',
    biology: '生物', history: '历史', geography: '地理', science: '科学',
    'information-technology': '信息科技', japanese: '日语', russian: '俄语', german: '德语',
    french: '法语', spanish: '西班牙语', music: '音乐', art: '美术' };

  function fmt(ts) {
    var d = new Date(ts);
    var p = function (n) { return n < 10 ? '0' + n : '' + n; };
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
  }

  function cell(tr, text, cls) {
    var td = document.createElement('td');
    if (cls) td.className = cls;
    td.textContent = text == null ? '' : String(text);
    tr.appendChild(td);
  }

  document.getElementById('title').textContent = child ? (child.name + ' · 诊断记录') : '诊断记录（全部档案）';

  var weak = K.weakSummary(childId);
  var wb = document.getElementById('weak-body');
  document.getElementById('weak-count').textContent = String(weak.length);
  document.getElementById('weak-empty').hidden = weak.length > 0;
  weak.slice(0, 50).forEach(function (w) {
    var tr = document.createElement('tr');
    cell(tr, w.name);
    cell(tr, w.count, 'count');
    cell(tr, Object.keys(w.subjects).map(function (s) { return SUBJECTS[s] || s; }).join('、'));
    cell(tr, fmt(w.last), 'mono');
    wb.appendChild(tr);
  });

  var recs = K.records(childId);
  var rb = document.getElementById('rec-body');
  document.getElementById('rec-count').textContent = String(recs.length);
  document.getElementById('rec-empty').hidden = recs.length > 0;
  recs.slice(0, 100).forEach(function (r) {
    var tr = document.createElement('tr');
    cell(tr, fmt(r.at), 'mono');
    cell(tr, SUBJECTS[r.subject] || r.subject || '—');
    cell(tr, r.target ? r.target.name : '—');
    cell(tr, r.asked ? r.asked + ' 题' : '—');
    cell(tr, (r.weak || []).length + ' 个');
    rb.appendChild(tr);
  });

  // 学科过滤下拉：多档案时方便切换
  if (kids.length > 1) {
    var sel = document.createElement('select');
    var all = document.createElement('option');
    all.value = ''; all.textContent = '全部档案';
    sel.appendChild(all);
    kids.forEach(function (k) {
      var o = document.createElement('option');
      o.value = k.id; o.textContent = k.name;
      if (k.id === childId) o.selected = true;
      sel.appendChild(o);
    });
    sel.style.marginBottom = '16px';
    sel.onchange = function () {
      location.search = sel.value ? '?child=' + encodeURIComponent(sel.value) : '';
    };
    document.querySelector('.wrap').insertBefore(sel, document.querySelector('.panel'));
  }
})();
