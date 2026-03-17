# 回答文作成システム 要件定義書

**作成日**: 2026-03-17
**ステータス**: ドラフト

---

## 1. プロジェクト概要

### 1.1 背景
商品に問題があった場合、原因調査を行い、その結果をお客様へ回答する業務が存在する。
現状はExcelベースのマニュアル集から適切な回答パターンを手動で選択し、回答文を作成している。
このプロセスをシステム化し、正確性の向上と作業効率の改善を図る。

### 1.2 現状の課題
- マニュアル集から適切な回答パターンを探す手間がかかる
- 条件に応じた追記の漏れリスクがある
- 回答の品質が担当者のスキルに依存する
- 回答履歴の管理・検索が困難

### 1.3 ゴール
条件を選択・入力することで、適切な回答文を自動生成するシステムを構築する。

---

## 2. 業務フロー

```
[問題発生] → [原因調査] → [システムで条件入力] → [回答文自動生成] → [確認・編集] → [お客様へ送付]
```

### 2.1 ユーザー操作フロー
1. 容器の種類を選択
2. 問題点を選択（大分類 → 中分類 → 小分類）
3. 程度・条件を入力/選択
4. システムが該当するマニュアル（テンプレート）を自動で特定
5. 回答文（調査結果/製造工程/まとめ）を自動生成
6. 条件に応じた追記が自動付与される
7. ユーザーが確認・必要に応じて編集
8. 最終成果物を出力

---

## 3. 機能要件

### 3.1 マスタ管理機能
- **容器マスタ**: 容器の種類を管理（6〜20種類、追加可能）
- **問題分類マスタ**: 3階層以上の階層構造で問題点を管理
- **条件マスタ**: 程度・条件のパターンを管理
- **テンプレートマスタ**: 回答文テンプレートを管理

### 3.2 回答文生成機能
- 条件の組み合わせから該当テンプレートを自動特定
- 3パート構成の回答文を生成:
  - **調査結果**: 調査内容と判明した原因
  - **製造工程**: 関連する製造工程の説明
  - **まとめ**: 結論と今後の対応
- 条件に応じた追記の自動付与
- 生成後の手動編集機能

### 3.3 出力機能
- 画面上でのプレビュー
- ファイル出力（形式は後続フェーズで決定）

### 3.4 履歴管理機能
- 過去の回答文を検索・参照
- どの条件で生成されたかの記録

---

## 4. DB設計（コア）

### 4.1 ER図（概念）

```
[containers]               [problem_categories]
容器マスタ                   問題分類マスタ（階層構造）
 |                            |
 |   [conditions]             |
 |   条件マスタ               |
 |     |                      |
 +-----+------+---------------+
               |
        [manual_entries]
        マニュアルエントリ
        （容器×問題分類×条件 → テンプレート群への紐付け）
               |
               |
   +-----------+-----------+
   |           |           |
[templates_investigation]  |  [templates_summary]
 調査結果テンプレート       |   まとめテンプレート
               |
   [templates_process]
    製造工程テンプレート

               |
        [appendices]
        追記テンプレート
        （条件付き追記）

        [response_history]
        回答履歴
```

### 4.2 テーブル定義

#### 4.2.1 containers（容器マスタ）
| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | 容器ID |
| name | VARCHAR | 容器名（例: 缶、ボトル、パウチ） |
| description | TEXT | 備考 |
| sort_order | INT | 表示順 |
| is_active | BOOLEAN | 有効フラグ |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

#### 4.2.2 problem_categories（問題分類マスタ）
階層構造を自己参照で実現する。

| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | 分類ID |
| parent_id | INT FK(self) | 親分類ID（NULLならルート） |
| depth | INT | 階層の深さ（1=大分類, 2=中分類, 3=小分類） |
| name | VARCHAR | 分類名 |
| description | TEXT | 備考 |
| sort_order | INT | 同階層内の表示順 |
| is_active | BOOLEAN | 有効フラグ |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

#### 4.2.3 conditions（条件マスタ）
問題の程度や状態など、テンプレート選択に影響する条件を管理。

| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | 条件ID |
| condition_group | VARCHAR | 条件グループ（例: "程度", "範囲", "頻度"） |
| name | VARCHAR | 条件名（例: "軽微", "重度"） |
| description | TEXT | 備考 |
| sort_order | INT | 表示順 |
| is_active | BOOLEAN | 有効フラグ |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

#### 4.2.4 manual_entries（マニュアルエントリ）
容器×問題分類×条件の組み合わせを管理するハブテーブル。

| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | エントリID |
| container_id | INT FK | 容器ID |
| problem_category_id | INT FK | 問題分類ID（末端の分類を指定） |
| name | VARCHAR | エントリ名（管理用） |
| description | TEXT | 備考 |
| is_active | BOOLEAN | 有効フラグ |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

#### 4.2.5 manual_entry_conditions（エントリ×条件 中間テーブル）
1つのエントリに複数の条件を紐付ける。

| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | ID |
| manual_entry_id | INT FK | エントリID |
| condition_id | INT FK | 条件ID |

#### 4.2.6 response_templates（回答テンプレート）
各パートのテンプレート本文を管理。

| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | テンプレートID |
| manual_entry_id | INT FK | マニュアルエントリID |
| section_type | ENUM | パート種別: 'investigation' / 'process' / 'summary' |
| body | TEXT | テンプレート本文（プレースホルダ対応） |
| sort_order | INT | 同セクション内の表示順 |
| is_active | BOOLEAN | 有効フラグ |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

#### 4.2.7 appendices（追記テンプレート）
条件に応じて各パートに追加される追記を管理。

| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | 追記ID |
| section_type | ENUM | 追記対象パート: 'investigation' / 'process' / 'summary' |
| body | TEXT | 追記本文 |
| sort_order | INT | 追記の表示順 |
| is_active | BOOLEAN | 有効フラグ |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

#### 4.2.8 appendix_conditions（追記の適用条件）
どの条件の時にどの追記を付与するかのルールを管理。

| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | ID |
| appendix_id | INT FK | 追記ID |
| container_id | INT FK NULL | 容器ID（NULLなら全容器対象） |
| problem_category_id | INT FK NULL | 問題分類ID（NULLなら全分類対象） |
| condition_id | INT FK NULL | 条件ID（NULLなら条件不問） |

#### 4.2.9 response_history（回答履歴）
生成された回答の履歴を記録。

| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | 履歴ID |
| manual_entry_id | INT FK | 使用したエントリID |
| container_id | INT FK | 容器ID |
| problem_category_id | INT FK | 問題分類ID |
| generated_text | TEXT | 生成された回答文全文 |
| edited_text | TEXT NULL | 編集後の回答文（編集があった場合） |
| created_by | VARCHAR | 作成者 |
| created_at | TIMESTAMP | 作成日時 |

#### 4.2.10 response_history_conditions（履歴×条件）
履歴にどの条件が選択されていたかを記録。

| カラム名 | 型 | 説明 |
|---------|------|------|
| id | INT PK | ID |
| response_history_id | INT FK | 履歴ID |
| condition_id | INT FK | 条件ID |

---

## 5. DB設計のポイント

### 5.1 階層構造の表現
- `problem_categories` テーブルの自己参照（`parent_id`）で任意の深さの階層を表現
- `depth` カラムでUI表示時の階層判定を高速化
- 将来的に4階層以上に拡張しても構造変更不要

### 5.2 柔軟な条件マッチング
- `manual_entries` がハブとなり、容器×問題分類の組み合わせを管理
- `manual_entry_conditions` で複数条件をAND/ORで紐付け可能
- 条件は `condition_group` でグループ化し、UI上の入力フォームを動的生成可能に

### 5.3 追記の条件付き適用
- `appendix_conditions` でNULLを「全対象」として扱うことで、柔軟なルール設定が可能
  - 例: container_id=NULL, condition_id=3 → 「全容器で条件3の時に追記」
  - 例: container_id=1, condition_id=NULL → 「容器1の時は常に追記」

### 5.4 テンプレートの構成
- `response_templates` で3パート（調査結果/製造工程/まとめ）を個別管理
- 本文にプレースホルダ（例: `{{container_name}}`, `{{problem_detail}}`）を埋め込み、動的に置換

---

## 6. 非機能要件

| 項目 | 要件 |
|------|------|
| 利用者数 | 6〜20名 |
| 同時利用 | 5名程度を想定 |
| 可用性 | 業務時間内（平日日中）に利用可能であること |
| データ量 | 容器: 〜20種類、問題分類: 〜数百件、テンプレート: 〜数千件 |
| セキュリティ | 社内ネットワークからのアクセスに限定（想定） |

---

## 7. 今後の検討事項

- [ ] 技術スタック選定（Web/デスクトップ、言語、フレームワーク）
- [ ] 出力フォーマットの最終決定（Excel / Word / PDF / HTML）
- [ ] ユーザー認証・権限管理の要否
- [ ] 既存マニュアル（Excel）からのデータ移行方法
- [ ] テンプレート内のプレースホルダ仕様の詳細化
- [ ] 条件マッチングロジックの詳細設計（AND/OR/優先度）
- [ ] UI/UXデザイン

---

## 8. 用語集

| 用語 | 意味 |
|------|------|
| 容器 | 商品の容器種別（缶、ボトル等） |
| 問題分類 | 問題点の階層的な分類体系 |
| 条件 | 問題の程度や状態を示す属性 |
| マニュアルエントリ | 容器×問題分類×条件の組み合わせに対応するマニュアル項目 |
| テンプレート | 回答文の雛形（プレースホルダを含む） |
| 追記 | 特定条件下で回答文に追加されるテキスト |
| パート | 回答文の構成要素（調査結果/製造工程/まとめ） |
