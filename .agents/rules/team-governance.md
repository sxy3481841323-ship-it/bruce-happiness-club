# Team Governance Rule (Auto-Loaded)

- Read and obey `AGENTS.md` at repository root before editing any file.
- Verify who is working:
  - If the user asks to develop a new 3D teleport scene as a collaborator, stay on a `feat/*` branch, write only under `js/scenes3d/`, `css/scenes3d.css`, `assets/models/<new>.glb`, or `scene-preview.html`, and do not modify protected Lead-owned files (`index.html`, `css/style.css`, `css/hub3d.css`, `js/main.js`, `js/map.js`, `js/state.js`, `js/api.js`, `js/shop.js`, `js/leaderboard.js`, `js/hub3d/*`, `functions/api/*`, `scripts/dev_server.py`).
  - Only Project Lead Alex (`sxy3481841323-ship-it`) may authorize changes to protected core files or merges into `main`.
- Always check JS syntax (`node --check`), forbidden regional terms, zero external CDNs, and clean browser rendering before proposing a PR.
