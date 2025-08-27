# storage_excel.py
import json
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

def _safe(x: Any) -> Any:
    if isinstance(x, (dict, list)):
        return json.dumps(x, ensure_ascii=False)
    return x

def export_records_to_excel(records: List[Dict], out_path: str | Path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # CORE
    core_rows = []
    for r in records:
        core_rows.append({
            "index_on_page": r.get("index_on_page"),
            "detail_url": r.get("detail_url_after_click"),
            "overview_numbers": _safe(r.get("overview_numbers")),
        })
    df_core = pd.DataFrame(core_rows)

    # SPREAD_METRICS
    sp_rows = []
    for r in records:
        sp = r.get("spread_performance", {}) or {}
        for key in ["A_30d_personal","B_30d_juxing","C_90d_juxing","D_90d_personal"]:
            met = sp.get(key, {}) or {}
            row = {
                "index_on_page": r.get("index_on_page"),
                "detail_url": r.get("detail_url_after_click"),
                "bucket": key
            }
            row.update(met)
            sp_rows.append(row)
    df_spread = pd.DataFrame(sp_rows)

    # SPREAD_CHARTS
    sc_rows = []
    for r in records:
        charts = (r.get("spread_performance") or {}).get("charts", {}) or {}
        sc_rows.append({
            "index_on_page": r.get("index_on_page"),
            "detail_url": r.get("detail_url_after_click"),
            "播放量": charts.get("播放量",""),
            "点赞量": charts.get("点赞量",""),
            "评论量": charts.get("评论量",""),
            "分享量": charts.get("分享量",""),
        })
    df_charts = pd.DataFrame(sc_rows)

    # AUDIENCE_GROWTH
    ag_rows = []
    for r in records:
        g = (r.get("audience_analysis") or {}).get("growth", {}) or {}
        for rng in ["30d","90d"]:
            row = {"index_on_page": r.get("index_on_page"), "detail_url": r.get("detail_url_after_click"), "range": rng}
            row.update(g.get(rng, {}) or {})
            ag_rows.append(row)
    df_growth = pd.DataFrame(ag_rows)

    # AUDIENCE_PORTRAITS
    ap_rows = []
    for r in records:
        p = (r.get("audience_analysis") or {}).get("portraits", {}) or {}
        for kind in ["观众画像","粉丝画像"]:
            row = {
                "index_on_page": r.get("index_on_page"),
                "detail_url": r.get("detail_url_after_click"),
                "kind": kind,
                "性别分布": (p.get(kind) or {}).get("性别分布",""),
                "年龄分布": (p.get(kind) or {}).get("年龄分布",""),
            }
            ap_rows.append(row)
    df_portraits = pd.DataFrame(ap_rows)

    # AUDIENCE_TAGS
    at_rows = []
    for r in records:
        tags_all = ((r.get("audience_tags") or {}).get("all_tags")) or []
        for tag in tags_all:
            at_rows.append({
                "index_on_page": r.get("index_on_page"),
                "detail_url": r.get("detail_url_after_click"),
                "tag": tag
            })
    df_tags = pd.DataFrame(at_rows)

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df_core.to_excel(writer, index=False, sheet_name="CORE")
        df_spread.to_excel(writer, index=False, sheet_name="SPREAD_METRICS")
        df_charts.to_excel(writer, index=False, sheet_name="SPREAD_CHARTS")
        df_growth.to_excel(writer, index=False, sheet_name="AUDIENCE_GROWTH")
        df_portraits.to_excel(writer, index=False, sheet_name="AUDIENCE_PORTRAITS")
        df_tags.to_excel(writer, index=False, sheet_name="AUDIENCE_TAGS")
