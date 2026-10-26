/* 档案页：新增 / 编辑 / 删除 / 切换当前孩子 */
(function () {
  'use strict';
  var K = window.CnmKids;
  var list = document.getElementById('list');
  var empty = document.getElementById('empty');
  var count = document.getElementById('count');
  var form = document.getElementById('form');
  var nameIn = document.getElementById('f-name');
  var gradeSel = document.getElementById('f-grade');
  var bookSel = document.getElementById('f-textbook');
  var errBox = document.getElementById('f-error');
  var submitBtn = document.getElementById('f-submit');
  var cancelBtn = document.getElementById('f-cancel');
  var formTitle = document.getElementById('form-title');
  var editing = null;

  function fill(sel, items, placeholder) {
    sel.textContent = '';
    if (placeholder) {
      var o = document.createElement('option');
      o.value = ''; o.textContent = placeholder; sel.appendChild(o);
    }
    items.forEach(function (x) {
      var o = document.createElement('option');
      o.value = x; o.textContent = x; sel.appendChild(o);
    });
  }
  fill(gradeSel, K.GRADES, '请选择年级');
  fill(bookSel, K.TEXTBOOKS);

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function resetForm() {
    editing = null;
    nameIn.value = '';
    gradeSel.value = '';
    bookSel.value = K.TEXTBOOKS[0];
    formTitle.textContent = '添加孩子';
    submitBtn.textContent = '添加孩子';
    cancelBtn.hidden = true;
    errBox.hidden = true;
  }

  function render() {
    var kids = K.list();
    var cur = K.current();
    list.textContent = '';
    count.textContent = String(kids.length);
    empty.hidden = kids.length > 0;

    kids.forEach(function (k) {
      var li = el('li');
      var who = el('div', 'who');
      who.appendChild(el('strong', null, k.name));
      who.appendChild(el('span', 'tag', k.grade || '未填年级'));
      who.appendChild(el('span', 'tag', k.textbook || ''));
      if (cur && cur.id === k.id) who.appendChild(el('span', 'tag current', '当前'));

      var ops = el('div', 'ops');
      var recs = K.records(k.id).length;
      var a = el('a', 'tag', recs + ' 条记录');
      a.href = 'history.html?child=' + encodeURIComponent(k.id);
      ops.appendChild(a);

      if (!cur || cur.id !== k.id) {
        var use = el('button', 'ghost', '设为当前');
        use.onclick = function () { K.setCurrent(k.id); render(); };
        ops.appendChild(use);
      }
      var edit = el('button', 'ghost', '编辑');
      edit.onclick = function () {
        editing = k.id;
        nameIn.value = k.name;
        gradeSel.value = k.grade || '';
        bookSel.value = k.textbook || K.TEXTBOOKS[0];
        formTitle.textContent = '修改「' + k.name + '」';
        submitBtn.textContent = '保存修改';
        cancelBtn.hidden = false;
        nameIn.focus();
      };
      ops.appendChild(edit);

      var del = el('button', 'danger', '删除');
      del.onclick = function () {
        if (!confirm('删除「' + k.name + '」及其诊断记录？此操作不可撤销。')) return;
        K.remove(k.id);
        if (editing === k.id) resetForm();
        render();
      };
      ops.appendChild(del);

      li.appendChild(who);
      li.appendChild(ops);
      list.appendChild(li);
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = nameIn.value.trim();
    if (!name) { errBox.textContent = '请填写称呼'; errBox.hidden = false; return; }
    if (!gradeSel.value) { errBox.textContent = '请选择年级'; errBox.hidden = false; return; }
    var dup = K.list().filter(function (p) {
      return p.name === name && p.id !== editing;
    });
    if (dup.length) { errBox.textContent = '同名的档案已存在，换个称呼或先编辑它'; errBox.hidden = false; return; }
    if (editing) {
      K.update(editing, { name: name, grade: gradeSel.value, textbook: bookSel.value });
    } else {
      K.add({ name: name, grade: gradeSel.value, textbook: bookSel.value });
    }
    resetForm();
    render();
  });

  cancelBtn.addEventListener('click', function () { resetForm(); render(); });

  resetForm();
  render();
})();
