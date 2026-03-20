---
name: github
description: Interact with GitHub using the gh CLI - issues, PRs, CI runs, and advanced queries.
homepage: https://cli.github.com/
metadata:
  deepcobot:
    emoji: "🐙"
    requires:
      bins: ["gh"]
---

# GitHub - GitHub CLI 集成

使用 `gh` CLI 与 GitHub 交互。不在 git 目录时，始终指定 `--repo owner/repo`。

## 安装

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# 认证
gh auth login
```

## Pull Requests

### 查看 PR
```bash
# 列出 PR
gh pr list --repo owner/repo
gh pr list --repo owner/repo --state open --limit 10

# 查看 PR 详情
gh pr view 123 --repo owner/repo

# 查看 PR 的文件变更
gh pr diff 123 --repo owner/repo
```

### 创建 PR
```bash
# 从当前分支创建 PR
gh pr create --title "feat: add new feature" --body "描述..."

# 从指定分支创建
gh pr create --base main --head feature-branch --title "标题"

# 使用编辑器
gh pr create --web
```

### 检查 CI 状态
```bash
# 查看 PR 的 CI 状态
gh pr checks 123 --repo owner/repo

# 等待 CI 完成
gh pr checks 123 --repo owner/repo --watch
```

### 合并 PR
```bash
# 合并 PR
gh pr merge 123 --repo owner/repo --merge
gh pr merge 123 --repo owner/repo --squash
gh pr merge 123 --repo owner/repo --rebase
```

## Issues

### 查看 Issue
```bash
# 列出 Issue
gh issue list --repo owner/repo
gh issue list --repo owner/repo --state open --label bug

# 查看详情
gh issue view 456 --repo owner/repo
```

### 创建 Issue
```bash
# 创建 Issue
gh issue create --repo owner/repo --title "Bug: something wrong" --body "描述..."

# 使用模板
gh issue create --repo owner/repo --template bug_report.md

# 添加标签和指派
gh issue create --repo owner/repo --title "标题" --label "bug,high-priority" --assignee username
```

### 管理 Issue
```bash
# 关闭 Issue
gh issue close 456 --repo owner/repo

# 重新打开
gh issue reopen 456 --repo owner/repo

# 添加标签
gh issue edit 456 --repo owner/repo --add-label "enhancement"

# 指派
gh issue edit 456 --repo owner/repo --add-assignee username
```

## Actions / Workflows

### 查看工作流
```bash
# 列出工作流运行
gh run list --repo owner/repo --limit 10

# 查看特定运行
gh run view 12345678 --repo owner/repo

# 查看失败步骤的日志
gh run view 12345678 --repo owner/repo --log-failed

# 下载日志
gh run download 12345678 --repo owner/repo
```

### 触发工作流
```bash
# 手动触发工作流
gh workflow run workflow-name --repo owner/repo

# 带参数触发
gh workflow run workflow-name --repo owner/repo -f param1=value1 -f param2=value2
```

### 取消/重新运行
```bash
# 取消运行
gh run cancel 12345678 --repo owner/repo

# 重新运行
gh run rerun 12345678 --repo owner/repo
```

## Repositories

### 仓库信息
```bash
# 查看仓库信息
gh repo view owner/repo

# 创建仓库
gh repo create my-repo --public
gh repo create my-repo --private --description "描述"

# 克隆仓库
gh repo clone owner/repo

# Fork 仓库
gh repo fork owner/repo --clone
```

### 搜索
```bash
# 搜索仓库
gh search repos "topic:python" --limit 10

# 搜索代码
gh search code "function name" --repo owner/repo

# 搜索 Issue
gh search issues "bug report" --repo owner/repo
```

## Gist

```bash
# 创建 Gist
gh gist create file.txt --public
gh gist create file.txt --desc "描述"

# 列出 Gist
gh gist list

# 查看 Gist
gh gist view gist_id
```

## JSON 输出与过滤

大多数命令支持 `--json` 输出结构化数据：

```bash
# JSON 输出
gh pr list --repo owner/repo --json number,title,state,author

# 使用 jq 过滤
gh pr list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'

# 获取特定字段
gh issue view 456 --repo owner/repo --json title,body,labels
```

## API 高级查询

`gh api` 用于访问其他命令不支持的 API：

```bash
# 获取 PR 特定字段
gh api repos/owner/repo/pulls/123 --jq '.title, .state, .user.login'

# 列出仓库的分支
gh api repos/owner/repo/branches --jq '.[].name'

# 获取文件内容
gh api repos/owner/repo/contents/README.md --jq '.content' | base64 -d

# 创建标签
gh api repos/owner/repo/releases -X POST -f tag_name="v1.0.0" -f name="Release 1.0.0"
```

## 常用组合命令

### 检查 PR 状态并等待 CI
```bash
gh pr view 123 --repo owner/repo && gh pr checks 123 --repo owner/repo --watch
```

### 查看最近失败的 Actions
```bash
gh run list --repo owner/repo --status failure --limit 5
```

### 批量关闭 PR
```bash
gh pr list --repo owner/repo --state open --json number --jq '.[].number' | xargs -I {} gh pr close {} --repo owner/repo
```

## 配置

```bash
# 设置默认编辑器
gh config set editor "code --wait"

# 设置默认仓库
gh repo set-default owner/repo

# 查看配置
gh config list
```