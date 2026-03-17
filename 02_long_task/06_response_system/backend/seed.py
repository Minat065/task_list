"""要件定義書 Section 5 のサンプルデータを投入する"""

from database import SessionLocal, engine, Base
from models import (
    Container,
    ManualEntry,
    ProblemCategory,
    ProblemDetail,
    ResponseTemplate,
    SubResponse,
)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # --- containers ---
    containers = [
        Container(id=1, name="350ml缶", description="スチール缶 350ml", sort_order=1),
        Container(id=2, name="500mlPETボトル", description="PETボトル 500ml", sort_order=2),
        Container(id=3, name="1LPETボトル", description="PETボトル 1L", sort_order=3),
        Container(id=4, name="200ml紙パック", description="紙容器 200ml", sort_order=4),
        Container(id=5, name="900mlパウチ", description="パウチ容器 900ml", sort_order=5),
        Container(id=6, name="280mlボトル缶", description="アルミボトル缶 280ml", sort_order=6),
    ]
    db.add_all(containers)

    # --- problem_categories ---
    categories = [
        # 大分類
        ProblemCategory(id=1, parent_id=None, depth=1, name="外観異常", sort_order=1),
        ProblemCategory(id=2, parent_id=None, depth=1, name="異物混入", sort_order=2),
        ProblemCategory(id=3, parent_id=None, depth=1, name="味・香り異常", sort_order=3),
        ProblemCategory(id=4, parent_id=None, depth=1, name="漏れ・破損", sort_order=4),
        # 中分類（漏れ・破損の下）
        ProblemCategory(id=40, parent_id=4, depth=2, name="亀裂", sort_order=1),
        ProblemCategory(id=41, parent_id=4, depth=2, name="漏れ跡", sort_order=2),
        ProblemCategory(id=42, parent_id=4, depth=2, name="缶蓋の亀裂", sort_order=3),
        ProblemCategory(id=43, parent_id=4, depth=2, name="変形", sort_order=4),
        ProblemCategory(id=44, parent_id=4, depth=2, name="接合不良", sort_order=5),
    ]
    db.add_all(categories)

    # --- problem_details ---
    details = [
        # 亀裂(40)の小分類
        ProblemDetail(id=1, category_id=40, name="小さな傷", description="表面の微小な傷", sort_order=1),
        ProblemDetail(id=2, category_id=40, name="大きな傷", description="明確に視認できる傷", sort_order=2),
        ProblemDetail(id=3, category_id=40, name="裂傷", description="缶体が裂けている", sort_order=3),
        ProblemDetail(id=4, category_id=40, name="押し込み", description="外部からの押圧による凹み", sort_order=4),
        # 漏れ跡(41)の小分類
        ProblemDetail(id=5, category_id=41, name="にじみ", description="微量の液体痕", sort_order=1),
        ProblemDetail(id=6, category_id=41, name="流出跡", description="明確な液だれ跡", sort_order=2),
        ProblemDetail(id=7, category_id=41, name="乾燥痕", description="乾いた漏れ跡", sort_order=3),
        # 缶蓋の亀裂(42)の小分類
        ProblemDetail(id=8, category_id=42, name="スコア割れ", description="開口部スコア線の亀裂", sort_order=1),
        ProblemDetail(id=9, category_id=42, name="巻締め部亀裂", description="巻締め部付近の亀裂", sort_order=2),
        ProblemDetail(id=10, category_id=42, name="リベット部亀裂", description="タブリベット周辺の亀裂", sort_order=3),
    ]
    db.add_all(details)

    # --- manual_entries ---
    entries = [
        ManualEntry(id=1, container_id=1, category_id=40, name="缶・亀裂"),
        ManualEntry(id=2, container_id=1, category_id=41, name="缶・漏れ跡"),
        ManualEntry(id=3, container_id=1, category_id=42, name="缶・缶蓋亀裂"),
        ManualEntry(id=4, container_id=2, category_id=40, name="PET・亀裂"),
    ]
    db.add_all(entries)

    # --- response_templates ---
    templates = [
        ResponseTemplate(
            id=1,
            manual_entry_id=1,
            section_type="investigation",
            body="お届けいたしました{{product_name}}に傷が確認された件につきまして、調査結果をご報告いたします。現品を確認したところ、缶体表面に傷が認められました。傷の形状および方向から、製造ラインの搬送過程において缶同士の接触により生じたものと判断いたしました。",
            sort_order=1,
        ),
        ResponseTemplate(
            id=2,
            manual_entry_id=1,
            section_type="process",
            body="当該製品の製造工程は以下の通りです。缶体成形 → 洗浄 → 充填 → 密封 → 殺菌 → 冷却 → 外観検査 → 梱包。外観検査工程ではカメラによる自動検査を実施しております。",
            sort_order=1,
        ),
        ResponseTemplate(
            id=3,
            manual_entry_id=1,
            section_type="summary",
            body="このたびはご不快な思いをおかけしましたことを深くお詫び申し上げます。搬送ラインのガイド調整を実施し、缶同士の接触を低減する対策を講じました。",
            sort_order=1,
        ),
    ]
    db.add_all(templates)

    # --- sub_responses ---
    subs = [
        SubResponse(id=1, template_id=1, detail_id=1, condition_label=None, position="after", body="なお、傷は微小であり、内容物への影響はございません。", sort_order=1),
        SubResponse(id=2, template_id=1, detail_id=2, condition_label=None, position="after", body="傷の深さから内容物への影響が懸念されたため、外部検査機関による分析を実施いたしました。", sort_order=1),
        SubResponse(id=3, template_id=1, detail_id=3, condition_label=None, position="after", body="缶体が裂けており、内容物の漏出が確認されました。健康被害の有無を確認するため、外部検査機関に分析を依頼いたしました。", sort_order=1),
        SubResponse(id=4, template_id=1, detail_id=None, condition_label="流通経路による場合", position="after", body="流通過程における取り扱い状況を確認いたしましたところ、輸送時の振動により缶体に負荷がかかった可能性が認められました。", sort_order=2),
        SubResponse(id=5, template_id=2, detail_id=None, condition_label="流通経路による場合", position="before", body="なお、本件は製造工程内ではなく、流通過程で生じた可能性が高いと判断しております。", sort_order=1),
        SubResponse(id=6, template_id=3, detail_id=3, condition_label=None, position="after", body="本件につきまして、保健所への報告を併せて行っております。", sort_order=1),
        SubResponse(id=7, template_id=1, detail_id=None, condition_label="当たったものが明確な場合", position="after", body="接触対象物の成分を分析した結果、{{contact_object}}由来の痕跡が確認されました。", sort_order=3),
    ]
    db.add_all(subs)

    db.commit()
    db.close()
    print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed()
