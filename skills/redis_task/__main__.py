#!/usr/bin/env python3
"""
Redis Task Consumer for Newton team.
Consumes tasks from smartfactory:stream:tasks, spawns subagent, publishes result.

Usage:
    python -m skills.redis-task [BLOCK_MS]
    BLOCK_MS: block timeout in ms (default: 30000)
"""
import json
import os
import sys
import socket
import redis
from datetime import datetime, timezone

REDIS_HOST = os.environ.get('REDIS_HOST', '192.168.3.75')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
STREAM = 'smartfactory:stream:tasks'
GROUP = 'newton'
CONSUMER = 'newton'
RESULTS_STREAM = 'smartfactory:stream:results'
BLOCKERS_STREAM = 'smartfactory:stream:blockers'
MACHINE_STATUS_STREAM = 'smartfactory:stream:machine:status'

BLOCK_MS = int(sys.argv[1]) if len(sys.argv) > 1 else 30000


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


def report_machine_status():
    """Send heartbeat to Redis stream."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.xadd(MACHINE_STATUS_STREAM, {
            'hostname': socket.gethostname(),
            'ip': get_local_ip(),
            'platform': os.uname().sysname + ' ' + os.uname().machine,
            'team': 'newton',
            'status': 'online',
            'reported_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        })
    except Exception as e:
        print(f'[WARN] heartbeat failed: {e}', file=sys.stderr)


def publish_result(task_entry_id, task_id, requirement_id, status, output=None, error=None):
    """Publish task result to results stream."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        payload = {
            'source': 'newton',
            'taskId': task_id,
            'requirementId': str(requirement_id) if requirement_id else '',
            'status': status,
            'output': json.dumps(output) if output else '',
            'error': str(error) if error else '',
            'completed_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'hostname': socket.gethostname(),
        }
        r.xadd(RESULTS_STREAM, payload)
        print(f'[OK] result published for task {task_id}')
    except Exception as e:
        print(f'[ERROR] publish result failed: {e}', file=sys.stderr)


def publish_blocker(task_id, requirement_id, description, severity='medium'):
    """Publish blocker to blockers stream."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.xadd(BLOCKERS_STREAM, {
            'type': 'blocker',
            'from': 'newton',
            'taskId': task_id,
            'requirementId': str(requirement_id) if requirement_id else '',
            'description': description,
            'severity': severity,
            'reported_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        })
    except Exception as e:
        print(f'[ERROR] publish blocker failed: {e}', file=sys.stderr)


def spawn_subagent(task):
    """Spawn subagent to handle task. Returns (success, result)."""
    task_type = task.get('type', 'development')
    task_id = task.get('taskId', '')
    title = task.get('title', '')
    
    # Determine subagent type based on task type
    if task_type == 'testing':
        agent_type = 'game-tester'
    elif task_type == 'ux-review':
        agent_type = 'ux-reviewer'
    else:
        agent_type = 'game-tester'  # default for development too
    
    task_label = f"{task_id}-{title[:30]}"
    
    try:
        from openclaw import sessions_spawn
        result = sessions_spawn(
            task=f"Execute task: {title}\nTask ID: {task_id}\nType: {task_type}\nRequirement: {task.get('requirementId', '')}\n\nSteps:\n1. Analyze requirements\n2. Implement/fix\n3. Test\n4. Report results to Redis stream",
            label=task_label,
            runtime='subagent',
            agentId=agent_type,
            mode='run',
            runTimeoutSeconds=3600,
        )
        return True, result
    except Exception as e:
        return False, str(e)


def process_task(entry_id, task):
    """Process a single task. Returns True if handled, False otherwise."""
    task_id = task.get('taskId', '')
    requirement_id = task.get('requirementId', '')
    title = task.get('title', '')
    task_type = task.get('type', 'development')
    assignee = task.get('assignee', '')
    
    print(f'[TASK] {task_id} - {title} (type={task_type}, assignee={assignee})')
    
    # Check if this task is for newton team
    if assignee and assignee != 'newton' and assignee != 'einstein' and assignee != 'curie':
        # Not for us, skip
        print(f'[SKIP] task {task_id} assigned to {assignee}, not newton')
        return True  # ACK anyway to avoid blocking
    
    try:
        success, result = spawn_subagent(task)
        if success:
            publish_result(entry_id, task_id, requirement_id, 'completed', output=result)
        else:
            publish_result(entry_id, task_id, requirement_id, 'failed', error=result)
            publish_blocker(task_id, requirement_id, f'Task failed: {result}', severity='high')
        return True
    except Exception as e:
        print(f'[ERROR] process_task failed: {e}', file=sys.stderr)
        publish_blocker(task_id, requirement_id, f'Consumer error: {e}', severity='high')
        return False


def consume_loop():
    """Main consume loop."""
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    
    # Ensure consumer group exists
    try:
        r.xgroup_create(STREAM, GROUP, id='0', mkstream=True)
        print(f'[OK] created consumer group {GROUP}')
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            pass  # Group already exists
        else:
            raise
    
    print(f'[*] Consuming from {STREAM} group={GROUP} consumer={CONSUMER} block={BLOCK_MS}ms')
    
    while True:
        try:
            # Report heartbeat before each read
            report_machine_status()
            
            # Blocking read
            results = r.xreadgroup(GROUP, CONSUMER, {STREAM: '>'}, count=1, block=BLOCK_MS)
            
            if not results:
                continue
            
            for stream_name, messages in results:
                for entry_id, fields in messages:
                    task = dict(fields)
                    handled = process_task(entry_id, task)
                    if handled:
                        # ACK the message
                        r.xack(STREAM, GROUP, entry_id)
                        print(f'[ACK] {entry_id}')
        
        except redis.ConnectionError as e:
            print(f'[ERROR] Redis connection failed: {e}, retrying...', file=sys.stderr)
            import time
            time.sleep(5)
        except Exception as e:
            print(f'[ERROR] consume_loop error: {e}', file=sys.stderr)
            import time
            time.sleep(5)


if __name__ == '__main__':
    consume_loop()
