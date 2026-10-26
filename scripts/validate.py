#!/usr/bin/env python3
"""
知识图谱数据验证脚本
验证 topics.json, dependencies.json, questions.json 的格式和一致性
"""

import json
import sys
from pathlib import Path

def load_json(path):
    """加载JSON文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_topics(topics):
    """验证知识点数据"""
    errors = []
    ids = set()
    
    for i, topic in enumerate(topics):
        # 检查必填字段
        required = ['id', 'name', 'subject', 'grade', 'description']
        for field in required:
            if field not in topic:
                errors.append(f"Topic {i}: missing required field '{field}'")
        
        # 检查ID唯一性
        if 'id' in topic:
            if topic['id'] in ids:
                errors.append(f"Topic {i}: duplicate id '{topic['id']}'")
            ids.add(topic['id'])
        
        # 检查年级范围
        if 'grade' in topic:
            if not (1 <= topic['grade'] <= 16):
                errors.append(f"Topic {i}: grade {topic['grade']} out of range")
        
        # 检查先修关系引用
        if 'prerequisites' in topic:
            for prereq in topic['prerequisites']:
                if prereq not in ids and prereq not in [t['id'] for t in topics]:
                    errors.append(f"Topic {i}: prerequisite '{prereq}' not found")
    
    return errors, ids

def validate_dependencies(deps, valid_ids):
    """验证先修关系数据"""
    errors = []
    
    for i, dep in enumerate(deps):
        # 检查必填字段
        required = ['from', 'to', 'type']
        for field in required:
            if field not in dep:
                errors.append(f"Dependency {i}: missing required field '{field}'")
        
        # 检查ID引用
        if 'from' in dep and dep['from'] not in valid_ids:
            errors.append(f"Dependency {i}: 'from' id '{dep['from']}' not found in topics")
        if 'to' in dep and dep['to'] not in valid_ids:
            errors.append(f"Dependency {i}: 'to' id '{dep['to']}' not found in topics")
        
        # 检查type值
        if 'type' in dep and dep['type'] not in ['hard', 'soft']:
            errors.append(f"Dependency {i}: invalid type '{dep['type']}'")
    
    return errors

def validate_questions(questions, valid_ids):
    """验证诊断题数据"""
    errors = []
    
    for i, q in enumerate(questions):
        # 检查必填字段
        required = ['id', 'topicId', 'question', 'answer', 'type']
        for field in required:
            if field not in q:
                errors.append(f"Question {i}: missing required field '{field}'")
        
        # 检查topicId引用
        if 'topicId' in q and q['topicId'] not in valid_ids:
            errors.append(f"Question {i}: topicId '{q['topicId']}' not found in topics")
        
        # 检查选择题答案
        if q.get('type') == 'choice':
            if 'options' not in q or not q['options']:
                errors.append(f"Question {i}: choice question missing options")
            elif 'answer' in q:
                valid_labels = [opt['label'] for opt in q['options']]
                if q['answer'] not in valid_labels:
                    errors.append(f"Question {i}: answer '{q['answer']}' not in options")
    
    return errors

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python validate.py <subject>")
        print("Example: python validate.py math")
        sys.exit(1)
    
    subject = sys.argv[1]
    data_dir = Path('data') / subject
    
    if not data_dir.exists():
        print(f"Error: directory '{data_dir}' not found")
        sys.exit(1)
    
    all_errors = []
    valid_ids = set()
    
    # 加载并验证所有topics文件
    topics_files = list(data_dir.glob('topics*.json'))
    if not topics_files:
        print(f"No topics files found in {data_dir}")
        sys.exit(1)
    
    all_topics = []
    for tf in topics_files:
        print(f"Validating {tf.name}...")
        topics = load_json(tf)
        errors, ids = validate_topics(topics)
        all_errors.extend(errors)
        valid_ids.update(ids)
        all_topics.extend(topics)
        print(f"  ✓ {len(topics)} topics, {len(errors)} errors")
    
    # 验证dependencies
    deps_files = list(data_dir.glob('dependencies*.json'))
    for df in deps_files:
        print(f"Validating {df.name}...")
        deps = load_json(df)
        errors = validate_dependencies(deps, valid_ids)
        all_errors.extend(errors)
        print(f"  ✓ {len(deps)} dependencies, {len(errors)} errors")
    
    # 验证questions
    q_files = list(data_dir.glob('questions*.json'))
    for qf in q_files:
        print(f"Validating {qf.name}...")
        questions = load_json(qf)
        errors = validate_questions(questions, valid_ids)
        all_errors.extend(errors)
        print(f"  ✓ {len(questions)} questions, {len(errors)} errors")
    
    # 汇总
    print("\n" + "="*50)
    print(f"Validation Summary for '{subject}':")
    print(f"  Topics: {len(all_topics)}")
    print(f"  Unique IDs: {len(valid_ids)}")
    print(f"  Total Errors: {len(all_errors)}")
    
    if all_errors:
        print("\nErrors found:")
        for err in all_errors[:20]:  # 只显示前20个
            print(f"  - {err}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more")
        sys.exit(1)
    else:
        print("\n✓ All validations passed!")
        sys.exit(0)

if __name__ == '__main__':
    main()
