/* 学习档案存储：孩子档案 + 诊断记录（localStorage）。
 * 供 children/ 页面与 diagnose/ 页面共用；无后端，数据只在本机浏览器。
 */
(function () {
  'use strict';

  var KEY = 'k12kids.v1';
  var GRADES = ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级',
    '七年级', '八年级', '九年级', '高一', '高二', '高三'];
  var TEXTBOOKS = ['人教版', '北师大版', '苏教版', '沪教版', '外研社版', '统编版', '其他'];

  function blank() {
    return { profiles: [], currentId: null, records: [] };
  }

  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return blank();
      var s = JSON.parse(raw);
      if (!s || typeof s !== 'object') return blank();
      s.profiles = Array.isArray(s.profiles) ? s.profiles : [];
      s.records = Array.isArray(s.records) ? s.records : [];
      return s;
    } catch (e) {
      return blank();
    }
  }

  function save(state) {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (e) { /* 隐私模式或配额满：静默降级 */ }
  }

  function uid(prefix) {
    return prefix + '_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  }

  var CnmKids = {
    GRADES: GRADES,
    TEXTBOOKS: TEXTBOOKS,

    list: function () { return load().profiles.slice(); },

    add: function (data) {
      var s = load();
      var p = {
        id: uid('kid'),
        name: String(data.name || '').trim(),
        grade: data.grade || '',
        textbook: data.textbook || TEXTBOOKS[0],
        createdAt: Date.now()
      };
      s.profiles.push(p);
      if (!s.currentId) s.currentId = p.id;
      save(s);
      return p;
    },

    update: function (id, patch) {
      var s = load();
      s.profiles = s.profiles.map(function (p) {
        return p.id === id ? Object.assign({}, p, patch) : p;
      });
      save(s);
    },

    remove: function (id) {
      var s = load();
      s.profiles = s.profiles.filter(function (p) { return p.id !== id; });
      s.records = s.records.filter(function (r) { return r.childId !== id; });
      if (s.currentId === id) s.currentId = s.profiles.length ? s.profiles[0].id : null;
      save(s);
    },

    current: function () {
      var s = load();
      return s.profiles.filter(function (p) { return p.id === s.currentId; })[0] || null;
    },

    setCurrent: function (id) {
      var s = load();
      s.currentId = id;
      save(s);
    },

    /* 诊断页调用：把一次诊断结果挂到当前孩子（没有档案则记为匿名） */
    addRecord: function (rec) {
      var s = load();
      var item = {
        id: uid('rec'),
        childId: s.currentId || null,
        at: Date.now(),
        subject: rec.subject || '',
        target: rec.target || null,
        asked: rec.asked || 0,
        weak: rec.weak || []
      };
      s.records.push(item);
      if (s.records.length > 500) s.records = s.records.slice(-500);
      save(s);
      return item;
    },

    records: function (childId) {
      var s = load();
      return s.records
        .filter(function (r) { return !childId || r.childId === childId; })
        .sort(function (a, b) { return b.at - a.at; });
    },

    /* 未掌握知识点聚合：同一知识点在多次诊断中出现的次数 */
    weakSummary: function (childId) {
      var map = {};
      this.records(childId).forEach(function (r) {
        (r.weak || []).forEach(function (w) {
          var k = w.id || w.name;
          if (!map[k]) map[k] = { id: w.id, name: w.name, count: 0, last: 0, subjects: {} };
          map[k].count += 1;
          map[k].last = Math.max(map[k].last, r.at);
          map[k].subjects[r.subject] = (map[k].subjects[r.subject] || 0) + 1;
        });
      });
      return Object.keys(map).map(function (k) { return map[k]; })
        .sort(function (a, b) { return b.count - a.count || b.last - a.last; });
    },

    clear: function () { localStorage.removeItem(KEY); }
  };

  window.CnmKids = CnmKids;
})();
