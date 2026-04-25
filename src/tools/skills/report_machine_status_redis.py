#!/usr/bin/env python3
"""
Skill: report_machine_status (Redis-only)
直接写入 smartfactory:stream:machine:status，不依赖 Vanguard API
"""
import argparse
import platform
import socket
from datetime import datetime, timezone

REDIS_HOST = "192.168.3.75"
REDIS_PORT = 6379
STREAM = "smartfactory:stream:machine:status"


def main():
    parser = argparse.ArgumentParser(description="Newton: report machine status to Redis")
    parser.add_argument("--team", default="newton")
    args = parser.parse_args()

    import redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    payload = {
        "hostname": socket.gethostname(),
        "platform": platform.system() + " " + platform.machine(),
        "team": args.team,
        "status": "online",
        "reported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    r.xadd(STREAM, payload)
    print(f"Reported: {payload}")


if __name__ == "__main__":
    main()
