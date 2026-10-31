# Engine 核心明细

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(41/41，一行一文件) · 上级页: [21-Engine核心运行时](../21-Engine核心运行时.md)

`E:\SurvivalcraftAPIProject\Engine\Engine\` 全部 41 个文件逐行实读后的明细。行号以当日源码为准。

| 文件 | 行数 | 一行明细 |
|---|---|---|
| Window.cs | 932 | 静态窗口门面：三态机(:37)、平台后端分派(GLFW/SDL/Emscripten)、Run/RunCore(:420/:478)、ANGLE 回退(:593-615)、事件族(:389-411)、RenderFrameHandler(:718)、关闭/重启链(:622-761) |
| WindowMode.cs | 7 | 枚举 Resizable/Fixed/Borderless/Fullscreen |
| UnhandledExceptionInfo.cs | 8 | `Exception`+`IsHandled` 载体，供 Window.UnhandledException 事件标记"已处理免退出" |
| Time.cs | 120 | 墙钟：FrameIndex/FrameDuration(:26-46)、Ticks 基于 Stopwatch 首取为零点(:28-34)、SingleEvent/PeriodicEvent(:56-67)、延时队列(:69,:91-102)、AfterFrame 限帧 Task.Delay().Wait()(:105-119) |
| Dispatcher.cs | 75 | 主线程号(:66)、Dispatch 三路(:38)：就地/入队/waitUntilCompleted+ManualResetEventSlim；BeforeFrame 排空队列，action 异常吞掉记日志(:17-36) |
| Storage.cs | 860 | 虚拟路径 ProcessPath(app:/data:/system:/android:/config:，桌面:533/Android:445/iOS:481)、全套文件 API、MoveFileSafely(:204)、文件名清洗两套(:590,:613)、ChooseFile/ShareFile(:709/:683)、浏览器 OPFS(:854) |
| OpenFileMode.cs | 7 | 枚举 Read/ReadWrite/Create/CreateOrOpen |
| RunPath.cs | 32 | 运行路径小工具：BaseDirectory/程序集 Location/AppContext.BaseDirectory/PATH 环境变量；`AndroidFilePath="android:Survivalcraft2.4_API1.9"`(:7) |
| Log.cs | 140 | 静态多 sink 日志：锁保护 Write(:16)、静态构造挂 ConsoleLogSink 且门槛 Information(:9-14)、Error(string) 写窗口标题(:86-89)、Error(Exception) 特判 NRE TargetSite(:100-108) |
| ILogSink.cs | 4 | 接口：`Log(LogType, string)` |
| LogType.cs | 8 | 枚举 Debug=0<Verbose=1<Information=2<Warning=3<Error=4 |
| ConsoleLogSink.cs | 56 | 控制台输出 `HH:mm:ss.fff LEVEL: msg`(:18-53)；Error→Console.Error；构造设 UTF8 编码；Verbose 前缀也是 "INFO: "(:27-30) |
| StreamLogSink.cs | 33 | 流 sink：构造 Position=Length 即追加(:9)、每行 Write+Flush(:22-27) |
| DebugLogSink.cs | 19 | 空壳实现：所有级别直接 return(:5-16) |
| DebugTextWriter.cs | 25 | TextWriter→System.Diagnostics.Debug 转发，null 安全 |
| MathUtils.cs | 364 | float/double/int/long 四套 Min/Max/Clamp/Saturate/Lerp/SmoothStep/CatmullRom；IsPowerOf2/NextPowerOf2(:45-61)、整数 Hash splitmix 风格(:65-72)、NormalizeAngle(:226)、Sigmoid(:237)、LinearStep(:363) |
| Vector2.cs | 298 | 2D 向量：CreateFromAngle(:53)、Rotate(:68)、Angle(:113)、Transform 行向量(:125)、数组版 SIMD Transform(:181，外门 AdvSimd/Sse :162-179)、FixNaN、与 System.Numerics 互转(Unsafe.As :291-297) |
| Vector3.cs | 391 | 3D 向量：XY/XZ…swizzle(:24-70)、Cross(:119)、Transform(:169)、数组版 SIMD(:257，TransformRows NEON Zip/SSE Shuffle :230-255，MonoVM 外门坑注释 :223-228)、Color 构造(:96) |
| Vector4.cs | 313 | 4D 向量：LengthSquared 只算 XYZ(:75)、Floor/Ceiling/Round 用 Vector128(:77-90)、Transform SIMD(:182)、swizzle 家族(:303-312) |
| Matrix.cs | 873 | 4x4 列主序存储(:20-35)+行向量语义：Forward=-M31..(:76)、Scale/Decompose(:94,:229)、CreateLookAt/Orthographic/PerspectiveFOV(:308,:332,:381)、CreateWorld(:644)、CreateShadow(:657)、Invert(:702)、SIMD 乘法 MultiplyRestricted(:780)、与 Matrix4x4 互转(:856) |
| Quaternion.cs | 328 | 四元数：CreateFromRotationMatrix 分支法(:54)、CreateFromYawPitchRoll(:94)、Lerp(:131)/Slerp(:154)、ToMatrix(:186)、GetRight/Up/ForwardVector(:216-220)、ToYawPitchRoll(:222) |
| Color.cs | 341 | RGBA 打包 uint(R 最低字节 :79-97)、30+ 预设色、Lerp/LerpNotSaturated(:166,:173)、PremultiplyAlpha(:180)、RgbToHsv/HsvToRgb(:208,:231)、全套运算符重载(:283-340)、隐式转 FontStashSharp FSColor(:156) |
| Point2.cs | 100 | 整型 2D：Dot/Cross/Perpendicular(:35-39)、Round/Ceiling/Floor(Vector2→Point2 :89-99) |
| Point3.cs | 110 | 整型 3D(方块坐标)：同 Point2 + Cross(:49) |
| BoundingBox.cs | 156 | 浮点 AABB(闭区间 Contains :67)：与球求交(:76)、静态 Intersection/Union(:107-123)、点到盒距离(:125)、Transform 8 角点(:132) |
| BoundingSphere.cs | 23 | 球心+半径纯数据体，求交在 Ray3/BoundingBox 侧 |
| BoundingCircle.cs | 25 | 2D 圆：Contains(:20) |
| BoundingFrustum.cs | 155 | class(非 struct)：viewProjection→6 平面归一化(Matrix setter :25-58)、Corners 懒算 8 角(:60-79)、点/球/盒求交(:97-137)、ComputeIntersectionLine(:148) |
| BoundingRectangle.cs | 97 | 2D 浮点 AABB：与圆求交(夹紧法 :64-68)、Intersection/Union/Distance |
| Box.cs | 91 | 整型 3D 区间(Left/Top/Near+Size)：半开 Contains(:66)、Intersection/Union(:68-86)——方块格专用 |
| Rectangle.cs | 79 | 整型 2D 区间：半开 Contains(:50)、Intersection(:52) |
| Line2.cs | 60 | 2D 直线(Normal+D)：两点构造(:12)、SignedDistance(:37)、直线交点(:48) |
| Plane.cs | 41 | 3D 平面(Normal+D)：三点构造(:14)、Normalize(:29) |
| Ray2.cs | 98 | 2D 射线：与矩形 slab 求交(:20)、与圆求交(:65)、Sample(:83)、Transform(:85) |
| Ray3.cs | 127 | 3D 射线：与 AABB slab 求交(盒内返 0 :20-90)、与球(:92)、与平面(:107)、Sample/Transform |
| DynamicArray.cs | 415 | IList<T> 动态数组：暴露底层数组(:87)、×2 扩容 min4(:368)、AddRange 类型化快速路径(:386-414，DynamicArray 直接 Array.Copy)、RemoveAll/RemoveRange、虚 Allocate/Free(:345-347) 可派生池化 |
| DynamicArrayExtensions.cs | 12 | `ToDynamicArray()` LINQ 扩展 5 个重载 |
| ReadOnlyList.cs | 74 | struct 只读包装 IList<T>，写操作全抛 NotSupportedException，Empty 单例(:28) |
| ReadOnlyListExtensions.cs | 6 | `ToReadOnlyList()` 扩展 |
| Random.cs | 118 | 双状态 xorshift 变体 UInt(:42-49)、静态计数器播种(:5,27-34)、Int(bound)/Float/Bool(probability)、NormalFloat 逆 CDF 近似(:61)、均匀方向 Vector2/Vector3(:75-115)、State 可存取复现(:11) |
| Utilities.cs | 52 | Swap/SizeOf/PtrToStructure/ArrayToStructure/StructureToArray、Dispose(ref)/DisposeCollection(:35-51) |

统计：合计 ~7073 行；最大 Window.cs 932、Matrix.cs 873、Storage.cs 860；最小 ILogSink.cs 4。
