"""
3D GLB 生成クライアント (Rodin API)

3Dモデルが必要な場合にGLBファイルを生成する。
model-viewerで表示するためのGLBを返す。

使用例:
    client = RodinClient(api_key="your-api-key")
    path = await client.generate("白いスニーカー", output_dir="output")
"""

import base64
import os
from dataclasses import dataclass


@dataclass
class GLBResult:
    """GLB生成結果"""
    path: str
    prompt: str
    base64_data: str = ""

    def to_data_uri(self) -> str:
        """HTMLに埋め込むためのData URI形式で返す"""
        if self.base64_data:
            return f"data:model/gltf-binary;base64,{self.base64_data}"
        if self.path and os.path.exists(self.path):
            with open(self.path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:model/gltf-binary;base64,{encoded}"
        return ""


class RodinClient:
    """Rodin 3Dモデル生成クライアント"""

    def __init__(self, api_key: str = "", endpoint: str = ""):
        """
        Args:
            api_key: Rodin API キー
            endpoint: API エンドポイントURL
        """
        self.api_key = api_key or os.environ.get("RODIN_API_KEY", "")
        self.endpoint = endpoint or os.environ.get(
            "RODIN_ENDPOINT", "https://hyperhuman.deemos.com/api"
        )

    async def generate(
        self,
        prompt: str,
        output_dir: str = "output",
    ) -> GLBResult:
        """
        3Dモデル(GLB)を生成する。

        Args:
            prompt: 3Dモデル生成プロンプト
            output_dir: 出力ディレクトリ

        Returns:
            GLBResult: 生成結果
        """
        os.makedirs(output_dir, exist_ok=True)

        if not self.api_key:
            return self._generate_placeholder(prompt, output_dir)

        # 実際のRodin API呼び出し
        raise NotImplementedError("Rodin API integration not yet implemented")

    def _generate_placeholder(self, prompt: str, output_dir: str) -> GLBResult:
        """プレースホルダー（API未設定時のフォールバック）

        実際のGLBは生成せず、メタデータのみ返す。
        HTML側では代替画像が表示される。
        """
        safe_name = "".join(c if c.isalnum() else "_" for c in prompt[:30])
        meta_path = os.path.join(output_dir, f"{safe_name}_3d_placeholder.json")

        import json
        meta = {
            "type": "placeholder",
            "prompt": prompt,
            "message": "Rodin API key not configured. Set RODIN_API_KEY env var.",
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        return GLBResult(path="", prompt=prompt, base64_data="")
