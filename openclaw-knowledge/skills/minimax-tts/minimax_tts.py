#!/usr/bin/env python3
"""
MiniMax Text-to-Speech CLI Tool
Generate speech using MiniMax TTS API
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Default API endpoint for domestic (CN) users
DEFAULT_API_URL = "https://api.minimaxi.com/v1/t2a_v2"

# Available voices
VOICES = {
    "male-qn-qingse": "青涩青年",
    "male-qn-jingying": "精英青年",
    "male-qn-badao": "霸道总裁",
    "female-shaonv": "活泼少女",
    "female-yujie": "温柔御姐",
    "female-chengshu": "成熟女性",
}

# Available emotions
EMOTIONS = ["neutral", "happy", "sad", "angry", "fearful"]


def load_config():
    """Load API configuration from environment"""
    api_key = os.environ.get("MINIMAX_API_KEY")
    return api_key


def generate_speech(text, api_key, model="speech-2.8-hd", voice_id="male-qn-qingse",
                   speed=1.0, vol=1.0, pitch=0, emotion="neutral",
                   sample_rate=32000, bitrate=128000, audio_format="mp3",
                   stream=False, output_path="./output.mp3"):
    """Generate speech using MiniMax TTS API"""
    
    url = DEFAULT_API_URL
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "text": text,
        "stream": stream,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": vol,
            "pitch": pitch,
            "emotion": emotion
        },
        "audio_setting": {
            "sample_rate": sample_rate,
            "bitrate": bitrate,
            "format": audio_format,
            "channel": 1
        }
    }
    
    print(f"🎤 正在生成语音...")
    print(f"   文本: {text[:50]}..." if len(text) > 50 else f"   文本: {text}")
    print(f"   模型: {model}")
    print(f"   声音: {voice_id} ({VOICES.get(voice_id, 'unknown')})")
    print(f"   情感: {emotion}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ API 返回错误: {response.text}")
            return False
        
        result = response.json()
        
        # Check for API errors
        if result.get("base_resp", {}).get("status_code", 0) != 0:
            print(f"❌ API 错误: {result.get('base_resp', {}).get('status_msg', 'Unknown error')}")
            return False
        
        if stream:
            # Handle streaming response
            audio_data = b""
            for chunk in result:
                if chunk.get("data", {}).get("audio"):
                    audio_chunk = bytes.fromhex(chunk["data"]["audio"])
                    audio_data += audio_chunk
        else:
            # Handle non-streaming response
            audio_hex = result.get("data", {}).get("audio")
            if not audio_hex:
                print("❌ 未获取到音频数据")
                return False
            audio_data = bytes.fromhex(audio_hex)
        
        # Save to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(audio_data)
        
        file_size = len(audio_data)
        print(f"✅ 已保存: {output_path}")
        print(f"   文件大小: {file_size:,} bytes")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="MiniMax TTS CLI - 语音合成工具")
    parser.add_argument("--text", "-t", type=str, required=True, help="要转换的文本")
    parser.add_argument("--model", type=str, default="speech-2.8-hd", help="模型名称")
    parser.add_argument("--voice", type=str, default="male-qn-qingse", 
                       help=f"声音ID (默认: male-qn-qingse)")
    parser.add_argument("--speed", type=float, default=1.0, help="语速 (0.5-2.0)")
    parser.add_argument("--emotion", type=str, default="neutral", 
                       help=f"情感 (默认: neutral)")
    parser.add_argument("--format", type=str, default="mp3", 
                       help="音频格式 (mp3/wav/aac)")
    parser.add_argument("--sample-rate", type=int, default=32000, 
                       help="采样率 (16000/32000)")
    parser.add_argument("--bitrate", type=int, default=128000, help="比特率")
    parser.add_argument("--stream", action="store_true", help="流式输出")
    parser.add_argument("--output", "-o", type=str, default="./output.mp3", 
                       help="输出文件路径")
    parser.add_argument("--api-key", type=str, help="API密钥 (可选)")
    parser.add_argument("--list-voices", action="store_true", help="列出所有可用声音")
    
    args = parser.parse_args()
    
    if args.list_voices:
        print("可用声音列表:")
        for voice_id, desc in VOICES.items():
            print(f"  {voice_id}: {desc}")
        return
    
    # Get API key
    api_key = args.api_key or load_config()
    if not api_key:
        print("❌ 请设置 MINIMAX_API_KEY 环境变量或通过 --api-key 参数传入")
        print("   获取 API Key: https://platform.minimax.io/user-center/basic-information/interface-key")
        sys.exit(1)
    
    # Generate speech
    success = generate_speech(
        text=args.text,
        api_key=api_key,
        model=args.model,
        voice_id=args.voice,
        speed=args.speed,
        emotion=args.emotion,
        sample_rate=args.sample_rate,
        bitrate=args.bitrate,
        audio_format=args.format,
        stream=args.stream,
        output_path=args.output
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
