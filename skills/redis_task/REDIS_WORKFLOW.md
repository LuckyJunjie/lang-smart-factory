# Redis Workflow - Newton 团队

## 概述
Newton 团队使用 Redis Streams 与 Vanguard 通信，不再依赖 API。

## Redis 配置
- Host: `192.168.3.75`
- Port: `6379`
- Consumer Group: `newton`
- Consumer Name: `newton`

## Stream 路由

| 操作 | Stream | 读写 |
|------|--------|------|
| 领取任务 | `smartfactory:stream:tasks` | XREADGROUP (consume) |
| 上报结果 | `smartfactory:stream:results` | XADD |
| 上报阻塞 | `smartfactory:stream:blockers` | XADD |
| 心跳/状态 | `smartfactory:stream:machine:status` | XADD |

## 任务消费流程

```bash
# 阻塞读取新任务（等待最多 BLOCK_MS 毫秒）
XREADGROUP GROUP newton newton BLOCK 30000 STREAMS smartfactory:stream:tasks ">"

# 处理任务...

# 完成后 ACK
XACK smartfactory:stream:tasks <entry_id>
```

## 心跳上报

```python
import redis
r = redis.Redis(host='192.168.3.75', port=6379, decode_responses=True)
r.xadd('smartfactory:stream:machine:status', {
    'hostname': socket.gethostname(),
    'team': 'newton',
    'status': 'online',
    'reported_at': datetime.utcnow().isoformat()
})
```

## 结果上报

```python
r.xadd('smartfactory:stream:results', {
    'taskId': task_id,
    'status': 'done',
    'output': result
})
```

## 阻塞上报

```python
r.xadd('smartfactory:stream:blockers', {
    'type': 'blocker',
    'from': 'newton',
    'taskId': task_id,
    'reason': 'description'
})
```
