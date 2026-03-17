# CLAUDE.md

## プロジェクト概要

商品クレーム対応の回答文を、容器・分類の選択により自動生成するシステム。
メインコードは `02_long_task/06_response_system/` にある。

## 開発コマンド

### バックエンド（`02_long_task/06_response_system/backend/`）

```bash
pip install -r requirements.txt
python seed.py            # DB初期化 + サンプルデータ投入
uvicorn main:app --port 8000 --reload
```

### フロントエンド（`02_long_task/06_response_system/frontend/`）

```bash
npm install
npm run dev               # http://localhost:5173
```

Vite プロキシで `/api/*` → `localhost:8000` に転送。

## アーキテクチャ

- **バックエンド**: FastAPI + SQLAlchemy + SQLite
- **フロントエンド**: React 19 + Vite 8
- **DB**: SQLite（`response.db`、seed.py で生成）

## DB テーブル構成

- `containers` — 容器マスタ
- `problem_categories` — 大分類→中分類（parent_id で階層化）
- `problem_details` — 小分類（category_id で中分類に紐づく）
- `manual_entries` — 容器×中分類の組み合わせ
- `response_templates` — 主回答文（section_type: investigation / process / summary）
- `sub_responses` — サブ回答文（小分類自動付与 or Yes/No条件付与）
- `response_history` / `response_history_subs` — 履歴

## コーディング規約

- バックエンドは Python 3.12+、型ヒント使用
- フロントエンドは JSX（TypeScript 未使用）
- API パスは `/api/` プレフィックス統一
