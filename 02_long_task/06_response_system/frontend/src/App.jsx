import React, { useState, useEffect } from "react";

const API = "/api";

export default function App() {
  // マスタデータ
  const [containers, setContainers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [details, setDetails] = useState([]);

  // 選択状態
  const [containerId, setContainerId] = useState("");
  const [majorId, setMajorId] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [detailId, setDetailId] = useState("");

  // 条件質問
  const [conditions, setConditions] = useState([]);
  const [conditionAnswers, setConditionAnswers] = useState({});

  // プレースホルダ
  const [placeholders, setPlaceholders] = useState({ product_name: "" });

  // 生成結果
  const [result, setResult] = useState(null);

  // ステップ管理
  const [step, setStep] = useState(1);

  // エラー状態
  const [error, setError] = useState(null);

  // --- マスタ取得 ---
  useEffect(() => {
    fetch(`${API}/containers`)
      .then((r) => {
        if (!r.ok) throw new Error(`containers: ${r.status}`);
        return r.json();
      })
      .then(setContainers)
      .catch((e) => setError(`APIエラー: ${e.message}（バックエンドが起動しているか確認してください）`));
    fetch(`${API}/categories`)
      .then((r) => {
        if (!r.ok) throw new Error(`categories: ${r.status}`);
        return r.json();
      })
      .then(setCategories)
      .catch((e) => setError(`APIエラー: ${e.message}（バックエンドが起動しているか確認してください）`));
  }, []);

  // 中分類選択時に小分類を取得
  useEffect(() => {
    if (!categoryId) {
      setDetails([]);
      return;
    }
    fetch(`${API}/details/${categoryId}`)
      .then((r) => r.json())
      .then(setDetails);
  }, [categoryId]);

  // --- 中分類のリスト ---
  const selectedMajor = categories.find((c) => c.id === Number(majorId));
  const midCategories = selectedMajor ? selectedMajor.children : [];

  // --- Step 1: 条件質問を取得 ---
  const fetchConditions = async () => {
    const res = await fetch(`${API}/generate/preview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        container_id: Number(containerId),
        category_id: Number(categoryId),
        detail_id: Number(detailId),
      }),
    });
    if (!res.ok) {
      alert("エントリが見つかりません。容器と中分類の組み合わせを確認してください。");
      return;
    }
    const data = await res.json();
    setConditions(data.conditions);
    const initial = {};
    data.conditions.forEach((c) => (initial[c.label] = false));
    setConditionAnswers(initial);
    setStep(2);
  };

  // --- Step 2: 回答文生成 ---
  const generate = async () => {
    const res = await fetch(`${API}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        container_id: Number(containerId),
        category_id: Number(categoryId),
        detail_id: Number(detailId),
        condition_answers: conditionAnswers,
        placeholders,
      }),
    });
    const data = await res.json();
    setResult(data);
    setStep(3);
  };

  // --- リセット ---
  const reset = () => {
    setContainerId("");
    setMajorId("");
    setCategoryId("");
    setDetailId("");
    setConditions([]);
    setConditionAnswers({});
    setPlaceholders({ product_name: "" });
    setResult(null);
    setStep(1);
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>回答文作成システム</h1>

      {error && (
        <div style={styles.errorBanner}>
          {error}
        </div>
      )}

      {/* ── Step 1: 分類選択 ── */}
      {step >= 1 && (
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>1. 分類選択</h2>

          <div style={styles.formGrid}>
            <label style={styles.label}>
              容器
              <select
                style={styles.select}
                value={containerId}
                onChange={(e) => setContainerId(e.target.value)}
              >
                <option value="">選択してください</option>
                {containers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>

            <label style={styles.label}>
              大分類
              <select
                style={styles.select}
                value={majorId}
                onChange={(e) => {
                  setMajorId(e.target.value);
                  setCategoryId("");
                  setDetailId("");
                }}
              >
                <option value="">選択してください</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>

            <label style={styles.label}>
              中分類
              <select
                style={styles.select}
                value={categoryId}
                onChange={(e) => {
                  setCategoryId(e.target.value);
                  setDetailId("");
                }}
                disabled={!majorId}
              >
                <option value="">選択してください</option>
                {midCategories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>

            <label style={styles.label}>
              小分類
              <select
                style={styles.select}
                value={detailId}
                onChange={(e) => setDetailId(e.target.value)}
                disabled={!categoryId}
              >
                <option value="">選択してください</option>
                {details.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label style={{ ...styles.label, marginTop: 12 }}>
            商品名（プレースホルダ）
            <input
              style={styles.input}
              type="text"
              placeholder='例: 緑茶「まるごと茶葉」'
              value={placeholders.product_name}
              onChange={(e) =>
                setPlaceholders({ ...placeholders, product_name: e.target.value })
              }
            />
          </label>

          {step === 1 && (
            <button
              style={styles.button}
              disabled={!containerId || !categoryId || !detailId}
              onClick={fetchConditions}
            >
              次へ（追加条件の確認）
            </button>
          )}
        </div>
      )}

      {/* ── Step 2: 追加条件 ── */}
      {step >= 2 && (
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>2. 追加条件</h2>

          {conditions.length === 0 ? (
            <p style={styles.muted}>追加条件はありません</p>
          ) : (
            conditions.map((c) => (
              <label key={c.label} style={styles.checkLabel}>
                <input
                  type="checkbox"
                  checked={conditionAnswers[c.label] || false}
                  onChange={(e) =>
                    setConditionAnswers({
                      ...conditionAnswers,
                      [c.label]: e.target.checked,
                    })
                  }
                />
                {c.label}
              </label>
            ))
          )}

          {step === 2 && (
            <button style={styles.button} onClick={generate}>
              回答文を生成
            </button>
          )}
        </div>
      )}

      {/* ── Step 3: 結果 ── */}
      {step === 3 && result && (
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>3. 生成結果</h2>

          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>【調査結果】</h3>
            <p style={styles.body}>{result.investigation}</p>
          </div>
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>【製造工程】</h3>
            <p style={styles.body}>{result.process}</p>
          </div>
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>【まとめ】</h3>
            <p style={styles.body}>{result.summary}</p>
          </div>

          {result.applied_subs.length > 0 && (
            <details style={{ marginTop: 16 }}>
              <summary style={styles.muted}>
                適用されたサブ回答文（{result.applied_subs.length}件）
              </summary>
              <ul>
                {result.applied_subs.map((s, i) => (
                  <li key={i} style={styles.muted}>
                    [{s.position}] {s.condition_label || "自動付与"} - {s.body_preview}...
                  </li>
                ))}
              </ul>
            </details>
          )}

          <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
            <button style={styles.button} onClick={reset}>
              最初からやり直す
            </button>
            <button
              style={{ ...styles.button, background: "#059669" }}
              onClick={() => {
                navigator.clipboard.writeText(result.full_text);
                alert("クリップボードにコピーしました");
              }}
            >
              コピー
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 800,
    margin: "0 auto",
    padding: 24,
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    color: "#1a1a1a",
  },
  title: {
    fontSize: 24,
    fontWeight: 700,
    marginBottom: 24,
    borderBottom: "2px solid #2563eb",
    paddingBottom: 8,
  },
  card: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: 20,
    marginBottom: 16,
    boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 600,
    marginBottom: 16,
    color: "#2563eb",
  },
  formGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 12,
  },
  label: {
    display: "flex",
    flexDirection: "column",
    fontSize: 14,
    fontWeight: 500,
    gap: 4,
  },
  select: {
    padding: "8px 12px",
    border: "1px solid #d1d5db",
    borderRadius: 6,
    fontSize: 14,
  },
  input: {
    padding: "8px 12px",
    border: "1px solid #d1d5db",
    borderRadius: 6,
    fontSize: 14,
  },
  button: {
    marginTop: 16,
    padding: "10px 24px",
    background: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
  },
  checkLabel: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    fontSize: 14,
    marginBottom: 8,
  },
  section: {
    marginBottom: 16,
    padding: 12,
    background: "#f9fafb",
    borderRadius: 6,
    border: "1px solid #e5e7eb",
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: 600,
    marginBottom: 8,
    color: "#374151",
  },
  body: {
    fontSize: 14,
    lineHeight: 1.8,
    margin: 0,
    whiteSpace: "pre-wrap",
  },
  muted: {
    fontSize: 13,
    color: "#6b7280",
  },
  errorBanner: {
    padding: "12px 16px",
    background: "#fef2f2",
    border: "1px solid #fecaca",
    borderRadius: 8,
    color: "#dc2626",
    fontSize: 14,
    marginBottom: 16,
  },
};
