# 布鲁斯 · 全屏互动演出

这是独立于原首页的 Three.js ES Module 引擎。没有改动 `index.html`、原活动入口、状态、API、文案、Functions 或本地服务。运行时只读取同站资源，不需要 npm、CDN、远程字体或远程图片。

## 本地试映

在仓库根目录启动原服务：

```sh
python3 scripts/dev_server.py --port 8778
```

打开 `http://127.0.0.1:8778/cinematic-preview.html`。默认自动演示当前场景；“亲自互动”会从开场重新播放，然后由玩家操作三维道具。“放映目录”可切换全部十幕、试映 85 分跌破阈值和 70 分冷战。“十幕连映”会在每幕结算后自动继续。

换分概率大于零的活动可在目录中点击“换分试映”：它使用固定随机种子和明确标注为“试映样例”的 168 分响应，只展示演出，不请求排行榜。普通试映只报告幸运候选，不编造换分结果。

环境音默认关闭，点击 ♪ 后才创建、恢复 AudioContext。雨声、低频呼噜和黑胶音场均在本地合成。隐藏页面会暂停演出时间与声音，回来后继续。

## 主程入口

在宿主 HTML 的第一个 module script **之前**加入本地映射：

```html
<script type="importmap">
{"imports":{"three":"./vendor/three.module.js","three/addons/":"./vendor/addons/"}}
</script>
```

```js
import { mountCinematicStage } from './js/cinematic/index.js';

let stage = mountCinematicStage(containerEl, {
  activityId: 'home_brush',
  owner: 'Alex',                 // 或 Meya
  happiness: player.happiness,
  content,                       // 原 data/content.json 的完整对象
  onComplete(result) {
    // result 的精确结构见下方。这里交给主程既有的记分流程。
    // 引擎不调用 API，也不修改 store / localStorage。
    settleActivity(result);
  },
  onExit() {
    // 关闭演出并返回活动列表；退出不产生分数。
    showActivityList();
  },
});

// 路由切换或父页面卸载时调用；可以重复调用。
stage.destroy();
```

`settleActivity`、`showActivityList` 是宿主提供的处理函数，不属于本模块。舞台会固定覆盖视口，使用 Shadow DOM 隔离样式，临时锁定页面滚动。多个实例的滚动锁按引用计数恢复；正常使用时请销毁前一舞台再挂载下一舞台。

### 回调与记分

```ts
onComplete({
  outcome: 'win' | 'phone_fail' | 'hazard_fail',
  delta: number,
  triggerSwapCandidate: boolean,
  summaryLine: string
})
```

- 开场 2.5 秒 → 互动及动作短片 → 收尾 3.5 秒 → 结算胶囊与一次 `onComplete`。自动导览也使用同一动作、预警、失败和结算路径。
- `summaryLine` 直接选自对应活动的 `win_lines` / `phone_fail_lines` / `hazard_fail_lines`，通过 `textContent` 显示。
- 主程按原流程调用 `apiUpdateScore`，使用返回的玩家、排行榜和 ticker 更新 store。跌破 80 的公告仍由主程通过原 `ticker_templates.collapse` 生成。
- `triggerSwapCandidate` 只表示一次幸运候选；主程在记分成功后按既有逻辑调用 `apiTriggerSwap`。实际交换对象、分数和排行规则始终由后端决定。
- 入场已经低于 80 时，仅播放冷战并提供退出，**不回调完成、不加减分**。活动失败后低于 80，会显示对应冷战收尾和提示。
- 主程应让舞台持续存在至用户退出，避免 store 的普通分数刷新意外卸载正在播放的揭示动画。

原版分值与概率保持一致：

| 活动 | 胜利 | 失败 | 换分候选概率 |
|---|---:|---:|---:|
| home_brush | +11 | -13 | 0 |
| home_rain_vinyl | +12 | -12 | 0 |
| home_hide_seek | +12 | -14 | 12% |
| home_kitchen | +13 | -15 | 0 |
| home_nap | +11 | -14 | 12% |
| street_cafe | +14 | -18 | 22% |
| street_walk | +12 | -14 | 0 |
| street_lawn | +13 | -15 | 18% |
| street_window | +11 | -15 | 0 |
| street_bridge | +14 | -16 | 14% |

### 真实换分揭示

除了稳定的 `destroy()`，返回对象提供 `revealSwap(response)`。可以等原 API 返回后调用：

```js
const swap = await apiTriggerSwap(nickname, pin, reason);
// 先按原流程保存真实响应；再将响应交给仍挂载着的舞台。
stage.revealSwap(swap);
```

也可以让 `onComplete` 返回 Promise：若它最终返回包含有限数值 `newScore` 的真实 swap 响应，舞台自动播放 4.5 秒的光环、粒子、镜头提升及数值揭示。支持原返回字段 `oldScore`、`newScore`、`targetNickname`、`topBonus`。没有幸运候选、重复响应、已销毁实例均不会启动揭示。不确认接口成功就不要调用此方法。

### 可选预览能力

`autoplay: true` 开启自动演出，默认 `false`。`setAutoplay(boolean)` 会销毁当前舞台并从新开场开始，返回对象始终指向新的实例。`getSnapshot()` 是只读的状态、模型模式及渲染资源计数，供验收使用。

`reducedMotion` 默认尊重系统“减少动态效果”，减少手持、环绕和闪光。`quality: 'low'` 降低渲染分辨率并使用接触阴影，适合软件渲染；默认保留真实阴影。`random` 可注入可复现的随机源，仅建议测试使用。

键盘：Tab 选择按钮和场景道具；焦点到道具时会出现简洁的可操作标签；画布获得焦点后 Space/Enter 执行当前安全提示，梳毛需再按一次停止；Escape 退出。触摸使用 Pointer Events，不依赖 hover。

## 角色与 GLB

`bruceModel.js` 导出 `createBruceModel(materials, options)`，返回 `root`、`ready`、`setMood()`、`lookAt(worldVectorOrNull)`、`update()`、`destroy()`。情绪包括 `happy`、`excited`、`curious`、`warn`、`sulk`、`sleep`、`belly`，过渡使用阻尼插值。

当前仓库没有 `assets/models/bruce.glb`，实际显示程序化长毛腊肠犬。角色具有连续曲面的长躯干、短腿、可动长耳、眼球角膜高光、鼻头高光和鼻孔、毛发颜色/凹凸纹理与弯曲垂坠毛束、酒红斜纹丝巾及铜牌。翻肚皮时毛束会按重力方向调整。程序化贴图使用 CanvasTexture，场景与交互全部使用 WebGL 3D。

日后把 GLB 放到 `assets/models/bruce.glb` 即可自动切换：包围盒居中、最低点落地、最长边归一到 2.65，开启网格阴影。约定导出时鼻子朝 +Z、Y 向上。存在 Head/Neck、Ear、Tail 等命名骨骼时会叠加情绪、视线和摇尾；没有骨骼时使用整体弹性呼吸和倾斜。识别 idle/walk/run/sleep 动画，无领巾命名节点时补充程序化领巾。

GLB 缺失的 404 会被正常消化并保留兜底角色；浏览器网络面板仍可看到这次存在性探测。损坏、无法解码或需要尚未配置的 Draco/KTX2 解码器时也会保留兜底。不要为解码器引入外网 CDN。销毁期间的加载会中止，晚到的模型会被立即释放。

## 组织与资源释放

- `director.js`：分镜、输入、自动演出、手机、结算与生命期。
- `scenes/home.js` / `street.js`：10 个完整活动配置；`world.js`：房间、街区、水岸与三维道具。
- `bruceModel.js`：统一角色情绪与双模加载。
- `effects.js`：程序化环境反射、三点光、接触阴影、雨窗、落叶、交互粒子池及景深/调色后期。
- `leash.js`：固定两端的 Verlet 软绳及长度约束，原位更新网格。
- `materials.js`、`sound.js`：本地纹理与可关闭的音场。

`destroy()` 取消 RAF、断开 ResizeObserver、移除输入与可见性监听、取消 GLB fetch、停止并关闭音频、释放 AnimationMixer、几何体、材质、纹理、ImageBitmap、阴影、PMREM 和后期 render targets，最后释放 renderer 并主动丢弃上下文。粒子使用固定池，牵引绳原位更新，不在每帧创建 GPU 资源。

## 验证

可选浏览器验收脚本：`scripts/test_cinematic.cjs`。仅测试需要 Playwright，线上没有此依赖。装好 Playwright 及其 Chromium 后，启动原服务并运行：

```sh
node scripts/test_cinematic.cjs
node scripts/test_cinematic_interactions.cjs
```

可通过 `CHROMIUM_PATH` 指定现成 Chromium，通过 `CINEMATIC_URL` 和 `CINEMATIC_QA_OUTPUT` 指定服务地址和报告目录。第一组覆盖 390×844 的十幕自动结算、1280×800 通知失败、85→72 冷战、70 分入场锁定、确认换分、重复切场销毁、本地资源请求和运行异常。第二组用实际光线拾取点击/拖动测试抛球、牵引环、禁入店及手动梳毛预警；用合成 GLB 校验模型坐标归一、七种情绪和资源释放。软件渲染验收不代表实机 GPU 帧率测量。
