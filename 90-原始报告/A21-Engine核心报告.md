# A21 原始报告：Engine 核心运行时域全量深读

> 任务：`E:\SurvivalcraftAPIProject\Engine\Engine\` 全部 ~41 个 .cs 逐个全读；产出 10-SC引擎/21-Engine核心运行时.md + 21a-Engine核心明细.md。
> 日期：2026-10-31。SC 源码项目只读。分工边界：帧顺序/入口链/ScreensManager 归 01 页；Engine.Graphics 归 06 页；Media/Animation/VR 归 19 页。

## 一、覆盖统计

| 家族 | 文件 | 读法 |
|---|---|---|
| 窗口 | Window.cs(932)、WindowMode.cs、UnhandledExceptionInfo.cs | 全文 |
| 时间/线程 | Time.cs(120)、Dispatcher.cs(75) | 全文 |
| 存储 | Storage.cs(860)、OpenFileMode.cs、RunPath.cs(32) | 全文 |
| 日志 | Log.cs(140)、ILogSink、LogType、ConsoleLogSink(56)、StreamLogSink(33)、DebugLogSink(19)、DebugTextWriter(25) | 全文 |
| 向量矩阵 | MathUtils(364)、Vector2(298)、Vector3(391)、Vector4(313)、Matrix(873)、Quaternion(328)、Point2(100)、Point3(110) | 全文 |
| 颜色/几何 | Color(341)、BoundingBox(156)、BoundingCircle、BoundingFrustum(155)、BoundingRectangle(97)、BoundingSphere、Box(91)、Rectangle(79)、Line2(60)、Plane(41)、Ray2(98)、Ray3(127) | 全文 |
| 集合/杂项 | DynamicArray(415)、DynamicArrayExtensions、ReadOnlyList(74)、ReadOnlyListExtensions、Random(118)、Utilities(52) | 全文 |

- 合计 41 文件、约 7,073 行，**41/41 全文实读，无抽样**。
- 任务书提到的 "GameWindow"：引擎里唯一对应是桌面后端字段 `Window.m_gameWindow`(Silk.NET `IWindow`，Window.cs:58)，没有独立 GameWindow 类。
- 任务书提到的 "Platform 抽象与多平台分派"：**无 Platform 类**，分派全靠 `#if ANDROID/IOS/BROWSER/WINDOWS/LINUX` 编译期选择 + 少量运行期探测(`OperatingSystem.IsLinux()` 等)；"ThreadPool" 同样不存在于本域(引擎用裸 `Thread`/`Task`)。

## 二、最重要机制发现（带 file:line）

1. **窗口是静态门面+三态机+编译期多后端**：`Window` 三态 `Uncreated/Inactive/Active`(Window.cs:37-41)。桌面走 GLFW(`m_gameWindow`，:58)，Android/iOS 走 SDL(`m_view`，:50)，浏览器走 Emscripten rAF(:711-716)。启动链 `Run`(:420)→挂 AppDomain 未捕获异常兜底(:436-445，未标 `IsHandled` 即 `Environment.Exit(1)`)→`RunCore`(:478)按平台选 GraphicsAPI→`m_view.Run()` 阻塞(:547)→每帧 `RenderFrameHandler`(:718)。Windows ANGLE 回退：仅"GL 尚未初始化"的创建期 `GlfwException(VersionUnavailable|ApiUnavailable)` 才重建窗口重试一次(:462-476, :593-615)。
2. **关闭/重启是"帧尾关闸"而非立即**：`Close()/Restart()`(:622-631)只置 `m_closing`(+`m_restarting`)；当帧 `RenderFrameHandler` 跳过 SwapBuffers 后，`m_closingRequested` 守卫保证 `ClosedHandler` 只执行一次(:737-761)→`Closed` 事件→反订阅→`DisposeAll`(:892-900)→桌面 `m_view.Close()` 后触发 `ToRestart` 事件(由 Survivalcraft 侧重启进程完成"重启生效")；Android `FinishAndRemoveTask`、浏览器 `BrowserInterop.Reload/Close`。
3. **虚拟路径五方案，平台映射不对称**：`ProcessPath` 桌面版(Storage.cs:533-567)认 `app:`(exe 目录，`failIfApp` 防越权)/`data:`(`%LOCALAPPDATA%\<入口程序集名>`，写访问加锁懒建 :515-531)/`system:`(绝对路径)/无前缀原样返回；Android 版(:445-478)认 `app:`(APK assets 只读)/`data:`(MyDocuments)/`android:`(外置存储)/`config:`(EngineActivity.ConfigPath)，**未知前缀抛异常**；iOS 版(:481-504) `app:`=`data:`=MyDocuments。桌面数据目录=LocalApplicationData+入口程序集名。
4. **存储层安全写与清洗**：`MoveFileSafely`(Storage.cs:204-245)=备份-替换-回滚(目标先挪成 `+随机UInt` 后缀，失败挪回并重抛)；`OpenFile` 恒 `FileShare.Read`(:156)；文件名清洗两套：`SanitizeFileName`(逐字符 :590)与 `SanitizeFileNameSegment`(段级 :613-637：非法字符→`_`、剥尾点空格、CON/PRN/COM1-9 等保留名加前缀(:598-651)、截 200 字符防孤立代理项)；`GetExtension` 手写版把点文件整体当扩展名，`GetExtensionBCL/GetFileNameWithoutExtensionBCL`(:379-398)修正 BCL 语义。
5. **线程模型=帧头排空的单队列**：`Dispatcher.Initialize` 记主线程号(Dispatcher.cs:66，由 Window.LoadHandler 调 :876)；`Dispatch`(:38-64)三路：主线程就地执行/跨线程入 lock 保护队列/`waitUntilCompleted` 加 ManualResetEventSlim 阻塞等；`Dispatcher.BeforeFrame`(:70)每帧头排空(:17-36)，**action 异常只记日志不外抛**，等待方照样放行。Time 侧另有按时间/按帧号的延时队列(Time.cs:69-75)，在 `Time.BeforeFrame` 边扫边执行(:91-102，回调里再排队当帧仍会被扫到)。
6. **日志=锁保护多 sink，Error 会写窗口标题**：`Log` 静态构造挂 ConsoleLogSink、门槛 Information(Log.cs:9-14)；`Write` 锁内逐 sink、sink 异常吞掉(:16-30)；`Log.Error(string)` 非 mobile 把消息接到 `Window.TitleSuffix`(:86-89，标题栏可见)，`Error(Exception)` 不写标题但对 NRE 打 `TargetSite`(:100-108)；`StreamLogSink` 构造 `Position=Length` 即追加+每行 Flush(StreamLogSink.cs:9,26)；`DebugLogSink` 是空壳；`Window.DisposeAll` 负责释放 IDisposable sink(Window.cs:899)。
7. **数学库三约定**：(a) Matrix 字段序 M11,M21,M31,M41,M12…=**列主序存储**(Matrix.cs:20-35)，但 API 是**行向量 v*M** 语义(平移 M41-M43，Vector3.cs:169-173)，`Forward=-M31..M33`(Matrix.cs:76-83)；SIMD 乘法 `MultiplyRestricted`(Matrix.cs:780-794)。(b) 批量 Transform 的 SIMD 外门必须 `AdvSimd.IsSupported||Sse.IsSupported`——MonoVM(Android)上 `AdvSimd.IsSupported` 恒 false 而 `Vector128.IsHardwareAccelerated` 恒 true，用后者在 ARM 落 SSE 分支抛 PlatformNotSupportedException(源码注释 2026-10-10 BestiaryScreen 崩溃实证，Vector3.cs:225-228，Vector2/Vector4 同款注释)。(c) `Normalize(零向量)` 返回 UnitX 非 Zero(Vector2.cs:103-106 等)；`Vector4.LengthSquared` 只算 XYZ(Vector4.cs:75)。
8. **几何两套坐标口径**：整数 `Box/Rectangle` 半开区间 `Contains`(`[Left,Left+Width)`，Box.cs:66、Rectangle.cs:50)给方块格；浮点 `BoundingBox/BoundingRectangle` 闭区间(:67/:60)给物理渲染。`BoundingFrustum` 是唯一 class：viewProjection→6 归一化平面(BoundingFrustum.cs:25-58)、Corners 懒算(:60-79)、盒求交用正负顶点法(:123-137)。射线求交：Ray3×AABB slab 法盒内返 0(Ray3.cs:20-90)、Ray3×平面(:107-110)。
9. **随机数自研 xorshift 变体**：双状态 s0/s1，`UInt` 旋转混合(Random.cs:42-49)；静态计数器播种(`Stopwatch.GetTimestamp()+DateTime.Now.Ticks`，:5)保证同进程多实例序列不同；`State` 属性(:11-17)可存档复现；`NormalFloat` 逆 CDF 有理近似(:61-73)；均匀方向 Vector2=极坐标拒绝采样(:75-92)、Vector3=球面法(:98-111)。
10. **DynamicArray 的价值=暴露底层数组**：`Array` 属性直接给 `T[]`(DynamicArray.cs:87)，`AddRangeTyped(DynamicArray)` 直接 `Array.Copy`(:410-414)；扩容 ×2 最小 4(:368-372)，`EnsureCapacityExact` 供预知大小的 AddRange 免多次翻倍(:374-378)；虚 `Allocate/Free`(:345-347) 可派生池化子类。`ReadOnlyList<T>` 是 struct 包装(写全抛 :34-69)，配 `Empty` 单例(:28)。

## 三、坑清单（一行一坑）

- `Storage.GetExtension(".gitignore")` 返回 `".gitignore"`（手写实现把点文件整体当扩展名），BCL 语义必须用 `GetExtensionBCL`（Storage.cs:345-354 vs 379-385）。
- `Storage.OpenFile` 恒 `FileShare.Read`（Storage.cs:156）：写句柄开着时第二次打开(含读)抛 IOException。
- Android `ProcessPath` 未知/无前缀路径抛异常，桌面原样返回相对 CWD（Storage.cs:477 vs 556-561）：跨平台路径必须显式带方案前缀。
- `Log.Error(string)` 非 mobile 追加窗口标题 TitleSuffix（Log.cs:86-89），高频报错别用这个重载；`Error(Exception)` 不写标题。
- `DebugLogSink` 全 return 空壳（DebugLogSink.cs:5-16），挂它=没日志。
- `ConsoleLogSink` 的 Verbose 前缀是 "INFO: "，与 Information 无法从输出区分（ConsoleLogSink.cs:27-34）。
- `Dispatcher.Dispatch` 执行的 action 抛异常只记日志（Dispatcher.cs:27-29），`waitUntilCompleted` 方感知不到失败。
- `Dispatcher.MainThreadId` 未初始化抛 InvalidOperationException（Dispatcher.cs:15）；`Dispatch` 同（:39-41）——窗口 Run 之前别用。
- `Vector2/3/4.Normalize(零向量)` 返回 UnitX 不是 Zero（Vector2.cs:105 等）。
- `Vector4.LengthSquared` 不含 W（Vector4.cs:75）。
- SIMD 批量 Transform 外门只能用 `AdvSimd.IsSupported||Sse.IsSupported`，`Vector128.IsHardwareAccelerated` 在 MonoVM-ARM 上误判（Vector3.cs:225-228 注释，BestiaryScreen 崩溃实证）。
- Matrix 列主序存储+行向量语义双重视角（Matrix.cs:20-35）；`Forward` 是取负的第三行（:76-83），直接复制三行当朝向会反向。
- `Box/Rectangle.Contains` 半开区间 vs `BoundingBox.Contains` 闭区间（Box.cs:66 vs BoundingBox.cs:67），边界判断别混。
- `BoundingFrustum.Corners` 懒算缓存且 `Matrix` setter 才失效（BoundingFrustum.cs:56,60-79）：改了视锥矩阵必须走 setter，直接改字段不存在（字段私有，安全）。
- `Window` 大部分属性在窗口未开时抛 InvalidOperationException（VerifyWindowOpened，Window.cs:813-819）；静态初始化阶段用 `IsCreated` 先判。
- `Window.Close()` 不是同步关：当帧 SwapBuffers 被跳过、下一帧才走 ClosedHandler（m_closingRequested 守卫，Window.cs:725-761）。
- `Time.FrameDurationLimit` 限帧是 `Task.Delay().Wait()` 同步睡（Time.cs:117-118），睡在游戏线程上。
- `Time.Ticks` 是相对进程内首次取用的差值，不是绝对时间戳（Time.cs:28-34，m_startTicks 懒记）。
- `Random.Seed(int)` 确定性复现；无参构造靠静态计数器（Random.cs:5,27-29），同一 tick 内 new 多个实例序列也不同。
- `Color` PackedValue 布局 R 在最低字节（RGBA 小端，Color.cs:79-97），手写十六进制字面量容易写反。
- `Color.Lerp` 会饱和到 0-255，`LerpNotSaturated` 不饱和可溢出（Color.cs:166-178），性能敏感路径用后者。
- `Storage.CombinePaths` 统一输出 '/' 分隔且空段跳过（Storage.cs:416-438），与 `Path.Combine` 行为不同。
- `Utilities.ArrayToStructure` pin 住托管数组拷贝（Utilities.cs:13-21），大数组高频调用有 GC 压力。

## 四、原版范例速记（页面已收录 10 条，此处补全文上下文）

- `Storage.MoveFileSafely`（Storage.cs:204-245）：唯一带备份回滚的移动，JsonFileStore 写档即抄它（Survivalcraft\Game\Community\Infrastructure\Persistence\JsonFileStore.cs:47）。
- `Storage.SanitizeFileNameSegment`：CommunityUploadFileNaming.cs:9、ModpackRegistry.cs:571、FontManager.cs:962 都是直接调用——原版自己"玩家输入→文件名"全走它。
- `BoundingFrustum`：消费端 Survivalcraft\Game\Camera.cs、TerrainRenderer.cs、Engine.Graphics\FlatBatch3D.cs——视锥剔除照抄这条链。
- `Vector3.Transform(数组版)` SIMD 外门：是全仓唯一带"崩溃实证"注释的数学代码，学 SIMD 写法必看。
- `Engine.Random.Vector3()/NormalFloat()`：粒子/生物随机方向的出处。
- `Dispatcher.Dispatch`：唯一跨线程通道，01 页"跨线程回主线"路由指到这里。

## 五、与既有页边界确认

- 01-程序入口与主循环 已覆盖：Program.Main→Window.Run 帧链、RenderFrameHandler 顺序、Time.BeforeFrame/AfterFrame 帧内位置、Dispatcher.BeforeFrame 位置。21 页只补 Window 本体(状态机/平台后端/关闭链/ANGLE)与全家族。
- 06 页已覆盖 Engine.Graphics(Display/GLWrapper/Shader…)；19 页已覆盖 Media/Animation/VR；21 页目录地图均只留"分工边界"一行，未复制内容。
- 11-存档持久化 属存档内容层(Utilities/WorldInfo/Project)；21 页 Storage 只写路径与文件原语层，未越界。
