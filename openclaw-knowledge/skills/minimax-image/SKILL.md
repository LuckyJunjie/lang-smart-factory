---
name: minimax-image
description: Generate images using MiniMax image-01 model via CLI. Supports text-to-image and image-to-image generation.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "os": ["linux", "darwin", "windows"],
        "requires": { "env": ["MINIMAX_API_KEY"] },
        "install": [],
      },
  }
---

# MiniMax Image Generation CLI

Generate images using MiniMax's `image-01` model directly from the terminal.

## When to Use

✅ **USE this skill when:**

- User wants to generate images from text descriptions
- Need image-to-image generation with reference images
- Batch generate multiple images
- Save images to specific output directory

## When NOT to Use

❌ **DON'T use this skill when:**

- User asks for image analysis → use `image` tool
- Need real-time streaming generation → not supported
- Using other image APIs (DALL-E, Midjourney, etc.)

## Setup

1. Get API Key from [MiniMax Platform](https://platform.minimax.io/user-center/basic-information/interface-key)
2. Set environment variable:
   ```bash
   export MINIMAX_API_KEY="your_api_key"
   ```
3. Or pass via `--api-key` argument

## Command Line Usage

### Text-to-Image (Basic)

```bash
python /home/pi/.openclaw/workspace/skills/minimax-image/minimax_image.py \
  --prompt "一只可爱的橘猫在阳光明媚的下午打盹" \
  --output-dir ./images
```

### Text-to-Image (Advanced)

```bash
python /home/pi/.openclaw/workspace/skills/minimax-image/minimax_image.py \
  --prompt "未来城市天际线，赛博朋克风格" \
  --aspect-ratio "16:9" \
  --num-images 4 \
  --response-format "url" \
  --prompt-optimizer \
  --output-dir ./cyberpunk
```

### Image-to-Image (图生图)

```bash
python /home/pi/.openclaw/workspace/skills/minimax-image/minimax_image.py \
  --prompt "相同角色，现在穿着宇航服" \
  --subject-reference "https://example.com/character.jpg" \
  --aspect-ratio "9:16" \
  --output-dir ./space
```

## Parameters

| 参数 | 说明 | 默认值 | 可选值 |
| :--- | :--- | :--- | :--- |
| `--prompt` | 图像生成的文本描述 | 必填 | 最多1500字符 |
| `--model` | 使用的模型 | `image-01` | `image-01`, `image-01-live` |
| `--aspect-ratio` | 宽高比 | `1:1` | `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9` |
| `--num-images` | 生成数量 | `1` | 1-9 |
| `--response-format` | 返回格式 | `url` | `url`, `base64` |
| `--output-dir` | 保存目录 | `./output` | 任意路径 |
| `--subject-reference` | 参考图片URL | 无 | 有效图片URL |
| `--prompt-optimizer` | 启用提示词优化 | False | True/False |
| `--api-key` | API密钥(可选) | 环境变量 | API Key |

## Integration with OpenClaw

This skill can be called from OpenClaw sessions:

```
User: 生成一张猫的图片
→ Use minimax-image skill with prompt "可爱的橘猫"
```

## Output

- Images saved to specified `--output-dir`
- Filenames: `generated_1.png`, `generated_2.png`, etc.
- Console shows progress and saved file paths