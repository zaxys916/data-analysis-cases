"""SQLite 数据层：连接、建表、种子数据"""
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            category    TEXT DEFAULT '未分类',
            status      TEXT DEFAULT '规划中',
            dataset     TEXT DEFAULT '',
            tech_stack  TEXT DEFAULT '',
            tags        TEXT DEFAULT '[]',
            summary     TEXT DEFAULT '',
            path        TEXT DEFAULT '',
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id    INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            title      TEXT NOT NULL,
            content    TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        """
    )
    _seed(conn)
    conn.commit()
    conn.close()


def _seed(conn: sqlite3.Connection):
    """首条真实案例：olist 实战（仅当案例表为空时写入）"""
    if conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0] > 0:
        return
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.execute(
        """INSERT INTO cases
           (title, category, status, dataset, tech_stack, tags, summary, path, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "Olist 巴西电商数据分析实战",
            "电商",
            "已完成",
            "Kaggle Olist Brazilian E-commerce Dataset（10 万订单、9 张关联表）",
            "Python, pandas, scikit-learn, Jupyter",
            json.dumps(["RFM", "复购留存", "差评归因", "流失预测", "需求预测"], ensure_ascii=False),
            "基于 Kaggle 公开数据集的完整分析项目：数据处理 → 客户分析 → 经营诊断 → 预测建模，共 14 个 Jupyter Notebook，附自包含 HTML 总结报告。",
            r"D:\study\数据分析\数据分析案例实例\olist实战",
            now, now,
        ),
    )
    case_id = cur.lastrowid
    conn.execute(
        "INSERT INTO notes (case_id, title, content, created_at) VALUES (?, ?, ?, ?)",
        (
            case_id,
            "核心结论复盘",
            "客户结构：93,358 名客户，复购率仅 3.0%，一次性交易型平台；RFM 四类客群中发展客户占 60%\n"
            "复购留存：复购间隔中位 28 天，51% 的复购发生在首购后 30 天内\n"
            "销售趋势：2017→2018 月订单量近翻倍后进入 6,000±500 平台期\n"
            "品类价格：健康美容/手表礼品/床品餐桌为销售额前三；100–200 价位贡献最大金额\n"
            "履约与评分：平均送达 12.1 天、准时率 93.2%；迟到订单差评率 61% vs 准时 9%，差评主因是物流\n"
            "建模结论：流失不可从首单特征预测（AUC 0.54）；差评可用迟到天数预警（AUC 0.67）；销量预测移动平均最优（MAE 386）",
            now,
        ),
    )


def row_to_case(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["tags"] = json.loads(d["tags"] or "[]")
    return d
