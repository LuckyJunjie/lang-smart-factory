#!/usr/bin/env python3
"""
Redis Machine Heartbeat - reports Newton node online status to Redis stream.
Replaces API-based heartbeat with Redis-only approach.

Usage:
    python -m skills.redis-task.heartbeat
    python heartbeat.py

Cron (every 5 min):
    */5 * * * * cd /home/pi/.openclaw/workspace/smart-factory && python -m skills.redis-task.heartbeat
"""
import os
import sys
import socket
import platform
import redis
from datetime import datetime, timezone

REDIS_HOST = os.environ.get('REDIS_HOST', '192.168.3.75')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
STREAM = 'smartfactory:stream:machine:status'
TEAM = 'newton'


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return 'unknown'


def get_load():
    try:
        import os
        l1, l5, l15 = os.getloadavg()
        return {'1m': round(l1, 2), '5m': round(l5, 2), '15m': round(l15, 2)}
    except:
        return {'1m': 0, '5m': 0, '15m': 0}


def main():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        payload = {
            'hostname': socket.gethostname(),
            'ip': get_local_ip(),
            'platform': platform.system() + ' ' + platform.machine(),
            'team': TEAM,
            'status': 'online',
            'load': str(get_load()),
            'reported_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        msg_id = r.xadd(STREAM, payload)
        print(f'OK: heartbeat sent to {STREAM}, msg_id={msg_id}')
    except redis.ConnectionError as e:
        print(f'ERROR: Redis connection failed: {e}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
