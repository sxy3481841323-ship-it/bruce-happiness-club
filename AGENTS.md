# 《布鲁斯日常 · 幸福指数俱乐部》双人 Antigravity 协作总规（必读）

只要打开本仓库作为 Workspace，所有 Antigravity 助手必须严格遵守以下权限边界、目录归属与开发红线。

---

## 一、决策权与 Git 分支纪律（防覆盖、防冲突）

1. **最终决策人与主分支归属**：
   - 项目负责人（Project Lead）：**Alex（GitHub: `sxy3481841323-ship-it`）**。
   - **只有 Alex 可以向 `main` 分支合入代码、部署上线或更改核心玩法规则。**
2. **协作者工作流（`shanmufu888@gmail.com` 等协作者）**：
   - 第一次拉取仓库后先运行一次：`bash scripts/setup_collab.sh`。
   - **严禁直接向 `main` 分支提交或强推（`git push origin main`）**。必须拉出功能分支开发，例如：`git checkout -b feat/street-3d`、`git checkout -b feat/warehouse-3d`，推送后在 GitHub 提交 **Pull Request（PR）** 等待 Alex 审阅合入。
   - 如需调整核心玩法（如 `>=80` 冷战阈值、8 档零食、高位换分权重、`index.html` 主架构），必须先在 PR 说明中请示 Alex，不得擅自改动。

---

## 二、目录分工（各自领地，零合并冲突）

### 1. 主导者受保护区（协作者分支未经 Alex 明确同意禁止修改）
- 入口与全局 UI 壳：`index.html`、`css/style.css`、`css/hub3d.css`
- 核心状态、算分与接口：`js/state.js`、`js/api.js`、`js/main.js`、`js/map.js`、`js/shop.js`、`js/leaderboard.js`
- 客厅 3D 主基地：`js/hub3d/*`、`assets/models/living_room.glb`、`assets/models/bruce.glb`
- 边缘后端与本地模拟服：`functions/api/*`、`scripts/dev_server.py`
- 工程治理文件：`AGENTS.md`、`.agents/*`、`.github/*`

### 2. 协作者自由创作区（可放开手脚、安全推分支）
- 独立新 3D 传送场景模块：`js/scenes3d/*.js`（参考示例 [street3d.js](./js/scenes3d/street3d.js)）
- 场景独立样式：`css/scenes3d.css`（统一使用 `.sc3d-` 类名前缀）
- 独立场景调试工作台：[scene-preview.html](./scene-preview.html)（浏览器打开 `http://127.0.0.1:8781/scene-preview.html?module=street3d`）
- 新 3D 场景模型：`assets/models/<scene_name>.glb`（例如 `street.glb`、`warehouse.glb`）
- 如需补充新场景文案，请先在独立 JSON 文件 `data/scenes_<name>.json` 撰写或由 DeepSeek 生成，等待 Alex 合入。

---

## 三、所有新 3D 场景必须实现的标准对接协议

你在 `js/scenes3d/<name>.js` 中导出的入口函数，必须严格保持以下签名，方便合入 `main` 时由 `js/map.js` 一键挂接传送门：

```js
export function mountScene(container, opts = {}) {
  // opts 包含：{ sulking, happiness, content, onSettle, onBackToHub }
  // 需支持根据 sulking (<80) 切换阴雨氛围与布鲁斯情绪
  return {
    setSulking(nextSulk) {},
    setContext({ happiness, content }) {},
    destroy() {
      // 必须 cancelAnimationFrame、移除事件监听并 dispose geometry/material/texture/renderer
    },
  };
}
```

---

## 四、项目硬红线（CI 将自动拦截违反以下任一条的 PR）

1. **中国大陆微信免梯子直连**：严禁引入任何外网 CDN（如 `fonts.googleapis.com`、`unpkg.com`、`jsdelivr.net`、`cdnjs.cloudflare.com`）；Three.js 必须通过 `./vendor/three.module.js` 与 `"three"` importmap 引用。
2. **严禁地域刻板词**：`index.html`、`css/`、`js/`、`data/` 中绝对禁止出现 `杭州`、`西湖`、`钱塘江`、`灵隐寺`、`龙井`、`宋城`、`桂花`、`三墩`、`滨江`、`江南`、`石桥`、`拱桥`、`乌篷船` 等词。
3. **3D 模型体积与兼容性红线**：
   - 单个新增 `.glb` 文件体积必须 `<= 6 MB`（建议先压缩贴图至 `1024px` JPEG 并适度减面）；
   - **禁止使用 `KHR_draco_mesh_compression` 或 `EXT_meshopt_compression`**，必须保持标准无扩展压缩 glTF 2.0，保证自托管 `GLTFLoader` 直接加载。
4. **安全与语法校验**：
   - 严禁将 `.env` 或任何 DeepSeek API Key 写入前端或提交进 Git；
   - 推送前必须通过所有 JS `node --check` 语法校验及浏览器 `1280x800` + `390x844` 实机截图无报错检查。
