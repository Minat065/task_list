import re

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import (
    Container,
    ManualEntry,
    ProblemCategory,
    ProblemDetail,
    ResponseHistory,
    ResponseHistorySub,
    ResponseTemplate,
    SubResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="回答文作成システム API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── マスタ取得 ──────────────────────────────────────


@app.get("/api/containers")
def list_containers(db: Session = Depends(get_db)):
    rows = (
        db.query(Container)
        .filter(Container.is_active)
        .order_by(Container.sort_order)
        .all()
    )
    return [{"id": r.id, "name": r.name, "description": r.description} for r in rows]


@app.get("/api/categories")
def list_categories(db: Session = Depends(get_db)):
    """大分類→中分類のツリー構造を返す"""
    majors = (
        db.query(ProblemCategory)
        .filter(ProblemCategory.depth == 1, ProblemCategory.is_active)
        .order_by(ProblemCategory.sort_order)
        .all()
    )
    result = []
    for m in majors:
        children = (
            db.query(ProblemCategory)
            .filter(
                ProblemCategory.parent_id == m.id,
                ProblemCategory.is_active,
            )
            .order_by(ProblemCategory.sort_order)
            .all()
        )
        result.append(
            {
                "id": m.id,
                "name": m.name,
                "children": [
                    {"id": c.id, "name": c.name} for c in children
                ],
            }
        )
    return result


@app.get("/api/details/{category_id}")
def list_details(category_id: int, db: Session = Depends(get_db)):
    """中分類IDに紐づく小分類を返す"""
    rows = (
        db.query(ProblemDetail)
        .filter(ProblemDetail.category_id == category_id, ProblemDetail.is_active)
        .order_by(ProblemDetail.sort_order)
        .all()
    )
    return [{"id": r.id, "name": r.name, "description": r.description} for r in rows]


# ── 回答文生成 ──────────────────────────────────────


class GenerateRequest(BaseModel):
    container_id: int
    category_id: int  # 中分類ID
    detail_id: int  # 小分類ID
    condition_answers: dict[str, bool] = {}  # {"流通経路による場合": true, ...}
    placeholders: dict[str, str] = {}  # {"product_name": "緑茶「まるごと茶葉」", ...}


class GenerateResponse(BaseModel):
    investigation: str
    process: str
    summary: str
    full_text: str
    applied_subs: list[dict]
    conditions: list[dict]  # Yes/No質問の一覧


@app.post("/api/generate/preview")
def preview_conditions(req: GenerateRequest, db: Session = Depends(get_db)):
    """Step 1: 選択に基づいて、Yes/No質問の一覧を返す"""
    entry = (
        db.query(ManualEntry)
        .filter(
            ManualEntry.container_id == req.container_id,
            ManualEntry.category_id == req.category_id,
            ManualEntry.is_active,
        )
        .first()
    )
    if not entry:
        raise HTTPException(404, "該当するマニュアルエントリが見つかりません")

    templates = (
        db.query(ResponseTemplate)
        .filter(ResponseTemplate.manual_entry_id == entry.id, ResponseTemplate.is_active)
        .all()
    )
    template_ids = [t.id for t in templates]

    # detail_id=NULL のサブ回答文 → Yes/No質問
    condition_subs = (
        db.query(SubResponse)
        .filter(
            SubResponse.template_id.in_(template_ids),
            SubResponse.detail_id.is_(None),
            SubResponse.is_active,
        )
        .order_by(SubResponse.sort_order)
        .all()
    )

    # 重複するcondition_labelを除いてユニークな質問リストを作る
    seen = set()
    conditions = []
    for s in condition_subs:
        if s.condition_label and s.condition_label not in seen:
            seen.add(s.condition_label)
            conditions.append({"label": s.condition_label})

    return {"conditions": conditions}


@app.post("/api/generate", response_model=GenerateResponse)
def generate_response(req: GenerateRequest, db: Session = Depends(get_db)):
    """Step 2: 回答文を生成"""
    entry = (
        db.query(ManualEntry)
        .filter(
            ManualEntry.container_id == req.container_id,
            ManualEntry.category_id == req.category_id,
            ManualEntry.is_active,
        )
        .first()
    )
    if not entry:
        raise HTTPException(404, "該当するマニュアルエントリが見つかりません")

    templates = (
        db.query(ResponseTemplate)
        .filter(ResponseTemplate.manual_entry_id == entry.id, ResponseTemplate.is_active)
        .order_by(ResponseTemplate.sort_order)
        .all()
    )

    section_map: dict[str, str] = {}
    applied_subs: list[dict] = []

    for tmpl in templates:
        subs = (
            db.query(SubResponse)
            .filter(SubResponse.template_id == tmpl.id, SubResponse.is_active)
            .order_by(SubResponse.sort_order)
            .all()
        )

        before_texts: list[str] = []
        after_texts: list[str] = []

        for s in subs:
            should_apply = False

            if s.detail_id is not None:
                # 小分類の選択で自動付与
                if s.detail_id == req.detail_id:
                    should_apply = True
            elif s.condition_label:
                # Yes/No質問
                if req.condition_answers.get(s.condition_label, False):
                    should_apply = True

            if should_apply:
                text = _replace_placeholders(s.body, req.placeholders)
                if s.position == "before":
                    before_texts.append(text)
                else:
                    after_texts.append(text)
                applied_subs.append(
                    {
                        "id": s.id,
                        "position": s.position,
                        "condition_label": s.condition_label,
                        "body_preview": text[:50],
                    }
                )

        main_body = _replace_placeholders(tmpl.body, req.placeholders)
        section_map[tmpl.section_type] = (
            "".join(before_texts) + main_body + "".join(after_texts)
        )

    investigation = section_map.get("investigation", "")
    process = section_map.get("process", "")
    summary = section_map.get("summary", "")

    full_text = (
        f"【調査結果】\n{investigation}\n\n"
        f"【製造工程】\n{process}\n\n"
        f"【まとめ】\n{summary}"
    )

    return GenerateResponse(
        investigation=investigation,
        process=process,
        summary=summary,
        full_text=full_text,
        applied_subs=applied_subs,
        conditions=[],
    )


def _replace_placeholders(text: str, placeholders: dict[str, str]) -> str:
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return placeholders.get(key, match.group(0))

    return re.sub(r"\{\{(\w+)\}\}", replacer, text)


# ── 履歴 ────────────────────────────────────────────


class SaveHistoryRequest(BaseModel):
    manual_entry_id: int
    container_id: int
    category_id: int
    detail_id: int
    generated_text: str
    edited_text: str | None = None
    applied_sub_ids: list[int] = []
    created_by: str = ""


@app.post("/api/history")
def save_history(req: SaveHistoryRequest, db: Session = Depends(get_db)):
    history = ResponseHistory(
        manual_entry_id=req.manual_entry_id,
        container_id=req.container_id,
        category_id=req.category_id,
        detail_id=req.detail_id,
        generated_text=req.generated_text,
        edited_text=req.edited_text,
        created_by=req.created_by,
    )
    db.add(history)
    db.flush()

    for sub_id in req.applied_sub_ids:
        db.add(
            ResponseHistorySub(
                response_history_id=history.id, sub_response_id=sub_id
            )
        )

    db.commit()
    return {"id": history.id}


@app.get("/api/history")
def list_history(db: Session = Depends(get_db)):
    rows = (
        db.query(ResponseHistory)
        .order_by(ResponseHistory.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": r.id,
            "container_id": r.container_id,
            "category_id": r.category_id,
            "detail_id": r.detail_id,
            "generated_text": r.generated_text[:100],
            "created_by": r.created_by,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
