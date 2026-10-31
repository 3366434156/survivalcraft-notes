# Mod 开发配方（任务 → 照抄原版代码）

> 独立库 · 更新: 2026-10-31 · 状态: 23 域全量收录；后续新批次随批补最典型范例
> 本表只含 Survivalcraft 原版实现；mod 侧用法案例不在本库收录范围。

## 这本配方怎么用

写 mod 时遇到"我想做 X"，三步：

1. **在下表找到你要做的事**，右边就是引擎里最值得照抄的原版实现（文件 + 实读行号）；
2. **打开那个文件核对**（源码仓库：https://gitee.com/SC-SPM/SurvivalcraftApi ），看它为什么这样写；
3. **照抄改造成自己的代码**——范例选的都是"最简/最全/唯一"的实现，抄它少踩坑。

例：想给方块加"按状态发光"→ 查"发光方块"行 → 抄 `CampfireBlock.cs:146-152`（`min(8+data/2,15)`，字段>0 是闸门）。
想理解某段代码的完整上下文（调用链/存档/坑），去对应主题页（导航"引擎主线"）；AI agent 从 [AGENTS.md](AGENTS.md) 进。

## AI 与生物

| 我要做… | 照抄哪里 |
|---|---|
| 新增一个引擎级 AI 行为 | `E:\SurvivalcraftAPIProject\Survivalcraft\Component\Behavior\ComponentWalkAroundBehavior.cs:6`（最简 ComponentBehavior 子类：ImportanceLevel+IsActive+Update）；调度器 `ComponentBehaviorSelector.cs` 自动收集，无需注册 |
| 生物追逐目标并打人 | `ComponentChaseBehavior.cs:6`（只置 AttackOrder）；命中链 `ComponentChaseBehavior.cs:180`→`ComponentMiner.cs:636-715`（伤害/命中率/耐久/统计全在 Miner，绕过会丢全套管线） |
| 伤害/死亡/掉落全链 | [03页](01-引擎/03-实体与组件体系.md)"生命/伤害结算链"（Injure→Process→Die→掉落→Despawn 带行号） |
| 生物骑乘 | `ComponentRider.cs:32-39`（ParentBody 反查+0.75s 插值）；"_Saddled" 模板尾缀开关 SteedBehavior |
| 自定义 dae 生物会动 | 模板必须配 AnimationConfigPath（四足/鸟/鱼 AnimateCreature 全空实现，`ComponentFourLeggedModel.cs:188`） |
| 属性因子/创造免伤 | `ComponentFactors.cs:199-214`（三段时序：先结算上帧→再重建→再放行 hook）+ `ComponentLevel.cs:187-189`（创造模式 ResilienceFactor=+∞） |

## 方块与地形

| 我要做… | 照抄哪里 |
|---|---|
| 新增方块/中间基类 | [04页](01-引擎/04-方块系统.md)（继承树概览+注册） |
| 拦截所有方块变更 | `SubsystemTerrain.ChangeCell:355`（总闸+TerrainChangeCell 钩子）；邻居通知延后到 `ProcessModifiedCells:66`——OnBlockAdded 里读邻居是"未通知态" |
| 活塞推方块写回地形 | `SubsystemMovingBlocks` Stopped 事件→`AddTerrainBlock:692`（BlockEntity/告示文本随迁） |
| 发光方块 | `Block.DefaultEmittedLightAmount`(:83) 或 override `GetEmittedLightAmount`(:508)；仿 `CampfireBlock.cs:146` |
| 按状态分档发光 | `CampfireBlock.cs:146-152`（min(8+data/2,15)；字段>0 是闸门） |
| 零代码常亮灯 | `WickerLampBlock.cs`+`Content\Assets\BlocksData.txt`（数据表优先于 override） |
| 最简新方块 | `IceBlock.cs`（4 行最小实现）；带染色仿 `BasaltBlock.cs:5` |
| 异形方块（门/楼梯/活塞） | 预烘变体表范式：`DoorBlock.cs:21-62`(16变体)/`StairsBlock.cs:26-104`(24×2)/`PistonBlock.cs:12-70`(48)；运行期只查表 |
| 液体方块 | `FluidBlock.cs:23-43`(反射建同族表)+`WaterBlock.cs:12`；顶面 8 邻平滑(:179-192) |
| 壁挂电路方块 | `MountedElectricElementBlock.cs:3-21`+`ButtonBlock.cs` |
| 模型物品方块 | `ChunkBlock.cs:16-37`/`FoodBlock.cs:18-39` |
| 多变体物品方块 | `SeedsBlock.cs`（尝试类型×粘性共 16 变体，预烘 TryTypeIndex） |
| AdHoc 程序化配方 | `FireworksBlock.cs:195-283`（配料矩阵→行；`CarpetBlock.cs` 同款） |
| 自定义地形生成 | [05页](01-引擎/05-世界与地形生成.md) TCG 生成器族（三版差异对照） |

## 子系统与存档

| 我要做… | 照抄哪里 |
|---|---|
| 新增子系统 | Subsystem 基类 + xdb MemberSubsystemTemplate（[02页](01-引擎/02-Subsystem体系.md) 全链含 XML 片段路由） |
| 子系统互查/顺序 | `Project.FindSubsystem` + Dependencies 声明；"全体 Load 前"窗口=`ProjectBeforeSubsystemsAndEntitiesLoad` |
| 往存档写自定义数据 | 重写 Subsystem.Save/Load；**Count>0 才落盘**，读端必须给默认值；类型硬拆箱规则见 [11页](01-引擎/11-存档持久化.md) |
| 电路固定步进模拟 | `SubsystemElectricity`（0.01s 固定步进=100步/秒）；注意 Simulate 异常 rethrow 全电路死 |
| 卸载实体随区块重放 | `SubsystemSpawn.cs:338`(SpawnsData 紧凑字符串)/:174(重放)；区域计数把未生成的 SpawnsData 也算数防循环（`SubsystemCreatureSpawn.cs:1311`） |
| 自定义类型进存档 | `Survivalcraft\Game\FloatCurve.cs:6-13`（struct 内嵌套 HumanReadableConverter，一个文件搞定注册+格式） |
| 值列表打包进一个键 | `ComponentClothing.cs:290/:299`（ValuesListToString/FromString(';') 官方惯用法） |
| 存档版本迁移转换器 | `VersionConverter21To22.cs:6-30`（SourceVersion/TargetVersion+按键定位改值；Version 更新应放最后防中间态） |
| 注册钩子标准写法 | `SurvivalCraftModLoader.cs:15-26`（__ModInitialize 注册块，勿晚注册） |
| 写生物生成规则类 | `StandardCreatureSpawnRule.cs:34-59`（继承它而非裸 CreatureType） |
| 声明模组设置页面 | `ModSettingsParser.cs:23-53`（Id 禁 /、类型全限定名） |
| 合并原版 Database | `ModsManager.cs:1083-1152`（.xdb 统一 new-*/Remove 前缀，不走 Harmony 硬改） |
| 后台任务+帧泵收尾 | `CommunityFramePump.cs:12-31`（Window.Frame 挂载+每轮 try/catch 防崩） |

## 渲染与特效

| 我要做… | 照抄哪里 |
|---|---|
| 新增粒子系统 | ParticleSystem 基类 5 步（[07页](01-引擎/07-粒子系统.md)） |
| 画面叠加层（受伤闪红等） | ScreenOverlays 隐式协议：Reset 时序先清零，各组件帧内 Max() 叠入（`ComponentScreenOverlays.cs:57-71`） |
| 天空/雾/闪电绘制 | [14页](01-引擎/14-光照天空与天气.md) SubsystemSky 三 pass(-100/5/105)；SkyDrawExtra 钩子(:398) |
| 新增顶点格式 | `VertexPositionColorTexture.cs:3-7`（最薄样板） |
| 新 Batch 类型接入 | `VectorFontBatch2D.cs`+`PrimitivesRenderer2D.cs:96-130` |
| 离屏 RT/回读/Blit | `RenderTarget2D.cs:133-185/52-78/88-123`（Raw GL 后置 m_framebuffer=-1） |
| 骨骼纹理蒙皮 | `JointTexture.cs:32-42,93-123`（每关节 8 像素 RGBA32F） |
| 网格级 shader 变体宏 | `ShaderDefines.cs:334-411`（稳定 hash 宏系统） |
| 新增粒子（最薄全流程） | `BlockDebrisParticleSystem.cs:18-59`+注册 `Block.cs:499-503` |
| 弹丸拖尾一行注册 | `SubsystemArrowBlockBehavior.cs:14`（AddTrail） |
| 常驻共享池 | `RainSplashParticleSystem.cs:28-73`+`SubsystemWeather.cs:252-253` |
| 跟随实体特效全套 | `OnFireParticleSystem.cs:26-77`+`ComponentOnFire.cs:60-83` |
| 入水溅花+限流 | `ComponentBody.cs:591-603`（TryBeginInstantiation 100次/帧） |
| 3D 漂浮文字粒子 | `HitValueParticleSystem.cs:55-111`（FontBatch3D/VectorFontSink3D 双路；可 SetHitValueParticleSystem 整体替换） |

## 音频

| 我要做… | 照抄哪里 |
|---|---|
| 世界内 3D 一次性音效 | `SubsystemBowBlockBehavior.cs:125`（走 SubsystemAudio 位置系重载，注意 minDistance 满音量半径语义） |
| 循环环境音（区域声场） | `SubsystemAmbientSounds.cs:26-79`+`ComponentOnFire.cs:68-72`（贡献聚合，勿每声源各开 source） |
| 背景音乐 | `MusicManager.cs:61-85,131-161`（ogg StreamingSource 流式+交叉淡化；游戏内音乐走 hook:107） |
| 声音材质（脚步/撞击） | `SubsystemSoundMaterials.cs:17-27`（新方块只给 SoundMaterialName 即复用全套映射；映射表存世界存档） |
| 防音效风暴 | `SubsystemPickables.cs:48-64`（每帧上限包装器） |
| 区域雨声积分 | `SubsystemWeather.cs:249-262`（0.33s 对 listener 15×15 雨柱按距离积分→目标音量→Lerp(5dt)；归一因子 Load 期预积分，见 [08a](01-引擎/明细/08a-音频明细.md)） |

## 电学与机构

| 我要做… | 照抄哪里 |
|---|---|
| 自定义电力元件 | `ElectricElement` 子类（[15页](01-引擎/15-电学与机构.md) 4 步）；**必须**补进 63 ID 硬编码表 `SubsystemElectricBlockBehavior.cs:8-70` |
| 电控 16 级亮度灯 | `LightbulbBlock.cs:120/:266-286`+`LightBulbElectricElement.cs:35`（data bit3-6 编码） |
| 最小执行元件 | `GunpowderKegElectricElement.cs:5-12`（11 行：高电平→调行为子系统） |
| 防抖机构执行状态机 | `TrapDoorElectricElement.cs:14-39`（上电复位+沿记步+10步节流；Door/FenceGate/SpikedPlank 同构） |
| 语义方向多端口 | `CounterElectricElement.cs:34-103`（GetConnectorDirection 分派+边沿武装+PV 持久化） |
| 轮询传感器 | `MotionDetectorElectricElement.cs:47-57`（周期自续+HashCode 抖动防同帧扎堆） |
| 模拟量分档 | `PressurePlateElectricElement.cs:68-94`（8 档质量→电压阶梯表） |
| 状态电控方块 | `SpikedPlankBlock.cs`+`ButtonBlock.cs`（data bit3-6 电压档反码，读取端 GetVoltagelevel） |

## 物理与碰撞

| 我要做… | 照抄哪里 |
|---|---|
| 自定义弹道 | `Projectile.cs:190(Raycast)/300(HitBody)/525(UpdateMovement)`（独立体系不走 ComponentBody） |
| 实体间挤压/击退 | `ComponentBody.cs:854-945`（HandleAxisCollision）+`InelasticCollision:1288`（非弹性碰撞系数） |
| 空间查询/射线 | `SubsystemBodies.cs:18`(FindBodiesAroundPoint)/`:52`(Raycast)+`BodyRaycastResult` |
| 爆炸 | `SubsystemExplosions`（压力/破坏/点燃链，见 [13页](01-引擎/13-物理与碰撞.md)） |

## UI 与弹道

| 我要做… | 照抄哪里 |
|---|---|
| 库存格子交互 | 原版 InventorySlotWidget（必调 base.Update 清单见 [09页](01-引擎/09-UI与Widget体系.md)；实为 CanvasWidget+IDragTargetWidget，非 ClickableWidget） |
| 组合控件（按钮+字+图） | `BevelledButtonWidget.cs:75-86`（XML 模板装配+Find 改装） |
| 带失效缓存的复杂自绘 | `BevelledRectangleWidget.cs:178-306`（批缓存+属性置脏+GlobalScale 失效） |
| 拖放目标 | `DragHostWidget.cs:17-55`+`FurnitureSetItemWidget.cs:24-35`（IDragTargetWidget 协议，Input.Drag 消失即 DragDrop） |
| 均衡断行 | `FlexPanelWidget.cs:257-320`（二分最小化最大行宽） |
| 血条式分格值条 | `ValueBarWidget.cs:85-211`（BarBlending/HalfBars/Flash，别自绘） |
| 两按钮确认框 | `MessageDialog.cs:18-47`（OnShowDialog 钩子=最小侵入替换点） |
| 列表选择+定制行 | `ListSelectionDialog.cs:23-57`+`SelectGameModeDialog.cs:5-20`（itemWidgetFactory 继承定制） |
| 全代码构建对话框 | `EditColorDialog.cs:19-136`（Canvas+DialogArea+Stack 结构，动态条数面板照抄） |
| 可取消进度框 | `CancellableBusyDialog.cs:38-78`（CancellableProgress 协作取消，长任务直用） |
| 滚到底才可确认 | `BulletinDialog.cs:58-63`（80% 阈值判定） |

## Screen 屏幕族

| 我要做… | 照抄哪里 |
|---|---|
| 最小设置/子菜单屏（XML+滑块+返回） | `Screen\SettingsAudioScreen.cs:5-34`（40 行含全部模板） |
| 异步加载列表不卡帧 | `Screen\PlayScreen.cs:82-118`（BusyDialog+Task.Run+Dispatcher.Dispatch 回填，跨线程封送） |
| 进世界流程状态机 | `Screen\GameLoadingScreen.cs:21-96`（Engine.StateMachine 四态+异常落日志框） |
| 设置页加自定义按钮 | `Screen\SettingsScreen.cs:32-43,86-115`（钩子+AddSettingButton 奇偶分列） |
| 屏内异步任务槽 | `Screen\Community\CommunityScreen.cs:52-55,236-254`（TaskSlot.Start 异步+Update.TryTake 收尾） |
| 多屏共享行为基类 | `Screen\Community\CommunityScreenBase.cs:9-90`（ctor 订阅/Dispose 退订/单槽委托） |

## 输入与相机

| 我要做… | 照抄哪里 |
|---|---|
| 环绕/跟随/自由飞行相机 | `OrbitCamera.cs:117-167`（参数化+平滑+地形钳制；继承 BasePerspectiveCamera 别重写） |
| 防相机穿墙 | `TppCamera.cs:127-149`（6 面不透明射线+0.5 退距） |
| 改 FOV/投影 | `BasePerspectiveCamera.cs:233-239`（RecalculateCameraProjection 钩子 ref 改参） |
| 读触摸手势 | `WidgetInput.cs:939-990`（阈值挂 SettingsManager 可调） |
| VR 手柄射线拾取 | `ComponentInput.cs:60-69` CalculateVrHandRay（HMD 逆矩阵换世界系范式） |

## 玩法与库存

| 我要做… | 照抄哪里 |
|---|---|
| 自定义初始装备/新手包 | `PlayerData.cs:632-645`（ValuesDictionary overrides 注入，一处改全体） |
| 护甲吸收公式 | `ClothingData.cs:122-167`+`Attackment.cs:71`（ArmorProtectionDivision 专用 mod 通道） |
| 掉落物生成参数化 | `Pickable.cs:129-145`（抛物初速/StuckMatrix/归属全参数；调优挂 MaxTimeExist/IsFireProof） |
| 出生状态机仿写 | `PlayerData.cs:142-343`（五态：FirstUpdate→PrepareSpawn→WaitForTerrain→Playing⇄PlayerDead） |
| 合成表接入 | `Managers\CraftingRecipesManager.cs:141,220`（先 AdHoc 再静态表+镜像平移穷举） |

## 媒体与动画

| 我要做… | 照抄哪里 |
|---|---|
| JSON 状态机动画控制器 | `AnimationConfigLoader.cs:334-426` CreateController（模板/内联双路径+校验器） |
| 缺切线网格生成切线 | `GltfMeshConverter.cs:519-594`（w 取反对齐引擎着色器） |
| 根运动冲量（跳跃/挥击） | `AnimationController.cs:474-499`（三测速法+父链旋转变换） |
| 1D/2D 混合空间 | `BlendSpaceSource.cs:299/:334`（预分配缓冲零每帧GC） |
| OpenXR 实例→会话→动作全启动链 | `OpenXrVrBackend.cs:184-426`（软降级+双轨 init 全序） |
| 全主流头显手柄绑定表 | `OpenXrVrBackend.cs:688-945` SuggestBindings（9 profile 现成） |
| recenter Y 漂移补偿 | `OpenXrVrBackend.cs:1471-1480`+`1239-1257`（事件快照+次帧差分） |
| 双眼 FBO 复用渲染 | `OpenXrVrBackend.cs:554-575`+`1100-1104`（acquire 后重挂颜色附件） |
| 非对称 FOV 投影 | `OpenXrVrBackend.cs:1570-1592`（tangent 差值+GL clipZ[-1,1]） |

## 内容与资源

| 我要做… | 照抄哪里 |
|---|---|
| 注册新资产类型读取器 | `IContentReader\JsonReader.cs:20-28`+`ContentManager.cs:201`（契约仅 3 成员） |
| 导入外部文件标准序 | `CharacterSkinsManager.cs:109-123`（Verify→Validate→Position=0→CopyTo） |
| 单条目白名单 zip 容器 | `FurniturePacksManager.cs:64-78,109-124`（恰好 1 条目+类型化失效） |
| 覆盖导入带回滚 | `ExternalContentManager.Import.cs:95-119`（TransactionalFileReplacement 同款备份） |
| 后台线程枚举主线程列表 | `ExternalContentManager.Analyze.cs:138-154`（先 Dispatcher 封送，竞态先例注释在此） |

## 数据资产

| 我要做… | 照抄哪里 |
|---|---|
| 加一种生物换色变体 | `Content\Assets\Database.xml:707`（Horse_White 只继承 Horse 改贴图/参数） |
| 调生物数值(血/攻击/掉落) | `Database.xml:46-110`（Cow 的 Health/Miner/Loot/EatPickableBehavior；ParameterSet 掉落行 `Block;min;max` 语法） |
| 加一种方块的数据表 | `BlocksData.txt:6`（DirtBlock 行，含 # 自引用掉落；79 列标准填法与留空默认） |
| 加合成配方 | `CraftingRecipes.xml:64-139`（Materials 节，含 Remains=EmptyBucketBlock 返桶样例） |
| 加防具 | `Clothes.xml:2-47`（43 条 ClothingData；Slot/Insulation/Layer 全属性面） |
| 动画分层(走/持/骼/步) | `AnimationTemplates\Human.template.json`+`Animations\Human.json`（layer blendMode+boneMask+驱动器参数三级） |

## Engine 核心与平台

| 我要做… | 照抄哪里 |
|---|---|
| 跨线程把结果交回主线程 | `Engine\Engine\Dispatcher.cs:38-64` Dispatch（后台线程算完 `Dispatch(()=>…)`，唯一正道） |
| 安全写档 | `Engine\Engine\Storage.cs:204-245` MoveFileSafely（备份-替换-回滚三段式；JsonFileStore 即抄它） |
| 玩家输入转文件名 | `Storage.cs:613-637` SanitizeFileNameSegment（原版三处直接调用） |
| 跨平台读写用户数据文件 | `Storage.cs:324-341` WriteAllText/ReadAllBytes（统一 `data:` 前缀虚拟路径） |
| 射线选方块/拾取 | `Engine\Engine\Ray3.cs:20-90` Intersection(BoundingBox)（slab 法带盒内提前返回） |
| 均匀随机方向/正态分布 | `Engine\Engine\Random.cs:61-115` NormalFloat/Vector2()/Vector3()（粒子与生物游走都用它） |
| SIMD 批量变换 | `Vector3.cs:257-280`（全仓唯一带崩溃实证注释的范本；外门必须 AdvSimd\|\|Sse） |
| 自定义日志落盘 | `Engine\Engine\StreamLogSink.cs:7-28`（实现 ILogSink 30 行完事） |
| 平台入口差异（Win/Android/iOS） | [01页](01-引擎/01-程序入口与主循环.md)"平台入口与启动差异"节（三形态入口+帧链收口 Program.FrameHandler） |

## 内嵌浏览器（WASM）

| 我要做… | 照抄哪里 |
|---|---|
| 高频数据 JS→C# 零拷贝传输 | `Engine.Browser\InputBridge.cs:12-36`+`main.js:115-159`（共享内存双缓冲+Atomics 原子翻转协议） |
| 新增一种输入事件类型 | `InputEventType.cs:2-27`+`InputBridge.cs:83-110`+`main.js:121-139`（三处镜像逐字段同步） |
| 大文件流式下载进 WASM | `Survivalcraft.Browser\ContentFileBridge.cs:8-18`+`main.js:34-56`（共享内存+就绪头+忙等接收端） |
| 防裁剪误删 delegate | `Engine.Browser\TrampolineFuncs.cs:8-11`（DynamicDependency 锚定+UnmanagedFunctionPointer 范式） |
| 浏览器宿主能力（文件选择器/全屏/下载） | `Engine.Browser\BrowserInterop.cs:49-56`+`main.js`（JSImport/JSExport 低频互操作契约） |

## 逐文件速查索引

- [02a-子系统明细](01-引擎/明细/02a-子系统明细.md)（111 文件一行一表）、[03a-组件明细](01-引擎/明细/03a-组件明细.md)（91+EntitySystem 20 文件）
- 04a-22a 共 20 张逐文件明细见各自主页链接（`01-引擎\明细\`）

## 回填规则

- 每完成一个深读批次 → 本页对应节 + 该域页面"原版范例"表同步补最典型范例；行号必须实读。
- 一句话说清"为什么抄它"（最简/最全/唯一）。
