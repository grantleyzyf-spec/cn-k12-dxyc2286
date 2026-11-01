# -*- coding: utf-8 -*-
"""S15 建造辅助。"""


def _q(prompt, typ, diff, answer, expl, options=None, verify=None):
    d = {"prompt": prompt, "type": typ, "difficulty": diff,
         "answer": answer, "explanation": expl}
    if options is not None:
        d["_correct"] = options[0]
        d["_distractors"] = options[1:]
    if verify is not None:
        d["verify"] = verify
    return d


def choice(prompt, diff, expl, correct, d1, d2, d3):
    return _q(prompt, "choice", diff, "A", expl, options=[correct, d1, d2, d3])


def fill(prompt, diff, ans, expl):
    return _q(prompt, "fill", diff, ans, expl)


def num(prompt, diff, ans, expl, verify):
    return _q(prompt, "numeric", diff, ans, expl, verify=verify)


def sa(prompt, diff, ans, expl):
    return _q(prompt, "short-answer", diff, ans, expl)


def P(tid, desc, mc, mis, std_id, qs):
    return {"topicId": tid, "description": desc, "mastery_criteria": mc,
            "misconceptions": mis, "std_id": std_id, "questions": qs}
