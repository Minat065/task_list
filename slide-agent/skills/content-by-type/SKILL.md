# Content By Type Skill

## 役割
ClassifierのJSON出力を受け取り、各スライド型に応じたコンテンツを生成する。

## 入力
Classifierが出力したスライド構成JSON

## 出力JSON形式

### TYPE_01 コンテンツ

```json
{
  "slide_number": 1,
  "type": "TYPE_01",
  "title": "スライドタイトル",
  "needs_3d": true,
  "visual": {
    "type": "3d",
    "prompt": "画像/3D生成用プロンプト",
    "path": ""
  },
  "blocks": [
    {
      "title": "ブロックAタイトル",
      "body": "ブロックA本文"
    },
    {
      "title": "ブロックBタイトル",
      "body": "ブロックB本文"
    },
    {
      "title": "ブロックCタイトル",
      "body": "ブロックC本文"
    }
  ],
  "bottom_message": "ボトムバーのメッセージ"
}
```

### TYPE_02 コンテンツ

```json
{
  "slide_number": 2,
  "type": "TYPE_02",
  "title": "スライドタイトル",
  "columns": [
    {
      "title": "カラム1タイトル",
      "icon_prompt": "アイコン生成用プロンプト",
      "icon_path": "",
      "points": ["ポイント1", "ポイント2", "ポイント3"]
    },
    {
      "title": "カラム2タイトル",
      "icon_prompt": "アイコン生成用プロンプト",
      "icon_path": "",
      "points": ["ポイント1", "ポイント2", "ポイント3"]
    },
    {
      "title": "カラム3タイトル",
      "icon_prompt": "アイコン生成用プロンプト",
      "icon_path": "",
      "points": ["ポイント1", "ポイント2", "ポイント3"]
    }
  ]
}
```

### TYPE_03 コンテンツ

```json
{
  "slide_number": 3,
  "type": "TYPE_03",
  "title": "スライドタイトル",
  "grid_cols": "repeat(3, 1fr)",
  "items": [
    {
      "category": "カテゴリ名",
      "icon_prompt": "アイコン生成用プロンプト",
      "icon_path": "",
      "description": "説明文"
    }
  ]
}
```

### TYPE_04 コンテンツ

```json
{
  "slide_number": 4,
  "type": "TYPE_04",
  "title": "スライドタイトル",
  "phases": [
    {
      "label": "Phase 1",
      "title": "フェーズタイトル",
      "details": ["詳細1", "詳細2"]
    }
  ],
  "result_label": "最終結果のラベル"
}
```

## GRID_COLS 自動計算ルール

| items数 | grid_cols | レイアウト |
|---------|-----------|-----------|
| 3件 | `repeat(3, 1fr)` | 3×1 |
| 4件 | `repeat(2, 1fr)` | 2×2 |
| 6件 | `repeat(3, 1fr)` | 3×2 |
| 8件 | `repeat(4, 1fr)` | 4×2 |
| 9件 | `repeat(3, 1fr)` | 3×3 |

## コンテンツ生成ガイドライン

- 各テキストは簡潔に（スライドに収まる量）
- タイトルは15文字以内
- ブロック本文は50文字以内
- 箇条書きは1項目20文字以内
- アイコンプロンプトはフラットデザイン指定
