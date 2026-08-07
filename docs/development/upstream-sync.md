# 与官方上游同步

本仓库 `origin` 指向 fork：`https://github.com/706412584/facefusion.git`  
官方上游应配置为 `upstream`：`https://github.com/facefusion/facefusion.git`

## 一次性配置

```bash
git remote add upstream https://github.com/facefusion/facefusion.git
# 若已存在可改 URL：
# git remote set-url upstream https://github.com/facefusion/facefusion.git

git remote -v
```

期望类似：

```
origin    https://github.com/706412584/facefusion.git (fetch/push)
upstream  https://github.com/facefusion/facefusion.git (fetch)
```

建议：**不要**对 `upstream` 执行 `git push`（无写权限或易误推）。

## 常规同步流程（推荐）

本地有大量定制（中文 UI、frame override、scripts/docs）。优先 **merge**，避免 rebase 整段定制历史。

```bash
git fetch upstream
git checkout master

# 查看将要合入的官方提交
git log --oneline HEAD..upstream/master | head -30

# 合并上游
git merge upstream/master

# 解决冲突后
git add -A
git commit   # 若 merge 已自动生成可省略
git push origin master
```

### 冲突高发区（本 fork）

合并时重点检查：

- `facefusion/locales.py` / `translator.py`（中文）
- `facefusion/uis/components/*`（repair、diagnostics、preview）
- `facefusion/frame_override.py`、`state_manager.py`、`workflows/core.py`
- `facefusion/core.py`（language 路由）
- 根目录启动 bat、`.gitignore`

冲突原则：**保留本 fork 定制行为**，再手工接入上游 bugfix / API 变更。

## 仅挑上游某次修复

```bash
git fetch upstream
git cherry-pick <upstream-commit-sha>
```

适合单点 hotfix（如内存泄漏），不适合大版本跳跃。

## 大版本（例如 3.8 → 4.x）

1. 先读官方 changelog / breaking changes  
2. 新建分支 `merge/upstream-4.x`，不要直接在 `master` 硬刚  
3. 先让官方测试 greening，再逐项移植定制  
4. 用 `tests/` 与 frame override 相关用例做回归

## 本机 remote 维护备忘

```bash
# 确认
git remote -v
git status -sb

# 只推自己的 fork
git push origin master

# 更新上游引用（不合并）
git fetch upstream --tags
```
