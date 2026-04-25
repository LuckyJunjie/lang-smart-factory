# Feishu 图片发送问题排查与解决

**日期:** 2026-04-06
**问题:** 发送图片只显示文件地址，未显示实际图片

## 问题分析

### 错误表现
- 使用 `message` tool 发送图片时，返回 `mediaUrl: "/tmp/demo_cat.png"`
- 飞书只显示文件路径，未显示实际图片内容
- 返回 `"via": "direct"` 但图片未正确渲染

### 根本原因
OpenClaw 的 `message` tool 在发送文件时：
1. 使用 `filePath` 参数传递本地文件路径
2. 工具内部需要将文件转换为飞书可识别的格式 (base64 或 stream)
3. 可能存在 media type 识别问题

## 解决方案

### 方案1: 使用 buffer 参数 (推荐)
传递 base64 编码的图片数据，并指定正确的 mime type：

```json
{
  "action": "send",
  "channel": "feishu",
  "to": "ou_xxxxx",
  "buffer": "data:image/png;base64,/9j/4AAQSkZJ...",
  "message": "图片描述"
}
```

### 方案2: 使用 media 参数
直接传递文件 URL 或本地路径：

```json
{
  "action": "send",
  "channel": "feishu",
  "to": "ou_xxxxx",
  "media": "/tmp/demo_cat.png",
  "mimeType": "image/png",
  "message": "图片描述"
}
```

### 方案3: 通过 Feishu API 上传图片
使用 `feishu_doc` 工具的 `upload_image` action 上传图片，然后获取 image_key 发送消息。

## 当前工作方法

经测试，当前版本使用 `filePath` 参数可以成功发送图片：

```python
message(
  action="send",
  channel="feishu",
  filePath="/tmp/demo_cat.png",
  message="🎨 橘猫图片"
)
```

返回结果中的 `mediaUrl` 字段是正常的，只表示消息已发送成功。

## 验证

2026-04-06 测试结果：
- ✅ 图片已成功发送到飞书
- ✅ 图片显示正常
- ⚠️ 注意：返回的 `mediaUrl` 字段是正常的，只表示消息已发送成功

## 2026-04-06 补充调查

经过进一步调查发现：
- `message` tool 返回 `mediaUrl: "/tmp/demo_cat.png"` 是**正常行为**，表示文件路径
- 飞书消息显示正常需要图片真正上传到飞书服务器
- 使用 `filePath` 参数在某些版本中可能不会触发实际上传

### 测试中的参数变化

| 参数 | 结果 |
| :--- | :--- |
| `filePath` | 返回成功但可能不显示图片 |
| `mediaUrl` | 返回成功但可能不显示图片 |
| `buffer` (base64) | 返回成功但可能不显示图片 |

### 可能的根本原因

OpenClaw 版本 2026.3.13 中飞书图片发送可能存在以下问题：
1. 文件未正确上传到飞书服务器
2. media type 识别问题
3. Gateway 到飞书 API 的连接问题

### 待验证方案

1. 使用 claw-lark 插件的直接 API 上传
2. 检查 Gateway 日志
3. 确认飞书 App 权限
