# HTML Builder Skill

## 役割
Content AgentのJSONをHTMLテンプレートに流し込み、
reveal.jsで動くプレゼンを1ファイルで出力する。

## 出力仕様
- 単一HTMLファイル（output/presentation.html）
- 外部依存はCDNのみ（配布しやすい）
- 3DアセットはBase64でHTMLに埋め込む（完全1ファイル化）

## 型別テンプレート選択
```
type: "TYPE_01" → templates/type01.html
type: "TYPE_02" → templates/type02.html
type: "TYPE_03" → templates/type03.html
type: "TYPE_04" → templates/type04.html
```

## 3D処理
TYPE_01でneeds_3d=trueの場合:
  `<model-viewer>`タグを使用
  GLBはBase64変換してsrcに直接埋め込む:
  `src="data:model/gltf-binary;base64,{base64data}"`

  PPTXのMorphに相当する演出:
  → reveal.jsのauto-animateを使用
  → 同じdata-id属性を持つ要素がスライド間でスムーズに遷移する

## auto-animate（MorphのHTML版）

```html
<!-- スライドN -->
<section data-auto-animate>
  <model-viewer data-id="hero-3d"
    style="transform: rotateY(0deg)">
  </model-viewer>
</section>

<!-- スライドN+1 -->
<section data-auto-animate>
  <model-viewer data-id="hero-3d"
    style="transform: rotateY(45deg)">
  </model-viewer>
</section>
```
→ reveal.jsが自動で補間アニメーションする

## GRID_COLS自動計算
items数 → CSSのgrid-template-columns:
```
6件 → "repeat(3, 1fr)"  (3×2)
8件 → "repeat(4, 1fr)"  (4×2)
```

## ビルド手順

1. `templates/base.html` を読み込む
2. Content Agent JSON の各スライドを型別テンプレートで展開
3. 展開済みスライドHTMLを `base.html` の `{{ SLIDES }}` に挿入
4. 3Dアセットがある場合はBase64エンコードして埋め込む
5. `output/presentation.html` に書き出す
