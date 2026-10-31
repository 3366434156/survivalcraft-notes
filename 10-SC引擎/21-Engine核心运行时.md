# Engine 核心运行时

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(41/41)

## 一句话定位

`E:\SurvivalcraftAPIProject\Engine\Engine\` 平台层：窗口与消息循环、虚拟路径存储、日志、跨线程调度、墙钟与数学/集合基础库，全游戏其余引擎模块都踩在这 41 个文件上。

## 目录地图

| 家族 | 文件(绝对路径前缀 `E:\SurvivalcraftAPIProject\Engine\Engine\`) | 职责 |
|---|---|---|
| 窗口 | `Window.cs`(932行) `WindowMode.cs` `UnhandledExceptionInfo.cs` | 静态窗口门面：平台分派、生命周期事件、帧回调挂载点 |
| 时间 | `Time.cs` | 墙钟单例：帧号/帧时长/延时队列/限帧 |
| 线程 | `Dispatcher.cs` | 跨线程动作排回主线程的唯一通道 |
| 存储 | `Storage.cs`(860行) `OpenFileMode.cs` `RunPath.cs` | 虚拟路径(app:/data:/system:/android:/config:)到真实路径的解析与全套文件操作 |
| 日志 | `Log.cs` `ILogSink.cs` `LogType.cs` `ConsoleLogSink.cs` `StreamLogSink.cs` `DebugLogSink.cs` `DebugTextWriter.cs` | 多 sink 日志：Console/Stream/Debug 三种实现 |
| 向量矩阵 | `MathUtils.cs` `Vector2/3/4.cs` `Matrix.cs`(873行) `Quaternion.cs` `Point2.cs` `Point3.cs` | 手写数学库：列主序存储+行向量变换+SIMD 批量变换 |
| 颜色 | `Color.cs` | RGBA 打包 uint、Lerp/HSV/预乘 |
| 几何 | `BoundingBox.cs` `BoundingCircle.cs` `BoundingFrustum.cs` `BoundingRectangle.cs` `BoundingSphere.cs` `Box.cs` `Rectangle.cs` `Line2.cs` `Plane.cs` `Ray2.cs` `Ray3.cs` | 包围体/射线/平面/视锥全套求交 |
| 集合 | `DynamicArray.cs` `DynamicArrayExtensions.cs` `ReadOnlyList.cs` `ReadOnlyListExtensions.cs` | 可暴露底层数组的动态数组与只读包装 |
| 杂项 | `Random.cs` `Utilities.cs` | 双状态 xorshift 随机数；指针/结构体/dispose 小工具 |

分工边界：帧内顺序、入口链、ScreensManager 属 [01-程序入口与主循环](01-程序入口与主循环.md)；Graphics 设备/着色器属 06 页；Media/Animation/VR 属 19 页；本页只写 Engine\Engine 本体。

## 核心机制

### 窗口生命周期与多平台分派

`Window` 是静态类，三态机 `Uncreated/Inactive/Active`(`Window.cs:37-41`)。平台分派全靠 `#if` 编译期选择后端：桌面=GLFW(`m_gameWindow`，Silk.NET.Windowing.Glfw，`Window.cs:58`)，Android/iOS=SDL(`m_view`，`Window.cs:50`)，浏览器=Emscripten rAF(`Window.cs:712` `BrowserRenderFrameHandler`)。

启动链：`Run`(`Window.cs:420`)挂 `AppDomain.UnhandledException` 兜底(`:436-445`，未标记 `IsHandled` 则 `Environment.Exit(1)`) → `RunCore`(`:478`)按平台选 `GraphicsAPI`(桌面 GLES 3.2 / iOS GLES 3.0 / Android 查 `GetGlEsVersion`) → 建 view → `m_view.Run()` 阻塞(`:547`) → 每帧回调 `RenderFrameHandler`(`:718`，帧内顺序见 01 页)。Windows 专属：原生 GLES 创建失败时 ANGLE 回退——`catch GlfwException` 且 `CanFallbackToAngle`(`:593-597`，仅限 GL 尚为 null 的创建期) → `DisposeFailedView`(`:602`)清静态态 → 整个 `RunCore` 重来(`:462-476`)。

初始化/销毁：`LoadHandler`(`:633`)→`InitializeAll`(`:855`，图标+输入上下文+`Dispatcher.Initialize`+`Display/Keyboard/Mouse/Touch/GamePad/Mixer.Initialize`)→`Created` 事件→`ResizeHandler`→`Activated`。失焦 `FocusedChangedHandler`(`:645`)切 Inactive 并清键盘/鼠标/触摸。关闭链：`Close()`/`Restart()`(`:622-631`)置 `m_closing` → 帧尾跳过 SwapBuffers → `ClosedHandler`(`:662`，`m_closingRequested` 守卫只跑一次，`:737-739`)→ `Closed` 事件→反订阅→`DisposeAll`(`:892`)→ Android `FinishAndRemoveTask` / 浏览器 `Reload`(重启)或 `Close` / 桌面 `m_view.Close()` 后 `ToRestart` 事件。

对外事件族(`:389-411`)：`Created/Resized/Activated/Deactivated/Closed/ToRestart/Frame/UnhandledException/HandleUri/LowMemory/FileDropped/DisplayCutoutInsetsChanged`；拖放文件 `FileDropHandler`(`:687`)把路径开成 Stream 列表后广播。`PresentationInterval`(`:315`)=VSync 0~4，ANGLE 走 `Egl.SwapInterval`；`Handle`(`:362`)按平台给原生窗口句柄(Win32 Hwnd/X11/Wayland/Android)。

### 存储路径解析(虚拟方案)

所有 IO 走 `Storage`，路径带方案前缀，`ProcessPath` 负责映射(`Storage.cs:533` 桌面/浏览器；`:445` Android；`:481` iOS)：

| 前缀 | 桌面 | Android | iOS |
|---|---|---|---|
| `app:` | exe 所在目录(`GetAppDirectory`，`:509`；`failIfApp=true` 抛"Access denied") | APK assets(只读，`OpenFile` 走 `Assets.Open`，`:142-145`) | = data: |
| `data:` | `%LOCALAPPDATA%\<入口程序集名>`(`GetDataDirectory`，`:515-531`，写访问时加锁懒建目录) | `Environment.SpecialFolder.MyDocuments` | MyDocuments |
| `system:` | 原样绝对路径(`:552-555`) | 无此方案(未知前缀抛异常，`:477`) | 无 |
| `android:` | 无 | 外置存储根(`:467-472`) | 无 |
| `config:` | 无 | `EngineActivity.ConfigPath`(`:473-476`) | 无 |
| 无前缀 | 原样返回(相对 CWD，`:556-561`) | 抛异常 | 抛异常 |

其上是全套文件 API：`OpenFile`(`:134`，`OpenFileMode.Read/ReadWrite/Create/CreateOrOpen` → `FileMode` 映射，恒 `FileShare.Read`)、`MoveFileSafely`(`:204`，备份-替换-回滚：目标先挪成 `目标+随机UInt` 后缀，move 失败把备份挪回去重抛)、`Append`(`:250`)、`ReadAllText/Bytes`、`ListFileNames/ListDirectoryNames`(`:302-315`)、`FreeSpace`(`:63`，Android StatFs/iOS NSFileManager/桌面 DriveInfo)。文件名清洗两套：`SanitizeFileName`(`:590`，逐字符替换非法字符)与 `SanitizeFileNameSegment`(`:613`，段级：非法字符→`_`、剥尾点空格、Windows 保留名加前缀、截 200 字符并防孤立代理项)。手写 `GetExtension`(`:345`)会把点文件整体当扩展名，BCL 语义用 `GetExtensionBCL`/`GetFileNameWithoutExtensionBCL`(`:379-398`)。系统文件对话框 `ChooseFile`(`:709`，桌面走 NativeFileDialogCore，浏览器走 OPFS FilePicker)、`ShareFile`(`:683`)、`OpenFileWithExternalApplication`(`:661`)。浏览器端额外把 OPFS 挂在 `/__root__`(`:854` `MountOPFS`)并自动建 symlink(`:820` `EnsurePathLinked`)。

### 线程模型与延迟执行

- **主线**：`Dispatcher.Initialize`(`Dispatcher.cs:66`)在 `LoadHandler` 里记主线程号；`Dispatch(action)`(`:38`)三条路——在主线程就地执行；跨线程默认入 `m_actionInfos` 队列(lock 保护)；`waitUntilCompleted=true` 再挂 `ManualResetEventSlim` 阻塞等待。队列由 `Dispatcher.BeforeFrame`(`:70`)→`ExecuteActionsOnCurrentThread`(`:17`)在每帧开头排空；**action 抛异常只记日志不外抛**(`:27-29`)，等待方照样被 `Event.Set()` 放行。
- **帧内延时**：`Time.QueueTimeDelayedExecution/QueueFrameIndexDelayedExecution`(`Time.cs:69-75`)入同一列表，`Time.BeforeFrame`(`:91-102`)边扫边执行(到期回调里再排的会在当帧继续被扫到)。`SingleEvent`(`:56`)/`PeriodicEvent`(`:63`)是"跨过某刻/每 N 秒"判定件；`FrameDurationLimit` 限帧在 `AfterFrame` 里 `Task.Delay().Wait()` 同步睡(`:109-118`)。
- **日志锁**：`Log.Write` 全程 `lock(m_lock)`(`Log.cs:16-30`)，任何线程可写；sink 自身抛异常被吞。
- **随机数**：`Engine.Random`(`Random.cs`)双状态 xorshift 变体(`UInt`，`:42-49`)，静态计数器播种保证同进程多实例序列不同(`:5,27-29`)；`NormalFloat`(`:61`)逆 CDF 近似，`Vector2()/Vector3()`(`:75-115`)均匀方向(Marsaglia 极坐标/球面法)。

### 日志系统

`LogType` 序：Debug(0)<Verbose(1)<Information(2)<Warning(3)<Error(4)(`LogType.cs`)。静态 `Log` 持 sink 列表，静态构造即挂 `ConsoleLogSink` 且 `MinimumLogType=Information`(`Log.cs:9-14`)。`Write` 按门槛过滤后逐 sink 调用、异常吞掉(`:16-30`)。`ConsoleLogSink`(`ConsoleLogSink.cs:18-53`)输出 `HH:mm:ss.fff LEVEL: msg`，Error 走 `Console.Error`，构造时把控制台编码设 UTF8。`StreamLogSink`(`StreamLogSink.cs`)写流、每行 Flush、构造时 `Position=Length` 即追加。`DebugLogSink` 是**空壳**(全 return)。`Log.Error(string)` 非 mobile 会把消息追加到窗口标题 `Window.TitleSuffix`(`Log.cs:86-89`)；`Error(Exception)` 对 NRE 额外打出 `TargetSite`(`:100-108`)。`Window.DisposeAll` 调 `Log.Dispose` 释放 IDisposable sink(`Window.cs:899`)。

### 数学库约定(坑多发区)

- **Matrix 列主序存储+行向量语义**：字段声明顺序 `M11,M21,M31,M41,M12,…`(`Matrix.cs:20-35`)即每列 4 float 连续(列主序)，但变换 API 是行向量 `v * M`(`Vector3.Transform`，`Vector3.cs:169-173`)，平移在 M41-M43，`Forward = -M31..M33`(`Matrix.cs:76-83`)。SIMD 转置在 `TransformRows`(NEON Zip / SSE Shuffle，`Vector3.cs:230-255`)。
- **SIMD 外门**：批量 Transform 必须用 `AdvSimd.IsSupported || Sse.IsSupported` 做外门——MonoVM(Android 默认)上 `AdvSimd.IsSupported` 恒 false 而 `Vector128.IsHardwareAccelerated` 恒 true，用后者会在 ARM 落进 SSE 分支抛 `PlatformNotSupportedException`(源码注释：2026-10-10 BestiaryScreen 崩溃实证，`Vector3.cs:225-228`)。
- **零向量 Normalize 返回 UnitX 不是 Zero**(`Vector2.cs:103-106`，Vector3/4 同)；`Vector4.LengthSquared` 只算 XYZ(`Vector4.cs:75`)。
- **Color** 是 RGBA 打包 uint，R 在最低字节(`Color.cs:79-97`)；`Lerp` 饱和版/`LerpNotSaturated` 不饱和版成对出现(`:166-178`)；HSV 互转 `:208-277`。
- **包围体两套**：整数版 `Box/Rectangle`(半开区间 `Contains`，`Box.cs:66`、`Rectangle.cs:50`)给方块格用；浮点版 `BoundingBox/BoundingRectangle`(闭区间，`BoundingBox.cs:67`)给物理/渲染用。`BoundingFrustum` 由 viewProjection 矩阵提取 6 平面(`BoundingFrustum.cs:25-58`)，`Intersection(BoundingBox)` 用正负顶点法(`:123-137`)。
- `MathUtils` 除三角/插值外还有整数哈希 `Hash(uint)`(splitmix 风格，`MathUtils.cs:65-72`)、`IsPowerOf2/NextPowerOf2`(`:45-61`)、`NormalizeAngle`(`:226`)、`Sigmoid`(`:237`)、`LinearStep`(`:363`)。

## 坑与对策

- **点文件扩展名**：`Storage.GetExtension(".gitignore")` 返回 `".gitignore"`(整体当扩展名) → 配对改用 `GetExtensionBCL/GetFileNameWithoutExtensionBCL`(`Storage.cs:379-398`)。
- **并发写同一文件**：`Storage.OpenFile` 恒 `FileShare.Read`(`Storage.cs:156`) → 写句柄打开期间任何第二次打开(含读)抛 IOException；长驻写句柄要自管生命周期。
- **Android 路径前缀必须带**：Android `ProcessPath` 遇未知前缀(含无前缀相对路径)抛异常，桌面则原样返回 → 跨平台路径永远显式 `app:/data:` 开头。
- **`Log.Error(string)` 污染窗口标题**：非 mobile 平台每次 Error 都把消息接到 `Window.TitleSuffix`(`Log.cs:86-89`) → 高频报错用 `Write(LogType.Error,…)` 或 `Error(Exception)`。
- **Dispatch 异常不可见**：`Dispatcher.Dispatch` 的 action 抛异常只记日志，`waitUntilCompleted` 等待方无法感知失败 → 需要结果的自己 try/catch 包住并回传状态。
- **零向量归一化变 UnitX**：`Vector2/3/4.Normalize(Zero)` 返回 `UnitX`(`Vector2.cs:105`) → 先判长度或用 `LengthSquared>0` 守卫。
- **`Vector4.LengthSquared` 不含 W**(`Vector4.cs:75`) → 当 3D 用没事，当 4D 求长度会错。
- **半开 vs 闭区间**：`Box/Rectangle.Contains` 是 `[Left, Left+Width)`，`BoundingBox.Contains` 是闭区间 → 边界判断别混用两套。
- **Matrix 布局**：想直接写内存/传给 GL 记住列主序，但手算用行向量 `v*M`；两种心智模型叠加时先看 `Matrix.cs:20-35` 字段序。
- **`Window` 属性门禁**：窗口未开(`m_view==null`)时读写 `Size/Position/Title/…` 抛 `InvalidOperationException`(`Window.cs:813-819`) → 静态初始化阶段别碰 Window 属性，改用 `Window.IsCreated` 先判。

## 原版范例

| 我要做… | 照抄哪里 |
|---|---|
| 写/读用户数据文件(跨平台) | `E:\SurvivalcraftAPIProject\Engine\Engine\Storage.cs:324-341` `WriteAllText/ReadAllBytes`——统一 `data:` 前缀即可，平台差异全被 ProcessPath 吸收 |
| 安全替换关键文件(防写一半坏档) | `E:\SurvivalcraftAPIProject\Engine\Engine\Storage.cs:204-245` `MoveFileSafely`——备份-替换-回滚三段式的标准答案 |
| 玩家输入转文件名/目录名 | `E:\SurvivalcraftAPIProject\Engine\Engine\Storage.cs:613-637` `SanitizeFileNameSegment`——保留名/超长/代理项全处理了 |
| 自定义日志落盘(带级别前缀+每行刷盘) | `E:\SurvivalcraftAPIProject\Engine\Engine\StreamLogSink.cs:7-28`——实现 ILogSink 30 行完事，挂上 `Log.AddLogSink` |
| 跨线程把结果交回主线程 | `E:\SurvivalcraftAPIProject\Engine\Engine\Dispatcher.cs:38-64` `Dispatch`——后台线程算完 `Dispatch(()=>…)`，帧头自动执行 |
| 射线选方块/拾取 | `E:\SurvivalcraftAPIProject\Engine\Engine\Ray3.cs:20-90` `Intersection(BoundingBox)`——slab 法带盒内提前返回 0，原版相机拾取同源 |
| 视锥剔除 | `E:\SurvivalcraftAPIProject\Engine\Engine\BoundingFrustum.cs:25-58,123-137`——矩阵→6 平面→正负顶点判定；消费端见 `E:\SurvivalcraftAPIProject\Survivalcraft\Game\TerrainRenderer.cs` |
| 均匀随机方向/正态分布 | `E:\SurvivalcraftAPIProject\Engine\Engine\Random.cs:61-115` `NormalFloat/Vector2()/Vector3()`——粒子与生物游走都靠这套 |
| SIMD 批量变换顶点数组 | `E:\SurvivalcraftAPIProject\Engine\Engine\Vector3.cs:257-280` `Transform(数组版)`——NEON/SSE 双分支+标量回退的外门写法范本 |
| 平滑插值/缓动 | `E:\SurvivalcraftAPIProject\Engine\Engine\MathUtils.cs:213-218` `Lerp/SmoothStep`——UI 动画与相机过渡的标准件 |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查一帧内谁先谁后/入口链 | [01-程序入口与主循环](01-程序入口与主循环.md)(本页只管 Window 本体) |
| 改窗口模式/VSync/标题/句柄 | `E:\SurvivalcraftAPIProject\Engine\Engine\Window.cs:126,315,237-313,362` |
| 监听窗口创建/关闭/失焦/拖放 | `E:\SurvivalcraftAPIProject\Engine\Engine\Window.cs:389-411` 事件族 + `:645` 失焦清输入 |
| 弄清 `data:` 到底落在哪 | `E:\SurvivalcraftAPIProject\Engine\Engine\Storage.cs:515-531`(桌面)、`:445-478`(Android)、本页路径表 |
| 选文件/分享文件/系统打开 | `E:\SurvivalcraftAPIProject\Engine\Engine\Storage.cs:709,683,661` |
| 每帧延时执行/跨帧排队 | `E:\SurvivalcraftAPIProject\Engine\Engine\Time.cs:69-75` + `:91-102` 执行点 |
| 后台线程回主线 | `E:\SurvivalcraftAPIProject\Engine\Engine\Dispatcher.cs:38` |
| 加日志 sink / 改日志级别 | `E:\SurvivalcraftAPIProject\Engine\Engine\Log.cs:110,7`；级别序见 `LogType.cs` |
| 看帧率统计 | `E:\SurvivalcraftAPIProject\Engine\Engine\Time.cs:83-90`(`AverageFrameDuration` 每秒刷新) |
| 高性能列表(暴露底层数组) | `E:\SurvivalcraftAPIProject\Engine\Engine\DynamicArray.cs:87`(`Array` 属性)+`:410` DynamicArray 快速合并 |
| 射线/包围盒求交 | 本页"数学库约定"+ `Ray3.cs`/`BoundingBox.cs`/`BoundingFrustum.cs` |
| 角度归一化/哈希/2 的幂 | `E:\SurvivalcraftAPIProject\Engine\Engine\MathUtils.cs:226,65,45` |
| 未捕获异常兜底 | `E:\SurvivalcraftAPIProject\Engine\Engine\Window.cs:436-445`(AppDomain)+`UnhandledException` 事件 |

另见：[01-程序入口与主循环](01-程序入口与主循环.md)(帧顺序)、[06-渲染管线与着色器](06-渲染管线与着色器.md)(Display/GLWrapper)、[11-存档持久化](11-存档持久化.md)(存档内容层)。
