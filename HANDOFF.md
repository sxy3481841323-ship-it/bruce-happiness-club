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
for f in js/*.js js/theater/*.js functions/api/*.js; do node --check "$f" || exit 1; done
```

---

## 六、2026-11-25 晚 · 路线 A 改造（当前主线架构）

为了彻底摆脱纯代码 3D 的积木感与重复感，主游戏已切换为**路线 A（2.5D 活态绘本大地图 + 全屏交互电影引擎）**，并收拢为 5 幕招牌场景：

1. **2.5D 活态绘本大地图（`js/map.js` + `css/worldmap.css`）**：
   - 优先加载新版无地域元素底图 `assets/img/world_map_v2.jpg`，缺失时无缝回退第一版手绘图 `assets/img/world_map.jpg`。
   - Canvas 实时叠加水面波光、飘动云影、阳光微尘与桌面微视差；`<80` 分冷战自动切换冷蓝阴雨滤镜、斜向雨丝与水面涟漪；手机竖屏（`<= 560px`）支持居中横向平滑拖屏。
2. **全屏交互电影引擎（`js/theater/{clips,player,interactions,stage}.js` + `css/theater.css`）**：
   - 双缓冲媒体层实现 `450ms` 零黑屏交叉淡化；热插拔读取 `assets/clips/<id>/` 下的 `poster.jpg`、`intro.mp4`、`win.mp4`、`fail_phone.mp4`、`fail_hazard.mp4` 与可选 `swap.mp4`。
   - 在真实 MP4 放入前，自动使用高清图 + Ken Burns 运镜兜底；5 幕全屏交互（顺毛、雨窗三步、抛球、探店门贴慢动作、水岸点灯）直接叠在全屏画面上，并支持「自动观影」Ghost 光标演示（75% 成功 / 25% 翻车）。
3. **5 幕招牌场景（`js/activities.js` 选幕大厅）**：
   - 布鲁斯的小院（3 幕）：`home_brush`、`home_rain_vinyl`、`home_hide_seek`。
   - 林荫小街（2 幕）：`street_cafe`、`street_bridge`。
4. **国产模型制片手册 & 一键压缩脚本**：
   - [`PRODUCTION_BRIEF.md`](./PRODUCTION_BRIEF.md)：含 1 张新版无地域大地图 + 5 幕首帧与分支视频的完整中文提示词与布鲁斯垫图指南。
   - [`scripts/optimize_clips.py`](./scripts/optimize_clips.py)：将 `assets/clips_raw/<id>/*.mp4` 批量压成 720p/30fps/H.264（`<= 1.2 MB`）输出到 `assets/clips/<id>/`。
5. **旧模块处置说明**：
   - `js/cinematic/`、`js/map3d.js`、`js/renderer.js`、`js/bruce3d.js`、`js/materials3d.js`、`cinematic-preview.html`、`map3d-preview.html` 已从主游戏停用，但文件完整保留在仓库中供参考；`assets/clips_raw/` 已加入 `.gitignore` 不入库。

---

## 七、2026-11-26 · 真 3D 阳光客厅主基地 + 点击传送 + DeepSeek 实时气泡文案

在路线 A 基础上，主入口（`导航「客厅」`）进一步升级为**单场景真 3D 客厅主基地 + 客厅内近景互动 + 点击传送去远方**：

1. **轻量化真 3D 资产（已全部入库 `assets/models/`）**：
   - `assets/models/living_room.glb`（`4.19 MB`、`23,230` 三角面、无压缩扩展依赖）：基于真实极简客厅白昼空间优化贴图并配置程序化室内 IBL 环境光与窗外天光。
   - `assets/models/bruce.glb`（`2.42 MB`、`66,935` 三角面、无压缩扩展依赖）：对原始 `89.39 MB` 混元 3D 奶油长毛腊肠犬完成 UV 保边减面与贴图压缩；由 `js/hub3d/bruceLiving.js` 通过 GPU `onBeforeCompile` 实时驱动呼吸、目光跟随、飞机耳预警、摇尾、歪头与开心跳跃，并自动剔除底盘扁平底座与内置隐形射线点击体（`BruceHitbox`）。
2. **3D 客厅主基地与传送体系（`js/hub3d/roomHub.js` + `css/hub3d.css` + `js/map.js`）**：
   - **客厅内 3 项近景陪伴**（无需切屏，直接在 3D 客厅拉近运镜游玩）：`home_brush`（阳光顺毛）、`home_rain_vinyl`（雨窗擦爪盖毯听黑胶）、`home_hide_seek`（3D 网球物理弹跳抛球寻宝），统一结算幸福指数、冷战氛围切换与高位换分金色光环。
   - **3 处点击传送热区**：`出门 · 林荫小街`（跳至街区双幕剧场，支持一键`返回 3D 客厅`）、`传送 · 会员超市`（二期预留弹窗）、`传送 · 环球旅行`（北欧峡湾 / 阳光海岸 / 雪山牧场 / 白帆游艇四标签弹窗）。
   - **后续扩充新 3D 场景指南**：只需将轻量 `.glb` 放入 `assets/models/` 并在 `js/map.js` 的 `onTeleportWarehouse` / `onTeleportGlobal` / `street` 中挂载对应新场景模块即可平滑替换。
3. **DeepSeek API 实时角色内心戏与全量文案工厂（`gen_hub_deepseek.py` / `gen_content_deepseek.py`）**：
   - [scripts/gen_hub_deepseek.py](./scripts/gen_hub_deepseek.py) 生成 [data/hub_deepseek.json](./data/hub_deepseek.json)，负责 3D 客厅头顶投影气泡独白（8 组心情/动作）、传送门悬停感应台词及 5 个远方目的地第一人称心愿单；
   - [scripts/gen_content_deepseek.py](./scripts/gen_content_deepseek.py) 已升级为分模块三段调用并产出 `v3` 版 [data/content.json](./data/content.json)（10 个活动共 60 条胜利台词 + 80 条分心/踩雷台词、24 条英文手机弹窗、32 条吃瓜模板、17 条哄狗台词），全量经过禁词校验且前端零暴露 Key。
4. **35mm 全画幅取景器与实物质感 UI（已推翻旧胶囊壳重构）**：
   - [index.html](./index.html)、[css/style.css](./css/style.css)、[css/hub3d.css](./css/hub3d.css)：在 `is-hub3d-view` 下升级为 `100vw × 100dvh` 35mm 取景器全画幅 3D 客厅，配备左上方**酒红斜纹真丝领巾身份牌**、中上方**黑底翻牌幸福计分器**、**带物理按压行程的机械按键**；
   - 客厅 3D 热区彻底抛弃白胶囊，替换为**黄铜眼孔+酒红竖边项圈铭牌**（陪伴互动）与**深林黑金撕裂虚线打孔登机存根**（街区/超市/环球传送门），并适配移动端宽视场（`FOV 64°`）同屏显示全 6 个热区与零 `404` 街区海报回退。

---

## 八、双人 Antigravity 协作与主导权保障（`AGENTS.md`）

1. **项目自动规则**：根目录 [AGENTS.md](./AGENTS.md) 与 `.agents/rules/team-governance.md` 会被所有协作者的 Antigravity 自动加载。
2. **主分支决策锁**：`.github/CODEOWNERS` 指定 `* @sxy3481841323-ship-it`；[ci-guard.yml](./.github/workflows/ci-guard.yml) 自动校验 JS 语法、JSON、禁词、CDN 与模型体积；协作者必须先运行 `bash scripts/setup_collab.sh` 启用 `.githooks/pre-push`，并在 `feat/*` 分支开发、提 PR 给 Alex 审阅合入 `main`。
3. **无冲突新 3D 场景调试**：协作者可直接在 `js/scenes3d/` 编写新 3D 传送场景，并通过 `scene-preview.html?module=street3d` 独立预览测试，无需修改 `index.html`、`js/map.js` 或 `js/hub3d/*`。

---

## 八、2026-11-26 · 1:1 海岸阳光咖啡馆 3D 场景（`OUT·01` 已接通）与超市接力蓝图

### 1. 本次已完成并上线的海岸咖啡馆（`Stylish and Open Café` 1:1 自建还原）
- **轻量化资产与离线构建器**：
  - [scripts/build_cafe_glb.py](./scripts/build_cafe_glb.py) → 生成标准无压缩 glTF 2.0 资产 [assets/models/coastal_cafe.glb](./assets/models/coastal_cafe.glb)（**`3.60 MB`**、`32,132` 三角面、`37` 网格、`36` 材质、`8` 张内嵌程序化 PBR 贴图）。
  - 严格还原参考建筑与软装：浅薄荷灰方砖地面（`SageTileFloor`）、左侧与尽头通顶黑框落地玻璃幕墙（外接海岸木栈道、红粉花丛、细沙碧海与摇曳椰子树 `PalmFronds`）、右侧白灰文化砖墙 + 黑铁几何酒水架 + 现代几何挂画、深炭黑竖向木格栅弧形吧台 + Calacatta 白大理石台面 + 台底暖光 LED + 弧形玻璃甜品展示柜 + 意式咖啡机磨豆机 + 7 张焦糖棕高脚凳、橡木吊顶与白色圆球吊灯、米色布艺沙发（青蓝/深咖抱枕）+ 原木圆桌 + 白盆阔叶绿植。
- **3D 交互场景与导航接通**：
  - [js/scenes3d/cafeHub.js](./js/scenes3d/cafeHub.js) 导出 `mountCoastalCafeHub(container, opts)`，复用全画幅 `35MM · COASTAL CAFÉ · F/1.8` 取景器壳、海岸定制 PMREM 环境光、点击布鲁斯触发气泡独白（[data/hub_deepseek.json](./data/hub_deepseek.json) `cafe_thought_bubbles`）、`<80` 冷战窗外雨景与暖光切换。
  - **3 项吧台/窗畔近景 3D 互动**（已接入 [js/map.js](./js/map.js) `settleScoreAndSwap` 与 [js/main.js](./js/main.js) `state.view === "street"`）：
    - `street_cafe`（吧台爪爪奶泡，`+13 / -14`，`15%` 高位换分，含 3D `Pup Cup` 动画）；
    - `street_window`（甜品橱窗品鉴，`+12 / -13`，`12%` 换分，含玻璃轻划与 `1s` 飞机耳预警）；
    - `street_walk`（海风窗畔晒毛，`+12 / -13`，`10%` 换分）。
  - **2 枚传送存根**：`HOME·00`（平滑退镜返回 3D 阳光客厅）与 `CLB·02`（预留衔接会员大超市）。
- **真机浏览器实测指标**：
  - 桌面 `1280×800` 与手机 `390×844` 均实现 **`5 / 5` 热区同屏显示、零碰撞、零横向溢出、0 控制台/网络报错**；
  - WebGL 渲染诊断：`calls: 80`、`triangles: 198,174`（含高精度 `bruce.glb`）、`geometries: 44`、`textures: 16`、`dpr: 2`。

### 2. 下一站接力施工接口：`CLB·02` 会员制大超市（朋友或后续接力指南）
1. **离线建模脚本**：参考 [scripts/build_cafe_glb.py](./scripts/build_cafe_glb.py) 新建 `scripts/build_warehouse_glb.py`，输出标准无压缩 `assets/models/supermarket.glb`（建议 `<= 4.5 MB`、`<= 55,000` 三角面），还原参考图的绿植生态墙、多排商品货架/生鲜木筐、发光冷风柜、标牌与亮红色手推车。
2. **场景挂载模块**：新建 `js/scenes3d/warehouseHub.js`，导出同构接口：
   ```js
   export function mountWarehouseHub(container, { sulking, happiness, content, getHappiness, onSettle, onOpenShop, onBackToHub, onBackToCafe })
   ```
   使用 `THREE.InstancedMesh` 批量摆放零食/饮料/牛乳/三文鱼礼盒商品（控制 Draw Calls `<= 150`），让布鲁斯坐在红色手推车内巡逛试吃。
3. **接入路由**：在 [js/map.js](./js/map.js) 中把 `onTeleportWarehouse` 替换为 `() => store.setView("warehouse")`，并在 [js/main.js](./js/main.js) 中增加 `warehouse` 视图分支挂载 `renderWarehouseView(viewScene)` 即可无缝上线。

