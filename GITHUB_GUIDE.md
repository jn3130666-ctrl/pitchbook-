# GitHub 界面使用指南

仓库地址：https://github.com/jn3130666-ctrl/pitchbook-

---

## 1. 首页 — 查看项目文件

打开仓库地址就能看到所有文件。点进 `docs/` 目录，再点 `.md` 文件就能看到渲染后的周报。

---

## 2. Actions — 查看运行状态

点击顶部导航栏的 **Actions** 标签页。

**查看最新运行：**
- 左侧点 **VC/PE Weekly**
- 中间列表显示每次运行记录
- ✅ 绿色勾 = 成功 / ❌ 红色叉 = 失败 / 🟡 黄点 = 运行中

**手动触发一次：**
- 在 VC/PE Weekly 页面 → 点 **Run workflow**（蓝色按钮）→ 再点 **Run workflow**

**查看运行日志：**
- 点任意一条运行记录 → 点 **run-and-deploy** → 展开每一步查看详细日志。出错了就把日志发给我。

---

## 3. Settings → Secrets — 管理密码

顶部导航栏点 **Settings** → 左侧点 **Secrets and variables** → **Actions**。

会看到已添加的 4 个 Secrets。如需修改：
- 点 Secrets 右侧的 **Update**（铅笔图标）
- 重新输入新值 → **Add secret**

---

## 4. Settings → Pages — 网页访问

顶部导航栏点 **Settings** → 左侧点 **Pages**。

当前配置：
- Branch: **main**
- Folder: **/ (root)**
- 访问地址：`https://jn3130666-ctrl.github.io/pitchbook-/`

如需关闭或更换发布目录，在这里修改。

---

## 5. 查看网页

浏览器打开：
```
https://jn3130666-ctrl.github.io/pitchbook-/
```

页面展示：
- **历史周报列表** — 所有周报按日期倒序排列，点"查看"阅读
- **可下载报告** — 成功下载的报告文件列表

---

## 常用操作速查

| 想做什么 | 操作路径 |
|----------|----------|
| 手动跑一次流水线 | Actions → VC/PE Weekly → Run workflow |
| 看是否跑成功了 | Actions → VC/PE Weekly → 查看 ✅/❌ |
| 看失败原因 | 点运行记录 → run-and-deploy → 看红色步骤的日志 |
| 改邮箱密码 | Settings → Secrets → EMAIL_PASS → Update |
| 看这周的周报 | 点 `docs/` → 点 `.md` 文件 |
| 看网页有没有更新 | 浏览器打开 Pages 地址 → 刷新 |
