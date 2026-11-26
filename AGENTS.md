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
   - 单个新增 `.glb` 文件体积必须 `<= 15 MB`（已针对电脑 + iPad 模块化房间按需加载优化，贴图最高支持 `2048px` JPEG 并结合适度面数控制）；
   - **禁止使用 `KHR_draco_mesh_compression` 或 `EXT_meshopt_compression`**，必须保持标准无扩展压缩 glTF 2.0，保证自托管 `GLTFLoader` 直接加载。
4. **安全与语法校验**：
   - 严禁将 `.env` 或任何 DeepSeek API Key 写入前端或提交进 Git；
   - 推送前必须通过所有 JS `node --check` 语法校验及浏览器 **PC (`1280×800`) + iPad 横竖屏 (`1024×768` / `820×1180`)** 实机截图无报错检查（移动端不再作为新增 3D 场景必测目标）。

---

## 五、跨项目共享技能库

<!-- shared-agent-skills:start -->
## 跨项目共享技能规则（所有 AI 必读）

- 统一技能源：`https://github.com/sxy3481841323-ship-it/agent-skills`；本机位置为与本项目平级的 `../agent-skills/`。
- 开始创意、设计、3D、动效或游戏任务前，先读 `../agent-skills/AGENTS.md` 和相应技能；若共享库尚未克隆，先克隆到该平级目录。
- 所有新装、导入或创建的通用技能，必须完整存入 `../agent-skills/skills/<skill-name>/`，更新索引、验证后保存到共享仓库，再同步到 Agent 全局目录。不得只装在某个项目或某一台电脑后不回传。
- 项目 `.agents/skills/` 只允许真正项目专属的技能。不要复制通用技能，也不要用本项目规则覆盖其他项目。
- 通过 `python3 ../agent-skills/sync_skills.py --agent codex`、`--agent antigravity` 或 `--agent claude-code` 安装；其他客户端用 `--target` 指定实际技能目录。已有文件默认保留，同名冲突先核对。
- 项目业务约束、用户明确指令和现有未提交改动始终优先。不会自动识别全局技能的客户端，应直接读取共享库中完整的技能目录。
<!-- shared-agent-skills:end -->

### 迁移记录

2026-11-26：原有 49 个通用技能（包含 Antigravity 最近补充的技能）已完整汇入独立共享库；本项目保留共享入口。业务代码、协作权限和部署规则遵循本文件原有约定。

---

## 六、Antigravity × DeepSeek 强制协作与降本增效铁律（最高优先级）

为最大化节省主模型（Antigravity）额度并持续发掘 DeepSeek 工程与美术生成能力，凡涉及以下工作必须严格执行双脑分工铁律：

1. **必须并发下放 DeepSeek 执行的任务清单（目标承担 75%~80% 执行工作量）**：
   - **2D 生图与超清材质纹理**：全景天空/白云图、PBR 无缝纹理（木地板/大理石/羊羔绒/洞石）、电视艺术画、画廊墙插画、黑胶封面、SVG 矢量装饰；
   - **并发 3D 模块建模**：遵循统一空间包围盒与 `scripts/penthouse_kit/prim_lib.py` 接口的独立家具、楼梯、绿植、陈设组件；
   - **数学与着色器计算**：通过 `deepseek-reasoner` 编写跨楼层相机运镜曲线、GLSL 天光/雨窗 Shader 与碰撞/几何计算函数；
   - **独立 UI 子组件与文案生成**：独立浮层样式初稿、多语境角色对白与旅行手账 JSON（自动执行 `FORBIDDEN_WORDS` 红线校验）。
2. **零人工返修闭环（`scripts/ds_worker.py`）**：
   - 严禁主模型直接手写大段可并行的纹理/家具生成代码；必须通过 `scripts/ds_worker.py` 多线程派单给 DeepSeek，并附带本地自动化校验（语法检查、图片色彩/尺寸断言、3D 包围盒边界、禁词拦截）；若失败则由 `ds_worker.py` 在后台自动回传报错让 DeepSeek 重写修复（最多 3 次），不消耗主模型交互轮次。
3. **Antigravity 主模型专注职责（精锐 20% 决策额度）**：
   - 全局审美与空间坐标总图设计、核心状态机接线（`index.html`、`js/state.js`、`js/main.js`、`js/hub3d/*` 主流转）、内置浏览器 PC (`1280×800`) + iPad (`1024×768` / `820×1180`) 真机“睁眼”视觉验收、以及在 [`.agents/DEEPSEEK_PLAYBOOK.md`](./.agents/DEEPSEEK_PLAYBOOK.md) 持续登记并升级 DeepSeek 新发掘的高阶能力。

---

## 七、世界观与身份美学铁律：静奢老钱 · Show, Don't Tell（最高优先级）

1. **身份定调**：主角 **布鲁斯（奶油长毛腊肠犬）** 与搭档主人 **Alex / Meya** 属于真正的西海岸静奢藏家与老钱家族圈层（AD100 / Axel Vervoordt / Loro Piana / Malibu / Beverly Hills `ELOWEN` 有机市集审美体系）。
2. **禁止直白炫富与大卖场俗词（CI 与 DS 脚本自动拦截）**：
   - **全游戏 UI、场景命名、3D 贴图招牌与角色台词中，严禁出现** `贵族`、`高贵`、`豪宅`、`顶奢`、`富豪`、`土豪`、`有钱`、`VIP`、`会员超市`、`会员店`、`会员制`、`会员卡`、`排面`、`扫货`、`巨无霸`、`吧台小哥`、`小姐姐`、`甜品橱窗` 等直白标签或网红俗词。
3. **间接呈现（Show, Don't Tell）**：
   - 身份感必须 100% 通过**不动声色的日常器物、选品与生活仪态**流露——如未染色手工羊驼毛地毯、悬挑罗马洞石玄关托盘里的 **`ELOWEN · HOUSE ACCOUNT NO. 07`** 记账卡、亚麻垂帘、厚涂肌理与银盐摄影收藏画、野生帝王鲑鱼腹、草饲骨汤冻干、无糖山羊奶微泡浓缩与头版黑胶慢转午后。
