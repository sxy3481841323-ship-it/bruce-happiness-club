# 共享技能已集中维护

通用技能已迁移到 [agent-skills](https://github.com/sxy3481841323-ship-it/agent-skills)。本机共享库位于与本项目平级的 `../agent-skills/`。

先阅读共享库的 `AGENTS.md`，再运行 `python3 sync_skills.py --agent antigravity`；Codex 使用 `--agent codex`。

本目录只保留项目专属技能与共享入口，不再保存通用技能的独立副本。其他客户端可根据共享库 README 选择实际安装目录。
