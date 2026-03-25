"""
2D画像生成クライアント

外部の画像生成API（DALL-E, Stable Diffusion等）を呼び出し、
スライド用の画像を生成する。

使用例:
    client = ImageGenClient(api_key="your-api-key")
    path = await client.generate("フラットデザインのロケットアイコン", output_dir="output")
"""

import base64
import json
import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ImageResult:
    """画像生成結果"""
    path: str
    prompt: str
    base64_data: str = ""

    def to_data_uri(self) -> str:
        """HTMLに埋め込むためのData URI形式で返す"""
        if self.base64_data:
            return f"data:image/png;base64,{self.base64_data}"
        if self.path and os.path.exists(self.path):
            with open(self.path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
        return ""


class ImageGenClient:
    """2D画像生成クライアント"""

    def __init__(self, api_key: str = "", provider: str = "placeholder"):
        """
        Args:
            api_key: API キー
            provider: 使用する画像生成サービス ("openai", "stability", "placeholder")
        """
        self.api_key = api_key or os.environ.get("IMAGE_GEN_API_KEY", "")
        self.provider = provider

    async def generate(
        self,
        prompt: str,
        output_dir: str = "output",
        width: int = 512,
        height: int = 512,
    ) -> ImageResult:
        """
        画像を生成する。

        Args:
            prompt: 画像生成プロンプト
            output_dir: 出力ディレクトリ
            width: 画像幅
            height: 画像高さ

        Returns:
            ImageResult: 生成結果
        """
        os.makedirs(output_dir, exist_ok=True)

        if self.provider == "placeholder":
            return self._generate_placeholder(prompt, output_dir, width, height)

        # 実際のAPI呼び出しはプロバイダーに応じて実装
        raise NotImplementedError(f"Provider '{self.provider}' is not yet implemented")

    def _generate_placeholder(
        self, prompt: str, output_dir: str, width: int, height: int
    ) -> ImageResult:
        """プレースホルダーSVGを生成（API未設定時のフォールバック）"""
        safe_name = "".join(c if c.isalnum() else "_" for c in prompt[:30])
        filename = f"{safe_name}.svg"
        filepath = os.path.join(output_dir, filename)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#f0f0f0" rx="8"/>
  <text x="50%" y="45%" text-anchor="middle" fill="#999" font-size="14"
        font-family="sans-serif">{prompt[:40]}</text>
  <text x="50%" y="55%" text-anchor="middle" fill="#ccc" font-size="12"
        font-family="sans-serif">{width}×{height}</text>
</svg>"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)

        b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        return ImageResult(
            path=filepath,
            prompt=prompt,
            base64_data=b64,
        )
