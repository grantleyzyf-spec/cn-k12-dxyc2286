/* 模式切换（自适应诊断 / 整卷测试）——原内联脚本外置 */
// 模式切换：自适应诊断 / 整卷测试
        (function () {
            const tabA = document.getElementById('tab-adaptive');
            const tabE = document.getElementById('tab-exam');
            const wrapA = document.getElementById('adaptive-wrap');
            const wrapE = document.getElementById('exam-wrap');
            const head = document.querySelector('.page-head');
            function show(which) {
                const isA = which === 'adaptive';
                tabA.classList.toggle('active', isA);
                tabE.classList.toggle('active', !isA);
                wrapA.style.display = isA ? '' : 'none';
                wrapE.style.display = isA ? 'none' : 'block';
                if (head) {
                    head.querySelector('h1').textContent = isA ? '自适应诊断' : '整卷测试';
                    head.querySelector('p').textContent = isA
                        ? '选一个目标知识点，系统沿必先修关系逐层出题，找出真正卡住的那一步。'
                        : '按教材册次选单元卷、期中卷或期末卷，计时答题；交卷后按知识点出得分率与补救路径。';
                }
                if (!isA && window.initExamMode) window.initExamMode();
            }
            tabA.onclick = () => show('adaptive');
            tabE.onclick = () => show('exam');
            if (new URLSearchParams(location.search).get('mode') === 'exam') show('exam');
        })();
