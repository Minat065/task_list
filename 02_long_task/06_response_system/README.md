# 回答文作成システム

商品クレーム対応の回答文を、分類選択により自動生成するシステム。

## 技術スタック

| 層 | 技術 |
|----|------|
| フロントエンド | React 19 + Vite |
| バックエンド | FastAPI + SQLAlchemy |
| DB | SQLite |

## プロジェクト構成

```
06_response_system/
├── backend/
│   ├── main.py          # API エンドポイント
│   ├── models.py         # DB モデル（7テーブル）
│   ├── database.py       # DB 接続設定
│   ├── seed.py           # サンプルデータ投入
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx       # メインUI（3ステップ）
    │   └── main.jsx      # エントリポイント
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## セットアップ

### バックエンド

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
cd backend
pip install -r requirements.txt
python seed.py            # 初回のみ（DB作成 + サンプルデータ投入）
uvicorn main:app --port 8000
```

API ドキュメント: http://localhost:8000/docs

### フロントエンド

```bash
cd frontend
npm install
npm run dev               # → http://localhost:5173
```

Vite のプロキシ設定により `/api/*` は自動的にバックエンド（port 8000）へ転送されます。

## 使い方

1. **容器を選択**（例: 350ml缶）
2. **大分類を選択**（例: 漏れ・破損）
3. **中分類を選択**（例: 亀裂）→ 主回答文が決定
4. **小分類を選択**（例: 小さな傷）→ サブ回答文が自動付与
5. **追加条件に回答**（Yes/No形式）
6. **回答文を確認** → コピーして利用

## DB 構成

```
containers（容器）
problem_categories（大分類→中分類）
problem_details（小分類、category_id でフィルタ）
manual_entries（容器×中分類の組み合わせ）
response_templates（主回答文：調査結果/製造工程/まとめ）
sub_responses（サブ回答文：小分類で自動付与 or Yes/No条件付与）
response_history / response_history_subs（履歴）
```

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/api/containers` | 容器一覧 |
| GET | `/api/categories` | 大分類→中分類ツリー |
| GET | `/api/details/{category_id}` | 中分類の小分類一覧 |
| POST | `/api/generate/preview` | 追加条件（Yes/No質問）一覧取得 |
| POST | `/api/generate` | 回答文生成 |
| POST | `/api/history` | 履歴保存 |
| GET | `/api/history` | 履歴一覧 |
