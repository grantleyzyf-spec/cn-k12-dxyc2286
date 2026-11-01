/* 诊断页主逻辑（原为 index.html 内联脚本）
 * 单独成文件的原因：部分环境会把内联脚本里的 HTML 片段剥掉 / 或直接禁用内联脚本，
 * 导致下拉永远空白、题面不渲染。外置后行为稳定，也便于 node --check。
 */
// 数据加载
        let topicsData = {};
        let questionsData = {};
        let dependenciesData = {};

        // 状态
        let currentSubject = new URLSearchParams(location.search).get('subject') || '';
        let targetTopic = null;
        let questionQueue = [];
        let currentQuestionIndex = 0;
        let answers = {};
        let weakTopics = [];
        let askedCount = 0;      // 实际问过的题数
        let correctCount = 0;    // 答对题数
        let phase = 'ask';       // ask=待作答；feedback=已出反馈待下一题

        // 学科名称映射
        const subjectNames = {
            'math': '数学', 'chinese': '语文', 'english': '英语',
            'physics': '物理', 'chemistry': '化学', 'biology': '生物',
            'history': '历史', 'geography': '地理', 'science': '科学',
            'information-technology': '信息科技', 'japanese': '日语',
            'russian': '俄语', 'german': '德语', 'french': '法语',
            'spanish': '西班牙语', 'music': '音乐', 'art': '美术', 'mental-health': '心理健康'
        };

        // 学科 → 版本：逻辑在外部 diag-selector.js（内联脚本里的 <option …> 串在某些环境下会被剥掉）
        function activeSubject() {
            if (window.DiagSelector) {
                var v = window.DiagSelector.activeSubject();
                if (v) return v;
            }
            var sel = document.getElementById('subject-select');
            return sel ? sel.value : '';
        }

        // 获取学科的topics文件列表
        function getTopicsFiles(subject) {
            // v2：topics.json 已含全部学段（grade 拆分文件仅作归档，不再叠加，避免重复）
            return ['topics.json'];
        }

        // 获取学科的dependencies文件列表
        function getDepsFiles(subject) {
            return ['dependencies.json'];
        }

        // 获取学科的questions文件列表
        function getQuestionsFiles(subject) {
            return ['questions.json'];
        }

        // 初始化：学科/版本下拉的联动交给 diag-selector.js，切换后重载知识点
        if (window.DiagSelector) window.DiagSelector.bind(function () { loadTopics(); });
        document.getElementById('start-btn').addEventListener('click', startDiagnosis);
        document.getElementById('next-btn').addEventListener('click', nextQuestion);

        // URL 参数 ?topic= 预选知识点（从知识图谱「诊断这个知识点」进来）
        const topicParam = new URLSearchParams(location.search).get('topic') || '';

        // URL 参数 ?subject= 初始化（学科下拉同步并加载知识点）
        (function initSubjectFromUrl() {
            const sel = document.getElementById('subject-select');
            const apply = function () {
                if (!currentSubject) return;
                if (window.DiagSelector && window.DiagSelector.syncFromUrl(currentSubject)) {
                    loadTopics();
                    return;
                }
                if (sel && [...sel.options].some(o => o.value === currentSubject)) {
                    sel.value = currentSubject;
                    loadTopics();
                }
            };
            if (window.DiagSelector) {
                window.DiagSelector.ready.then(apply);
            } else {
                apply();
            }
        })();

        // 加载知识点列表
        async function loadTopics() {
            const subject = activeSubject();
            if (!subject) return;

            currentSubject = subject;
            const topicSelect = document.getElementById('topic-select');
            topicSelect.replaceChildren(new Option('加载中...', ''));
            topicSelect.disabled = true;

            try {
                // 加载所有topics文件
                const files = getTopicsFiles(subject);
                let allTopics = [];
                for (const file of files) {
                    const response = await fetch(`../data/${subject}/${file}`);
                    if (response.ok) {
                        const data = await response.json();
                        allTopics = allTopics.concat(data);
                    }
                }
                topicsData = Array.from(new Map(allTopics.map(t => [t.id, t])).values());
                
                topicSelect.replaceChildren(new Option('请选择目标知识点', ''));
                topicsData.sort((a, b) => (a.grade || 0) - (b.grade || 0));
                topicsData.forEach(topic => {
                    const option = document.createElement('option');
                    option.value = topic.id;
                    option.textContent = `${topic.name} (${bookLabel(topic)})`;
                    topicSelect.appendChild(option);
                });
                topicSelect.disabled = false;
                
                topicSelect.addEventListener('change', () => {
                    document.getElementById('start-btn').disabled = !topicSelect.value;
                });

                // 从知识图谱「诊断这个知识点」进来时预选该点
                if (topicParam && [...topicSelect.options].some(o => o.value === topicParam)) {
                    topicSelect.value = topicParam;
                    document.getElementById('start-btn').disabled = false;
                }
            } catch (e) {
                topicSelect.replaceChildren(new Option('数据加载失败', ''));
                console.error('加载知识点失败:', e);
            }
        }

        // 获取年级文本
        function bookLabel(topic) {
            const head = ((topic && topic.chapter) || '').split(' ')[0].replace('各单元', '');
            const m = head.match(/^(选择性必修|必修)(第?[一二三四五六七八九十]册|上册|下册|中册)$/);
            if (m) {
                const tail = m[2].replace('册', '')
                    .replace('第一', '一').replace('第二', '二').replace('第三', '三')
                    .replace('第四', '四').replace('第五', '五');
                return (m[1] === '选择性必修' ? '选必' : '必修') + tail;
            }
            return head || getGradeText(topic && topic.grade);
        }

        function getGradeText(grade) {
            // 1–9 年级用「X年级」；10 以上是高中册次，按册名显示
            const CN = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
            const g = Number(grade);
            if (g <= 9) return (CN[g] || g) + '年级';
            return '高中';
        }

        // 开始诊断
        async function startDiagnosis() {
            const topicId = document.getElementById('topic-select').value;
            targetTopic = topicsData.find(t => t.id === topicId);
            
            if (!targetTopic) return;

            // 加载题库和依赖关系（支持多文件）
            try {
                const depsFiles = getDepsFiles(currentSubject);
                const qFiles = getQuestionsFiles(currentSubject);
                
                let allDeps = [];
                for (const file of depsFiles) {
                    const response = await fetch(`../data/${currentSubject}/${file}`);
                    if (response.ok) {
                        const data = await response.json();
                        allDeps = allDeps.concat(data);
                    }
                }
                dependenciesData = Array.from(new Map(allDeps.map(d => [`${d.from}->${d.to}:${d.type}`, d])).values());
                
                let allQuestions = [];
                for (const file of qFiles) {
                    const response = await fetch(`../data/${currentSubject}/${file}`);
                    if (response.ok) {
                        const data = await response.json();
                        allQuestions = allQuestions.concat(data);
                    }
                }
                questionsData = Array.from(new Map(allQuestions.map(q => [q.id, q])).values());
            } catch (e) {
                alert('数据加载失败，请刷新重试');
                return;
            }

            // 构建诊断路径（从目标知识点向上追溯先修）
            questionQueue = buildDiagnosisPath(targetTopic);
            currentQuestionIndex = 0;
            answers = {};
            weakTopics = [];
            askedCount = 0;
            correctCount = 0;
            phase = 'ask';

            document.getElementById('setup-area').style.display = 'none';
            document.getElementById('question-area').style.display = 'block';
            document.getElementById('progress-total').textContent = `共 ${questionQueue.length} 题`;
            
            showQuestion();
        }

        // 每知识点最多问几题（题库已补到 5 题/点，答错即停）
        const MAX_PER_TOPIC = 5;
        const DIFF_RANK = { basic: 0, standard: 1, hard: 2 };

        // 构建诊断路径：先修在前；每个知识点带上它的全部题目（按难度升序，最多 5 题）
        function buildDiagnosisPath(topic) {
            const path = [];
            const visited = new Set();

            function traverse(t) {
                if (visited.has(t.id)) return;
                visited.add(t.id);

                // 先递归处理先修知识点
                const deps = dependenciesData.filter(d => d.to === t.id && d.type === 'hard');
                deps.forEach(dep => {
                    const prereq = topicsData.find(tp => tp.id === dep.from);
                    if (prereq) traverse(prereq);
                });

                // 当前知识点的题目：难度升序，最多 MAX_PER_TOPIC 题
                const qs = questionsData
                    .filter(q => q.topicId === t.id)
                    .sort((a, b) => (DIFF_RANK[a.difficulty] ?? 1) - (DIFF_RANK[b.difficulty] ?? 1));
                if (qs.length > 0) {
                    path.push({ topic: t, questions: qs.slice(0, MAX_PER_TOPIC), idx: 0, failed: false });
                }
            }

            traverse(topic);
            return path;
        }

        function currentStep() { return questionQueue[currentQuestionIndex] || null; }
        function currentQ() { const st = currentStep(); return st ? st.questions[st.idx] : null; }

        // 显示题目：choice→选项；fill/numeric→输入框；short-answer→文本域＋自评
        function showQuestion() {
            if (currentQuestionIndex >= questionQueue.length) {
                showResult();
                return;
            }
            const step = currentStep();
            const q = currentQ();
            if (!q) { currentQuestionIndex++; showQuestion(); return; }

            phase = 'ask';
            document.getElementById('question-text').textContent = (q.prompt || q.question);
            const typeName = { choice: '选择', fill: '填空', numeric: '数值计算', 'short-answer': '简答' }[q.type] || '选择';
            document.getElementById('progress-text').textContent =
                `${step.topic.name} · 第 ${step.idx + 1}/${step.questions.length} 题（${typeName}）`;
            document.getElementById('progress-total').textContent =
                `进度 ${currentQuestionIndex + 1}/${questionQueue.length} 知识点`;
            document.getElementById('progress-fill').style.width =
                `${(currentQuestionIndex / questionQueue.length) * 100}%`;

            const optionsDiv = document.getElementById('options');
            const inputArea = document.getElementById('answer-input');
            const feedback = document.getElementById('feedback');
            const btn = document.getElementById('next-btn');
            optionsDiv.innerHTML = ''; inputArea.innerHTML = ''; feedback.innerHTML = '';
            btn.disabled = false; btn.textContent = '提交答案';
            answers[currentQuestionIndex] = undefined;

            const optsOf = (q.choices && q.choices.length) ? q.choices : (q.options || []);
            if (q.type === 'choice' && optsOf.length > 0) {
                optsOf.forEach(opt => {
                    const div = document.createElement('div');
                    div.className = 'option';
                    div.textContent = `${opt.label}. ${opt.text}`;
                    div.onclick = () => selectOption(div, opt.label);
                    optionsDiv.appendChild(div);
                });
            } else if (q.type === 'numeric' || q.type === 'fill') {
                const inp = document.createElement('input');
                inp.id = 'answer-box';
                inp.type = 'text';
                inp.autocomplete = 'off';
                inp.placeholder = q.type === 'numeric' ? '输入计算结果（只填数字，如 12 或 3/4）' : '输入你的答案';
                inp.onkeydown = (e) => { if (e.key === 'Enter') nextQuestion(); };
                inputArea.appendChild(inp);
            } else {
                const ta = document.createElement('textarea');
                ta.id = 'answer-box';
                ta.rows = 3;
                ta.placeholder = '写下你的答案要点（可分行）';
                inputArea.appendChild(ta);
            }
        }

        // 选择选项
        function selectOption(element, label) {
            if (phase !== 'ask') return;
            document.querySelectorAll('.option').forEach(o => o.classList.remove('selected'));
            element.classList.add('selected');
            answers[currentQuestionIndex] = label;
        }

        // 全角→半角、去空白、统一大小写，便于机判
        function normAns(v) {
            return (v || '').replace(/[\uFF01-\uFF5E]/g, c => String.fromCharCode(c.charCodeAt(0) - 0xFEE0))
                .replace(/[，、]/g, ',').replace(/。/g, '.').replace(/\s+/g, '').toLowerCase();
        }

        // 数值解析：支持小数、分数、正负号
        function parseNum(v) {
            const t = normAns(v).replace(/[%％]/g, '');
            if (/^-?\d+(\.\d+)?$/.test(t)) return parseFloat(t);
            const m = t.match(/^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/);
            if (m && parseFloat(m[2]) !== 0) return parseFloat(m[1]) / parseFloat(m[2]);
            return NaN;
        }

        function near(a, b) { return Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(b)); }

        function getUserAnswer() {
            if (currentQ().type === 'choice') return answers[currentQuestionIndex];
            const box = document.getElementById('answer-box');
            return box ? box.value : '';
        }

        // 简答题「要点关键词」初步判定：学生作答与每个得分要点的中文二元组覆盖率
        function matchKeypoints(q, ans) {
          const kps = q.keypoints || [];
          if (!kps.length) return null;
          const big = (t) => {
            const c = (t || '').replace(/[^\u4e00-\u9fa5]/g, '');
            const s = new Set();
            for (let i = 0; i < c.length - 1; i++) s.add(c.slice(i, i + 2));
            return s;
          };
          const A = big(ans);
          let hit = 0;
          kps.forEach(k => {
            const K = big(k);
            if (!K.size) return;
            let n = 0; K.forEach(g => { if (A.has(g)) n++; });
            if (n / K.size >= 0.34) hit++;
          });
          return { hit: hit, total: kps.length, ratio: hit / kps.length };
        }

        function gradeCurrent() {
            const q = currentQ();
            const u = getUserAnswer();
            if (q.type === 'choice') return { ok: u === q.answer, empty: !u };
            if (q.type === 'numeric') {
                const un = parseNum(u);
                return { ok: !isNaN(un) && near(un, parseFloat(q.answer)), empty: !normAns(u) };
            }
            const a = normAns(q.answer), uu = normAns(u);
            if (uu === a) return { ok: true };
            const na = parseNum(a), nu = parseNum(uu);
            return { ok: (!isNaN(na) && !isNaN(nu) && near(nu, na)), empty: !uu };
        }

        function renderFeedback(ok, q) {
            const fb = document.getElementById('feedback');
            const head = ok ? '<span class="fb-ok">✅ 答对了</span>' : '<span class="fb-no">❌ 答错了</span>';
            const ansText = q.type === 'short-answer'
                ? q.answer.split('；').filter(Boolean).map(x => `<li>${x}</li>`).join('')
                : (q.type === 'choice'
                    ? `${q.answer}. ${((q.choices && q.choices.length ? q.choices : (q.options || [])).find(o => o.label === q.answer) || {}).text || ''}`
                    : q.answer);
            const ansBlock = q.type === 'short-answer'
                ? `<div class="fb-box"><strong>参考答案要点：</strong><ul class="fb-key">${ansText}</ul></div>`
                : `<div class="fb-box"><strong>正确答案：</strong>${ansText}</div>`;
            fb.innerHTML = head + ansBlock + `<div class="fb-box"><strong>解析：</strong>${q.explanation || ''}</div>`;
        }

        // 提交 / 下一题
        function nextQuestion() {
            const step = currentStep();
            if (!step) return;
            const btn = document.getElementById('next-btn');

            // 已出反馈：推进到下一题 / 下一个知识点
            if (phase === 'feedback') {
                if (step.idx >= step.questions.length) currentQuestionIndex++;
                showQuestion();
                return;
            }

            const q = currentQ();
            if (!q) { currentQuestionIndex++; showQuestion(); return; }

            // 简答题：已给出参考要点（awaitingSelf）但没点自评按钮，又点「下一题」⇒ 记为未掌握
            if (step.awaitingSelf) {
                step.awaitingSelf = false;
                step.failed = true;
                weakTopics.push(step.topic);
                step.idx = step.questions.length;
                phase = 'feedback';
                btn.textContent = '下一个知识点';
                return;
            }

            if (phase === 'ask') {
                const r = gradeCurrent();
                if (r.empty) {
                    const tip = document.getElementById('feedback');
                    tip.innerHTML = '<span class="fb-no">请先作答</span>';
                    return;
                }
                askedCount++;
                if (q.type === 'short-answer' && !r.ok) {
                    // 简答题无法机判：给参考答案，让学生自评
                    step.awaitingSelf = true;
                    renderFeedback(false, q);
                    const fb = document.getElementById('feedback');
                    const mk = matchKeypoints(q, getUserAnswer());
                    if (mk) {
                      const tip = document.createElement('div');
                      tip.className = 'self-hint';
                      const word = mk.ratio >= 0.66 ? '建议记为掌握' : (mk.ratio >= 0.34 ? '建议对照要点再自评' : '建议记为未掌握');
                      tip.innerHTML = '自动判读：命中 <b>' + mk.hit + '/' + mk.total + '</b> 个要点 —— ' + word;
                      fb.appendChild(tip);
                    }
                    const selfCheck = document.createElement('div');
                    selfCheck.className = 'self-check';
                    selfCheck.innerHTML = '<button class="yes">我写到了要点</button><button class="no">我没写到</button>';
                    selfCheck.querySelector('.yes').onclick = () => {
                        step.awaitingSelf = false;
                        correctCount++;
                        step.idx++;
                        phase = 'feedback';
                        fb.querySelector('.fb-no').outerHTML = '<span class="fb-ok">✅ 已记为掌握</span>';
                        btn.textContent = '下一题';
                    };
                    selfCheck.querySelector('.no').onclick = () => {
                        step.awaitingSelf = false;
                        step.failed = true;
                        weakTopics.push(step.topic);
                        step.idx = step.questions.length;
                        phase = 'feedback';
                        fb.querySelector('.fb-no').outerHTML = '<span class="fb-no">❌ 已记为未掌握</span>';
                        btn.textContent = '下一题';
                    };
                    fb.appendChild(selfCheck);
                    return;
                }
                if (r.ok) correctCount++;
                else {
                    step.failed = true;
                    weakTopics.push(step.topic);
                    step.idx = step.questions.length;   // 答错即停，不再追问本知识点
                }
                if (!step.failed) step.idx++;
                renderFeedback(r.ok, q);
                phase = 'feedback';
                btn.textContent = step.idx >= step.questions.length ? '下一个知识点' : '下一题';
                return;
            }

        }

        // 显示结果
        function showResult() {
            document.getElementById('question-area').style.display = 'none';
            document.getElementById('result-area').style.display = 'block';
            
            const content = document.getElementById('result-content');
            
            if (weakTopics.length === 0) {
                content.innerHTML = `
                    <p style="color: #28a745; font-size: 16px;">
                        ✅ 太棒了！你的前置知识掌握得很好，可以开始学习「${targetTopic.name}」了！
                    </p>
                `;
            } else {
                content.innerHTML = `
                    <p style="margin-bottom: 15px;">
                        建议先复习以下 <strong>${weakTopics.length}</strong> 个知识点：
                    </p>
                    <ul class="result-list">
                        ${weakTopics.map(t => `
                            <li>
                                <div class="topic-name">📌 ${t.name}</div>
                                <div class="topic-desc">${t.description}</div>
                            </li>
                        `).join('')}
                    </ul>
                `;
            }

            // 存入学习档案（无档案时按匿名记录保存）
            try {
                if (window.CnmKids) {
                    var kid = window.CnmKids.current();
                    window.CnmKids.addRecord({
                        subject: currentSubject,
                        target: targetTopic ? { id: targetTopic.id, name: targetTopic.name } : null,
                        asked: askedCount,
                        weak: weakTopics.map(function (t) { return { id: t.id, name: t.name }; })
                    });
                    var tip = document.createElement('p');
                    tip.style.cssText = 'margin-top:12px;font-size:14px;color:#6b7280';
                    tip.innerHTML = kid
                        ? '已存入「' + kid.name + '」的档案 · <a href="../children/history.html?child=' + encodeURIComponent(kid.id) + '">查看记录</a>'
                        : '尚未建档，本次结果未保存 · <a href="../children/">去建档</a>';
                    content.appendChild(tip);
                }
            } catch (e) { console.warn('保存诊断记录失败', e); }
        }
