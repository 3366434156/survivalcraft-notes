# A31 · Community 与杂项深度补全报告

> 批次: A30b 深学 · 日期: 2026-10-31 · 执行: 五项深度补全（16b / 17a / 13 / 20a+20 / 11）

## 1. Game\Community 72 文件（16b）

**实读清单**：`E:\SurvivalcraftAPIProject\Survivalcraft\Game\Community\` 全目录 72 个 .cs 文件逐个全文实读（Domain 26 + Infrastructure 35 + Models 11，共约 6916 行），行数与 16b 表逐一核对一致。

**改动**：`01-引擎\明细\16b-Game明细2.md` 整表一次 Write 写回（133 行）。状态行 `全列(72/72，头部注释级)` → `全读(72/72，全文实读)`；72 行职责全部升级为带 `文件:行号` 级要点，HTTP/持久化/传输基础设施按任务要求重点标注端点/协议/坑。

**新发现 top**：
- `CommunityHttpDownloader.cs`：断点续传全套验证器协议（ETag/LastModified/总长三重比对 :299-330；416+完整缓存免重下 :127；部分 CDN 206 不回显验证器的放宽规则 :323）；读空闲超时 30s（linked CTS，stall 抛 `CommunityReadIdleTimeoutException` is-a OCE 区分用户取消 :16,88）。
- `CommunityCredentialStore.cs`：v4 凭据格式全貌（每服一文件 sha256(归一化地址).bin、魔数 SCBPAUTH4 :20、Windows DPAPI / 其他平台 AES-GCM+PBKDF2 600k 口令=机器名，威胁模型注释自述仅隔离不知机器名者 :16）；原子写三级降级 :165-212。
- `CommunityDownloadFeedbackClient.cs:84`：fallback token 仅在当前服务器与入队服务器一致时补取——防 B 服令牌发往 A 服外泄+误登出（审查复审 F1 注释）。
- `CommunityDownloadQueuePersistence.cs:124`：恢复的 TempFilePath 只接受缓存目录内 `{id}_*.part` 形态，防手工编辑路径被续传语义读+写穿任意文件。
- `ModpackRegistry.cs`：异源冲突改名 "(2)" 判据=双方 meta SourceUrl，无证据保守判异源 :327,364；解析缓存键含 FNV-1a 内容哈希防同 tick 同大小替换 :465。
- `CommunityUploadClient.cs:170`：又拍云直传仅放行 https+*.upyun.com（防签名明文/中间人）；`ProgressStreamContent:234` 必须重写带 CT 的 SerializeToStreamAsync 重载否则大文件上传取消失效。
- `PostIconRules.cs:35`：img.suancaixianyu.cn 的 https 图标自动加缩略图后缀 `!/fwfh/368x238`。

## 2. Screen 7 个节选文件（17a）

**实读清单**（7 个〔节〕→〔深〕，共 3662 行全文）：
- `Screen\ModsManageContentScreen.Community.cs` (859)
- `Screen\ModpacksManageContentScreen.cs` (939)
- `Screen\Shared\PostTreePresenter.cs` (757)
- `Screen\Community\PostIconLoader.cs` (311)
- `Screen\Community\ModpackIconLoader.cs` (173)
- `Screen\Community\ModpackIconManager.cs` (193)
- `Screen\OriginalCommunity\OriginalCommunityContentManager.cs` (481)

**改动**：`17a-Screen明细.md` 外科手术式 7 行替换+状态行 `全读(〔深〕64、〔节〕7)` → `全读(71/71，全文实读)`；`17-Screen屏幕族.md` 仅状态行同步。未整表 Write。

**新发现 top**：
- `PostTreePresenter.cs:743` ResolveListTotals：服务端分页协议漂移（/user/posts total=页数 count=条数；/post/list 无 count）+ total 谎报（实测恒 2）时弃用回退"已加载到哪算哪"口径。
- `EntityReferenceComparer`（ModsManageContentScreen.Community.cs:21-24）：ModEntity 重写 Equals 后列表定位必须引用比较——主行既有结论的全文件级证据。
- `ModpacksManageContentScreen.cs:195`：下载完成回调专用刷新——PackDownloadCompleted 先于 completedAction 同帧触发，直接刷新拿空列表会误清选中。
- `ModpackIconManager.cs:135`：分离 widget 也先贴 Subtexture（纯字段赋值，滚回重挂即显示），结算即出册。
- `OriginalCommunityContentManager.cs:385`：Feedback 防重复 TryAdd+重复请求延迟 1.5s 报错；:153 用户取消导入不计 Success 也不计 ImportFailure。
- `PostIconLoader.cs:291` CropSubtextureToSquare：图集 UV 归一化坐标下居中正方形裁剪的像素空间推导（:285-290 注释）。

## 3. 物理两个抽样点（13 页）

**实读清单**：
- `E:\SurvivalcraftAPIProject\Survivalcraft\Component\ComponentLocomotion.cs` 360-563 行补全（全文 563/563 读毕）
- `E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemTerrain.cs` Raycast 两重载 86-353 行全文（文件共 613 行）

**改动**：`13-物理与碰撞.md` 状态行 `抽样(...)` 清零；"实体与地形交互判定"节新增"走路速度合成"与"方块射线"两条（走/游/爬/跳既有行号全部实读核对无误并补充冷却/闸门细节）；弹道节 Raycast 描述同步。

**新发现 top**：
- 走路加速度=dt*6*AccelerationFactor*max(地面 FrictionFactor, minFrictionFactor)，摩擦<0.25 记 SlipSpeed 打滑（ComponentLocomotion.cs:429-437）；坐骑衣物 SteedMovementSpeedFactor 参与速度合成 :416-424。
- 梯子脱出冷却 0.2s、梯上跳 0.33s 前扑（:537-552）；冲刺游按 m_swimBurstRemaining 提速 1→2/1→4 倍（:491-496）。
- `SubsystemTerrain.Raycast` 双重载：静态版 :226 给方块 Raycast 传 null terrain，家具等依赖子系统的方块会异常（文档注释 :214-217）；face 判定=命中点到碰撞盒 6 面最近（X-:3/X+:1/Y-:5/Y+:4/Z-:2/Z+:0，:147-178）。

## 4. 内容资源抽样行（20a+20）

**实读清单**（grep `抽样` 找全 6 行，6 文件全文共约 2942 行）：
- `Managers\MotdManager.cs` (443)、`Managers\WebManager.cs` (424)、`Managers\PerformanceManager.cs` (227)、`Managers\ScreenCaptureManager.cs` (161)、`Managers\PlantsManager.cs` (559)、`Managers\Fonts\FontManager.cs` (1128)

**改动**：`20a-内容资源明细.md` 6 行升级去抽样备注+状态行同步；`20-内容与资源管理.md` 仅状态行 "Fonts 抽样" 清零。

**新发现 top**：
- `MotdManager.cs:179-180`：MOTD XML 的 UpdatePeriodHours/UpdateUrl 属性可被服务端下发改写；SaveBulletin 的 /com/api/zh/setnotice 已 [Obsolete] 死接口；编辑/更新钮已被隐藏（:424-425）。
- `WebManager.cs`：每请求 new HttpClient+Referrer=目标地址；ANDROID 分支 progress==null 时退 StreamContent；VerifyResponse 抛状态码+响应体。
- `PerformanceManager.cs:67-133`：三态测量状态机（进世界 60s 后才在 GameScreen 内采 180s 帧）产出长期均值并 Log 上报；m_extraStats 每帧消费即清。
- `ScreenCaptureManager.cs`：>8294400 像素自动 Bmp 否则 Png（:128）；Android 落盘后发 MEDIA_SCANNER_SCAN_FILE 广播；文件尾注"修复 Image 问题后改 WebP"。
- `PlantsManager.cs`：六树型各 16 变体 TerrainBrush 静态构建（种子 33）；树型选择=六概率乘 RangeProbability 梯形隶属取最大再过密度闸门。
- `FontManager.cs`：槽位协议五值+双链构建序全文核实；MonoChain 无 Regular 面回落 DefaultChain 同引用（:655，双 Dispose 去重 :648-650）；CFF2-only 变量字体在发现/导入/匹配面三处一致拒收。

## 5. 存档页状态行（11 页）

**抽样指向核实**：页内除状态行外无"抽样"字样；"+ 抽样"实指状态行所列 7 个"核心段"文件（Project/Entity/ValuesDictionary/GameManager/ProjectData/XmlUtils/VersionsManager）未全文读。

**实读清单**（7 文件全文共 1355 行）：`EntitySystem\GameEntitySystem\Project.cs`(387)、`Entity.cs`(234)、`ProjectData.cs`(66)、`EntitySystem\TemplatesDatabase\ValuesDictionary.cs`(191)、`EntitySystem\XmlUtilities\XmlUtils.cs`(104)、`Survivalcraft\Managers\GameManager.cs`(213)、`VersionsManager.cs`(160)。

**改动**：`11-存档持久化.md` 状态行 `核心段 + 抽样` → `全文`；加载链第 2 步补 mod 组件 LoadOrder+10000 排序事实（Entity.cs:122-124，本次实读新发现）；ProjectData.cs:26-52→:26-54、Project.cs:284-298→:284-297、Entity.cs:217-226→:217-225 行号校正。既有关键断言全数实读复核无误（含"静态事件 Dispose 不清"——Project.Dispose 仅清 OnProjectLoad/EntityAdded/EntityRemoved 三个，BeforeSubsystemsAndEntitiesLoad 与 EntityComponentsInitialized 确实不清）。

## 总行数与遗留

- 全文实读总量：72 文件(≈6916 行) + 7 文件(3662 行) + 2 个物理段(约 470 行) + 6 文件(≈2942 行) + 7 文件(1355 行) ≈ **1.53 万行**；笔记侧改动 8 个文件（16b 整表重写 + 17a/13/20a/11/17/20 六页外科手术）。
- 遗留（非本批次范围，未动）：
  - 20a Fonts 表 `FontLocator.Android.cs(204)/Browser.cs(255)/Linux.cs(302)` 仍标"未深读"（备注是"未深读"非"抽样"，不在本批范围）。
  - 20a Managers 表 `SettingsManager.cs` 仍为"节读"（键位/VR 段归 10 页）；若干"归属页"行按规则不在此重复。
  - 13 页 ComponentLocomotion.cs 前 360 行为既往批次深读成果，本批仅复核其后 204 行涉及的行号引用。
- 禁令遵守：SC 源码零写入、未碰 16a/16 主页/README/台账/skill、未执行任何 git 写命令。
