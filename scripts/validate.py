#!/usr/bin/env python3
"""
知识图谱数据验证脚本（参考 cn-math-taxonomy 节点结构）

验证 topics.json / dependencies.json / questions.json 的格式与一致性。

用法：
  python3 scripts/validate.py math     # 单学科
  python3 scripts/validate.py --all     # 全学科（CI 用）
"""

import json
import sys
from pathlib import Path

SEMESTERS = {'上', '下', 'fall', 'spring'}
TOPIC_TYPES = {'conceptual', 'procedural', 'reasoning', 'modeling', 'application'}
QUESTION_TYPES = {'choice', 'fill', 'short-answer', 'numeric'}
DIFFICULTIES = {'basic', 'standard', 'hard', 'easy', 'medium'}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_topics(topics):
    errors = []
    ids = set()
    all_ids = {t.get('id') for t in topics if isinstance(t, dict)}

    for i, topic in enumerate(topics):
        required = ['id', 'name', 'subject', 'grade', 'description']
        for field in required:
            if field not in topic:
                errors.append(f"Topic {i}: missing required field '{field}'")

        if 'id' in topic:
            if topic['id'] in ids:
                errors.append(f"Topic {i}: duplicate id '{topic['id']}'")
            ids.add(topic['id'])

        if 'grade' in topic and not (1 <= topic['grade'] <= 16):
            errors.append(f"Topic {i}: grade {topic['grade']} out of range")

        if topic.get('semester') not in SEMESTERS:
            errors.append(f"Topic {i}: invalid semester {topic.get('semester')!r} (期望 上/下)")

        if 'type' in topic and topic['type'] not in TOPIC_TYPES:
            errors.append(f"Topic {i}: invalid type '{topic['type']}'")

        if 'mastery_criteria' in topic and not isinstance(topic['mastery_criteria'], list):
            errors.append(f"Topic {i}: mastery_criteria must be a list")

        dq = topic.get('diagnostic_question')
        if dq is not None:
            if not isinstance(dq, dict) or 'question' not in dq or 'answer' not in dq:
                errors.append(f"Topic {i}: diagnostic_question must be {{question, answer}}")

        std = topic.get('standards')
        if std is not None:
            if not isinstance(std, list):
                errors.append(f"Topic {i}: standards must be a list")
            else:
                for s in std:
                    if not isinstance(s, dict) or 'id' not in s:
                        errors.append(f"Topic {i}: standards item missing 'id'")
                        break

        if 'external' in topic and not isinstance(topic['external'], bool):
            errors.append(f"Topic {i}: external must be boolean")

        for prereq in topic.get('prerequisites', []) or []:
            if prereq not in all_ids:
                errors.append(f"Topic {i}: prerequisite '{prereq}' not found")

    return errors, ids


def validate_dependencies(deps, valid_ids):
    errors = []
    for i, dep in enumerate(deps):
        for field in ['from', 'to', 'type']:
            if field not in dep:
                errors.append(f"Dependency {i}: missing required field '{field}'")
        if 'from' in dep and dep['from'] not in valid_ids:
            errors.append(f"Dependency {i}: 'from' id '{dep['from']}' not found in topics")
        if 'to' in dep and dep['to'] not in valid_ids:
            errors.append(f"Dependency {i}: 'to' id '{dep['to']}' not found in topics")
        if 'type' in dep and dep['type'] not in ['hard', 'soft']:
            errors.append(f"Dependency {i}: invalid type '{dep['type']}'")
    return errors


def validate_questions(questions, valid_ids):
    errors = []
    for i, q in enumerate(questions):
        prompt = q.get('prompt') or q.get('question') or q.get('stem')
        if not prompt:
            errors.append(f"Question {i}: missing prompt")
        if 'id' not in q:
            errors.append(f"Question {i}: missing required field 'id'")
        tid = q.get('topicId') or q.get('topic_id')
        if not tid:
            errors.append(f"Question {i}: missing topicId")
        elif tid not in valid_ids:
            errors.append(f"Question {i}: topicId '{tid}' not found in topics")
        if 'answer' not in q:
            errors.append(f"Question {i}: missing required field 'answer'")
        if 'type' in q and q['type'] not in QUESTION_TYPES:
            errors.append(f"Question {i}: invalid type '{q['type']}'")
        if q.get('difficulty') and q['difficulty'] not in DIFFICULTIES:
            errors.append(f"Question {i}: invalid difficulty '{q['difficulty']}'")
        if q.get('type') == 'choice':
            if not q.get('options'):
                errors.append(f"Question {i}: choice question missing options")
            elif 'answer' in q:
                labels = [o.get('label') for o in q['options'] if isinstance(o, dict)]
                if q['answer'] not in labels:
                    errors.append(f"Question {i}: answer '{q['answer']}' not in options")
    return errors


def validate_subject(subject, quiet=False):
    data_dir = Path('data') / subject
    if not data_dir.exists():
        return [f"directory '{data_dir}' not found"], {}

    errors = []
    valid_ids = set()
    counts = {'topics': 0, 'dependencies': 0, 'questions': 0}

    topics_files = [data_dir / 'topics.json'] if (data_dir / 'topics.json').exists() else sorted(data_dir.glob('topics*.json'))
    if not topics_files:
        return [f"No topics files found in {data_dir}"], counts
    for tf in topics_files:
        topics = load_json(tf)
        e, ids = validate_topics(topics)
        errors.extend(e)
        valid_ids.update(ids)
        counts['topics'] += len(topics)

    dep_files = [data_dir / 'dependencies.json'] if (data_dir / 'dependencies.json').exists() else sorted(data_dir.glob('dependencies*.json'))
    for df in dep_files:
        deps = load_json(df)
        errors.extend(validate_dependencies(deps, valid_ids))
        counts['dependencies'] += len(deps)

    q_files = [data_dir / 'questions.json'] if (data_dir / 'questions.json').exists() else sorted(data_dir.glob('questions*.json'))
    for qf in q_files:
        qs = load_json(qf)
        errors.extend(validate_questions(qs, valid_ids))
        counts['questions'] += len(qs)

    return errors, counts


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate.py <subject> | --all")
        sys.exit(1)

    if sys.argv[1] == '--all':
        subjects = sorted(p.name for p in Path('data').iterdir()
                          if p.is_dir() and (p / 'topics.json').exists())
        total_err = 0
        print(f"{'学科':<22}{'知识点':>7}{'先修边':>8}{'题目':>7}{'错误':>6}")
        for s in subjects:
            errs, c = validate_subject(s, quiet=True)
            total_err += len(errs)
            print(f"{s:<22}{c['topics']:>7}{c['dependencies']:>8}{c['questions']:>7}{len(errs):>6}")
            for e in errs[:3]:
                print(f"    ! {e}")
        print(f"{'总计':<22}{'':>7}{'':>8}{'':>7}{total_err:>6}")
        sys.exit(1 if total_err else 0)

    subject = sys.argv[1]
    errors, counts = validate_subject(subject)
    print(f"Validation Summary for '{subject}':")
    print(f"  Topics: {counts.get('topics', 0)}")
    print(f"  Dependencies: {counts.get('dependencies', 0)}")
    print(f"  Questions: {counts.get('questions', 0)}")
    print(f"  Total Errors: {len(errors)}")
    if errors:
        print("\nErrors found:")
        for err in errors[:20]:
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
        sys.exit(1)
    print("\n✓ All validations passed!")
    sys.exit(0)


if __name__ == '__main__':
    main()
