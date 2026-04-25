#!/usr/bin/env python3
"""Split long Feishu messages into multiple parts"""
import subprocess
import sys

def send_msg(webhook, text):
    """Send a single message to Feishu"""
    text = text.replace('"', '\\"').replace('\n', '\\n')
    cmd = f'curl -s -X POST "{webhook}" -H "Content-Type: application/json" -d "{{\\"msg_type\\": \\"text\\", \\"content\\": {{\\"text\\": \\"{text}\\"}}}}"'
    subprocess.run(cmd, shell=True, capture_output=True)

def split_and_send(webhook, report):
    """Split report and send in parts"""
    # Split by gameplay suggestions marker
    if "游戏性改进" in report:
        parts = report.split("游戏性改进", 1)
        header = parts[0] + "\n\n--- 游戏建议 (续) ---\n"
        suggestions = parts[1]
        
        # Send header first
        send_msg(webhook, header)
        print("Sent part 1")
        
        # Send suggestions in chunks if needed
        if len(suggestions) > 3500:
            # Split into smaller chunks
            chunk_size = 3500
            for i in range(0, len(suggestions), chunk_size):
                chunk = suggestions[i:i+chunk_size]
                send_msg(webhook, chunk)
                print(f"Sent suggestions chunk {i//chunk_size + 1}")
        else:
            send_msg(webhook, suggestions)
            print("Sent part 2")
    else:
        # Single message
        if len(report) > 4000:
            # Split into chunks
            chunk_size = 3500
            for i in range(0, len(report), chunk_size):
                chunk = report[i:i+chunk_size]
                send_msg(webhook, chunk)
                print(f"Sent chunk {i//chunk_size + 1}")
        else:
            send_msg(webhook, report)
            print("Sent single message")

if __name__ == "__main__":
    webhook = sys.argv[1] if len(sys.argv) > 1 else "https://open.feishu.cn/open-apis/bot/v2/hook/19f6bbd4-10bf-4242-acf0-5a4f960781ce"
    report = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if not report:
        print("No report to send")
        sys.exit(1)
    
    split_and_send(webhook, report)
