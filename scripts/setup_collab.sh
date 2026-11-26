#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

git config core.hooksPath .githooks
chmod +x .githooks/pre-push

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "✅ 已创建本地 .env 模板（仅本机有效，不会被提交到 GitHub）"
fi

echo "✅ 已启用项目级 Git Hook（.githooks/pre-push）"
echo "📌 接下来请先拉出你自己的功能分支再开发，例如："
echo "   git checkout -b feat/street-3d"
echo "📌 本地预览独立 3D 场景调试台："
echo "   python3 scripts/dev_server.py --port 8781"
echo "   浏览器访问 http://127.0.0.1:8781/scene-preview.html?module=street3d"
