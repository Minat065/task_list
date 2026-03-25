"""
HTML Presentation Builder

Content Agent の JSON 出力を受け取り、型別テンプレートに流し込み、
reveal.js ベースの単一 HTML プレゼンテーションを生成する。

使用例:
    python build.py --input content.json --output output/presentation.html
    python build.py --demo  # デモプレゼンを生成
"""

import argparse
import json
import os
import sys
from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "output"


def load_template(name: str) -> str:
    """テンプレートファイルを読み込む"""
    path = TEMPLATES_DIR / name
    return path.read_text(encoding="utf-8")


def render_type01(slide: dict) -> str:
    """TYPE_01: ビジュアル＋解説型をレンダリング"""
    template = load_template("type01.html")

    # ビジュアル部分
    visual = slide.get("visual", {})
    if visual.get("type") == "3d" and visual.get("path"):
        visual_html = (
            f'<model-viewer data-id="hero-3d" src="{visual["path"]}" '
            f'auto-rotate camera-controls style="width:100%;height:100%">'
            f"</model-viewer>"
        )
    elif visual.get("path"):
        visual_html = f'<img src="{visual["path"]}" alt="{slide.get("title", "")}">'
    else:
        visual_html = (
            '<div style="background:#f0f0f0;width:100%;height:100%;'
            'display:flex;align-items:center;justify-content:center;'
            'border-radius:8px;color:#999;">ビジュアル</div>'
        )

    # ブロック部分
    blocks = slide.get("blocks", [])
    blocks_html = ""
    for block in blocks:
        blocks_html += (
            f'<div class="block">\n'
            f'  <h4>{block.get("title", "")}</h4>\n'
            f'  <p>{block.get("body", "")}</p>\n'
            f"</div>\n"
        )

    html = template.replace("{{ TITLE }}", slide.get("title", ""))
    html = html.replace("{{ VISUAL }}", visual_html)
    html = html.replace("{{ BLOCKS }}", blocks_html)
    html = html.replace("{{ BOTTOM_MESSAGE }}", slide.get("bottom_message", ""))
    return html


def render_type02(slide: dict) -> str:
    """TYPE_02: 3列比較型をレンダリング"""
    template = load_template("type02.html")

    columns = slide.get("columns", [])
    cols_html = ""
    for col in columns:
        icon_path = col.get("icon_path", "")
        icon_html = (
            f'<img src="{icon_path}">'
            if icon_path
            else '<div style="font-size:3em;color:#ccc;">●</div>'
        )
        points_html = "\n".join(f"        <li>{p}</li>" for p in col.get("points", []))
        cols_html += (
            f'<div class="column">\n'
            f'  <div class="col-header">{col.get("title", "")}</div>\n'
            f'  <div class="col-icon">{icon_html}</div>\n'
            f"  <ul>\n{points_html}\n  </ul>\n"
            f"</div>\n"
        )

    html = template.replace("{{ TITLE }}", slide.get("title", ""))
    html = html.replace("{{ COLUMNS }}", cols_html)
    return html


def render_type03(slide: dict) -> str:
    """TYPE_03: グリッド一覧型をレンダリング"""
    template = load_template("type03.html")

    items = slide.get("items", [])
    grid_cols = slide.get("grid_cols", "repeat(3, 1fr)")

    items_html = ""
    for item in items:
        icon_path = item.get("icon_path", "")
        icon_html = (
            f'<img src="{icon_path}">'
            if icon_path
            else '<div style="font-size:2em;color:#ccc;">◆</div>'
        )
        items_html += (
            f'<div class="cell">\n'
            f'  <div class="cell-header">{item.get("category", "")}</div>\n'
            f'  <div class="cell-icon">{icon_html}</div>\n'
            f'  <div class="cell-desc">{item.get("description", "")}</div>\n'
            f"</div>\n"
        )

    html = template.replace("{{ TITLE }}", slide.get("title", ""))
    html = html.replace("{{ GRID_COLS }}", grid_cols)
    html = html.replace("{{ ITEMS }}", items_html)
    return html


def render_type04(slide: dict) -> str:
    """TYPE_04: フェーズ/プロセス型をレンダリング"""
    template = load_template("type04.html")

    phases = slide.get("phases", [])
    phase_count = str(len(phases))

    # フェーズ楕円
    phases_html = ""
    for phase in phases:
        phases_html += (
            f'<div class="phase-oval">\n'
            f'  <small>{phase.get("label", "")}</small>\n'
            f'  <div>{phase.get("title", "")}</div>\n'
            f"</div>\n"
        )

    # 詳細行
    details_html = ""
    for phase in phases:
        points = "\n".join(
            f"      <li>{p}</li>" for p in phase.get("details", [])
        )
        details_html += (
            f'<div class="detail-box">\n'
            f"  <ul>\n{points}\n  </ul>\n"
            f"</div>\n"
        )

    html = template.replace("{{ TITLE }}", slide.get("title", ""))
    html = html.replace("{{ PHASE_COUNT }}", phase_count)
    html = html.replace("{{ PHASES }}", phases_html)
    html = html.replace("{{ RESULT_LABEL }}", slide.get("result_label", ""))
    html = html.replace("{{ DETAILS }}", details_html)
    return html


RENDERERS = {
    "TYPE_01": render_type01,
    "TYPE_02": render_type02,
    "TYPE_03": render_type03,
    "TYPE_04": render_type04,
}


def build_presentation(content: dict, output_path: str | None = None) -> str:
    """
    コンテンツJSONからプレゼンテーションHTMLを生成する。

    Args:
        content: Content Agent の出力JSON
        output_path: 出力先パス（Noneの場合はデフォルト）

    Returns:
        生成されたHTMLファイルのパス
    """
    base = load_template("base.html")
    slides_html = ""

    for slide in content.get("slides", []):
        slide_type = slide.get("type", "TYPE_01")
        renderer = RENDERERS.get(slide_type)
        if renderer:
            slides_html += renderer(slide) + "\n"
        else:
            print(f"Warning: Unknown slide type '{slide_type}', skipping", file=sys.stderr)

    title = content.get("title", "Presentation")
    html = base.replace("{{ TITLE }}", title)
    html = html.replace("{{ SLIDES }}", slides_html)

    if output_path is None:
        output_path = str(OUTPUT_DIR / "presentation.html")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Generated: {output_path}")
    return output_path


def demo_content() -> dict:
    """デモ用コンテンツを返す"""
    return {
        "title": "プロダクト紹介デモ",
        "slides": [
            {
                "slide_number": 1,
                "type": "TYPE_01",
                "title": "革新的なプロダクト",
                "visual": {"type": "image", "path": ""},
                "blocks": [
                    {"title": "高性能", "body": "最新技術で従来比200%の処理速度を実現"},
                    {"title": "省エネ", "body": "消費電力を50%削減する独自アーキテクチャ"},
                    {"title": "コンパクト", "body": "従来機の1/3のサイズで設置場所を選ばない"},
                ],
                "bottom_message": "2026年4月発売予定 ｜ 詳細はお問い合わせください",
            },
            {
                "slide_number": 2,
                "type": "TYPE_02",
                "title": "選ばれる3つの理由",
                "columns": [
                    {
                        "title": "信頼性",
                        "icon_path": "",
                        "points": ["稼働率99.99%", "24時間監視体制", "冗長構成標準"],
                    },
                    {
                        "title": "拡張性",
                        "icon_path": "",
                        "points": ["モジュール式設計", "API連携対応", "クラウドネイティブ"],
                    },
                    {
                        "title": "サポート",
                        "icon_path": "",
                        "points": ["専任エンジニア配置", "SLA保証", "導入支援プログラム"],
                    },
                ],
            },
            {
                "slide_number": 3,
                "type": "TYPE_03",
                "title": "導入実績",
                "grid_cols": "repeat(3, 1fr)",
                "items": [
                    {"category": "製造業", "icon_path": "", "description": "生産ライン最適化で30%効率向上"},
                    {"category": "金融", "icon_path": "", "description": "リアルタイム分析で意思決定を高速化"},
                    {"category": "医療", "icon_path": "", "description": "画像診断の精度を95%以上に向上"},
                    {"category": "小売", "icon_path": "", "description": "需要予測で在庫コスト40%削減"},
                    {"category": "物流", "icon_path": "", "description": "配送ルート最適化で配送時間20%短縮"},
                    {"category": "教育", "icon_path": "", "description": "個別学習プランで学習効果2倍"},
                ],
            },
            {
                "slide_number": 4,
                "type": "TYPE_04",
                "title": "導入プロセス",
                "phases": [
                    {"label": "Phase 1", "title": "ヒアリング", "details": ["現状課題の把握", "要件定義", "ゴール設定"]},
                    {"label": "Phase 2", "title": "設計", "details": ["アーキテクチャ設計", "データフロー定義", "セキュリティ設計"]},
                    {"label": "Phase 3", "title": "導入", "details": ["環境構築", "データ移行", "テスト実行"]},
                    {"label": "Phase 4", "title": "運用", "details": ["モニタリング開始", "最適化チューニング", "定期レビュー"]},
                ],
                "result_label": "✓ 平均3ヶ月で本番稼働開始",
            },
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="HTML Presentation Builder")
    parser.add_argument("--input", "-i", help="Content JSON file path")
    parser.add_argument("--output", "-o", help="Output HTML file path")
    parser.add_argument("--demo", action="store_true", help="Generate demo presentation")
    args = parser.parse_args()

    if args.demo:
        content = demo_content()
    elif args.input:
        with open(args.input, encoding="utf-8") as f:
            content = json.load(f)
    else:
        parser.print_help()
        sys.exit(1)

    build_presentation(content, args.output)


if __name__ == "__main__":
    main()
