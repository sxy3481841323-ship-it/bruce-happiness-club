# 腾讯云 EdgeOne Pages 国内免梯子 + 免备案上线指南

这套游戏的前端、边缘后端接口（`functions/api/*.js`）与本地静态资源已经全部按 **腾讯云 EdgeOne Pages** 标准目录结构写好，**无需购买服务器、无需工信部域名备案**，中国大陆同学在微信里点开默认链接就能直接玩。

---

## 第一步：准备账号与实名认证
1. 打开腾讯云官网 `https://cloud.tencent.com/`，使用微信扫码登录你的腾讯云账号。
2. 前往控制台右上角「账号中心 → 实名认证」，完成个人实名认证（微信人脸扫码 1 分钟搞定）。

## 第二步：把本项目推送到一个 GitHub 仓库
1. 在 GitHub 新建一个仓库（例如 `bruce-happiness-club`）。
2. 在本机项目根目录执行：
```bash
cd /Users/alex/.gemini/antigravity/scratch/bruce-happiness-club
git init
git add .
git commit -m "feat: Bruce Happiness Club phase 1"
git branch -M main
git remote add origin https://github.com/<你的用户名>/bruce-happiness-club.git
git push -u origin main
```
*(注意：`.gitignore` 已自动排除 `.local_kv.json` 等本地临时文件，本机绝对没有硬编码任何 API Key。)*

## 第三步：在 EdgeOne Pages 一键部署
1. 进入 **腾讯云 EdgeOne 控制台 → Pages（边缘网页托管）**。
2. 点击 **创建项目 → 连接 Git 仓库**，授权并选中你刚推送的 `bruce-happiness-club` 仓库。
3. 构建设置保持全空 / 默认即可：
   - **构建命令**：留空（本游戏纯原生静态 + EdgeOne Functions，无需 `npm build`）
   - **输出目录**：`.`（根目录）
4. 点击 **开始部署**，等待约 30 秒。

## 第四步：绑定 KV 存储（让全班共用同一个实时排行榜与吃瓜公告）
1. 在 EdgeOne Pages 控制台左侧进入 **KV 存储**，点击 **新建命名空间**，名称填 `bruce-kv`（任意好记的名字）。
2. 回到你的 `bruce-happiness-club` 项目 → **设置 → 环境变量与绑定（KV Bindings）**。
3. 添加一条 KV 绑定：
   - **变量名称（Variable Name）**：必须严格填写 **`BRUCE_KV`**
   - **绑定命名空间**：选择刚才创建的 `bruce-kv`
4. 点击 **重新部署（Redeploy）** 使绑定生效。

## 第五步：拿免备案链接发给微信群！
部署完成后，EdgeOne Pages 会自动分配一个免费默认二级域名（如 `https://bruce-happiness-club-xxxx.edgeone.app`）：
- **无需域名备案**，中国大陆移动/联通/电信及微信内置浏览器均可直接秒开；
- 以后你把复活小视频放到 `assets/video/rescue.mp4` 后，只要 `git push` 推一次，EdgeOne 就会在 30 秒内自动更新上线。
