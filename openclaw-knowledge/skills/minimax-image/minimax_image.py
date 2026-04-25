#!/usr/bin/env python3
"""
MiniMax Image Generation CLI Tool
Generate images using MiniMax image-01 model
"""

import os
import sys
import json
import base64
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Default API endpoint
DEFAULT_API_URL = "https://api.minimaxi.com/v1/image_generation"

def load_config():
    """Load API configuration from OpenClaw config or environment"""
    # Try to get from environment first
    api_key = os.environ.get("MINIMAX_API_KEY")
    
    # Try OpenClaw config
    config_paths = [
        "/home/pi/.openclaw/config.json",
        os.path.expanduser("~/.openclaw/config.json"),
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                    if not api_key and config.get("minimax_api_key"):
                        api_key = config["minimax_api_key"]
                    if config.get("minimax_endpoint"):
                        return api_key, config["minimax_endpoint"]
            except:
                pass
    
    return api_key, DEFAULT_API_URL


def generate_image(args):
    """Generate images based on command line arguments"""
    # Get API key from args or environment
    api_key = args.api_key or os.environ.get("MINIMAX_API_KEY")
    
    if not api_key:
        print("❌ 错误: 请设置环境变量 MINIMAX_API_KEY 或使用 --api-key 参数", file=sys.stderr)
        print("   示例: export MINIMAX_API_KEY=\"your_api_key\"", file=sys.stderr)
        sys.exit(1)
    
    # Build request payload
    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "n": args.num_images,
        "response_format": args.response_format
    }
    
    # Add optional parameters
    if args.aspect_ratio:
        payload["aspect_ratio"] = args.aspect_ratio
    if args.prompt_optimizer:
        payload["prompt_optimizer"] = True
    if args.subject_reference:
        payload["subject_reference"] = [{
            "type": "character",
            "image_file": args.subject_reference
        }]
    
    # Send API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🎨 正在生成 {args.num_images} 张图片...")
    print(f"   Prompt: {args.prompt[:50]}{'...' if len(args.prompt) > 50 else ''}")
    print(f"   Model: {args.model}")
    print(f"   Aspect Ratio: {args.aspect_ratio}")
    
    try:
        response = requests.post(
            DEFAULT_API_URL, 
            headers=headers, 
            json=payload, 
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        
        # Check API response status
        if result.get("base_resp", {}).get("status_code") != 0:
            error_msg = result.get("base_resp", {}).get("status_text", "Unknown error")
            print(f"❌ API 返回错误: {error_msg}", file=sys.stderr)
            sys.exit(1)
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save generated images
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if args.response_format == "url":
            image_urls = result["data"]["image_urls"]
            for i, url in enumerate(image_urls):
                # Download and save image
                img_response = requests.get(url, timeout=30)
                img_response.raise_for_status()
                
                ext = ".png" if args.response_format == "url" else ".jpeg"
                file_path = output_dir / f"generated_{timestamp}_{i+1}{ext}"
                file_path.write_bytes(img_response.content)
                print(f"✅ 已保存: {file_path}")
                print(f"   URL: {url}")
        else:
            # Base64 format
            images = result["data"]["image_base64"]
            for i, img_base64 in enumerate(images):
                img_data = base64.b64decode(img_base64)
                file_path = output_dir / f"generated_{timestamp}_{i+1}.jpeg"
                file_path.write_bytes(img_data)
                print(f"✅ 已保存: {file_path}")
        
        print(f"\n✨ 完成! 共生成 {len(image_urls) if args.response_format == 'url' else len(images)} 张图片")
        print(f"   保存目录: {output_dir}")
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接或稍后重试", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络或API请求失败: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ API响应解析失败", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 处理图片时出错: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="🎨 MiniMax Image-01 CLI 图像生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 文生图
  python %(prog)s --prompt "可爱的橘猫" --output-dir ./cats
  
  # 指定宽高比和数量
  python %(prog)s -p "未来城市" --aspect-ratio 16:9 -n 4 --output-dir ./future
  
  # 图生图
  python %(prog)s --prompt "穿宇航服的相同角色" --subject-reference "https://example.com/img.jpg"
  
  # 启用提示词优化
  python %(prog)s -p "a cat" --prompt-optimizer --output-dir ./optimized
        """
    )
    
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="图像生成的文本描述，最多1500字符"
    )
    parser.add_argument(
        "--model", "-m",
        default="image-01",
        choices=["image-01", "image-01-live"],
        help="使用的模型 (默认: image-01)"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        default="1:1",
        choices=["1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16", "21:9"],
        help="生成图像的宽高比 (默认: 1:1)"
    )
    parser.add_argument(
        "--num-images", "-n",
        type=int,
        default=1,
        help="生成图片数量，1-9 (默认: 1)"
    )
    parser.add_argument(
        "--response-format", "-f",
        default="url",
        choices=["url", "base64"],
        help="返回图片的格式 (默认: url)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="./output",
        help="保存图片的目录 (默认: ./output)"
    )
    parser.add_argument(
        "--subject-reference", "-s",
        help="用于图生图的参考图片URL"
    )
    parser.add_argument(
        "--prompt-optimizer",
        action="store_true",
        help="启用提示词优化"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="MiniMax API密钥 (也可通过环境变量 MINIMAX_API_KEY 设置)"
    )
    
    # Validate num_images range
    args = parser.parse_args()
    if args.num_images < 1 or args.num_images > 9:
        print("❌ 错误: --num-images 必须在 1-9 之间", file=sys.stderr)
        sys.exit(1)
    
    generate_image(args)


if __name__ == "__main__":
    main()