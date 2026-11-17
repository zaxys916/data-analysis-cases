"""自动扫描案例文件夹：扫描工作区根目录下的案例文件夹并同步进数据库"""
import os
import re
from datetime import datetime

from db import get_conn, init_db

# 平台自身目录不作为案例
SKIP_NAMES = {"案例管理平台"}
SKIP_PREFIXES = (".", "_", "$")


def scan_root() -> str:
    """案例根目录 = 案例管理平台的上一级目录"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _norm(p: str) -> str:
    return os.path.normcase(os.path.normpath(p))


def list_case_folders() -> list[str]:
    root = scan_root()
    folders = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if not os.path.isdir(path):
            continue
        if name in SKIP_NAMES or name.startswith(SKIP_PREFIXES):
            continue
        folders.append(path)
    return folders


def _read_summary(folder: str) -> str:
    """优先取 README.md 的第一个正文段落，否则按内容概况生成"""
    readme = os.path.join(folder, "README.md")
    if os.path.exists(readme):
        text = ""
        for encoding in ("utf-8", "gbk"):
            try:
                text = open(readme, encoding=encoding).read()
                break
            except UnicodeDecodeError:
                continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith(("#", "```", "|", "![", "![", "---", "├", "└", "[")):
                continue
            line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)  # 去掉 markdown 链接
            return line[:300]
    nb_count = sum(1 for f in os.listdir(folder) if f.endswith(".ipynb"))
    if nb_count:
        return f"自动导入：包含 {nb_count} 个 Jupyter Notebook"
    return "自动导入（未发现 README，建议补充案例描述）"


def _detect_tech(folder: str) -> str:
    """从 requirements.txt / notebook 文件推断技术栈"""
    tech = []
    if any(f.endswith(".ipynb") for f in os.listdir(folder)):
        tech += ["Python", "Jupyter"]
    req = os.path.join(folder, "requirements.txt")
    if os.path.exists(req):
        try:
            pkgs = []
            for raw in open(req, encoding="utf-8"):
                name = re.split(r"[<>=~!\s\[]", raw.strip())[0].lower()
                if name and name not in pkgs:
                    pkgs.append(name)
            tech += [p for p in pkgs[:8] if p != "python"]
        except OSError:
            pass
    seen, out = set(), []
    for t in tech:
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return ", ".join(out)


def scan_and_sync() -> dict:
    """扫描并同步：新增未录入的文件夹，返回新增与失效信息"""
    init_db()  # 首次运行先建表
    conn = get_conn()
    now = datetime.now().isoformat(timespec="seconds")

    existing = {
        _norm(r["path"]): r["id"]
        for r in conn.execute("SELECT id, path FROM cases WHERE path != ''").fetchall()
    }

    folders = list_case_folders()
    folder_set = {_norm(p) for p in folders}

    added = []
    for path in folders:
        if _norm(path) in existing:
            continue
        conn.execute(
            """INSERT INTO cases
               (title, category, status, dataset, tech_stack, tags, summary, path, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                os.path.basename(path),  # title = 文件夹名
                "未分类",
                "规划中",
                "",
                _detect_tech(path),
                "[]",
                _read_summary(path),
                path,
                now, now,
            ),
        )
        added.append(os.path.basename(path))

    # 已录入但文件夹已不存在（含手动填写路径的案例）
    missing = [
        dict(r)
        for r in conn.execute("SELECT id, title, path FROM cases WHERE path != ''").fetchall()
        if _norm(r["path"]) not in folder_set
    ]

    conn.commit()
    conn.close()
    return {"added": added, "missing": missing}


if __name__ == "__main__":
    print(scan_and_sync())
