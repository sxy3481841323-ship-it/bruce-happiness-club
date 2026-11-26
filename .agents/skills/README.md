# 《布鲁斯日常 · 幸福指数俱乐部》共享 AI 技能库（`.agents/skills/`）

本目录托管本游戏项目所需的全部 **49 个** 专业 Agent Skills（包含 3D 渲染、四足骨骼动画、镜头与对话系统、音效合成、高定 UI 微交互与反套路美学规范），确保协作者、跨工程助手以及其他支持 `SKILL.md` 规范的 AI 工具均可直接读取、互相调用与一键下载。

---

## 一、跨主体发现与下载方式（Multi-Agent Usage）

### 1. 本项目协作者（Antigravity / Cursor / Claude Code）
- 只要克隆或拉取本仓库并在编辑器中打开为 Workspace，系统会自动通过 `.agents/skills/*/SKILL.md` 与 [`.agents/skills.json`](../skills.json) 发现并加载全部技能，**零额外配置**。
- **技能间互调保证**：所有技能以平铺单层结构存放在 `.agents/skills/<skill-id>/SKILL.md`，因此类似 `threejs-game-director` 调用 `../threejs-debug-profiler/SKILL.md`、`emil-design-eng` 调用 `../choreograph/SKILL.md` 或 `game-ui-ux` 引用 `camera-systems` 时，相对与兄弟路径 **100% 互通**。

### 2. 其他外部项目 / 外部 Agent 工具直接拉取
- **方式 A（`skills` CLI 一键安装全部或单个技能）**：
  ```bash
  npx skills add sxy3481841323-ship-it/bruce-happiness-club
  # 或只拉取指定技能：
  npx skills add sxy3481841323-ship-it/bruce-happiness-club --skill threejs-animation
  ```
- **方式 B（仅拉取 `.agents/skills` 目录到其他仓库或 `~/.gemini/config/skills`）**：
  ```bash
  git clone --filter=blob:none --sparse https://github.com/sxy3481841323-ship-it/bruce-happiness-club.git /tmp/bruce-skills
  git -C /tmp/bruce-skills sparse-checkout set .agents/skills
  cp -R /tmp/bruce-skills/.agents/skills/* ~/.gemini/config/skills/
  ```
- **方式 C（程序化索引读取）**：其他自动化工作流或脚本可直接拉取并解析 [`.agents/skills/registry.json`](./registry.json) 获取每个技能的分类、路径、脚本清单与激活描述。

---

## 二、技能分类目录（共 49 项）

### 1. Three.js 核心渲染与骨骼动画（Three.js Core & Animation）（12）
> 负责四足骨骼动画混合、GLTF 异步加载、射线交互、材质灯光、着色器与性能控制。

| 技能目录 ID | 声明名 (`name`) | 配套资源 | 来源仓库 | 职责简述 |
| :--- | :--- | :--- | :--- | :--- |
| [`threejs-animation`](./threejs-animation/SKILL.md) | `threejs-animation` | SKILL.md | `CloudAI-X/threejs-skills` | Keyframe, skeletal and morph-target animation, procedural motion and clip blending, on WebGL or with WebGPU... |
| [`threejs-asset-pipeline`](./threejs-asset-pipeline/SKILL.md) | `threejs-asset-pipeline` | SKILL.md | `CloudAI-X/threejs-skills` | Shrinking glTF assets for three.js with gltf-transform: inspect, validate and optimize commands, Draco, mes... |
| [`threejs-fundamentals`](./threejs-fundamentals/SKILL.md) | `threejs-fundamentals` | SKILL.md | `CloudAI-X/threejs-skills` | Three.js scene setup: scenes and fog, cameras, the renderer and tone mapping, the animation loop, object hi... |
| [`threejs-geometry`](./threejs-geometry/SKILL.md) | `threejs-geometry` | SKILL.md | `CloudAI-X/threejs-skills` | Creating and shaping three.js geometry: built-in shapes, 3D text, vertex buffers and attributes, merging, i... |
| [`threejs-interaction`](./threejs-interaction/SKILL.md) | `threejs-interaction` | SKILL.md | `CloudAI-X/threejs-skills` | Picking with raycasting, camera controls, transform gizmos, drag, hover and box selection for three.js, ide... |
| [`threejs-lighting`](./threejs-lighting/SKILL.md) | `threejs-lighting` | SKILL.md | `CloudAI-X/threejs-skills` | Light types and physical units, shadow maps, HDR environment lighting, light probes, and lighting performan... |
| [`threejs-loaders`](./threejs-loaders/SKILL.md) | `threejs-loaders` | SKILL.md | `CloudAI-X/threejs-skills` | Loading three.js assets: glTF with Draco, meshopt and KTX2 compression, other model formats, textures, HDR ... |
| [`threejs-materials`](./threejs-materials/SKILL.md) | `threejs-materials` | SKILL.md | `CloudAI-X/threejs-skills` | Choosing and configuring three.js materials - unlit, diffuse, specular, PBR, toon, point and line materials... |
| [`threejs-performance`](./threejs-performance/SKILL.md) | `threejs-performance` | SKILL.md | `CloudAI-X/threejs-skills` | Measuring and optimizing three.js speed: render statistics, memory counters, fewer draw calls via merging, ... |
| [`threejs-postprocessing`](./threejs-postprocessing/SKILL.md) | `threejs-postprocessing` | SKILL.md | `CloudAI-X/threejs-skills` | Three.js post-processing: composer pass chains, built-in renderer effects, and the WebGPU/TSL node pipeline... |
| [`threejs-shaders`](./threejs-shaders/SKILL.md) | `threejs-shaders` | SKILL.md | `CloudAI-X/threejs-skills` | Custom GLSL vertex and fragment shaders: uniforms, varyings, shader chunks, extending built-in materials, i... |
| [`threejs-textures`](./threejs-textures/SKILL.md) | `threejs-textures` | SKILL.md | `CloudAI-X/threejs-skills` | Three.js textures: image loading, color spaces, UV channels and transforms, texture types from canvas to HD... |

### 2. Three.js 精品游戏制片与质检（Three.js Game Production & QA）（9）
> 负责主控调度、AAA 画面升级、WebGL 显存剖析、游戏 UI、程序化音效与自动画布验收。

| 技能目录 ID | 声明名 (`name`) | 配套资源 | 来源仓库 | 职责简述 |
| :--- | :--- | :--- | :--- | :--- |
| [`threejs-3d-generator`](./threejs-3d-generator/SKILL.md) | `threejs-3d-generator` | docs×3, scripts×1 | `majidmanzarpour/threejs-game-skills` | Generate, texture, rig, animate, stylize, convert, and download 3D assets for Three.js games via the Tripo ... |
| [`threejs-aaa-graphics-builder`](./threejs-aaa-graphics-builder/SKILL.md) | `threejs-aaa-graphics-builder` | docs×4 | `majidmanzarpour/threejs-game-skills` | Upgrade Three.js games from prototype visuals to premium browser graphics: art-direction critique, procedur... |
| [`threejs-audio-generator`](./threejs-audio-generator/SKILL.md) | `threejs-audio-generator` | docs×1, scripts×1 | `majidmanzarpour/threejs-game-skills` | Generate, convert, clean, and integrate audio for Three.js browser games with ElevenLabs: sound effects, lo... |
| [`threejs-debug-profiler`](./threejs-debug-profiler/SKILL.md) | `threejs-debug-profiler` | docs×1 | `majidmanzarpour/threejs-game-skills` | Debug and profile Three.js browser games: blank canvases, render and runtime bugs, asset and audio loading,... |
| [`threejs-game-director`](./threejs-game-director/SKILL.md) | `threejs-game-director` | docs×3, scripts×2 | `majidmanzarpour/threejs-game-skills` | Entrypoint for building, upgrading, and finishing Three.js browser games. Routes work across the sibling th... |
| [`threejs-game-ui-designer`](./threejs-game-ui-designer/SKILL.md) | `threejs-game-ui-designer` | docs×1 | `majidmanzarpour/threejs-game-skills` | Design premium Three.js game UI: HUDs, menus, overlays, pause/win/lose screens, settings, icon controls, to... |
| [`threejs-gameplay-systems`](./threejs-gameplay-systems/SKILL.md) | `threejs-gameplay-systems` | docs×3, scripts×1 | `majidmanzarpour/threejs-game-skills` | Build and iterate playable Three.js game systems: starter scaffold, architecture, design briefs, core loops... |
| [`threejs-image-generator`](./threejs-image-generator/SKILL.md) | `threejs-image-generator` | scripts×1 | `majidmanzarpour/threejs-game-skills` | Generate and edit 2D image assets for Three.js games with Google's Gemini image API: concept sheets, image-... |
| [`threejs-qa-release`](./threejs-qa-release/SKILL.md) | `threejs-qa-release` | docs×3, scripts×1 | `majidmanzarpour/threejs-game-skills` | Verify and release Three.js browser games: playtest QA, automated bot playtests, mobile and responsive chec... |

### 3. 游戏机制、运镜、对话与声学设计（Game Systems, Camera & Audio）（9）
> 负责 3D 镜头追踪阻尼、底部对白队列、输入控制、手感反馈（Juice）与空间声音设计。

| 技能目录 ID | 声明名 (`name`) | 配套资源 | 来源仓库 | 职责简述 |
| :--- | :--- | :--- | :--- | :--- |
| [`audio-design`](./audio-design/SKILL.md) | `audio-design` | docs×1 | `gamedev-skills/awesome-gamedev-agent-skills` | Engine-neutral game audio technique: bus layout, volume sliders in decibels, loudness, ducking music under ... |
| [`camera-systems`](./camera-systems/SKILL.md) | `camera-systems` | docs×1 | `gamedev-skills/awesome-gamedev-agent-skills` | Builds and tunes game cameras, engine-neutral with Godot and Cinemachine 3 mappings: 2D follow with deadzon... |
| [`dialogue-systems`](./dialogue-systems/SKILL.md) | `dialogue-systems` | docs×2 | `gamedev-skills/awesome-gamedev-agent-skills` | Builds engine-neutral branching dialogue with Ink, Yarn Spinner or a small JSON graph runner: lines, choice... |
| [`game-brainstorm`](./game-brainstorm/SKILL.md) | `game-brainstorm` | docs×1 | `gamedev-skills/awesome-gamedev-agent-skills` | Guides the user through finding and choosing a game concept. Use when the user wants game ideas, a new conc... |
| [`game-feel`](./game-feel/SKILL.md) | `game-feel` | docs×1 | `gamedev-skills/awesome-gamedev-agent-skills` | Adds engine-neutral juice to a working mechanic: trauma-based screen shake, hit-stop, eased tweens, squash ... |
| [`game-quick-design`](./game-quick-design/SKILL.md) | `game-quick-design` | SKILL.md | `gamedev-skills/awesome-gamedev-agent-skills` | Lightweight spec for small changes — tuning adjustments, minor mechanics. Embeds directly into stories; ski... |
| [`game-ui-ux`](./game-ui-ux/SKILL.md) | `game-ui-ux` | docs×1 | `gamedev-skills/awesome-gamedev-agent-skills` | Engine-neutral design rules for game HUDs and menus: anchors and containers, scaling, safe areas, gamepad f... |
| [`input-systems`](./input-systems/SKILL.md) | `input-systems` | docs×1 | `gamedev-skills/awesome-gamedev-agent-skills` | Engine-neutral input architecture with Godot InputMap code: named actions, stick deadzones, buffered presse... |
| [`level-design`](./level-design/SKILL.md) | `level-design` | docs×1 | `gamedev-skills/awesome-gamedev-agent-skills` | Engine-neutral level design with Godot checks: player metrics from the real controller, key and ability gat... |

### 4. 高定界面、微交互编排与移动端原生体验（UI Craft, Motion & Mobile）（16）
> 负责克制高级感布局、多元素出场编排、手机微信触控防崩与极端数据压测。

| 技能目录 ID | 声明名 (`name`) | 配套资源 | 来源仓库 | 职责简述 |
| :--- | :--- | :--- | :--- | :--- |
| [`animate`](./animate/SKILL.md) | `animate` | SKILL.md | `emilkowalski/skills` | Build an animation from scratch, making the decisions in the order that determines whether it feels right —... |
| [`animation-performance`](./animation-performance/SKILL.md) | `animation-performance` | SKILL.md | `emilkowalski/skills` | Keep web animations inside the frame budget — animate composite-only properties, keep motion off the main t... |
| [`animation-vocabulary`](./animation-vocabulary/SKILL.md) | `animation-vocabulary` | SKILL.md | `emilkowalski/skills` | Reverse-lookup glossary that turns a vague description of a web animation or motion effect into its exact t... |
| [`break-ui`](./break-ui/SKILL.md) | `break-ui` | SKILL.md | `emilkowalski/skills` | Try to break a piece of UI by feeding it worst-case data — long names, unbreakable emails, one-letter names... |
| [`choreograph`](./choreograph/SKILL.md) | `choreograph` | SKILL.md | `emilkowalski/skills` | Coordinate several elements that animate together — decide what moves, in what order, how much they overlap... |
| [`emil-design-eng`](./emil-design-eng/SKILL.md) | `emil-design-eng` | SKILL.md | `emilkowalski/skills` | Emil Kowalski's design-engineering philosophy for UI polish, component design, animation decisions, and the... |
| [`frontend-design`](./frontend-design/SKILL.md) | `frontend-design` | SKILL.md | `local-curated` | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Help... |
| [`gestures`](./gestures/SKILL.md) | `gestures` | SKILL.md | `emilkowalski/skills` | Build drag, swipe, and sheet interactions that track the finger 1:1 and stay interruptible. Use when buildi... |
| [`impeccable`](./impeccable/SKILL.md) | `impeccable` | docs×50, scripts×12 | `local-curated` | Use to design, redesign, critique, audit, polish or animate a frontend: websites, landing pages, dashboards... |
| [`improve-animations`](./improve-animations/SKILL.md) | `improve-animations` | SKILL.md | `emilkowalski/skills` | Survey a codebase's animation and motion code as a senior motion advisor, then produce a prioritized audit ... |
| [`interface-design`](./interface-design/SKILL.md) | `interface-design` | SKILL.md | `local-curated` | Craft-first interface design for dashboards, admin panels, SaaS apps, tools, settings pages, data interface... |
| [`learn-taste`](./learn-taste/SKILL.md) | `learn-taste` | SKILL.md | `emilkowalski/skills` | Turn a session's design corrections into rules, with their why, in DESIGN.md, a project skill, or a lint ch... |
| [`mobile-native`](./mobile-native/SKILL.md) | `mobile-native` | SKILL.md | `emilkowalski/skills` | Make a web app feel native on a phone — the small CSS and meta-tag fixes that separate "a website in a brow... |
| [`review-animations`](./review-animations/SKILL.md) | `review-animations` | SKILL.md | `emilkowalski/skills` | Reviews animation and motion code against a high craft bar derived from Emil Kowalski's design engineering ... |
| [`taste-skill`](./taste-skill/SKILL.md) | `design-taste-frontend` | docs×22, scripts×12 | `local-curated` | tasteskill 2.5.1, the anti-slop frontend skill. Builds professional company websites at the level of figma.... |
| [`ui-ux-pro-max`](./ui-ux-pro-max/SKILL.md) | `ui-ux-pro-max` | docs×2, scripts×39 | `local-curated` | UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, building,... |

### 5. 反套路审美、视觉艺术与排版体系（Visual Art & Anti-Slop）（3）
> 负责打破 AI 模板感、建立私宅美学记忆点、程序化纹理与海报级视觉规范。

| 技能目录 ID | 声明名 (`name`) | 配套资源 | 来源仓库 | 职责简述 |
| :--- | :--- | :--- | :--- | :--- |
| [`algorithmic-art`](./algorithmic-art/SKILL.md) | `algorithmic-art` | SKILL.md | `local-curated` | Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this... |
| [`antialgorithm`](./antialgorithm/SKILL.md) | `antialgorithm` | docs×9, scripts×5 | `local-curated` | Stops the safe, average, comfortable pick that AI reaches for first. Use when a creative choice is left ope... |
| [`canvas-design`](./canvas-design/SKILL.md) | `canvas-design` | SKILL.md | `local-curated` | Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill w... |
