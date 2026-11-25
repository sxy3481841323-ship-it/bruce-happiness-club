# 项目接力交接文档 · 《布鲁斯日常 · 幸福指数俱乐部》

> **交接时间**：2026-11-25  
> **GitHub 仓库**：`https://github.com/sxy3481841323-ship-it/bruce-happiness-club`（分支：`main`）  
> **给接手人 & AI 助手**：先读本文件，即可无缝接力，无需翻看历史聊天记录。

---

## 一、项目定位与不可修改的核心规则

1. **核心玩法闭环**：
   - 主角是奶油长毛腊肠犬 **布鲁斯（Bruce）**，配有一条酒红色斜纹丝巾。
   - **幸福指数 = 排行榜分数 = 唯一消费货币**，初始值 `100`。
   - **正常陪玩（`>= 80`）**：在「布鲁斯的小院」（5 个互动）和「林荫小街」（5 个互动）陪伴布鲁斯，每次有概率加分，也有概率触发手机分心或场景雷点扣分。部分活动胜利后有概率触发**高位换分**。
   - **高位换分规则（Meaning-A，后端已实现）**：只从**当前分数严格高于你**的玩家池中抽取，**第 1 名被抽中概率最低，越靠近你的玩家概率越高**；若自己已是第 1 名，改为额外 `+6` 分榜首巡礼。
   - **冷战锁死（`< 80`）**：一旦幸福指数跌破 `80`，无法再主动陪玩加分，自动切入冷战氛围，只能去「零食急救柜」花自己的幸福指数买 8 档零食概率拉回 `80` 以上。
   - **破产救命（`< 5`）**：买不起最便宜的 5 分磨牙饼干时，解锁「看小视频拉回 80 分」（当前为 5 秒倒计时占位，待换真视频）。
2. **部署与审美红线**：
   - **中国大陆微信免梯子直连**：零外网 CDN（Three.js 已自托管在 `vendor/`，不引入 Google Fonts / 外部图床）。
   - **严禁出现任何杭州/西湖/钱塘江/江南等地名与旅游元素**；场景标牌（如 `PAWS WELCOME` / `NO DOGS` / `BRUCE` / `VINYL`）保留英文，中文 UI 使用系统无衬线字体。
   - **请勿破坏后端与数据契约**：`data/content.json`、`js/state.js`、`js/api.js`、`functions/api/*.js`、`scripts/dev_server.py` 已完整跑通，不要随意改字段结构。

---

## 二、当前已完成内容（均已合并在 `main` 分支）

1. **3D 阳光建筑沙盘世界地图**（源自 Codex 分支 `codex/world-map-3d`）
   - 核心文件：`js/map3d.js`、`js/map.js`、`map3d-preview.html`、`vendor/addons/objects/Reflector.js`。
   - 已接入 `index.html`，支持阳光独栋别墅 + 镜面水池 + 林荫精品街区 + 二期预告地标、`<80` 冷战雨天切屏、桌面与手机竖屏自适应。
2. **全屏沉浸式 3D 自动播放演出引擎 & 10 个完整活动**（源自 Codex 分支 `feat/cinematic-bruce`）
   - 核心目录：`js/cinematic/`（`index.js`、`director.js`、`bruceModel.js`、`effects.js`、`leash.js`、`materials.js`、`math.js`、`sound.js`、`cinematic.css`、`scenes/{index,home,street,world}.js`）。
   - 独立试映页：`cinematic-preview.html`（支持切换全部 10 幕、十幕连映、亲自互动、冷战与换分试映）。
   - 对外入口：`mountCinematicStage(containerEl, { activityId, owner, happiness, content, autoplay, onComplete, onExit })`。
3. **主游戏接入与 GLB 视觉 Bug 修复（已做 `node --check` 全量语法校验，待真机集成验收）**
   - `js/activities.js`、`js/main.js`、`css/style.css`：已将旧 2D Canvas 小游戏替换为柔光磨砂玻璃「3D 全屏选幕大厅」，每幕提供**「开启沉浸陪伴」**与**「自动观影」**双入口，已对接 `apiUpdateScore`、`apiTriggerSwap`（`revealSwap`）和 `<80` 自动跳零食柜。
   - `js/cinematic/bruceModel.js`：根据 `cinematic-preview.html` 实机截图反馈，已修复两处 GLB 视觉 Bug：
     1. 加载 `bruce.glb` 时不再额外生成胸前漂浮的程序化红领巾，改为在真实脖颈位置挂隐形牵引绳锚点 `collarAnchor`；
     2. 针对坐姿 GLB 收紧垂直归一上限（`Math.min(2.55 / maxDim, 1.62 / size.y)`），避免桌面 `1280×800` 下布鲁斯耳朵顶边裁切。
4. **非卡通年轻杂志风主角头像**
   - 已替换为新图 `assets/img/owner_alex.jpg`（600×600）和 `assets/img/owner_meya.jpg`（600×600，已裁去右下角水印）。
   - 已把 `index.html`、`js/leaderboard.js`、`js/main.js` 中全部 6 处旧 `.svg` 头像引用更新为 `.jpg`。
5. **自托管 Three.js `0.187.0`**
   - `vendor/three.module.js`、`vendor/three.core.js`、`vendor/addons/loaders/GLTFLoader.js`、`vendor/addons/utils/{BufferGeometryUtils,SkeletonUtils}.js`、`vendor/addons/objects/Reflector.js`。
6. **后端、文案与本地测试服**
   - `functions/api/{register,score,swap,leaderboard,_shared}.js`（EdgeOne Pages Functions + KV `BRUCE_KV`）。
   - `data/content.json`（含 DeepSeek 生成台词、8 档零食、16 条英文手机通知、8 名初始种子玩家）。
   - `scripts/dev_server.py`（自带本地 KV `.local_kv.json` 模拟，端口 `8778`）。

---

## 三、唯一未入库的大文件：`assets/models/bruce.glb`（真 3D 布鲁斯）

- 混元 3D 原始导出文件在 Alex 本机 `~/Downloads/布鲁斯.glb`（`89.39 MB`，1 个无骨骼无动画网格，`825,086` 顶点，`1,500,004` 三角面，3 张 `4096×4096` PNG 贴图）。
- Alex 本机已完成第一轮**贴图压缩**（3 张 4K PNG → `1024×1024` JPEG q84，贴图从 `47.05 MB` 降至 `441 KB`），产出本机文件 `assets/models/bruce.glb`（当前 **`42.78 MB`**）。
- 因为剩下的 `42.35 MB` 是未经减面的 150 万三角面网格，**体积过大，本次暂未提交到 GitHub**（`assets/models/` 当前处于未追踪状态）。
- **兜底说明**：仓库代码不依赖 `bruce.glb` 也能正常运行——当 `assets/models/bruce.glb` 不存在时，`js/cinematic/bruceModel.js` 会自动无报错回退到高工艺程序化 3D 长毛腊肠犬。

---

## 四、朋友接手后的待办清单（按优先级）

### 【P0】1. 对 `bruce.glb` 做几何减面瘦身（目标：`<= 4–5 MB` / `3.5 万–6 万` 三角面）
- 让 Alex 把本机的 `assets/models/bruce.glb`（42.78 MB，贴图已压好）或原始 `~/Downloads/布鲁斯.glb` 传给你。
- 使用 `@gltf-transform/cli` + `meshoptimizer` 或 Blender Decimate 减面：
  ```bash
  npx @gltf-transform/cli weld bruce.glb bruce_w.glb
  npx @gltf-transform/cli simplify bruce_w.glb bruce_opt.glb --ratio 0.035 --error 0.002
  npx @gltf-transform/cli prune bruce_opt.glb bruce_opt.glb
  npx @gltf-transform/cli dedup bruce_opt.glb bruce_opt.glb
  ```
- **重要避坑**：**不要**在最终文件上启用 `EXT_meshopt_compression` 或 `KHR_draco_mesh_compression`，保持标准无扩展压缩 glTF，确保现有的 `vendor/addons/loaders/GLTFLoader.js` 零额外 WASM/CDN 解码器直接加载。
- 压到 `<= 5 MB` 后放到 `assets/models/bruce.glb` 再提交入库。

### 【P0】2. 主游戏全流程真机/浏览器验收（桌面 `1280×800` + 手机竖屏 `390×844`）
- 本次交接前只跑了全量 `node --check` 语法校验，**主游戏 `index.html` 集成后的浏览器端到端回归尚未运行**（此前仅跑过独立试映页 `cinematic-preview.html`）。
- 重点检查：
  1. 首次打开选角弹窗：`owner_alex.jpg` / `owner_meya.jpg` 加载清晰、中文唯一昵称校验正常；
  2. 3D 沙盘大地图点击「布鲁斯的小院」与「林荫小街」正常切入新选幕大厅；
  3. 从选幕大厅点「开启沉浸陪伴」和「自动观影」进入全屏 3D 演出：确认**无胸前漂浮红领巾**、**桌面端耳朵不裁切**、结算后 HUD 与排行榜分数同步、`revealSwap` 换分正常、`退出演出` 返回大厅或 `<80` 自动跳零食急救柜正常；
  4. 手机竖屏 `390×844` 全程零横向溢出（`scrollWidth <= innerWidth`）、零控制台报错与 WebGL 上下文丢失。

### 【P1】3. 替换 `<5` 分救命小视频
- 将真实搞笑/治愈小视频放进 `assets/video/`，替换 `js/shop.js` 里当前的 5 秒占位倒计时逻辑。

### 【P1】4. 国内免梯子线上部署（腾讯云 EdgeOne Pages）
- 参照仓库里的 [`DEPLOY_EDGEONE.md`](./DEPLOY_EDGEONE.md) 部署静态资源 + `functions/api/*` + 绑定 KV `BRUCE_KV`，并在手机微信内打开实测首屏加载速度与多人排行榜实时同步。

---

## 五、常用本地开发与测试命令

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 启动本地完整前后端模拟服务（含 .local_kv.json 排行榜模拟）
python3 scripts/dev_server.py --port 8778

# 3. 浏览器访问入口
# 主游戏：http://127.0.0.1:8778/
# 3D 演出独立试映页：http://127.0.0.1:8778/cinematic-preview.html
# 3D 大地图独立试映页：http://127.0.0.1:8778/map3d-preview.html

# 4. JS 语法检查
for f in js/*.js js/cinematic/*.js js/cinematic/scenes/*.js functions/api/*.js; do node --check "$f" || exit 1; done
```
