# ModAPI 与加载链

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(ModsManager/ModEntity/ModLoader/LoadingScreen 关键段) + 抽样

## 一句话定位

.scmod 从扫描到 `__ModInitialize` 的完整时序、modinfo 字段类型陷阱、钩子注册窗口与 HarmonyX 平台差异。

## 目录地图

| 符号(类/文件) | 绝对路径 | 职责 |
|---|---|---|
| `ModsManager` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModsManager.cs | 扫描 .scmod、modinfo 解析、钩子表、拓扑排序、CombineDataBase |
| `ModEntity` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModEntity.cs | 一个模组的内存表示：文件清单/资源合并/程序集加载 |
| `SurvivalCraftModEntity` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\SurvivalCraftModEntity.cs | 原版 Content.zip（恒第一） |
| `FastDebugModEntity` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\FastDebugModEntity.cs | Mods/ 散文件虚拟模组（包名 fastdebug） |
| `ModLoader` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModLoader.cs | 模组入口抽象类 + 224 个钩子 |
| `ModInfo` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModInfo.cs | modinfo 字段模型与 LoadOrder 参考区间 |
| `LoadingScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\LoadingScreen.cs | 加载动作队列（全流水线在此） |
| `ModSettingsManager` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModSettingsManager.cs | 键位/手柄/相机注册与设置值 |
| `ModSettingsParser` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModSettingsParser.cs | Settings 页面树解析 |
| `ZipArchive` | E:\SurvivalcraftAPIProject\Survivalcraft\Game\ZipArchive.cs | 手写 zip 读取器（Deflate/Store 子集） |
| `ContentManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\ContentManager.cs | Assets/ 键注册与缓存 |
| `SubsystemUpdate` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemUpdate.cs | IUpdateable 驱动（补丁高频目标） |

## 核心机制

### 加载链：从进程启动到主菜单

启动 `Program.cs` 第 0 帧建 `LoadingScreen` → `Enter()` 调 `InitActions()`（LoadingScreen.cs:673-685）排 30+ 动作 → `Update()` 消费队列（`:698` 起，`while (!m_isContentLoaded || sw.ElapsedMilliseconds < 100)`，每帧 100ms 预算；`ModLoadingActoins` 优先于 `LoadingActoins`）。主链（当前源码行号）：

| 步 | 行(LoadingScreen.cs) | 做什么 |
|---|---|---|
| 1 | :160-164 | `ContentManager.Initialize` + `ModsManager.Initialize`：扫 `Mods/` 递归收集 `.scmod`（ModsManager.cs:788 GetScmods；后缀 `ToLowerInvariant` 比较）→ 过 `GetDecipherStream`（加固包还原，:1083 起）→ 构造 ModEntity，`InitResources` 读 modinfo/modsettings、**`FileSize > 0` 才登记**（ModEntity.cs:191-275）、五道禁用判定 |
| 2 | :220-238 | 依赖检查 `CheckDependencies`，启用的灌进 `ModList` |
| 3 | :242-246 | `CombineContent()`：各模组 `Assets/` 前缀剥掉后 `ContentManager.Add`（AddOrUpdate → **后者覆盖前者**） |
| 4 | :248-272 | `GetAssemblies()` 读 dll（ModEntity.cs:383-404：**排除 Assets/ 下的 dll、黑名单 Survivalcraft/Engine/EntitySystem.dll**，`Assembly.Load(byte[])`）；登记 `ModsManager.Dlls` 同 FullName 高版本优先 |
| 5 | :274-275 | `ModHooks.Clear()` + `m_tempModHooks.Clear()` |
| 6 | :277-300 | 逐程序集 `HandleAssembly`（ModEntity.cs:406-436：枚举类型，`IsSubclassOf(ModLoader)` 且非抽象 → `Activator.CreateInstance` → **`__ModInitialize()`**）；异常 → `Handle assembly failed` 三段日志 + **踢掉全部非原版模组** + LoadingFailedScreen |
| 7 | :455-471 | 语言加载 `LoadLauguage`、`LanguageControl.SetUsual`、FontManager |
| 8 | :470 | `ParseAllModSettings`（Settings 树解析，依赖模组类型故延后到此） |
| 9 | :481 | JS 模组（`#if !IOS && !BROWSER`） |
| 10 | :480 | `DealWithTempModHooks`（ModsManager.cs:205-213）：暂存表倒进正式表——**钩子注册窗口 = 第 5 步到第 10 步之间**，错过窗口的注册静默丢弃 |
| 11 | :483-496 | `OnLoadingStart` 钩子（可往队列塞动作，先于原版界面注册） |
| 12-16 | :497-549 | ClothingSlot/TextureAtlasManager → `DatabaseManager.Initialize` + `LoadXdb` + `CombineDataBase`（ModEntity.cs:321-335 调 ModsManager.cs:1083，Guid 匹配合并进 Database 根）→ `LoadDataBaseFromXml` → `BlocksManager.Initialize`（分配方块 ID、读模组 .csv、发 `BlocksInitalized` 钩子）→ `CraftingRecipesManager.Initialize` → 各 Manager |
| 17 | :552-555 | `ModSettingsManager.LoadModSettings()`：**设置值/键位/相机注册从这里才可读** |
| 18 | :558 | `InitScreens()`（LoadingScreen.cs:609-651 注册 41 个原版 Screen） |
| 19 | :578-582 | 遍历 `modEntity.Loaders` 调 `OnLoadingFinished(actions)`——**不走钩子表、注册与否都执行**；读设置/建界面的正确时机 |
| 20 | :583+ | 键位兼容组初始化（`InitKeyCompatibleGroups` 是真钩子要注册）→ 切主菜单 |

### modinfo.json 字段解析（含类型陷阱）

解析函数 `ModsManager.DeserializeJson`（ModsManager.cs:219-346），只 `TryGetProperty` + ValueKind 白名单，**未知键无告警**；允许注释与尾逗号（JsonReader.DefaultJsonOptions）。13 个键：

| 键 | 要求 | 写错的后果 | 锚点 |
|---|---|---|---|
| `Name` | 字符串，**唯一不做类型校验的键** | 非字符串 → `GetString()` 抛 → modinfo 整份失败 → `NoModInfo` 禁用 | :221-223 |
| `Version`/`ApiVersion` | 字符串 | 非字符串静默忽略；NuGetVersion 解析失败降级字符串相等比较 | :225-244 |
| `PackageName` | 全局唯一非保留字 | 空/含 `;`/`survivalcraft`/`fastdebug` → `InvalidPackageName` 完全不加载 | :260-262 |
| `LoadOrder` | **JSON 数字** | `"10000"` 字符串 → 静默退 0；超 int32 → 整份解析失败 | :333-336 |
| `NonPersistentMod` | **JSON 字面量 true** | `"true"`/1/`"True"` 全视为 false（会进存档 UsedMods） | :338-341 |
| `GameplayImpactLevel` | 字符串且**大小写敏感** | `"cosmetic"` → TryParse 失败静默退 `Cosmetic`（合法值 Cosmetic/Assist/Turbo/Break/Godmode） | :342-346 |
| `Settings` | 数组 | 对象形态被忽略（设置面板空）；先 Clone 到 RawSettings 延后解析 | :348-352 |
| `Dependencies` | 数组或对象 | 依赖缺失 → `DependencyError` 禁用 | :247-331 |
| `$schema`/`Email` | 不读 | 零输出 | — |

加载顺序三层：`LoadOrder` 升序 → `SortModListAll` 稳定 Kahn 拓扑（依赖 + 玩家 `LoadAfter`，ModsManager.cs:509-574，环不丢模组只退回原序追加队尾）→ 玩家管理页改序落 `SettingsManager.ModLoadAfters`（分号对，奇数段整串作废）。参考区间：ThemeMod=-16384、Default=0、HelpfulMod=16384（ModInfo.cs:5-10）。**"必须比 X 先/后"优先用 `RegisterHook` 第三参，别依赖 LoadOrder**。

### ModLoader 契约与钩子全集

`public abstract class ModLoader`（ModLoader.cs:10）：`Entity` 反向引用（:11）、`Priority`（:16，同模组多 Loader 时最小者为主 Loader）、`__ModInitialize()`（:21，**唯一初始化入口**）、`ModDispose()`（:61，只在 `ModsManager.Reboot` 链上被调；退出游戏/离开存档不调）。发现判据只有 `IsSubclassOf(typeof(ModLoader)) && !IsAbstract` + **public 无参构造**（internal 类或带参构造 → `MissingMethodException` 且连坐）。

- 224 个 `public virtual` 钩子，重写**不会**自动生效，必须 `ModsManager.RegisterHook("钩子名", this[, priority])`（ModsManager.cs:182-203，优先级 `(priority<<16)|注册序号`，越小越先）。
- 例外（不走钩子表）：`OnLoadingFinished`、`LoadSettings/SaveSettings`、`OnXdbLoad`、`ModDispose`、`GetKeyboardMappings/GetGamepadMappings/GetCameraList`（直接轮询）。
- 调用 `HookAction(name, lambda)`：lambda **return true 就地截断**后面的模组；截断名单（当前源码）：`SetShaderParameter`、`ModelShaderParameter`、`ChangeSkyColor`、部分 `GenerateChunkVertices`。钩子异常每 (钩子,Loader) 组合只 `Log.Error` 第一次，之后静默。
- 钩子名是字符串：注册名与方法名可能不一致（如 `"UpdatePlayerInputDrop"` 调的是 `OnPlayerInputDrop`），以源码 `HookAction` 调用点字符串为准。
- `OnCameraListInit` 注册了但全仓无派发点（死钩子），相机入口是 `ManageCameras`。

### HarmonyX 平台差异

| 平台 | Harmony | 依据 |
|---|---|---|
| Windows/Linux/Android | 可用（Android 额外锁 MonoMod.Core） | Survivalcraft.Android.csproj:34 |
| iOS / 网页版 | **无**：`<PackageReference Remove="HarmonyX" />`；iOS 连 dll 都不可用（无 JIT），网页版完全不支持模组 | Survivalcraft.IOS.csproj:27、Survivalcraft.Browser.csproj:14 |

运行时程序集名 `0Harmony.dll`；编译期引用来自 NuGet 包 `SurvivalcraftAPI.Survivalcraft` 传递依赖。游戏本体零 Harmony 调用 → API 升级改方法后补丁**静默消失**，每个 patch 目标升级时重读源码。补丁删不掉（Unpatch 语义=零补丁重 patch 且全局）；Reboot 后旧实例补丁仍在，同一 postfix 可能跑两遍 → 补丁内自判重。补丁装在 `__ModInitialize` 里且 `try/catch` 包住（否则连坐）。patch `SubsystemUpdate.Update` 类方法注意：`UpdatesPerFrame` 睡觉时=20、ESC 菜单 dt=0、主菜单不跑。

### .scmod 包结构

zip 根：`modinfo.json`（必需）、`Assets/**`（前缀剥掉注册进 ContentManager；**拼写必须一字不差 `Assets/`**）、根层 `*.dll`（加载）、`modsettings.json`（根为数组才生效，优先级高于 modinfo 的 Settings）、`icon.webp`→`icon.png`。要点：

- **扩展名比较大小写敏感**：`.CSV`/`.Xdb`/`.DLL` 一律静默跳过（GetFiles 精确相等；`.scmod` 文件名后缀本身倒是忽略大小写）。
- **0 字节条目当不存在**（FileSize>0 才登记）；条目重名 → 整包加载失败；条目名必须 UTF-8；反斜杠归一化后可能与正斜杠条目撞名。
- 压缩只认 Deflate/Store（不支持 LZMA/BZIP2/AES/ZIP64）；整包内容一次性进内存。
- `Assets/` 下 dll 永不加载；黑名单 dll（去目录后文件名比对）：Survivalcraft.dll、Engine.dll、EntitySystem.dll——两道都**无日志**。
- 加固包：读前过 `GetDecipherStream`（中文标记串→倒序/奇偶还原），普通工具打不开不等于坏包；自己的模组默认明文 zip。
- 发布 `-c Release`（Debug 会把 .pdb 打进包）；双击导入同名文件已存在抛异常不覆盖。

## 坑与对策

- **一闪"Loading failed"后只剩原版内容**：某模组 `__ModInitialize` 抛异常连坐全部模组 → 日志搜 `Handle assembly failed`，其后有已加载程序集清单 + `Error assembly` + `Dependencies:` 引用列表（缺哪个引用直接看）。
- **钩子重写了但一次不跑**：注册时机错过窗口（第 5~10 步之间）；或钩子名字符串打错；或该钩子根本不走钩子表 → `__ModInitialize` 里打一行日志确认入口在跑。
- **LoadOrder/NonPersistentMod/GameplayImpactLevel 没生效**：全是 ValueKind/大小写陷阱（见上表）→ 逐键核对 JSON 类型；确认手段：加载顺序看日志 `Loading .csv` 先后；NonPersistent 看存档 UsedMods；影响等级看游戏内菜单。
- **资源在、代码不跑**：dll 进了 `Assets/`、撞了黑名单名、后缀大写 → 看日志有没有 `Handling assembly [你的程序集]`。
- **`Loaded 0 resource files.`**：资源没在 `Assets/` 下或全是空文件/空目录条目。
- **模组设置面板空**：`Settings` 写成对象而非数组；或解析异常（单模组隔离，只丢设置）。
- **改 dll 重启没变化**：Reboot 不卸载程序集、TypeCache 缓存不清 → 换代码必须重启进程。
- **`Get file [x] failed`**：包内路径/大小写与代码读取不一致（ContentManager 键区分大小写）。

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查某钩子是否存在/何时派发 | `E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModLoader.cs` 搜方法名；再全仓搜 `HookAction("名字"` 找调用点 |
| modinfo 某键到底怎么解析 | `ModsManager.DeserializeJson`（ModsManager.cs:219-346）逐键读 |
| 排查"模组没加载" | 日志顺序：`Loaded N resource files` → `Checking dependencies` → `Loading .dll` → `Handling assembly`；断在哪步查哪步 |
| 注册键位/手柄/相机 | `GetKeyboardMappings`/`GetGamepadMappings`/`GetCameraList` 重写（ModLoader.cs:1931 起），时机见 10-输入与相机.md |
| 打包 .scmod 自查 | 上文"包结构"要点：zip 根 modinfo、Assets/ 拼写、扩展名全小写、无 0 字节、Deflate/Store |
| 往队列加自定义加载动作 | `OnLoadingStart(actions)`（早于原版界面注册）vs `OnLoadingFinished(actions)`（晚于），LoadingScreen.cs:483-496/:578 |
| 存档里记录/校验模组 | `SubsystemUsedMods.cs` + `CompareModVersion`；另见 11-存档持久化.md |
| HarmonyX 用法与平台规避 | 上文平台差异表；游戏侧零 Harmony → 每次升级重验 patch 目标 |
