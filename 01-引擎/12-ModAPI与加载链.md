# ModAPI 与加载链

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(72/72 文件, 16,876 行, ModsManager\ 全目录含 Community\ 子域)
> 一行一文件明细另见 12a-ModsManager明细.md

## 一句话定位

.scmod 从扫描到 `__ModInitialize` 的完整时序、modinfo 字段类型陷阱、钩子注册窗口、资源合并协议与模组设置/热对账机制。

## 目录地图

| 符号(类/文件) | 绝对路径 | 职责 |
|---|---|---|
| `ModsManager` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModsManager.cs | 扫描 .scmod、modinfo 解析、钩子表、拓扑排序、CombineDataBase、Rescan |
| `ModEntity` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModEntity.cs | 一个模组的内存表示：文件清单/资源合并/程序集加载/依赖检查 |
| `SurvivalCraftModEntity` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\SurvivalCraftModEntity.cs | 原版 Content.zip（恒第一），注册 19 个内容读取器 |
| `FastDebugModEntity` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\FastDebugModEntity.cs | Mods/ 散文件虚拟模组（包名 fastdebug/debug） |
| `ModLoader` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModLoader.cs | 模组入口抽象类 + 236 个 virtual 成员 |
| `SurvivalCraftModLoader` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\SurvivalCraftModLoader.cs | 原版自身 Loader（钩子注册/摄像机/键位组示例） |
| `ModInfo` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModInfo.cs | modinfo 字段模型与 LoadOrder 参考区间 |
| `LoadingScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\LoadingScreen.cs | 加载动作队列（全流水线在此） |
| `ModSettingsManager` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModSettingsManager.cs | 键位/手柄/相机注册 + 数据驱动设置值存取 |
| `ModSettingsParser` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModSettingsParser.cs | Settings 页面树 JSON→描述符 |
| `LanguageControl` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\LanguageControl.cs | 语言表加载/合并/回退/切语言全屏重建 |
| `JsInterface` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\JsInterface.cs | Jint JS 模组运行时 + HTTP 远程控制 |
| `ZipArchive` | E:\SurvivalcraftAPIProject\Survivalcraft\Game\ZipArchive.cs | 手写 zip 读取器（Deflate/Store 子集） |
| `Community\`(48 文件) | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\Community\ | 社区下载/整合包/认证/游玩时长上报（见 12a 明细） |

## 核心机制

### 加载链：从进程启动到主菜单

启动 `Program.cs` 第 0 帧建 `LoadingScreen` → `Enter()` 调 `InitActions()`（LoadingScreen.cs:673-685）排 30+ 动作 → `Update()` 消费队列（`:698` 起，每帧 100ms 预算；`ModLoadingActoins` 优先于 `LoadingActoins`）。主链（当前源码行号）：

| 步 | 行(LoadingScreen.cs) | 做什么 |
|---|---|---|
| 1 | :160-164 | `ContentManager.Initialize` + `ModsManager.Initialize`：扫 `Mods/` 递归收集 `.scmod`（ModsManager.cs:788 GetScmods）→ 过 `GetDecipherStream`（加固包还原，:1294 起）→ `TryCreateModEntity`（:806-841）构造实体，`FileSize > 0` 才登记（ModEntity.cs:197-201）、五道禁用判定 |
| 2 | :220-238 | 依赖检查 `CheckDependencies`（ModEntity.cs:463-511），启用的灌进 `ModList` |
| 3 | :242-246 | `CombineContent()`：各模组 `Assets/` 前缀剥掉后 `ContentManager.Add`（AddOrUpdate → **后者覆盖前者**） |
| 4 | :248-272 | `GetAssemblies()` 读 dll（ModEntity.cs:383-404：**排除 Assets/ 下的 dll、黑名单 Survivalcraft/Engine/EntitySystem.dll**，`Assembly.Load(byte[])`）；登记 `ModsManager.Dlls` |
| 5 | :274-275 | `ModHooks.Clear()` + `m_tempModHooks.Clear()` |
| 6 | :277-300 | 逐程序集 `HandleAssembly`（ModEntity.cs:406-442：四类类型自动发现，见下节）；异常 → `Handle assembly failed` 三段日志 + **踢掉全部非原版模组** + LoadingFailedScreen |
| 7-8 | :455-471 | 语言加载 `LoadLauguage`（en-US 先行、当前语言随后，ModEntity.cs:167-186）、`ParseAllModSettings`（设置树解析依赖模组类型故延后） |
| 9-10 | :479-496 | JS 模组（`#if !IOS && !BROWSER`）→ `DealWithTempModHooks`（ModsManager.cs:205-214）：暂存表倒进正式表——**钩子注册窗口 = 第 5 步到第 10 步之间**，错过窗口的注册静默丢弃 |
| 11 | :483-496 | `OnLoadingStart` 钩子（可往队列塞动作，先于原版界面注册） |
| 12-16 | :497-549 | ClothingSlot/TextureAtlasManager → `DatabaseManager.Initialize` + `LoadXdb` + `CombineDataBase`（ModEntity.cs:321-336）→ `LoadDataBaseFromXml` → `BlocksManager.Initialize`（读模组 .csv、发 `BlocksInitalized`）→ `CraftingRecipesManager.Initialize` → 各 Manager |
| 17 | :552-555 | `ModSettingsManager.LoadModSettings()`：**设置值/键位/相机注册从这里才可读** |
| 18-19 | :558-582 | `InitScreens()` 注册 41 个原版 Screen → 遍历 `modEntity.Loaders` 调 `OnLoadingFinished(actions)`——**不走钩子表、注册与否都执行** |
| 20 | :583+ | 键位兼容组初始化（`InitKeyCompatibleGroups` 是真钩子要注册）→ 切主菜单 |

### modinfo.json 字段解析（含类型陷阱）

解析函数 `ModsManager.DeserializeJson`（ModsManager.cs:219-354），只 `TryGetProperty` + ValueKind 白名单，**未知键无告警**；允许注释与尾逗号（JsonReader.DefaultJsonOptions）。13 个键：

| 键 | 要求 | 写错的后果 | 锚点 |
|---|---|---|---|
| `Name` | 字符串，**唯一不做类型校验的键** | 非字符串 → `GetString()` 抛 → modinfo 整份失败 → `NoModInfo` 禁用 | :222-224 |
| `Version`/`ApiVersion` | 字符串 | 非字符串静默忽略；NuGetVersion 解析失败降级字符串相等比较；`"1.80"`→`"1.8"`、`"1.81"`→`"1.8.1"` 归一 | :225-243 |
| `PackageName` | 全局唯一非保留字 | 空/含 `;`/`\n`/`survivalcraft`/`fastdebug` → `InvalidPackageName` 完全不加载 | :238-244, :260-263 |
| `LoadOrder` | **JSON 数字** | `"10000"` 字符串 → 静默退 0；超 int32 → 整份解析失败 | :333-337 |
| `NonPersistentMod` | **JSON 字面量 true** | `"true"`/1/`"True"` 全视为 false（会进存档 UsedMods） | :338-341 |
| `GameplayImpactLevel` | 字符串且**大小写敏感** | `"cosmetic"` → TryParse 失败静默退 `Cosmetic`（合法值 Cosmetic/Assist/Turbo/Break/Godmode） | :342-346 |
| `Settings` | 数组 | 对象形态被忽略（设置面板空）；先 Clone 到 RawSettings 延后解析 | :347-352 |
| `Dependencies` | 数组或对象 | 依赖缺失 → `DependencyError` 禁用；对象写法支持富信息 `{Name, Version, Link}` | :268-332 |
| `Description`/`ScVersion`/`Link`/`Author` | 字符串 | 只存展示字段（ScVersion 注释明言"没有实际用处"） | :244-259 |

版本范围语法 `TryParseVersionRange`（ModsManager.cs:1214-1289）：`=` `>` `>=` `<` `<=` `^`（同大版本）`~`（同次版本）前缀，其余整串丢给 NuGet `VersionRange.TryParse`。加载顺序三层：`LoadOrder` 升序 → `SortModListAll` 稳定 Kahn 拓扑（依赖 + 玩家 `LoadAfter`，ModsManager.cs:543-608，**键用 ReferenceEqualityComparer**——ModEntity 重写了按包名+版本的 Equals，值比较会串键；环不丢模组只退回原序追加队尾）→ 玩家管理页改序落 `SettingsManager.ModLoadAfters`（分号对，奇数段整串作废，Initialize 内解析 ModsManager.cs:493-523）。参考区间：Survivalcraft=int.MinValue、ThemeMod=-16384、Default=0、HelpfulMod=16384（ModInfo.cs:5-10）；文档建议主题 -100000~-10000、辅助 10000~100000（ModInfo.cs:40-41）。

### ModLoader 契约与钩子全集

`public abstract class ModLoader`（ModLoader.cs:10）：`Entity` 反向引用（:11）、`Priority`（:16，同模组多 Loader 时最小者为主 Loader，`HandleAssembly` 末尾按它排序取第一个，ModEntity.cs:440-441）、`__ModInitialize()`（:21，**唯一初始化入口**）、`ModDispose()`（:61，只在 `ModsManager.Reboot` 链上被调）。发现判据只有 `IsSubclassOf(ModLoader) && !IsAbstract` + **public 无参构造**。

- 当前源码 **236 个 `public virtual` 成员**（含 Priority 属性与 5 个带返回值的钩子），重写**不会**自动生效，必须 `ModsManager.RegisterHook("钩子名", this[, priority])`（ModsManager.cs:182-203，优先级 `(priority<<16)|注册序号`，同优先级顺序不定）。全仓 233 处 `HookAction` 派发点 + 1 处 `HookActionReverse`（ComponentLocomotion.cs:288，反向遍历）。
- 例外（不走钩子表）：`OnLoadingFinished`、`LoadSettings/SaveSettings`、`OnXdbLoad`（Loaders 全员直调，ModEntity.cs:334-335）、`ModDispose`、`GetKeyboardMappings/GetGamepadMappings/GetCameraList`（轮询）、`OnModSettingChanged`（ModSettingsManager.Set 精准分发 :306-324）、`GetModFiles/GetModFile`（仅主 Loader，资源枚举拦截）。
- 调用 `HookAction(name, lambda)`：lambda **return true 就地截断**；钩子异常每 (钩子,Loader) 组合只 `Log.Error` 第一次（`m_hookBugLogged`，ModsManager.cs:156-173）。
- `GetMaxInstancesCount` 多模组取最大；`CompareModVersion` 返回 false 拒绝读档；主 Loader 专属钩子仅 `GetModFiles/GetModFile`（ModLoader.cs:31-46，注释明言）。
- 死钩子：`OnCameraListInit` 注册了（SurvivalCraftModLoader.cs:17）但全仓无派发点，相机入口是 `ManageCameras`。
- `OnBuildingBodyFontChainEntries/OnBuildingMonoFontChainEntries/OnFontChainsRebuilt`（ModLoader.cs:2324-2337）：字体双链重建钩子，回调可能在**线程池线程**，勿碰 UI。

### HandleAssembly 四类类型自动发现

`ModEntity.HandleAssembly`（ModEntity.cs:406-442）枚举程序集全部类型，分四类收编：
1. `ModLoader` 子类非抽象 → 实例化、`Entity=this`、**立即 `__ModInitialize()`**、进 `ModsManager.ModLoaders`；
2. `IContentReader` 子类 → `ContentManager.ReaderList.TryAdd(reader.Type, reader)`——**模组可注册自定义资源读取器**；
3. `Block` 子类 → 收进 `BlockTypes`（原版版还会校验 `public static int Index` 字段，缺失直接抛异常，SurvivalCraftModEntity.cs:100-114）；
4. `CreatureType` 子类 → `SubsystemCreatureSpawn.m_creatureSpawnRules.TryAdd(type.FullName, type)`——**类全名即 .xdb 生成规则里的引用名**。

### 数据合并协议（.xdb/.clo/.cr）

三套 XML 合并共用"属性前缀 DSL"（ModEntity.LoadXdb/LoadClo/LoadCr 逐文件喂给 ModsManager）：
- **.xdb** `CombineDataBase`（ModsManager.cs:1083-1152）：`Remove` 属性+Guid → 删节点；`new-*` 属性+Guid → 改属性（特例：改的是 `Class` 参数的 Value → 记入 ClassSubstitutes 谈判表）；无前缀 → `Modify()` 按 Guid 递归找同节点改/加。新增 EntityTemplate 自动补 `ModSource` 参数（:1087-1110，包名溯源）。
- **类替换谈判** `DealWithClassSubstitutes`（ModsManager.cs:1153-1212）：两个候选时，非关键类自动用后到者；`ImportantDatabaseClasses`（:1056-1077，**仅 ModList.Count > 3 时启用**的 15 个受保护 GUID：ComponentBody/Health/Player/Miner/RunAwayBehavior/Gui、SubsystemTerrain/Explosions/Projectiles/Pickables/Time、ComponentDispenser/Factors/Level/Clothing）与多候选时弹 `SelectClassSubstituteDialog` 人工裁决，玩家选择持久化。
- **.clo** `CombineClo`（:938-967）：按 `Index` 匹配，`new-*` 改属性、`r-*`/`Remove` 删元素、其余追加。
- **.cr** `CombineCr`（:969-996）：`new-*` → 按"属性全等+配方文本一致"找同款配方改写（`FindSameCraftingRecipeXElement` :898-936）；`r-*`/`Remove` → 删同款配方；其余追加。

### 模组生命周期：禁用/查重/热对账（Rescan）

- 禁用判定顺序（ModEntity.InitResources :233-269）：`NoModInfo` → `InvalidPackageName` → `Manually`（`DisabledMods` 是 **包名→版本集合**，按版本精确禁用 :249-254）→ `Duplicated`（跳过手动禁用的对手；**同相态才互标**——启动期实体 vs rescan 待重启实体豁免 :262-268）。
- `IsPendingRestart`（待重启）与 `IsDisabled` 正交（ModEntity.cs:19-20）；`IsFileDeleted` 是"运行中尸体"标记。rescan 期间同路径出现"已加载+待重启"双实体属合法覆盖升级态。
- `RescanModsAsync`（ModsManager.cs:644-763）：后台线程对账磁盘 vs `ModListAll`（路径归一化键 + Size/LastWriteTime 比对）→ 新文件构造待重启实体 → 主线程合入（Add/排序/释放未启用包流）→ 发 `ModListRescanned` 事件。**IO 与解析在后台、GL 操作封送主线程**是本域线程模型的范本。
- `DisposeNotEnabledModsResources`（:610-622）：禁用/未生效实体的 zip 流即时释放（引用比较去重）。
- `Reboot()`（:121-128）：存设置 → 全 ModList `Dispose()`（逐 Loader `ModDispose()`）→ 切 Loading 屏重启加载；程序集永不卸载。

### 资源枚举管线与 GetModFiles 拦截

所有"读模组内某类文件"都走 `ModEntity.GetFiles(extension, action)`（ModEntity.cs:98-121）：先问主 Loader 的 `GetModFiles`（可 `skip=true` 完全接管），再精确匹配扩展名（**大小写敏感**）逐条 `ExtractFile` 进内存流。单文件读取 `GetFile`/`GetAssetsFile`（:140-162）同理过 `GetModFile` 拦截。`.csv/.xdb/.clo/.cr/.dll/.js/Lang/*.json/icon` 全部经此管线；FastDebug 版直接读磁盘 `Mods/` 下除 `.scmod` 外所有散文件（FastDebugModEntity.cs:36-51）。

### 数据驱动设置层

- 来源优先级：**modsettings.json > modinfo.json 的 Settings 字段**（ModEntity.cs:214-227）；两者都在 `InitResources` 阶段只 Clone 原始 JSON 到 `RawSettings`，等 dll 加载完由 `ParseAllModSettings` 统一解析（ModsManager.cs:369-382，单模组解析失败只丢设置不连坐）。
- 树结构：页面 `{Id, Name, Title, Description, Items[]}`、项 `{Id, Type, Default, Widget, WidgetProperties, Name, Description}`、分隔符 `{Separator:true}`、标签（Text 或裸 Id）；Id 禁 `/`（ModSettingsParser.cs:31-89）。类型解析：简单名自动补 `Game.` 前缀，模组类型须全限定名（:93-102）。默认 Widget 按值类型选：bool→BoolButton、enum→EnumSelectionDialog、数值→NumberSlider、string→TextBox（:23-29）。
- 存取：`ModSettingsManager.Get<T>(params string[] path)`（path=包名+逐级 Id+项 Id）/`TryGet`/热路径 `Get<T>(ModSettingItem)`；`Set(path,value)` 写字典→发 `SettingChanged` 事件→**精准分发**到该包 `OnModSettingChanged(subPath,value)`（ModSettingsManager.cs:232-324）。值以 `HumanReadableConverter` 字符串形式持久化进 ModSettings.xml 的 `<DataDrivenSettings>`（:383-398）。
- 键位/手柄/相机：`GetKeyboardMappings/GetGamepadMappings/GetCameraList` 的 yield 返回即默认值，`LoadModSettings` 时逐模组灌入并 ApplyOverrides（:113-151）；重置函数逐模组重建（:413-453）。`s_loaded` 门闩防启动竞态期空缓存覆写盘（:39-40, :166-169）。

### HarmonyX 平台差异

| 平台 | Harmony | 依据 |
|---|---|---|
| Windows/Linux/Android | 可用（Android 额外锁 MonoMod.Core） | Survivalcraft.Android.csproj:34 |
| iOS / 网页版 | **无**：`<PackageReference Remove="HarmonyX" />`；iOS 连 dll 都不可用（无 JIT），网页版完全不支持模组 | Survivalcraft.IOS.csproj:27、Survivalcraft.Browser.csproj:14 |

运行时程序集名 `0Harmony.dll`；游戏本体零 Harmony 调用 → API 升级改方法后补丁**静默消失**。补丁删不掉（Unpatch 语义=零补丁重 patch 且全局）；Reboot 后旧实例补丁仍在，同一 postfix 可能跑两遍 → 补丁内自判重。补丁装在 `__ModInitialize` 里且 `try/catch` 包住。dll 解析回退链：`AppDomain.AssemblyResolve` 先查 `ModsManager.Dlls` 再查 `TypeCache.LoadedAssemblies`（ModsManager.cs:525-538）——模组 dll 互相引用靠它。

### .scmod 包结构

zip 根：`modinfo.json`（必需）、`Assets/**`（前缀剥掉注册进 ContentManager；**拼写必须一字不差 `Assets/`**）、根层 `*.dll`（加载）、`modsettings.json`（根为数组才生效）、`icon.webp`→`icon.png`（webp 先到先得，icon 两段加载：后台解数据+主线程传 GPU，ModEntity.cs:70-91）。要点：

- **扩展名比较大小写敏感**（`.CSV`/`.Xdb`/`.DLL` 静默跳过；`.scmod` 文件名后缀本身忽略大小写）；**0 字节条目当不存在**；条目重名 → 整包加载失败；条目名必须 UTF-8。
- 压缩只认 Deflate/Store；整包内容一次性进内存。`Assets/` 下 dll 永不加载；黑名单 dll（去目录后文件名比对）两道都**无日志**。
- 加固包：`GetDecipherStream`（ModsManager.cs:1294-1347）识别两条中文标记串（:1291-1292），标记1=全文件倒序、标记2=奇偶交织还原；`StrengtheningMod`（:1349-1399）生成强化副本。普通工具打不开不等于坏包。
- SafeMode（ModEntity.cs:228-232）：非原版模组全部清空 ModFiles 并释放包流。
- 发布 `-c Release`；双击导入 `ImportMod` 同名文件抛 `FileAlreadyExistsException` 不覆盖（ModsManager.cs:446-466）。

### JS 模组与远程控制（Windows/Android，非 iOS/Browser）

`JsInterface.Initiate`（JsInterface.cs:29-68）：Jint 引擎 `AllowClr(全部程序集)`——**JS 可直接调 C#**；先执行外置 `app:init.js`。约定：JS 侧定义 `keyDownHandlers/keyUpHandlers/frameHandlers/{钩子名}Handlers` 数组，`RegisterEvent` 挂原生事件并按需把 `JsModLoader` 注册进钩子表（JsModLoader.cs 桥接 8 个钩子）。附带 HTTP 远程控制：DEBUG 固定 `http://+:28256/`、RELEASE 只绑回环+随机端口，POST 带 password 头可远程执行脚本（:228-335）。**安全敏感：AllowClr+HTTP 常驻，别在非隔离环境启用。**

## 坑与对策

- **一闪"Loading failed"后只剩原版内容**：某模组 `__ModInitialize` 抛异常连坐全部模组 → 日志搜 `Handle assembly failed`。
- **钩子重写了但一次不跑**：错过注册窗口（第 5~10 步）；或钩子名字符串打错；或该钩子不走钩子表 → `__ModInitialize` 里打日志确认。
- **LoadOrder/NonPersistentMod/GameplayImpactLevel 没生效**：全是 ValueKind/大小写陷阱（见上表）。
- **资源在、代码不跑**：dll 进了 `Assets/`、撞了黑名单名、后缀大写 → 看日志有没有 `Handling assembly`。
- **`.json` 方块模型加载直接抛异常**：`JsonModelReader.Load` 现为 `throw new Exception("很抱歉，JsonModel功能暂时下线")`（JsonModelReader.cs:98），MC 式 JSON 模型功能已被下线，模型用 .obj/gltf。
- **.obj 模型解析失败**：非三角面直接抛"模型必须为三角面"（ObjModelReader.cs:141-143）；`vt/vn` 索引缺一不可。
- **模组设置面板空**：`Settings` 写成对象而非数组；或 Type 解析失败（简单名只补 `Game.` 前缀）；单模组隔离只丢设置。
- **改 dll 重启没变化**：Reboot 不卸载程序集、TypeCache 缓存不清 → 换代码必须重启进程。
- **同包名模组互标 Duplicated**：同相态才互标；"禁用旧版+装新版"是合法共存态（ModEntity.cs:255-268）。
- **依赖成环双双禁用**：A 依赖 B 且 B 依赖 A → 两边都 `DependencyError`（ModEntity.cs:486-492），日志 `is dependent on ... which is not allowed`。
- **手动禁用失效**：`DisabledMods` 字典大小写敏感，键必须是 modinfo 侧包名原文（社区下载自动禁用旧版时特意用它，DownloadFlowManager.cs:161-163）。

## 原版范例

| 我要做… | 照抄哪里 |
|---|---|
| 注册钩子（标准入口写法） | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\SurvivalCraftModLoader.cs:15-26 —— 9 条 RegisterHook 一行一个，优先级缺省 |
| 加自定义摄像机 | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\SurvivalCraftModLoader.cs:41-61 —— GetCameraList 给序号 + ManageCameras 建实例挂条件委托 |
| 加按键兼容组 | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\SurvivalCraftModLoader.cs:28-39 —— 同组键位不显示冲突 |
| 写生物生成规则类 | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\StandardCreatureSpawnRule.cs:34-59 —— 构造签名 (SubsystemCreatureSpawn, ValuesDictionary) 是注册协议 |
| 声明模组设置页面 | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModSettingsParser.cs:23-53 —— 树形 JSON 形状与 Id 规则；读值见 ModSettingsManager.cs:235-263 |
| 拦截自己的资源枚举 | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModEntity.cs:98-121 —— GetFiles 先问 Loader.GetModFiles 再走 zip |
| 声明依赖版本范围 | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModsManager.cs:1214-1289 —— =/>/>=/</<=/^/~ 全语法 |
| 合并原版 Database | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModsManager.cs:1083-1152 —— new-*/Remove 前缀 DSL 与 ModSource 注入 |
| 多语言包结构与回退 | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModEntity.cs:167-186 + LanguageControl.cs:266-282 —— en-US 基表+语言覆盖表+英文回退 |
| 后台任务+帧泵收尾 | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\Community\CommunityFramePump.cs:12-31 —— Window.Frame 挂轮询、逐轮询 try/catch 防崩进程 |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查某钩子是否存在/何时派发 | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModLoader.cs 搜方法名；再全仓搜 `ModsManager.HookAction("名字"` |
| modinfo 某键到底怎么解析 | `ModsManager.DeserializeJson`（ModsManager.cs:219-354）逐键读 |
| 排查"模组没加载" | 日志顺序：`Loaded N resource files` → `Checking dependencies` → `Loading .dll` → `Handling assembly`；断在哪步查哪步 |
| modinfo 之外一个文件是干嘛的 | 12a-ModsManager明细.md 一行一文件表 |
| 注册键位/手柄/相机 | `GetKeyboardMappings/GetGamepadMappings/GetCameraList`（ModLoader.cs:1931-1955），灌入时机 ModSettingsManager.cs:113-151 |
| 打包 .scmod 自查 | 上文"包结构"要点：zip 根 modinfo、Assets/ 拼写、扩展名全小写、无 0 字节、Deflate/Store |
| 往队列加自定义加载动作 | `OnLoadingStart(actions)` vs `OnLoadingFinished(actions)`（后者不走钩子表） |
| 存档里记录/校验模组 | `SubsystemUsedMods.cs` + `CompareModVersion`；另见 11-存档持久化.md |
| HarmonyX 用法与平台规避 | 上文平台差异表；每次升级重验 patch 目标 |
| 覆盖/新增/删除原版配方或实体 | 数据合并协议节（new-*/Remove 前缀），范例表 8 |
| 模组设置项读不到值 | path 必须全链（包名+页面Id+项Id）；值未 `Set` 过且无 Default → `Get` 抛 KeyNotFound，用 `TryGet` |
| 下载社区模组/自动更新逻辑 | Community\Downloads\DownloadFlowManager.cs（队列状态机）+ LocalResources\LocalModNetworkManager.cs（更新检查） |
| 整合包(.zip/清单)如何生效 | Community\Modpacks\ModpackManager.cs（激活=按记录批量改 DisabledMods + 备份状态） |
| 模组包被改过的两种加固格式 | ModsManager.cs:1291-1292 两条标记串 + GetDecipherStream 还原算法 |
| JS 模组能干什么 | JsInterface.cs:29-111 —— AllowClr 全量、init.js、handlers 数组约定、HTTP 远程控制 |
