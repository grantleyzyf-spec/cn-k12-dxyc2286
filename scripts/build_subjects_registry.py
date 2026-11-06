#!/usr/bin/env python3
"""生成 data/subjects.json：学科 → 版本 的注册表。

为什么要有它：站点「学科图谱」的一级目录只能是**学科**（数学、语文、物理…），
同一学科的不同教材版本（人教版/北师大版/苏教版…）必须是学科下的二级分支，
而不是各自单列成一个学科。数据侧本来就是一个版本一个目录（`data/math`、`data/math-bsd`…），
本脚本把目录归并成「学科 + editions」，前端（首页学科卡、explore 的学科/版本下拉）统一读这份注册表。

用法：
  python3 scripts/build_subjects_registry.py          # 重新生成 data/subjects.json
  python3 scripts/build_subjects_registry.py --check  # 只比对不写入（收尾/CI 用）
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "subject-groups.json")   # ⚠️ 不要覆盖 data/subjects.json（那是他方维护的 id/name/icon/count 清单）

# 版本目录 → 版本名（人教版排第一，其余按体量）
EDITIONS = {
    "geography-lujiao": "鲁教版",
    "math": "人教版",
    "math-bj": "北京版",
    "math-bsd": "北师大版",
    "math-hebei": "冀教版",
    "math-qd": "青岛版",
    "math-sujiao": "苏教版",
    "math-suke": "苏科版",
    "math-xiangjiao": "湘教版",
    "math-xnd": "西南大学版",
    "math-hujiao": "沪教版",
    "math-ejiao": "鄂教版",
    "math-hukeji": "沪科技版",
    "math-hds": "华东师大版",
    # 单版本学科：教材出版社/版本名（不写会在站点「版本」下拉里显示成空白）
    "chinese": "统编版",
    "history": "统编版",
    "politics": "统编版",
    "english": "人教版",
    "physics": "人教版",
    "physics-yj": "粤教版",
    "physics-bsd-lcm": "北师大版·李春密",
    "physics-hkj-yj": "沪科技粤教版",
    "physics-bsd-gyy": "北师大版·郭玉英",
    "chemistry": "人教版",
    "chemistry-kepu": "科普版",
    "chemistry-lujiao": "鲁教版",
    "chemistry-luke": "鲁科版",
    "chemistry-bj": "北京版",
    "chemistry-hujiao": "沪教版",
    "physics-jk": "教科版",
    "physics-hkjy": "沪科教版",
    "chemistry-sujiao": "苏教版",
    "chemistry-hukeji": "沪科技版",
    "chemistry-yuejiao": "科学粤教版",
    "biology": "人教版",
    "geography": "人教版",
    "geography-jin": "晋教版",
    "geography-kepu": "科普版",
    "geography-shangwu": "商务星球版",
    "geography-xiangjiao": "湘教版",
    "geography-yuejiao": "粤教粤人版",
    "geography-zhongtu-cz": "中图版·钟作慈",
    "information-technology": "人教版",
    "japanese": "人教版",
    "russian": "人教版",
    "german": "外研社版",
    "french": "外研社版",
    "spanish": "外研社版",
    "music": "人教版",
    "art": "人教版",
    "science": "教科版",
    "mental-health": "北师大版",
}

# 学科显示名（不写就沿用 stats.json 里的名字，去掉「（XX版）」后缀）
SUBJECT_NAME = {
    "math": "数学",
    "information-technology": "信息科技",
}

SUBJECT_LABEL = {
    "math": "小·初·高", "chinese": "小·初·高", "english": "小·初·高", "physics": "初·高",
    "biology": "高", "history": "初·高", "german": "高", "russian": "小·初·高", "geography": "初·高",
    "chemistry": "初·高", "information-technology": "小·初", "french": "高", "japanese": "高",
    "spanish": "小·初·高", "art": "小·初·高", "music": "小·初·高", "science": "小",
    "mental-health": "小·初·高", "politics": "小·初·高",
}


def base_of(dir_id):
    """数据目录 → 学科基础 id：math-bsd → math；chemistry-yuejiao → chemistry；其余原样。"""
    for pref in ("math-", "geography-", "chemistry-", "biology-", "physics-",
                 "politics-", "history-", "english-", "art-", "music-",
                 "chinese-", "mental-health-", "information-technology-"):
        if dir_id.startswith(pref):
            return dir_id.split("-")[0]
    return dir_id


def strip_edition(name):
    """'数学（北师大版）' → '数学'；'信息科技／信息技术' 原样。"""
    for sep in ("（", "("):
        if sep in name:
            return name.split(sep)[0].strip()
    return name.strip()


def count_json(path):
    try:
        return len(json.load(open(path, encoding="utf-8")))
    except Exception:  # noqa: BLE001
        return 0


def main():
    stats = {}
    sp = os.path.join(DATA, "stats.json")
    if os.path.exists(sp):
        for row in json.load(open(sp, encoding="utf-8")).get("per_subject") or []:
            stats[row["id"]] = row

    icons = {}
    legacy_p = os.path.join(DATA, "subjects.json")
    if os.path.exists(legacy_p):
        try:
            for row in (json.load(open(legacy_p, encoding="utf-8")).get("subjects") or []):
                if row.get("icon"):
                    icons[row["id"]] = row["icon"]
        except Exception:  # noqa: BLE001
            pass

    # 只统计「已纳入版本库」的学科目录：没提交的目录（别的工作区在途数据）不能出现在站点上，
    # 否则线上会把查不到的目录也列成学科/版本。
    tracked = set()
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files", "data/*/topics.json"],
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            parts = line.split("/")
            if len(parts) >= 3:
                tracked.add(parts[1])
    except Exception:  # noqa: BLE001
        tracked = set()

    dirs = []
    for name in sorted(os.listdir(DATA)):
        d = os.path.join(DATA, name)
        if not (os.path.isdir(d) and os.path.exists(os.path.join(d, "topics.json"))):
            continue
        if tracked and name not in tracked:
            continue
        dirs.append(name)

    groups = {}
    for dir_id in dirs:
        base = base_of(dir_id)
        topics = count_json(os.path.join(DATA, dir_id, "topics.json"))
        questions = count_json(os.path.join(DATA, dir_id, "questions.json"))
        g = groups.setdefault(base, {"id": base, "subject_name": "", "editions": []})
        if not g["subject_name"]:
            st = stats.get(dir_id) or {}
            g["subject_name"] = strip_edition(st.get("name") or "") or base
        g["editions"].append({
            "id": dir_id,
            "name": EDITIONS.get(dir_id, ""),
            "icon": icons.get(dir_id, ""),
            "topics": topics,
            "questions": questions,
        })

    subjects = []
    for base, g in groups.items():
        eds = sorted(g["editions"], key=lambda e: (0 if e["id"] in ("math", "geography") else 1, -e["topics"], e["id"]))
        subjects.append({
            "id": base,
            "name": SUBJECT_NAME.get(base) or g["subject_name"] or base,
            "label": SUBJECT_LABEL.get(base, ""),
            "icon": next((e["icon"] for e in g["editions"] if e.get("icon")), ""),
            "topics": sum(e["topics"] for e in eds),
            "questions": sum(e["questions"] for e in eds),
            "editions": eds,
        })
    subjects.sort(key=lambda s: (-s["topics"], s["id"]))

    payload = {
        "generated_by": "scripts/build_subjects_registry.py",
        "note": "一级=学科，二级=教材版本；学科下拉只列学科，版本下拉列 editions；深链仍用 ?subject=<版本目录>",
        "subjects": subjects,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    if "--check" in sys.argv:
        old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if old != text:
            print("❌ data/subjects.json 已过期，请跑 python3 scripts/build_subjects_registry.py")
            return 1
        print("✅ data/subjects.json 与数据一致")
        return 0

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    multi = [s for s in subjects if len(s["editions"]) > 1]
    print(f"✅ 写入 {OUT}")
    print(f"   学科 {len(subjects)} 个（数据目录 {len(dirs)} 个）· 多版本学科："
          + "；".join(f"{s['name']} {len(s['editions'])} 版" for s in multi))
    return 0


if __name__ == "__main__":
    sys.exit(main())
