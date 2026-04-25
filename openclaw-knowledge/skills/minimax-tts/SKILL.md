---
name: minimax-tts
description: Generate speech audio using MiniMax TTS API. Supports text-to-speech with various voices, emotions, and streaming.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎤",
        "os": ["linux", "darwin", "windows"],
        "requires": { "env": ["MINIMAX_API_KEY"] },
        "install": [],
      },
  }
---

# MiniMax Text-to-Speech (TTS) CLI

Generate speech audio using MiniMax's TTS API with support for various voices, emotions, and streaming output.

## When to Use

✅ **USE this skill when:**

- User wants to convert text to speech
- Need different voices and emotions
- Generate speech in Chinese or English
- Save audio to file

## When NOT to Use

❌ **DON'T use this skill when:**

- User asks for music generation → use `minimax-music` skill
- Need voice cloning → not supported in this skill
- Using other TTS APIs (Google, Azure, etc.)

## Setup

1. Get API Key from [MiniMax Platform](https://platform.minimax.io/user-center/basic-information/interface-key)
2. Set environment variable:
   ```bash
   export MINIMAX_API_KEY="your_api_key"
   ```
3. Or pass via `--api-key` argument

## Command Line Usage

### Basic Text-to-Speech

```bash
python /home/pi/.openclaw/workspace/skills/minimax-tts/minimax_tts.py \
  --text "你好，世界！" \
  --output /tmp/speech.mp3
```

### With Voice and Emotion

```bash
python /home/pi/.openclaw/workspace/skills/minimax-tts/minimax_tts.py \
  --text "The time is limited!" \
  --voice male-qn-qingse \
  --emotion angry \
  --output /tmp/speech.mp3
```

### Streaming Mode

```bash
python /home/pi/.openclaw/workspace/skills/minimax-tts/minimax_tts.py \
  --text "这是一段很长的文本..." \
  --stream \
  --output /tmp/stream.mp3
```

## Parameters

| 参数 | 说明 | 默认值 | 可选值 |
| :--- | :--- | :--- | :--- |
| `--text` | 要转换的文本 | 必填 | 最多10000字符 |
| `--model` | 使用的模型 | `speech-2.8-hd` | `speech-2.8-hd`, `speech-2.8-turbo` |
| `--voice` | 声音ID | `male-qn-qingse` | 见下方语音列表 |
| `--speed` | 语速 | `1` | 0.5-2.0 |
| `--emotion` | 情感 | `neutral` | `neutral`, `happy`, `sad`, `angry`, `fearful` |
| `--format` | 音频格式 | `mp3` | `mp3`, `wav`, `aac` |
| `--sample-rate` | 采样率 | `32000` | `16000`, `32000` |
| `--stream` | 流式输出 | `false` | `true`, `false` |
| `--output` | 输出文件路径 | `./output.mp3` | 任意路径 |
| `--api-key` | API密钥 | 环境变量 | API Key |

## Available Voices

| Voice ID | Description |
| :--- | :--- |
| `male-qn-qingse` | 青涩青年 |
| `male-qn-jingying` | 精英青年 |
| `male-qn-badao` | 霸道总裁 |
| `female-shaonv` | 活泼少女 |
| `female-yujie` | 温柔御姐 |
| `female-chengshu` | 成熟女性 |

## Example: Warcraft III Arthas Voice

```bash
python /home/pi/.openclaw/workspace/skills/minimax-tts/minimax_tts.py \
  --text "The time is limited!" \
  --voice male-qn-badao \
  --emotion angry \
  --output /tmp/arthas.mp3
```

## Output

- Audio file saved to specified `--output` path
- Format: MP3/WAV/AAC based on `--format`
- Console shows progress and file info
