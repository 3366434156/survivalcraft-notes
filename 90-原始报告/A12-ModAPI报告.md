# A12 - ModAPI 与加载链域原始报告（ModsManager 全目录深读）

> 日期: 2026-10-31 · 范围: E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ 全部 72 个 .cs（含 Community\ 子域 48 个），16,876 行，全部实读（ModLoader.cs 2338 行分 2 段读完全文，其余单次全文）
> 回写: 10-SC引擎\12-ModAPI与加载链.md（更新）、10-SC引擎\12a-ModsManager明细.md（新建）

## 一、覆盖统计

- 顶级 24 文件 / Community 根 7 / Authentication 2 / Community 子目录 10 / Downloads 5 / LocalResources 14 / Modpacks 3 / Settings 1 / Transfers 6 = 72。
- 旧页面断言核对：钩子数 224 → 实数 **236 个 public virtual 成员**（含 Priority 属性与带返回值钩子）；`HookAction` 派发点 233 处 + `HookActionReverse` 1 处（ComponentLocomotion.cs:288）。`OnCameraListInit` 仍为死钩子（仅 SurvivalCraftModLoader.cs:17 注册、无派发点）。`OnModSettingChanged` 确认不走钩子表（ModSettingsManager.cs:317 直调）。

## 二、机制发现（按重要性）

1. **Rescan 热对账系统**（ModsManager.cs:644-763）：不重启进程的对账循环。后台线程枚举磁盘 .scmod（Size+LastWriteTime），与 ModListAll 按归一化路径对账；新文件→构造 `IsPendingRestart` 实体（禁用实体不置待重启，:812-815）；文件消失→`IsFileDeleted` 尸体标记；覆盖升级→同路径"已加载+待重启"双实体共存。合入（Add/SortModListAll/DisposeNotEnabledModsResources/ModListRescanned 事件）全部 Dispatcher 封送主线程。`SortModListAll`（:543-608）必须用 ReferenceEqualityComparer——ModEntity.Equals 是包名+版本值语义，直接做字典键会串。
2. **HandleAssembly 四类类型自动发现**（ModEntity.cs:406-442；原版版 SurvivalCraftModEntity.cs:80-120）：ModLoader 子类实例化后**立即** `__ModInitialize`；`IContentReader` 子类注册进 ContentManager.ReaderList（模组可加资源读取器）；Block 子类收进 BlockTypes（原版校验 public static int Index，缺失抛异常）；CreatureType 子类以 **type.FullName** 为键注册进 SubsystemCreatureSpawn.m_creatureSpawnRules。
3. **数据合并协议**：.xdb `CombineDataBase`（ModsManager.cs:1083-1152）Remove/new-* 前缀 DSL + Guid 匹配 + 新 EntityTemplate 自动注入 ModSource 参数（:1087-1110）；改 Class 参数 Value 时进入 **ClassSubstitutes 谈判**（:1153-1212）：非关键类两候选自动取后者，`ImportantDatabaseClasses`（:1056-1077，15 个受保护 GUID，**仅 ModList.Count>3 时生效**）与更多候选时弹人工裁决框。.clo 按 Index+new-/r- 前缀（:938-967），.cr 按"属性+配方文本"找同款配方改/删（:969-996 + :898-936）。
4. **手动禁用是"包名→版本集合"**（ModEntity.cs:249-254）：同包名可多版本共存、精确禁某版本；查重跳过手动禁用对手、且**同相态才互标 Duplicated**（:255-268）。社区下载同包名新版时自动按此机制禁用旧版（DownloadFlowManager.cs:148-173，且挡掉 survivalcraft/fastdebug 防服务端恶意数据禁用核心模组 :155）。
5. **数据驱动设置层全链**：modsettings.json > modinfo.Settings（ModEntity.cs:214-227），RawSettings 延迟到 dll 加载后 ParseAllModSettings 解析（ModsManager.cs:369-382，单模组失败隔离）；ModSettingsParser 树解析（Id 禁 `/`、简单名补 `Game.` 前缀 :93-102、Widget 按值类型默认映射 :23-29）；ModSettingsManager.Get/Set（:232-324），Set 精准分发 OnModSettingChanged 而非广播；持久化进 ModSettings.xml `<DataDrivenSettings>`（:383-398）；`s_loaded` 门闩防启动竞态空缓存覆写盘（:39-40,:166-169）；ModSettings.xml 解析失败也必须走 RegisterAllDataDriven 否则下次保存剥掉全部设置（:103-110）。
6. **依赖检查语义**（ModEntity.cs:463-511）：版本匹配 = NuGetVersion.Satisfies 或 VersionRange.All 或字符串与 OriginalString 相等（:482）；依赖环 A↔B → **双方都 DependencyError**（:486-492）；富写法 {Name,Link} 进日志与缺失依赖展示（:500-504）。
7. **语言系统**：en-US 基表 + 当前语言覆盖表深合并（LanguageControl.cs:180-238，数组按索引合并）；Get 回退英文表（:266-282）；TryGetBlock 支持 "名:data" 回退 "名:0"（:350-361）；切语言 = 全屏重建 + CraftingRecipesManager.Initialize 重跑 + 字体链同步重建（:371-406）。
8. **JS 模组面**：Jint `AllowClr(全程序集)` + DebugMode（JsInterface.cs:33-38）——JS 可直调任意 C#；handlers 数组约定 + JsModLoader 桥 8 个钩子；HTTP 远程控制（DEBUG 全卡 28256 / RELEASE 回环随机口 + password 头）。
9. **社区下载管线**（Community/Downloads）：队列状态机 8 态（DownloadQueueManager.cs）+ URL+文件名去重 + 旧格式明文 Token 检测即重写（:200-207）；导入成功即时落盘"已导入"标记防进程死亡后重复导入（QueueDialog.cs:50-57）；FileAlreadyExistsException 类型化携带路径供覆盖确认（:873-876）；失联对话框存活判据 = 在 DialogsManager.Dialogs 且父链可达 RootWidget（QueueDialog.cs:231-261，AuthSessionManager.cs:357-361 同型）。
10. **整合包激活 = 状态备份 + 批量禁用切换**（ModpackManager.cs:178-249）：激活时快照当前模组启停态、按清单批量 setDisabledState、备份持久化；停用时恢复备份文件与模组状态。原子文件层由 TransactionalFileReplacement（.-backup-<32hex> 格式 + 启动扫描回滚）兜底。
11. **JsonModelReader.Load 已下线**（JsonModelReader.cs:98）：MC 式 JSON 方块模型读取直接抛异常，正文只剩注释代码；模型走 .obj（强制三角面，ObjModelReader.cs:141-143）或 glTF。
12. **API 自更新检查**（APIUpdateManager.cs）：AtomGit release API、版本比较=点分十进制转 uint、DTO 字段名反序列化敏感（源码三连警告注释）。
13. **FastDebug 虚拟模组**（FastDebugModEntity.cs）：递归把 Mods/ 下**所有非 .scmod 文件**当包内容（:36-51）；包名 ctor 为 "debug"（:11）但默认 modinfo 为 "fastdebug"（:127）——散文件调试期包内 modinfo.json 可覆盖元信息并加 "[FastDebug]" 前缀（:26）。
14. **Content.zip 外置优先**（SurvivalCraftModEntity.cs:50-58）：`app:/Content.zip` 存在则用它，否则内嵌资源 "Game.Content.zip"——原版内容替换入口；网页版走 ContentFileBridge 下载等待。
15. **PlayedTime 上报**（PlayedTimeTracker.cs）：按项目自动保存（300s）结算；间隔封顶 2×周期防挂起虚增（:17）；键=包名\n版本\n文件名（:164-169）；队列先落盘、整批成功才出队（:355-409）；读取失败跳过保存防空台账覆盖历史（:232-238）。
16. **加固包双格式**（ModsManager.cs:1291-1347）：标记串1"有头有脸天才少年…"→全文件倒序；标记串2"修改他人mod…"→奇偶交织；StrengtheningMod 生成格式2副本（:1349-1399）。

## 三、新坑列表

1. JsonModelReader.Load 抛异常——.json 模型已下线，用了即崩（JsonModelReader.cs:98）。
2. .obj 非三角面直接抛"模型必须为三角面"（ObjModelReader.cs:141-143）。
3. LoadOrder 文档建议（ModInfo.cs:40-41：主题 -100000~-10000）与枚举 ThemeMod=-16384 数值不一致，别混用两套参考。
4. ManualDisabled 键大小写敏感且用 modinfo 原文包名；社区侧包名大小写不一致会静默失效（DownloadFlowManager.cs:161-163 注释）。
5. DisabledMods 精确到版本：同包名新版不会被旧版的手动禁用连坐（ModEntity.cs:249-254）。
6. 依赖环双双禁用，不是静默忽略（ModEntity.cs:486-492）。
7. ModSettings.xml 解析失败若提前 return 会剥掉所有 <DataDrivenSettings>——引擎已修，mod 侧仿写时注意同坑（ModSettingsManager.cs:103-110）。
8. ModSetting 项 Type 简单名只补 `Game.` 前缀；模组自定义类型必须全限定名（ModSettingsParser.cs:93-102）。
9. 设置 Widget 声明了但不 Supports(Type) 时静默回退默认 Widget（Log.Error 一条），非报错中断（ModSettingItemWidgetFactory.cs:10-23）。
10. SafeMode 下非原版模组包流全部释放，GetFiles 拿不到任何文件（ModEntity.cs:228-232）。
11. 字体链钩子回调可能在线程池线程，禁止碰 UI（ModLoader.cs:2320-2321 注释）。
12. GetMaxInstancesCount 多模组取最大值语义；CompareModVersion false 拒绝读档（ModLoader.cs:616/:56）。
13. OnCameraListInit 死钩子；相机入口 ManageCameras（GameWidget 创建时）。
14. HookActionReverse 仅 ComponentLocomotion.cs:288 一处（OnLocomotionStopped 反向）——反向钩子的截断语义与正向一致。
15. 社区下载/similar 管线大量"await 点后复查 requestId"模式——仿写异步导入必须同款防陈旧（RemoteModpackInstaller.cs:177-182 等）。
16. Jint AllowClr + HTTP 远程控制默认存在（RemoteControlEnabled 打开后），安全面要知情（JsInterface.cs:33-67）。

## 四、页面改动清单

1. 12-ModAPI与加载链.md：状态行改全读结论；目录地图 +5 行（SurvivalCraftModLoader/LanguageControl/JsInterface/Community 概览/明细页指针）；新增 4 个机制小节（HandleAssembly 四类发现、数据合并协议、生命周期禁用/查重/热对账、资源枚举管线、数据驱动设置层——其中 4 个全新）；钩子数 224→236 并补 HookActionReverse/不走钩子表清单扩全；modinfo 表补 4 展示键与 ApiVersion 归一；新增 .json 模型下线/.obj 三角面/同包名互标/依赖环/手动禁用大小写 5 条坑；原版范例表 10 条（全部实读行号）；快查路由 7→16 条。
2. 新建 12a-ModsManager明细.md：72 文件一行一表，按 9 个子目录分组，含行数与实读要点（file:line）。
