# Mod 排错手册 2（按症状查 · 后半）

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 汇编自 01-引擎 23 个主线页"坑与对策"+明细页坑列，按症状重组去重（共 250 条，本文件 5-10 类 123 条）· 前半: [Mod排错手册.md](Mod排错手册.md)（加载/不生效/崩溃/存档）

## 怎么用

同手册 1：先按现象定大类 → 查表比对"症状"列 → 按对策处理；详址含 file:line 的直接开源码核对。详址约定：`N页` = `E:\数据\生存战争系列\SC完全学习笔记\01-引擎\N-主题.md`；源码行号省略根前缀 `E:\SurvivalcraftAPIProject\`。

## 五、渲染贴图类（不显示 / 颜色错 / 顺序错 / 闪烁）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 半透明贴图边缘白边/整体偏亮 | AlphaBlend 是 One/InverseSourceAlpha 预乘语义，纹理 RGB 没乘 A | 加载时 `Texture2D.Load(s, true)` 或改用 NonPremultiplied 批次 | 06页 · BlendState.cs:17-41 |
| 自绘 UI 颜色发灰/过亮 | UI 管线默认 AlphaBlend 预乘，自绘顶点色 RGB 未乘 A | 照 BevelledRectangleWidget.PremultiplyAlpha 在控件内预乘 | 06页/09页 |
| 同 Layer 的批次绘制顺序抖动 | Flush 排序用 List.Sort 只按 Layer 排，不稳定 | 需要 Z 序的内容拆不同 Layer，或用深度缓冲 | 06页 · BasePrimitivesRenderer.cs:123-131 |
| 自定义顶点着色器画面上下颠倒/深度异常 | 漏 OPENGL_POSITION_FIX/u_glymul 宏段 | 顶点源码保留 `#ifdef GLSL` 段并应用该宏（引擎注入定义） | 06页坑表 |
| 覆盖原版着色器后全游戏区块都变了 | Assets/Shaders/Opaque.vsh 同名覆盖全局生效 | 只覆写自己新增的名字（如 Fx01_Xxx.vsh） | 06页坑表 |
| mod 资产意外顶掉原版/其他 mod 的同名文件 | ContentManager.Add 是 AddOrUpdate，后载 mod 赢 | 包内 Assets/ 路径别与原版同名；故意做补丁先确认加载序 | 20页坑表 |
| 画的东西出现在水面之前/之后不对 | drawOrder 语义：1 AlphaThreshold 模型/99 水前透明/201 水后透明/100 地形透明 | 对照 drawOrder 全景表选 DrawOrders | 06页/02页 |
| 渲染到 RenderTarget 的三角形消失被剔除（后备缓冲正常） | FrontFace 在 RT 与后备缓冲语义相反 | 自定义绕向按目标缓冲验证；用 CullNone 最稳 | 06页 · GLWrapper.cs:719,724 |
| 原始 GL BlitFramebuffer 后画面错乱 | 绕过 GLWrapper 状态脏检查缓存 | 照 RenderTarget2D.BlitFromBackbuffer 置 `GLWrapper.m_framebuffer = -1` 再绑回 | 06页 · RenderTarget2D.cs:98-100 |
| 换了纹理的采样器设置不生效 | 采样器参数按纹理句柄缓存（m_textureSamplerStates） | 同一句柄换采样器要换纹理实例或清缓存 | 06页 · GLWrapper.cs:928-963 |
| 方块光照异常（鬼影亮格/光不更新） | 直接 SetCellValueFast 绕过 ChangeCell 不触发重算；ChangeCell 写格会清零 light 再重算 | 走 ChangeCell；想保留光值自己 ReplaceLight 回写 | 14页 · SubsystemTerrain.cs:374-375 |
| 发光方块照常投影（想要无影） | 发光≠无影，默认照常算阴影 | GetShadowStrength 返回负值（原版用 -99） | 14页 · ChristmasTreeBlock.cs:213 |
| 方块碎屑采到邻格贴图 | 纹理槽 16→32 换算公式隐含在基类 | 自带纹理的构造重载自己算 slot | 07页 · BlockDebrisParticleSystem.cs:59 |
| 自己排 quad 却看不见 | 批次 Layer/混合态与默认不同，或没走 AlphaTested shader 灌雾 uniform | 照抄 SubsystemParticles.cs:133-152 的统一刷新路径 | 07页坑表 |
| 自定义四足/鸟/鱼模型完全静止 | AnimateCreature 是空实现，无动画控制器 | 必须配 AnimationConfigPath/AnimationController；仅 HumanModel 有后备 | 03页/03a · ComponentFourLeggedModel.cs:188 |
| UI 持有纹理导致内存持续上涨 | widget 树无 Dispose 级联，异步纹理句柄累积 | 释放放 UpdateCeases；照 RichContentImageLoader 代际守卫 | 09页坑表 |
| 位图字体里某些像素被吃掉 | 洋红 (255,0,255) 是切格/透明键 | 美术导出避开纯洋红 | 19页 · BitmapFont.cs:528-547 |
| glTF 长动画后半段细节丢失 | 装载时均匀重采样 30fps、上限 300 帧，CubicSpline 被拍平 | 长动画拆分或接受线性精度 | 19页 · GltfAnimationConverter.cs:627-631 |
| VR 画面发灰 | swapchain 落到 Rgba8，Meta runtime 二次伽马 | 保持 sRGB 优先的选择顺序 | 19页 · OpenXrVrBackend.cs:463-473 |
| VR 眼内渲染内容丢失/错帧 | 眼 FBO 颜色附件每帧变；眼内渲染必须在 GetEyeFrame 之后、ReleaseEye 之前 | 别缓存"该 FBO 挂某纹理"的假设 | 19页 · OpenXrVrBackend.cs:1100-1104 |
| HUD 叠层组件（ScreenOverlays）效果被清/被顶 | Reset=-100 每帧最先清零，其他组件 Max() 叠入；另一处 Clothing 贴图开关是 static 全局互踩 | 自存旧值会被清，改成每帧重算；static 开关按玩家互斥设计 | 03页/03a · ComponentScreenOverlays.cs:57-71、ComponentClothing.cs:76-83 |

## 六、音频类（没声音 / 声音不对 / 声音风暴）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 放了音频文件没声音（总排查链） | 按序：路由带扩展名/大小写不符 → 不在 Assets/ 下 → AudioManager 吞异常 → 格式不认 → volume≤0.05 听阈闸 → SoundsVolume=0 | 按序排查；自包 try/catch Get 打日志；选 flac/ogg 最稳 | 08页坑表 |
| mp3 加载抛 Unsupported sound file format | "mp3"分支只认带 ID3v2 标签的（Mp3.IsFlacStream 实为读 ID3v2） | 给文件带 ID3v2 头或换 flac/ogg | 08页/19页 · Mp3.cs:83-90 |
| FLAC 文件解码失败 | 带 ID3v2 的 FLAC 落进 mp3 分支（fLaC 嗅探只看首 4 字节）[推测] | 转存去掉 ID3v2 | 19页坑表 |
| wav 读不了 | 仅 PCM(1)/16bit/1-2 声道/8k-48kHz；StreamingSource 的 Position setter 按固定头长 seek 会错位 | 转码；避免对 Wav StreamingSource 赋 Position | 19页 · Wav.cs:229-236/:34 |
| pitch 传 1 想升调结果升了八度 | ToEnginePitch=2^pitch | 半音级微调用 2^(semitone/12) | 08页 · AudioManager.cs:28 |
| volume 传 >1 无效 | BaseSound.Volume Saturate 夹到 1 | 想传远加大 minDistance | 08页 · BaseSound.cs:32-52 |
| minDistance=0 全静音 | 衰减公式分子就是 minDistance | 生物/方块参数给非零值 | 08页 · SubsystemAudio.cs:135-137 |
| 睡觉/时间加速时音效全没 | 闸门 1：GameTimeFactor≠1 时队列音效全丢 | 设计行为，非 bug | 08页 · SubsystemAudio.cs:156 |
| 一群同类生物只叫几声 | UpdateCongestion 按资源路径限流 >6 拒播（同目录随机音共享键） | 换目录/分目录摊键 | 08页 · SubsystemAudio.cs:182-201 |
| 整个游戏无声，日志仅 `Could not create audio device` | OpenAL32.dll 缺失或设备打不开，m_isInitialized=false 后全部播放调用被跳过 | 发行包带 openal32.dll | 08页 · Mixer.cs:50-54 |
| 世界内音效绕过了限流/进屏静音 | 直接调 AudioManager（UI 直通入口） | 世界内一律 SubsystemAudio.PlaySound；只有菜单/Widget 用 AudioManager | 08页坑表 |
| PlayRandomSound 没声音也没异常 | 目录空只 Log.Warning 不抛 | 目录拼错查日志而非断点 | 08页 · SubsystemAudio.cs:114-116 |
| 长音播多了 source 泄漏 | new Sound 忘 disposeOnStop，m_soundsToStopPoll 恒持有 | 短音走 AudioManager；长音用 CreateSound 且自己 Dispose | 08页坑表 |
| 游戏内没背景音乐 | 原版 Mix.InGame 每帧只调 hook "PlayInGameMusic"，不实现就静音 | 实现 hook；hook 每帧都进，自己节流/判状态 | 08页 · MusicManager.cs:107-115 |
| 换曲时爆音 | 直接 Stop 再 Play 无淡出 | 照 m_fadeSound 交叉淡化 | 08页 · MusicManager.cs:87-98 |
| 雷声延迟与高度不符 | 只算水平 XZ 距离 | 设计行为 | 08页 · SubsystemSky.cs:209 |
| 流式音频内存翻倍 | 四种 StreamingSource 构造都把整份文件拷进 MemoryStream | 长音乐勿走 StreamingSource，短音效用 Load | 19页坑表 |

## 七、输入与 UI 类（点不动 / 不响应 / 界面错乱 / 相机与 VR）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 键位注册了但不生效/改键界面没有 | 没重写 GetKeyboardMappings()；或两个 Loader 返回同名键抛异常丢后半 | 映射名加模组前缀 | 10页坑表 |
| IsKeyOrMouseDownOnce 永远 false | 映射值类型不是 Key/MouseButton 直接 return false；Key.Null（禁用）也 false | 核对注册值类型 | 10页坑表 |
| 死亡/睡觉/相机模式下输入被抹 | 闸门整体换成白名单结构体（只留 Camera* 与 5 个环境开关） | 自定义数据每帧重写 | 10页 · ComponentInput.cs:89-114 |
| 自建相机读 Move/Look 拿到零 | UsesMovementControls=true 时 Move/Look/Jump 被清零 | 像 OrbitCamera 一样读 PlayerInput.CameraLook/CameraMove/CameraCrouchMove | 10页 · ComponentInput.cs:107-114 |
| 手柄组合键误触/不触发 | 扳机既是动作又是修饰键；Once 只在松开帧且未参与组合键时触发 | 理解修饰键模型再设计键位 | 10页 · GamePad.cs:333-397 |
| 多手柄杆值串味 | GetPadStickPosition 把 4 槽求和再归一化 | 单手柄场景确认只开一个 GamePadN 位 | 10页 · WidgetInput.cs:497-507 |
| 触摸判定失灵（IsTouched 永真 / 点击连触两次） | Touch.IsTouched 是只置 true 永不复位的锁存标记；一次点击存活 2-3 帧（ReleaseQueued 机制） | 用 TouchLocations 或 IsControlledByTouch；按 touch Id 去重 | 10页 · Touch.cs:122/:87-104 |
| 注册的相机切不过去 | 没 ManageCameras 里 AddCamera / 值负数被禁用 / 注册名必须是类型全名 | 照三条件核对；重排后序号会压缩，别存注册值当持久索引 | 10页 · GameWidget.cs:43-93 |
| VR 矩阵全零 | 后端 null 时 VrManager 返回 default(Matrix) | 先判 VrManager.IsFrameActive | 10页 · VrManager.cs:46-48 |
| VR 模式不渲染/有残影 | EndFrame 只在 RenderToEyes 被调过才提交，否则提交空层 | 每帧必须走 RenderToEyes；BeginFrame/EndFrame 成对 | 10页/19页 · VrManager.cs:233-244 |
| VR 手柄没绑定且无报错 | 建议绑定一票否决（任一路径失败弃整 profile），ErrorPathUnsupported 只 Verbose | 开 Verbose 日志排查 | 19页 · OpenXrVrBackend.cs:951-979 |
| 启动期拿 IsVrAvailable 门控逻辑出错 | Windows 后台初始化未完成时 false 是"还没结果" | 别拿它门控启动 | 19页 · OpenXrVrBackend.cs:150-172 |
| VR ControllerType 前 30 帧是 Unknown | 探测需首次 SyncActions 之后 | 键位默认值要等 BeginFrame 里类型已知才落盘 | 19页 · OpenXrVrBackend.cs:1074-1080 |
| 同屏 SwitchScreen 无效 | 目标==CurrentScreen 直接 return | 屏内分级导航用内部栈（抄 ModSettingsScreen） | 17页 · ScreensManager.cs:59-61 |
| 切屏后同帧读新屏的初始化结果读不到 | Enter 要等切换动画过半（Factor≥0.5）才执行，同帧两屏都不在更新中 | 初始化放 Enter 内部完成；或走 OnScreenEntered/OnScreenLeaved 钩子 | 01页/17页 · ScreensManager.cs:305-317 |
| 屏实例状态跨 Enter 残留（页码/选中项串数据） | 屏实例全局复用 | 每次 Enter 显式重置状态 | 17页坑表 |
| 多屏共享的单例委托被顶掉 | 后注册者赢 | Enter/Leave 配对安装/释放，且"只在自己仍持有时清空" | 17页 · CommunityScreen.cs:77-79 |
| 返回键被"等待按键"状态吞掉 | 改键屏等待新键时 Input.Back 先被解释为取消改键 | 录入型屏分层处理返回键 | 17页坑表 |
| 嵌套对话框同帧连关两层 | 父框 Update 读 Input.Ok/Back 是全局共享的 | 子框存活期间跳过全局输入分支；存活判据=在 Dialogs 中且父链可达 RootWidget | 18页 · CommunityFiltersDialog.cs:64-72 |
| ShowDialog 后当帧找不到刚弹的框 | ShowDialog 经 Dispatcher.Dispatch 异步挂树 | 延后一帧或用回调；连续两个框叠放顺序也不保证 | 18页 · DialogsManager.cs:57-76 |
| HasDialogs 误判 | 切屏不清理 m_dialogs，死屏实例仍占位 | 用 HasDialogsOrAnimations + 自己校验父链 | 18页 · DialogsManager.cs:23-44 |
| BusyDialog 弹出后 Back 无效 | 其 Update 里 Input.Clear() 吞掉 | 想强制等待照抄；反之自己的框用 BusyDialog 当子框时注意 Back 被吞 | 18页 · BusyDialog.cs:34-38 |
| TextBoxDialog 取消时逻辑没走 | 取消也回调 handler 传 null | handler 内判 null | 18页 · TextBoxDialog.cs:72-77 |
| 父 ClickableWidget/InventorySlotWidget 点不动 | 子树里 IsHitTestVisible=true 的子件抢命中 | 排查子树命中；图元类默认 false、容器默认 true | 09页坑表 |
| 自绘部件不显示 | 没置 IsDrawRequired；或被 base.MeasureOverride 重置（InventorySlotWidget 系） | IsDrawRequired=true 写在 base.MeasureOverride() 之后 | 09页坑表 |
| ClickableWidget 子类交互失效 | 漏调 base.Update()（置 IsClicked/IsTapped） | 子类化必调 base.Update | 09a · ClickableWidget.cs:22-45 |
| XML 里写 abstract 控件抛异常 | `<ButtonWidget>`/`<ContainerWidget>`/`<ClickTextWidget>` 无无参构造 | 用 BevelledButtonWidget/BitmapButtonWidget/CanvasWidget 等具体类 | 09页坑表 |
| XML 枚举/布尔值写错整个界面建不出来 | 枚举大小写敏感、bool 认 True/False、Vector2 用逗号 | 值格式照规范；值错是抛异常非静默 | 09页坑表 |
| GridPanel 隐藏的孩子仍撑宽列 | MeasureOverride 不看 IsVisible | 想让隐藏件退出布局用 Remove 或换 Table/Flex | 09页 · GridPanelWidget.cs:73 |
| 生物/方块名显示为 `[DisplayName:N]` 原始令牌 | Lang 的 Database 节没有对应键 | 增实体模板必须同步补 Lang 键 | 22页坑表 |
| 浏览器端自定义手柄没输入 | 只收 `mapping==="standard"` 的手柄 | 自定义手柄在浏览器端不出输入是正常现象 | 23页 · main.js:174 |
| 浏览器端"意外"收到 Esc | 指针锁定丢失/浏览器后退会合成一对 Esc 键 | 依赖 Esc 的逻辑在浏览器要有防御 | 23页 · main.js:569-575 |
| 浏览器端鼠标键号/滚轮与预期不符 | JS 端中/右键映射互换；滚轮 JS 除以 100、C# 再取负 Y | 以引擎 MouseButton 为准；扩展滚轮逻辑先在两端打数值对照 | 23页 · main.js:404-413/:547-551 |

## 八、电力类（电路不动 / 电路炸 / 行为怪）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 一个元件 Simulate 抛异常，全图电路停摆无日志 | 异常 rethrow 冒泡到 SubsystemUpdate 被静默吞 | 自定义元件 Simulate 内部全 try/catch | 15页 · SubsystemElectricity.cs:415-423 |
| 新电力方块电路完全不建也不报错 | 方块编号不在 SubsystemElectricBlockBehavior.HandledBlocks（61 个硬编码 ID）且 csv 第 4 列没写行为 | csv Behaviors 列写 ElectricBlockBehavior，或自写 behavior 转发 OnElectricElementBlock* | 15页 · SubsystemElectricBlockBehavior.cs:8-70 |
| 排队了的电路模拟一直不执行 | 传的步数 ≤ 当前 CircuitStep 被静默丢弃 | 一律 `CircuitStep + n` | 15页 · SubsystemElectricity.cs:357-373 |
| 元件每 10ms 都跑，CPU 炸 | Simulate 无条件 return true 自续排队 | 只在值变化时 return true（原版惯例） | 15页坑表 |
| 对话框改了电压/数据，电路不刷新 | ChangeCell 只保证元件重建，不主动唤醒 | 补 `QueueElectricElementForSimulation(element, CircuitStep+1)` | 15页 · SubsystemBatteryBlockBehavior.cs:42-49 |
| 一改方块 data，元件 C# 字段全没了 | UpdateElectricElements 按点销毁重建且删本格持久电压 | 状态写 data 或自己的 BlockBehavior 子系统 | 15页 · SubsystemElectricity.cs:611-654 |
| 活塞推拉后途经电路重置 | OnBlockStartMoving/StopMoving 也塞 m_pointsToUpdate 销毁重建 | 途经点电路元件不跨推拉存活，设计如此 | 15页 · SubsystemElectricBlockBehavior.cs:88-94 |
| 与门/与非门输出恒 0 | 要求恰好 2 个输入连接；非门多连线只认第一条 | 检查连线数 | 15页 · AndGateElectricElement.cs:20 |
| 两根不同色线不通/两 Output 挨着不连 | 颜色掩码不交不连、Output↔Output 不连，设计如此 | 不是 bug | 15页 · SubsystemElectricity.cs:339-344 |
| 活塞给半档电压收不回/只伸 1 格 | 伸出长度是模拟量 `Max((int)(v*15.999)-7,0)`，v<0.5 时长度 0 | 给满档电压或按模拟量设计 | 15页 · PistonElectricElement.cs:27 |
| LED 接 4 档信号全程不亮 | OneLED/多彩 LED 电压 8..15 才选色，0..7 灭 | 信号抬到 8 以上 | 15页 · OneLedElectricElement.cs:52 |
| 铁活板门/接电门"按不动" | 接电后手动开合被禁（木活板门 83/栅栏门 166 豁免） | 设计如此；要可手开换豁免编号 | 15页 · SubsystemTrapdoorBlockBehavior.cs:46 |
| 改电路拓扑后延迟门延迟不对 | 档位缓存 50 步，0.5s 后自动重算 | 等待或主动重算 | 15页 · DelayGateElectricElement.cs:11-13 |
| Counter 的持久电压挪作他用出错 | 符号位被偷存溢出标志 | 别动 Counter 的 PV 语义 | 15页 · CounterElectricElement.cs:99 |
| Hygrometer 读数永远不变 | 它不自续轮询 | 要主动排它或改用其他传感器 | 15页 · HygrometerElectricElement.cs:9-15 |
| 持久电压存档部分丢失 | 上限 501 条（num>500 break），取舍顺序不定 | 别依赖大量持久电压 | 15页 · SubsystemElectricity.cs:483-485 |
| 几十个轮询传感器同时跑掉帧 | 全部同相位轮询 | 抄相位抖动（period×(0.9+0.0002×GetHashCode%1000)） | 15页 · MotionDetectorElectricElement.cs:54 |
| 按 MC 思路找传送带/矿车/铁轨 | 源码 grep 零命中，原版没有这些机构 | 别在引擎层浪费检索时间 | 15页负事实 |

## 九、世界与地形类（地形怪 / 光照怪 / 刷怪怪）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 生成步骤里跨区块读邻居拿到未生成数据 | 内容四趟不等邻居 | 只用 chunk.Get/SetCellValueFast；跨区结构学原版"3×3 邻域各自画自己那片+种子只由坐标派生" | 05页坑表 |
| 改 SeaLevelOffset 后矿相对深度变了 | OceanLevel=64+offset 而矿 y 区间硬编码 | 改海平面时同步考虑矿表 | 05页坑表 |
| 矿刷画不上染色/带 data 的格子 | PaintFastSelective 按"整值相等"比较宿主（data/light 必须为 0） | 想兼容染色/元数据格自己写 Painter | 05页 · TerrainBrush.cs:214-236 |
| 同一世界种子在 2.3 与 2.4 生成器下矿物形状不同 | 笔刷种子 21/22/23=Random(17)，24=Random(24) | 别用 2.3 存档验 2.4 矿表 | 05页坑表 |
| 温湿度写入后读回超界/串位 | Shafts 只存温湿各 4 位（`温度<<4|湿度` 挤一字节） | 温湿永远 0-15 | 05a · TerrainSerializer23.cs:656-659 |
| 自写区块压缩读回抛 "Corrupt chunk data" | RLE 游程>271 会拆段，解压必须精确填满 16×256×16 | 自写压缩按 271 拆段 | 05a · TerrainSerializer23.cs:678-681 |
| 超大世界单文件模式区块绕回 | SingleFileStorage 描述符只有 65536 槽，第 65537 个覆写 0 号 | 超大世界用默认 Region 存储 | 05a · TerrainSerializer23.cs:126 |
| 天亮瞬间卡一下 | SkyLightValue 变化全区块降级重传光，属正常 | mod 别在热路径再触发大片降级 | 14页 · TerrainUpdater.cs:319-322 |
| 满月判断不对 | MoonPhase==4 是新月（更暗表），满月是 ==0 | 校正索引 | 14页 · SubsystemSky.cs:783-785 |
| 生物刷怪限额改了全局生效且换世界不清零 | m_totalLimit 等是 static 字段 | 意识到全局性；要每世界隔离自己存实例 | 02页 · SubsystemCreatureSpawn.cs:54-61 |
| 自定义生物不刷出来 | 落点验证严格：Surface 要天光-光照>3+两格空非水，Cave 要 SkyLight-光照≥5，Water 要 3 格水 | 按验证条件设计生成环境 | 02页 · TestSpawnPoint:1199-1261 |
| 大面积水扩散时邻居回调风暴 | SpreadFluid 每轮手动 ProcessModifiedCells，每 0.25s 两轮全量回调 | 大水体注意回调成本 | 02页 · SubsystemFluidBlockBehavior.cs:263 |
| OnBlockAdded 里看邻居，邻居还没收到通知 | 邻居通知延后到 ProcessModifiedCells（Terrain 更新之后） | 依赖邻居状态用 OnNeighborBlockChanged | 02页 · SubsystemTerrain.cs:66-84 |

## 十、数值与平衡类（含性能 / 内存 / 数学陷阱）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 混战越打越卡 | 大量活体同格 → Body 挤压 O(n²)+尸体常驻（无全局碰撞对缓存） | 玩法侧限单区域活体上限+尸体填包；探针用 NewBodyCollision 分段 | 13页性能节 |
| 巨型爆炸卡顿 | SimulateExplosion 同帧同步，BFS 域随压力平方级增长 | 控制单次 pressure | 13页 · SubsystemExplosions.cs:271/:343 |
| 大位移技能/冲量被吃掉 | Velocity setter 钳 MaxSpeed=25 | 大位移用 ApplyDirectMove 不受钳制 | 13页 · ComponentBody.cs:176-186 |
| 大爆炸后掉落物"没了" | 抛射物数≥40 后掉落概率骤降（限流非 bug） | `ExplosionKeepsPickables=true` 豁免 | 02页 · SubsystemExplosions.cs:707-710 |
| 大规模刷物场东西 60 秒就消失 | 掉落物寿命与场上数量挂钩：Terrain/植物类 >80 个时 60s | MaxTimeExist 覆盖 | 16页 · Pickable.cs:174-196 |
| 粒子永不消失、帧率持续掉 | 没覆写 Simulate（基类恒 return false） | 按活跃计数返回 true；跟随型按 IsStopped 协议 | 07页 · ParticleSystem.cs:164 |
| 粒子多时 CPU 线性涨 | Puke/Paint/BurntDebris 每粒子每帧地形射线 | 压容量/寿命，或学水花只在液面判定 | 07页坑表 |
| 跟随型粒子系统永久泄漏 | 宿主忘了置 IsStopped/手动 Remove | 照 ComponentOnFire.cs:81-83 的收尾协议 | 07页坑表 |
| 异形方块掉帧 | 顶点阶段现算矩阵每帧重复 | 学原版 Initialize 预烘全部 data 变体的 BlockMesh/碰撞盒表 | 04页渲染套路 |
| 浏览器端高刷屏卡顿 | interop（JSImport/JSExport）每次跨界开销大 | 高频数据走共享内存（InputBridge 模式），interop 只做低频服务 | 23页 · main.js:66 |
| Get 过的大资产常驻内存 | ContentManager.Caches 不自动逐出 | 一次性数据 Get 后立刻 `ContentManager.Dispose("名字")` | 20页坑表 |
| 浏览器端 JS 堆被钉住 | 跨界的 JSObject（file/bytes）不 Dispose | 照 Storage.ChooseFile 的 using/Dispose 序 | 23页 · Storage.cs:749-753 |
| 零向量 Normalize 结果不是 Zero 而是 UnitX | 引擎数学库约定 | 先判 LengthSquared>0 | 21页 · Vector2.cs:103-106 |
| Vector4 长度算错 | LengthSquared 只算 XYZ 不含 W | 当 4D 用时手算 W | 21页 · Vector4.cs:75 |
| 边界包含判断出错 | Box/Rectangle 是半开区间，BoundingBox 是闭区间，两套别混 | 按数据类型选对判定 | 21页 · Box.cs:66、BoundingBox.cs:67 |
| 直接写内存/传 GL 的矩阵排布不对 | Matrix 列主序存储+行向量语义（v*M），平移在 M41-M43 | 写内存前对照 Matrix.cs:20-35 字段序 | 21页 · Matrix.cs:20-35 |
| 直接扣血没有命中判定/音效/统计 | AI 打人也走 Miner.Hit；绕过 Miner 直接扣血失去全链 | 伤害过 ComponentMiner/Attackment 结算链 | 03a · ComponentChaseBehavior.cs:180 |
| 检索不到 Attackment 类相关代码 | 类名错拼为 Attackment（历史错误，注释禁止改名） | 照错拼名搜 | 16页 · Attackment.cs:7-11 |
| 自定义蛋行为不生效 | LayEgg 蛋块 value=118 硬编码 | hook OnEatPickable 级替换或重写组件 | 03a · ComponentLayEggBehavior.cs:61 |
| A* 寻路初始化行为怪 | AStar ctor 校验 ClosedStorage 的 if 复制粘贴误判 OpenStorage（引擎 bug） | 使用时注意构造校验误报 | 16a · AStar.cs:53-55 |
| SortedMultiCollection.Find 拿到的不是第一个 | 重复键返回最后一个匹配 | 需要第一个就自己遍历 | 16a · SortedMultiCollection.cs:164-190 |

## 还查不到？路由

1. **回到主题页坑节**：`E:\数据\生存战争系列\SC完全学习笔记\01-引擎\` 下 23 个主线页各带"坑与对策"节，明细页（同目录 `明细\`）含逐文件坑列——本手册只收 mod 视角条目，引擎内部行为细节以原页为准。
2. **加载与钩子总纲**：`E:\数据\生存战争系列\SC完全学习笔记\01-引擎\12-ModAPI与加载链.md`（最密集：加载 20 步、modinfo 字段表、钩子注册窗口、打包要点）。
3. **实操配方**：`E:\数据\生存战争系列\SC完全学习笔记\Mod开发配方.md`（跨域任务路由）。
4. **页面地图**：`E:\数据\生存战争系列\SC完全学习笔记\README.md`。
5. **仍没覆盖**：按库规则执行查找协议——Grep `E:\SurvivalcraftAPIProject\` 引擎源码定位后，回写对应主题页坑节（保持库越用越准）。
