"""数据分析案例管理平台 - FastAPI 后端"""
import json
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from db import get_conn, init_db, row_to_case
from scanner import scan_and_sync

app = FastAPI(title="数据分析案例管理平台 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CaseIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: str = "未分类"
    status: str = "规划中"
    dataset: str = ""
    tech_stack: str = ""
    tags: list[str] = []
    summary: str = ""
    path: str = ""


class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = ""


@app.on_event("startup")
def startup():
    init_db()
    scan_and_sync()  # 启动时自动扫描案例文件夹


@app.post("/api/scan")
def scan():
    """手动触发扫描：新增未录入文件夹 / 检测已失效路径"""
    return scan_and_sync()


# ---------- 案例 ----------

@app.get("/api/cases")
def list_cases(
    keyword: str = "",
    category: str = "",
    status: str = "",
    tag: str = "",
):
    sql = "SELECT * FROM cases WHERE 1=1"
    params: list = []
    if keyword:
        sql += " AND (title LIKE ? OR summary LIKE ? OR dataset LIKE ?)"
        kw = f"%{keyword}%"
        params += [kw, kw, kw]
    if category:
        sql += " AND category = ?"
        params.append(category)
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY updated_at DESC"
    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    cases = [row_to_case(r) for r in rows]
    if tag:  # 标签包含筛选
        cases = [c for c in cases if tag in c["tags"]]
    return cases


@app.post("/api/cases", status_code=201)
def create_case(body: CaseIn):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO cases
           (title, category, status, dataset, tech_stack, tags, summary, path, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            body.title, body.category, body.status, body.dataset,
            body.tech_stack, json.dumps(body.tags, ensure_ascii=False),
            body.summary, body.path, now, now,
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM cases WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_case(row)


@app.get("/api/cases/{case_id}")
def get_case(case_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "案例不存在")
    return row_to_case(row)


@app.put("/api/cases/{case_id}")
def update_case(case_id: int, body: CaseIn):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    cur = conn.execute(
        """UPDATE cases SET title=?, category=?, status=?, dataset=?, tech_stack=?,
           tags=?, summary=?, path=?, updated_at=? WHERE id=?""",
        (
            body.title, body.category, body.status, body.dataset,
            body.tech_stack, json.dumps(body.tags, ensure_ascii=False),
            body.summary, body.path, now, case_id,
        ),
    )
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(404, "案例不存在")
    conn.commit()
    row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    conn.close()
    return row_to_case(row)


@app.delete("/api/cases/{case_id}")
def delete_case(case_id: int):
    conn = get_conn()
    cur = conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(404, "案例不存在")
    return {"ok": True}


# ---------- 笔记 ----------

@app.get("/api/cases/{case_id}/notes")
def list_notes(case_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM notes WHERE case_id = ? ORDER BY created_at DESC, id DESC",
        (case_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/cases/{case_id}/notes", status_code=201)
def create_note(case_id: int, body: NoteIn):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    if not conn.execute("SELECT 1 FROM cases WHERE id = ?", (case_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "案例不存在")
    cur = conn.execute(
        "INSERT INTO notes (case_id, title, content, created_at) VALUES (?, ?, ?, ?)",
        (case_id, body.title, body.content, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int):
    conn = get_conn()
    cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(404, "笔记不存在")
    return {"ok": True}


# ---------- 统计 ----------

@app.get("/api/stats")
def stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    by_status = dict(
        conn.execute("SELECT status, COUNT(*) FROM cases GROUP BY status").fetchall()
    )
    by_category = dict(
        conn.execute(
            "SELECT category, COUNT(*) FROM cases GROUP BY category ORDER BY COUNT(*) DESC"
        ).fetchall()
    )
    tag_rows = conn.execute("SELECT tags FROM cases").fetchall()
    conn.close()

    tag_count: dict = {}
    for r in tag_rows:
        for t in json.loads(r["tags"] or "[]"):
            tag_count[t] = tag_count.get(t, 0) + 1
    top_tags = dict(sorted(tag_count.items(), key=lambda x: -x[1])[:10])

    done = by_status.get("已完成", 0)
    return {
        "total": total,
        "done": done,
        "completion_rate": round(done / total * 100, 1) if total else 0,
        "by_status": by_status,
        "by_category": by_category,
        "top_tags": top_tags,
    }
