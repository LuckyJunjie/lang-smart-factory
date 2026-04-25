# GitHub 网络与 git push（OpenClaw 设备）

面向 **OpenClaw 运行机**（Jarvis / CodeForge / NAS / 树莓派等）：当 **`git push`/`git fetch` 因网络访问 GitHub 失败**时的排查顺序与应急做法。  
**注意**：镜像与代理涉及供应链与凭证安全，仅在内控允许时使用；优先 SSH + 稳定网络。

---

## 1. 常见现象

- `Connection timed out`、`Could not resolve host`、`recv failure: Connection reset by peer`
- `SSL certificate problem`、`HTTP 403`（受限网络或企业代理拦 HTTPS）
- 大仓库 `pack-objects` 慢或中断

---

## 2. 推荐排查（按顺序）

1. **确认 DNS 与基础连通**  
   `ping github.com`（或 `nslookup github.com`）；必要时换可靠 DNS（网络策略允许前提下）。

2. **HTTPS → SSH（或反向尝试）**  
   - HTTPS：`git remote -v`，确认 URL。  
   - SSH：`git@github.com:ORG/REPO.git`，本机 `ssh -T git@github.com` 应可认证。  
   企业环境可在 **`~/.ssh/config`** 中为 `Host github.com` 配置 `ProxyJump` / `ProxyCommand`（由运维提供）。

3. **HTTP/HTTPS 代理（仅当合规）**  
   ```bash
   export HTTPS_PROXY=http://127.0.0.1:7890
   export HTTP_PROXY=http://127.0.0.1:7890
   ```
   Git 也可：`git config --global http.proxy …`（**用完可 `unset` 或 `--unset`**，避免影响内网 Git）。

4. **增大 HTTP 缓冲（大推送）**  
   ```bash
   git config --global http.postBuffer 524288000
   ```

5. **分拆推送 / 减小单次对象**  
   大文件用 LFS；或分批 `push` 分支/标签。

6. **镜像站（高风险，慎选）**  
   若组织允许使用 **ghproxy 类** 前置，仅作过渡；**勿**把生产令牌交给不可信第三方界面。

---

## 3. OpenClaw 专用：5 分钟 cron 自动重试 push，成功即卸下任务

适用于：**当前必须完成 push 关单，但网络间歇性故障**，人工不便一直重试。

### 3.1 脚本（仓库已提供）

路径：**`openclaw-knowledge/scripts/git_push_retry_until_ok.sh`**

- 入参：`仓库路径` [`remote` 默认 `origin`] [`分支` 默认当前分支]
- **成功**：写入日志，并 **`crontab -l` 中删除所有包含该脚本路径的行**（请每台设备**只配置一条**此类重试任务，避免误删多条）。
- **失败**：退出码 0，等待下一次 cron（避免邮件刷屏）；详情见日志。

首次执行：

```bash
chmod +x /path/to/smart-factory/openclaw-knowledge/scripts/git_push_retry_until_ok.sh
```

### 3.2 配置 cron（每 5 分钟）

```bash
crontab -e
```

示例（把路径换成你的本机绝对路径）：

```cron
*/5 * * * * /Users/you/program_managment/smart-factory/openclaw-knowledge/scripts/git_push_retry_until_ok.sh /Users/you/your-game-repo origin main
```

日志默认：**`~/.openclaw-git-push-retry.log`**，可通过环境变量 **`OPENCLAW_GIT_PUSH_RETRY_LOG`** 覆盖。

### 3.3 成功后的行为

- 脚本在 **push 成功后** 会尝试从 crontab **去掉包含 `git_push_retry_until_ok.sh` 的行**。  
- 若环境无 `crontab`（极少见）或权限不足，请 **手动 `crontab -e` 删掉对应行**。  
- **Windows（CodeForge）**：请用「任务计划程序」等同逻辑（每 5 分钟运行脚本；成功后在任务里禁用或删除）；或在本机 WSL 内用 `cron`。

### 3.4 与流程文档的关系

- **禁止**用此类 cron 替代 **跨团队 Redis/API 协作主路径**（见 `docs/REDIS_COLLABORATION.md`）；本机制仅用于 **Git 远端同步** 辅助。
- 关单仍以 **`standards/DEVELOPMENT_FLOW.md`**：push 成功后 **`PATCH` 需求/任务状态** 与 **`stream:results`** 为准。

---

## 4. 相关

- 开发流程与 push：`openclaw-knowledge/standards/DEVELOPMENT_FLOW.md`
- Godot 与技能选型：`openclaw-knowledge/docs/GODOT_SKILLS_AND_TESTING.md`
