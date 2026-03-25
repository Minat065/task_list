# Slide Agent — HTML Presentation Builder

## 概要
プレゼン資料のテーマ・内容を受け取り、スライド型を判定し、
型別にコンテンツを生成し、reveal.js ベースの HTML プレゼンを出力するオーケストレーター。

## アーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│                 CLAUDE.md (Orchestrator)             │
└────┬──────────────┬──────────────┬──────────────────┘
     │              │              │
┌────▼────┐  ┌──────▼──────┐ ┌────▼─────────────────┐
│Classifier│  │Content Agent│ │   HTML Builder Agent  │
│          │  │             │ │                       │
│型判定    │  │型別文章生成  │ │reveal.js構造生成      │
│→JSON    │  │→JSON        │ │CSS Grid型別レイアウト  │
└─────────┘  └─────────────┘ │3D: model-viewer       │
                              │アニメーション設定      │
                              └───────────────────────┘
```

## ワークフロー

1. **ユーザー入力**: プレゼンのテーマ、対象、目的を受け取る
2. **Classifier** (`skills/slide-type-classifier/`): 各スライドの型を判定 → JSON
3. **Content Agent** (`skills/content-by-type/`): 型に応じたコンテンツ生成 → JSON
4. **HTML Builder** (`skills/html-builder/`): テンプレートにコンテンツ流し込み → `output/presentation.html`

## スライド型

| 型 | 用途 | レイアウト |
|----|------|-----------|
| TYPE_01 | ビジュアル＋解説 | 左60%ビジュアル + 右3段スタック + 下バー |
| TYPE_02 | 3列比較 | 3カラム（ヘッダー+アイコン+箇条書き） |
| TYPE_03 | グリッド一覧 | N×M グリッド（件数から自動算出） |
| TYPE_04 | フェーズ/プロセス | 楕円フロー + 結果バー + 詳細行 |

## ツール

- `tools/image_gen_client.py` — 2D画像生成クライアント
- `tools/rodin_client.py` — GLB生成（3D必要時のみ）

## 出力

- `output/presentation.html` — 単一HTMLファイルで完結
- 外部依存は CDN のみ（reveal.js, model-viewer）
- ブラウザで即確認可能
