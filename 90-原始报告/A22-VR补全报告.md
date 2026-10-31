# A22 原始报告 · OpenXrVrBackend.cs 1690 行补深读（VR 域收尾）

> 日期: 2026-10-31 · 范围: E:\SurvivalcraftAPIProject\Engine\VR\OpenXrVrBackend.cs 分段全文 1690/1690 + Engine\VR 其余 6 文件复核 + Engine.Windows\VR、Engine.Android\VR 平台子类 + Survivalcraft 侧 VR 渲染消费点 8 处核实 · 产出页: 10-SC引擎\19-媒体动画与VR.md（VR 节扩"OpenXR 后端全链"）、19a-媒体动画明细.md（OpenXrVrBackend 行改实读）

## 0. 统计

| 域 | 文件 | 行数 | 状态 |
|---|---|---|---|
| Engine\VR | OpenXrVrBackend.cs | 1690 | A22 分段全文深读（此前 A19/A10 标"未深读"） |
| Engine\VR | IVrBackend.cs 51 / EyeFrame.cs 8 / VrEye.cs 5 / VrController.cs 5 / VrControllerButton.cs 17 / VrControllerType.cs 10 | 96 | 复核（A19 已读） |
| Engine.Windows\VR | WindowsOpenXrVrBackend.cs | 28 | 新读 |
| Engine.Android\VR | AndroidOpenXrVrBackend.cs | 50 | 新读 |
| Survivalcraft 消费点 | Program/LoadingScreen/SettingsGraphicsScreen/ViewWidget/VrManager/BasePerspectiveCamera/FppCamera/ComponentVrHandsModel/GameWidget | 定区段 | 8 处行号逐条核实 |

全文件 `#if WINDOWS || ANDROID`（OpenXrVrBackend.cs:1、1691），其余平台整个 VR 域不编译。

## 1. 全链结构（实例→会话→动作→交换链→提交→销毁）

### 1.1 装配与平台拆分

- Program.Initialize：`VrManager.SetBackend(new WindowsOpenXrVrBackend()/AndroidOpenXrVrBackend())` + `VrManager.Initialize()`（Program.cs:266-270）。
- 抽象基类只留 3 平台钩子：`GraphicsBindingType` / `GetGraphicsBindingSize()` / `PopulateGraphicsBinding(void*)`（OpenXrVrBackend.cs:89-91）。
- Windows 子类：wglGetCurrentDC/wglGetCurrentContext 填 GraphicsBindingOpenGLWin32KHR，DC/GLRC 为零即 throw（WindowsOpenXrVrBackend.cs:11-20）。
- Android 子类：EGL display/context + eglQuerySurface(EGL_CONFIG_ID)→eglChooseConfig 反查 config 填 GraphicsBindingOpenGLESAndroidKHR（AndroidOpenXrVrBackend.cs:11-29）。
- 主循环接线：`Program.Run` 开头 `bool vrFrame = VrManager.IsVrStarted && VrManager.BeginFrame()`（Program.cs:282），finally 里 `VrManager.EndFrame(); VrManager.Update();`（:359-362）。

### 1.2 实例链 DoInitialize（:184-349，全程软降级）

1. Android **必须先** xrInitializeLoaderKHR（JniRuntime VM 指针 + Window.Activity，:187-210）——注释原话：不先初始化 loader 无法与 runtime broker 通信、看不到任何扩展。
2. 检查 XR_KHR_opengl_enable（Windows）/XR_KHR_opengl_es_enable（Android），缺则 return 放弃（:212-222）；可选扩展 XR_EXT_local_floor、Android 加 XR_KHR_android_create_instance + XR_BD_controller_interaction（PICO 手柄）（:224-231）。
3. xrCreateInstance：ApplicationInfo "Survivalcraft"、ApiVersion 1.0.0；扩展名 HGlobalAnsi + stackalloc 指针数组，finally FreeHGlobal（:233-281）。
4. xrGetSystem(FormFactor.HeadMountedDisplay)（:283-294）。
5. GetOpenGLgraphicsRequirements / GetOpenGLESgraphicsRequirements（:296-329）。
6. EnumerateViewConfigurationView(PrimaryStereo) 取 RecommendedImageRectWidth/Height 存 m_swapchainWidth/Height（:331-345）→ `IsAvailable=true`（:348）。
- 任何一步失败：Log.Information/Error + return（IsAvailable 保持 false），**不抛异常**——调用方无需 try。
- **双轨初始化**：Windows 下 Initialize 把 DoInitialize 丢 `Task.Run`（xrCreateInstance 在"注册了 runtime 但无 HMD"时同步拉起 runtime broker 卡数秒，:150-172，注释详述；幂等 m_initStarted）；Android 同步（:174-181）。StartVr 先 `m_initTask.Wait()` 收口（:356-359）；m_instance.Handle==0 时补一次 DoInitialize（:364-366）。
- StartVr（:351-379）：!IsAvailable/已启动直接 return；DoStartVr 后重置 ControllerType=Unknown、m_controllerDetectAttempts=0、IsStarted=true；异常 catch 里 DestroyGraphicsResources+DestroySessionResources+IsStarted=false（:373-378）。

### 1.3 会话链 DoStartVr（:381-426）

1. CreateSessionWithGraphicsBinding（:428-445）：binding 内存 stackalloc+MemClear+手写 StructureType，xrCreateSession 失败 throw（唯一在 StartVr 链上抛的点，被 :373 catch）。
2. Android SetAndroidApplicationThread(RendererMainKhr)（非关键，失败仅 Warning，:387-397）。
3. CreatePlaySpace（见 1.4）。
4. 重置 recenter 状态四字段（:402-406）。
5. SelectSwapchainFormat（:447-474）→ 双眼 CreateSwapchain（:410-412）→ m_views/m_layerViews 数组 → CreateActions（:423）→ m_sessionState=Idle（:425）。

### 1.4 参考空间三级回退 CreatePlaySpace（:1517-1553）

- 顺序 LOCAL_FLOOR（OpenXR 1.1；注释：规格说 recenter 不移 Y，但 Quest/SteamVR 违规）→ Stage → Local（眼级，最后手段）；全失败 throw。
- 每次 EventDataReferenceSpaceChangePending 事件都 DestroySpace+重建（PollEvents :1471-1480 内联调 CreatePlaySpace）。

### 1.5 会话状态机

- PollEvents（:1463-1482）循环 xrPollEvent；只处理两类：EventDataSessionStateChanged → HandleSessionStateChange；EventDataReferenceSpaceChangePending → 重建 playspace + recenter 快照（见 1.6）。
- HandleSessionStateChange（:1484-1498）：Ready→BeginSession（xrBeginSession PrimaryStereo，成功隐式记 Synchronized，:1500-1511）；Stopping→EndSession（xrEndSession，:1513-1515）；LossPending/Exiting→IsStarted=false。
- BeginFrame 状态门（:1032-1041）：LossPending/Exiting → IsStarted=false+return false；非 Focused/Synchronized/Visible（即 Idle/Ready）→ 只泵事件 return false（不调 xrWaitFrame/BeginFrame）。

### 1.6 Recenter Y 补偿（事件快照+次帧差分）

- 事件侧：ReferenceSpaceChangePending 且 `!m_recenterPending && m_trackingEstablished` → `m_hmdYBeforeRecenterRaw = 当前 rawY − 已累积 offset`；m_recenterPending=true（:1471-1480）。m_trackingEstablished 在首个有效 HMD 姿态置位（UpdateHmdState :1234-1237），防启动期 ReferenceSpaceChangePending 假事件。
- 应用侧：下一帧 UpdateHmdState，`delta = 快照 − 当前 rawY`，|delta|>0.01m 才累积进 m_recenterYOffset（:1239-1251）。
- 补偿贯穿四路：
  - HmdMatrix.Translation += offset（UpdateHmdState :1253-1257，重算 Inverted）。
  - GetEyeFrame：viewMatrix *= CreateTranslation(0,−offset,0)（:1110-1114）；CameraPosition.Y += offset（:1116-1120）。
  - UpdateControllers：控制器矩阵 Translation += offset（:1292-1296）。
  - EndFrame：提交 pose.Position.Y += offset（:1139-1149，注释：保 compositor 重投影一致）。

### 1.7 交换链

- SelectSwapchainFormat（:447-474）：枚举 runtime 支持格式 → 优先 [Srgb8Alpha8, Rgba8] → 都没有取第一个。注释：游戏输出 sRGB 编码值且 FRAMEBUFFER_SRGB 关闭；声明 sRGB 告诉 compositor 数据已伽马校正；线性 Rgba8 会让 Meta runtime 二次伽马→发灰。
- CreateSwapchain（:491-552）：每眼一条（ColorAttachmentBit|SampledBit、SampleCount=1、ArraySize=1、FaceCount=1、MipCount=1），枚举 SwapchainImageOpenGL(KHR) 图像句柄存 m_swapchainImages[eye][]。
- CreateFBO（:554-575）：每眼一条 FBO = DepthComponent24 renderbuffer + 初始挂 image[0]，CheckFramebufferStatus 不过 throw。
- **GetEyeFrame 每次重挂**：Acquire+WaitSwapchainImage（timeout 1e9 ns）后 `gl.FramebufferTexture2D(COLOR_ATTACHMENT0, m_swapchainImages[eye][m_acquiredImageIndex])`（:1100-1104）——FBO 句柄恒定、颜色附件每帧变。

### 1.8 动作系统

- CreateActions（:577-650）：单 actionSet "gameplay"（priority 0）；每手 13 动作：trigger(float)/grip(float)/grip_click(bool)/menu(bool)/stick_x+stick_y(float 拆分，注释：GetActionStateVector2f 不存在 :602)/pose/stick_click/primary（左 X=右 A）/secondary（左 Y=右 B）/thumbrest(touch)/trackpad_x+trackpad_y。
- SuggestBindings（:688-945）= 9 个 SuggestProfileBindings 调用：
  | profile | 要点 |
  |---|---|
  | /oculus/touch_controller | 全动作表（squeeze=value） |
  | /microsoft/motion_controller | squeeze 是 **click**；trackpad 路径 |
  | /htc/vive_controller | squeeze click；trackpad 兼 stick 与 trackpad |
  | /valve/index_controller | squeeze=value；stickClick 绑 **trackpad/force**；A/B |
  | /meta/touch_controller_pro | 同 Quest 路径 |
  | /meta/touch_controller_plus | 同 Quest 路径（Quest 3） |
  | /bytedance/pico_neo3_controller | squeeze value+click 双绑；无 thumbrest |
  | /bytedance/pico4_controller | **Menu 只左手**（注释：右手 system/click 不可靠） |
  | /htc/vive_focus3_controller | 同 Quest 路径 |
- SuggestProfileBindings（:947-983）：任一 StringToPath 失败 → valid=false 弃**整 profile**（一票否决 :951-964）；结果 Success→Information、**ErrorPathUnsupported→Verbose**（runtime 不支持该 profile 属正常）、其他→Warning。
- AttachSessionActionSets（:623-631）；pose 动作各建 ActionSpace（identity pose，:637-649）。
- DetectControllerType（:985-1023）：GetCurrentInteractionProfile(左)→PathToString→映射 9 profile→5 枚举（:1005-1016；vive_focus3 归 MetaQuestTouch，pico 两个 profile 归 PICO）。**必须首次 SyncActions 后调用**（xrGetCurrentInteractionProfile 之前返回 XR_NULL_PATH，注释 :633-635）；BeginFrame 里 ControllerType==Unknown 且尝试 <30 帧逐帧重试，30 次放弃（:1074-1080；Log 文案写"10 frames"是历史遗留，实际 30）。

### 1.9 帧循环

- BeginFrame（:1027-1086）：PollEvents → 状态门（1.5）→ xrWaitFrame（阻塞式节拍 :1043-1046）→ xrBeginFrame（:1048-1049）→ `ShouldRender==0 仍返回 true`（:1051-1053，EndFrame 会走空层）→ xrLocateView(PrimaryStereo, m_playSpace, PredictedDisplayTime) 取双 View（:1055-1065）→ UpdateHmdState → SyncActions（xrSyncActiveActionSets :1262-1273）→ 探测 → UpdateControllers。
- GetEyeFrame（:1088-1128）：Acquire+Wait → 重挂 FBO → viewMatrix=Invert(PoseToMatrix(pose))+recenter 平移 → projMatrix=CreateProjectionMatrix(Fov,0.1,2048) → 返回 EyeFrame{Fbo, ViewMatrix, ProjectionMatrix, CameraPosition}。
- ReleaseEye（:1130-1133）= xrReleaseSwapchainImage。
- EndFrame（:1135-1185）：ShouldRender 才组 CompositionLayerProjection（space=m_playSpace、每 view SubImage 全幅、BlendMode.Opaque、LayerCount=1）；`fixed` 块盖住 xrEndFrame 防 GC 移托管数组（:1168-1180）；else EndFrameEmpty（:1187-1197 LayerCount=0，注释：防 compositor 显示陈旧帧）。
- UpdateHmdState（:1201-1258）：HMD 位置=双眼中点、朝向=左眼四元数→旋转矩阵×平移；m_hmdLast* 保存上帧；HeadMove=(M41,M43) 平移差；recenter 补偿（1.6）。
- UpdateControllers（:1275-1338）：连接=LocateSpace 成功且 PositionValid+OrientationValid 位（:1284-1286）；矩阵=PoseToMatrix+recenter（:1292-1297）；Grip=float≥0.5 **或** gripClick bool（:1303-1306）；stick=X/Y 两 float 拼（:1316-1319）；trackpad 另一组 float（:1333-1336）。
- IsButtonDown 映射（:1385-1404）：Trigger≥0.5；Grip/Menu/Primary/Secondary/Thumbrest 直 bool；**Trackpad→StickClick**；TrackpadCenter=StickClick 且 |stick.X|<0.3 且 |stick.Y|<0.3；TrackpadLeft/Right/Up/Down=**真 trackpad** 轴 ±0.5。
- IsButtonDownOnce（:1406-1425）：与 m_lastControllers 差分；Trackpad 四方向 Once 回程阈值 0.4（>0.5 触发 / ≤0.4 复位，滞回防抖）。
- 死区：ApplyDeadZone 重映射式（sign×max(|v|−dz,0)/max(1−dz,0.001)，:140-148），非简单截断。

### 1.10 眼变换与投影

- GetEyeToHeadTransform（:1429-1447）：**只返回 IPD 平移**——双眼相对中点偏移经 m_hmdMatrixInverted.OrientationMatrix 变换到头部局部；注释：旋转已在相机 CreateLookAt 经 HmdMatrix 应用，再含会双旋转（roll 反转）。
- GetProjectionMatrix（:1449-1452）→ CreateProjectionMatrix（:1570-1592）：四 tan（AngleLeft/Right/Up/Down）非对称视锥；GL 约定 clipZ∈[−1,1]；m23 行 = −2fn/(f−n)；矩阵第 4 列 −1（行主序存储）。
- CreateViewMatrix/PoseToMatrix（:1557-1568）：四元数→旋转矩阵×平移，视图=逆。

### 1.11 遗留接口与销毁

- WalkingVelocity 恒 Vector2.Zero（:1596，OpenXR 不跟踪）；Update() 空实现（:1456-1459，注释：Once 差分已在 UpdateControllers 做）；VrRenderTarget 恒 null（:127）——VrManager 侧三者中后两者标 Obsolete（VrManager.cs:43-44、107-111）。
- StopVr（:1600-1616）：DestroyGraphicsResources（swapchain/FBO/depth RB :1618-1634）→ DestroySessionResources（spaces→12×2 动作→actionSet→playspace→session :1646-1682）→ DestroyInstance → m_glExt/m_xr Dispose；**IsAvailable 保持 true**（注释：让 StartVr 可重启）。
- Dispose（:1636-1644）：先 m_initTask.Wait() 防后台 init 在飞时拆毁；GC.SuppressFinalize。
- VrManager.Shutdown 挂 Window.Closed（VrManager.cs:62-65），先 Program.DisableVrCameras 再 _backend.Dispose()。

## 2. Survivalcraft 侧消费点核实（8 处，行号当日实测）

1. **Program.cs:266-270** 装配后端+Initialize；**:282** vrFrame 判定；**:359-362** finally EndFrame+Update。
2. **LoadingScreen.cs:186-204**：Android 头显强制 `SettingsManager.UseVr=true`（:186-189）；UseVr 时 StartVr，失败回写 UseVr=false；注释警告**别用 IsVrAvailable 门控**（Windows 异步解析中恒 false 会误跳过，:191-194）。
3. **SettingsGraphicsScreen.cs:43-51**：用户开关——先 StopVr 再 StartVr；`SettingsManager.UseVr = VrManager.StartVr()`；:61 VR 眼高偏移面板随 IsVrAvailable 显隐。
4. **ViewWidget.cs:122-128** DrawToScreen 判 `VrManager.IsFrameActive && Input.Devices 含 VrControllers && ActiveCamera is BasePerspectiveCamera` → DrawToScreenVr；**:149-187** DrawToScreenVr=RenderToEyes 闭包逐眼（PrepareForDrawing(vrEye)→m_subsystemDrawing.Draw→GameWidget.DrawVrGui(eyeFrame)→急转弯黑幕 VrFadeAlpha）+ Windows 左眼 BlitVrEyeToDesktop 回桌面（:171-175，:190 起）。
5. **VrManager.cs:264-311** RenderToEyes：保存 origFbo/BackbufferSizeOverride/Viewport/Scissor/RenderTarget → 逐眼 GetEyeFrame→改绑 eyeFrame.Fbo+BackbufferSizeOverride(swapchain 尺寸)+关 FRAMEBUFFER_SRGB+GLWrapper.Clear（注释：手动 GL.Clear 会漏 ColorMask/DepthMask 复位）→ renderAction → finally 全恢复+双眼 ReleaseEye。**:219-227** BeginFrame 首次 ControllerType 已知时 EnsureVrMappingDefaults；**:233-244** EndFrame m_eyesRendered 才真提交否则 EndFrameEmpty；**:74-86** Windows StartVr 禁 VSync（PresentationInterval=0，帧节奏交 xrWaitFrame），StopVr 恢复（:99-104）。
6. **BasePerspectiveCamera.cs:42-56** ViewMatrix：Eye!=null 时 `LookAt × Invert(GetEyeToHeadTransform)`；**:137-155** ViewportSize=SwapchainWidth/Height；**:157-177** ViewportMatrix=Identity；**:231** 投影=VrManager.GetProjectionMatrix(Eye,0.1,2048)（CalculateBaseProjectionMatrix VR 分支）。
7. **FppCamera.cs:25-36**：VR 分支=身体位置 + (HMD Y+VrEyeHeightOffset 钳 0.2..boxY×蹲姿系数) + 身体 yaw 与 HMD yaw 差 CreateRotationY 校正。
8. **ComponentVrHandsModel.cs:59-61** 右柄不在位不画；**:104-106** 手模型世界矩阵=`VrManager.HmdMatrixInverted × CreateWorld(camera.ViewPosition/Direction/Up) × camera.ViewMatrix`（另 :53-58 门：存活+本实体第一人称+IsControlledByVr）。
9. **GameWidget.cs:388-407** DrawVrGui：GUI 渲染目标投 3D quad（VrGuiQuadMatrix 面向 HMD）进眼缓冲，用 eyeFrame.ViewMatrix×ProjectionMatrix flush。

## 3. 新坑（回写 19 页 9 条中本次新增 8 条）

1. xrCreateInstance 无 HMD 卡数秒（Windows 同步 broker 拉起）→ 已后台 Task 化；Initialize~StartVr 窗口 IsVrAvailable=false 是"未出结果"非"无 VR"（LoadingScreen.cs:191-194 明示）。
2. BeginFrame 返回 true ≠ 有画面：ShouldRender==0 仍 true、EndFrame 自动空层（:1051-1053、1182-1184）；跳过 EndFrame 破坏 xrWaitFrame 节拍（begin/end 必须成对）。
3. 眼 FBO 颜色附件每帧重挂（:1100-1104）：别缓存附件假设；眼内渲染须在 GetEyeFrame 后、ReleaseEye 前。
4. ControllerType 首帧后 30 帧内 Unknown（探测依赖首次 SyncActions :633-635/:1074-1080）；VR 映射默认值落盘跟着等（VrManager.cs:222-225）。日志文案"after 10 frames"与实际 30 帧不符。
5. Android 必须先 xrInitializeLoaderKHR（:187-210），否则扩展全不可见。
6. 绑定建议一票否决+静默：任一路径 StringToPath 失败弃整 profile（:951-964）；ErrorPathUnsupported 仅 Verbose（:979）。
7. recenter 补偿 1cm 死区+tracking 门（:1235-1237、1476-1479、1246）：换物理高度 recenter 会被拉回旧眼高（设计行为）。
8. VrRenderTarget 恒 null（:127）/WalkingVelocity 恒零（:1596）/StopVr 保留 IsAvailable（:1615）。

## 4. 回写记录

- 19-媒体动画与VR.md：状态行同步 A22；"VR 补充"段扩为"### 5. OpenXR 后端全链"（装配/实例链/会话链/状态机/参考空间/recenter/交换链/动作/帧循环/HMD 控制器状态/眼变换/销毁/渲染消费链 13 小点，全带 file:line）；坑 +8 条；原版范例 +4 行；快查路由 +6 条；目录地图 VR 行更新+平台子类行。页 169 行（限 350）。
- 19a-媒体动画明细.md：OpenXrVrBackend 行改实读结论+关键方法行号；VR 节改"VR（7）+ 平台子类（2）"加两行子类；状态行+A22 报告指针。
- 禁改文件未动：README.md、45-SC原版范例菜谱.md、00-页面模板与规则.md、10-输入与相机.md（其状态行仍留"OpenXrVrBackend.cs 1690 行未深读"，属该页自己的标注，本次未获授权修改）、SC与完美世界完全学习笔记\ 全部。SC 源码项目只读未动。
