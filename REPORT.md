# 代码变更与性能报告

## 1. 代码变更清单

### 1.1 架构优化 (Host/Guest -> Client-Server)
- **移除** `config/settings.py` 中过时的 Relay 和 Host/Guest 配置 (Relay Port, Host IP 等)。
- **移除** `main.py` 中的 `get_local_ip` 冗余函数。
- **重构** `README.md`，更新架构说明为 CS 架构，移除 Host/Guest 模式说明。

### 1.2 网络协议升级
- **文件**: `core/network.py`
- **新增**: 消息发送队列 `_send_queue` 和后台处理线程 `_process_send_queue`，确保高并发下消息不丢失。
- **协议扩展**:
  - `chat_message` 增加 `sender_avatar` 字段。
  - `typing_status` 增加 `sender_name` 字段。
- **信号更新**:
  - `message_received` 信号增加 `sender_avatar` 参数。
  - `typing_status_changed` 信号增加 `sender_name` 参数。

### 1.3 UI 重构与规范化
- **文件**: `ui/main_window.py`
- **消息展示优化**:
  - 实现头像显示：固定尺寸 40x40 像素 (`min-width: 40px; max-width: 40px; min-height: 40px; max-height: 40px`)。
  - 布局调整：头像在左，右侧为垂直布局（上方用户名，下方消息气泡）。
  - 用户名显示：仅在对方消息中显示，位于头像右侧上方。
- **输入状态**: 状态栏提示现在包含具体的发送者名称（如 "Alice 正在输入..."）。
- **初始化**: `MainWindow` 现在接收 `user_id` 和 `user_avatar`，确保本地用户信息传递正确。

### 1.4 主程序逻辑
- **文件**: `main.py`
- **实例化**: `MainWindow` 实例化时传递完整的用户信息 (`id`, `name`, `avatar`)。
- **信号处理**: 更新 `_on_message_received` 和 `_on_typing_status` 以适配新的信号参数。

## 2. 性能测试报告

### 2.1 测试环境
- **测试脚本**: `tests/stress_test.py`
- **并发规模**: 20 个客户端同时连接。
- **消息负载**: 每个客户端发送 10 条消息（共 200 条消息）。
- **模拟延迟**: 随机 50-150ms 发送间隔。

### 2.2 测试结果
```
=== Performance Report ===
Total Sent: 200
Total Received (Monitor): 200
Errors: 0
Average Latency: 1.10 ms
Max Latency: 8.94 ms
Result: PASS
```

### 2.3 结论
- **稳定性**: 100% 消息送达率 (200/200)，无消息丢失。
- **低延迟**: 平均延迟 1.10ms，最大延迟 8.94ms，远低于 200ms 的目标限制。
- **并发性**: 成功处理 20 个并发客户端的连接和消息广播。
- **队列机制**: 新增的消息队列机制有效保障了高并发下的发送稳定性。

## 3. API 文档更新说明

### 3.1 消息协议 (Chat Message)
```json
{
  "type": "chat_message",
  "sender_id": "uuid",
  "sender_name": "Alice",
  "sender_avatar": "base64_or_url",  // [新增]
  "target": "public",
  "content": "Hello World"
}
```

### 3.2 输入状态协议 (Typing Status)
```json
{
  "type": "typing_status",
  "sender_id": "uuid",
  "sender_name": "Alice",  // [新增]
  "is_typing": true
}
```
