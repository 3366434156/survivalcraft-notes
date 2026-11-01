# Mod 开发配方 2（全量任务索引 · 任务 → 照抄原版代码）

> 独立库 · 更新: 2026-11-01 · 状态: 23 个引擎主线页"原版范例"表 + [Mod开发配方.md](Mod开发配方.md) 全量去重合并（243 条）；按任务动词分 15 大类，类内按域分组。
> 精选高频 30 条在 [Mod开发配方.md](Mod开发配方.md)；本页是全量索引，一条一行。

**路径约定**：裸文件名均在 `E:\SurvivalcraftAPIProject\Survivalcraft\` 子树下；带 `Engine\Engine\`、`Engine.Media\`、`Engine.Animation\`、`Engine.Browser\`、`Survivalcraft.Browser\` 前缀的按前缀定位。行号以各页写页当日实读为准（关键行已抽验）。
**页锚**：`〔NN〕`＝深入上下文去 `01-引擎\NN-主题.md`（目录地图/调用链/坑表）；多锚＝跨页合并条目。

## 一、新增类 · 方块 / 地形 / 世界

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 方块 | 最简新方块 | `IceBlock.cs`（4 行最小实现）；带染色仿 `BasaltBlock.cs:5`；可入家具抄 `CanBeBuiltIntoFurniture` 〔04〕 |
| 方块 | 加一套多材质工具 | `AxeBlock.cs`（基类 Initialize 烘模型）+`CopperAxeBlock.cs:5`（叶填参）——材质差异全部收敛为 ctor 参数 〔04〕 |
| 方块 | 异形方块（楼梯/活塞，预烘变体） | `DoorBlock.cs:21-62`(16 变体)/`StairsBlock.cs:26-104`(24×2)/`PistonBlock.cs:12-70`(48)；Initialize 预烘 BlockMesh+碰撞盒表，运行期只查表 〔04〕 |
| 方块 | 门/开关类方块（data 位+朝向放置） | `DoorBlock.cs:208-228`（data 位工具）+:120（朝向放置）；活板门倒装看 `TrapdoorBlock.cs:92-118` 〔04〕 |
| 方块 | 液体方块 | `FluidBlock.cs:23-43`（反射建同族表，免写比较器）+`WaterBlock.cs:12`（着色）；顶面 8 邻平滑 :179-192 〔04〕 |
| 方块 | 壁挂电路方块 | `MountedElectricElementBlock.cs:3-21`（三 abstract 钩子）+`ButtonBlock.cs`（实现样板）；活塞可推规则免写 〔04〕 |
| 方块 | 模型类物品方块（不入地形） | `ChunkBlock.cs:16-37`（ctor 传 transform/颜色/smooth）或 `FoodBlock.cs:18-39`（带腐烂值） 〔04〕 |
| 方块 | 家具/换装家具外观 | `FurnitureBlock.cs:604-628`（data 编码）+`SubsystemFurnitureBlockBehavior`（FurnitureDesign 表）；AdHoc 组合合成 :436 〔04〕 |
| 方块 | 可染色立方（16 色调色板） | `PaintedCubeBlock.cs:126-140`（位编码）+:121(Paint)+:66(GetCreativeValues 17 值) 〔04〕 |
| 方块 | 染料上色任意方块/脱漆 | `PaintedCubeBlock.cs:121`（IPaintableBlock.Paint）+`ClothingBlock.cs:189-268`（AdHoc 染色+脱漆） 〔04〕 |
| 方块 | 一类多变体物品（data 切贴图/种下变形） | `SeedsBlock.cs:36-55`（按种型变 7 种方块）+`BulletBlock.cs:86-88`（位编码+参数表）——一个类承载一族物品的标准位编码 〔04〕 |
| 方块 | "方块+方块"AdHoc 配方（染色/褪色/合成） | `CarpetBlock.cs:103-169`（地毯+油漆桶染色/漂白剂褪色，热≥1）；批量程序化配方矩阵抄 `FireworksBlock.cs:195-283`（配料矩阵→行） 〔04〕 |
| 方块 | 带运行状态的电控方块（状态存 data） | `SpikedPlankBlock.cs:63-78`（刺出/收回位+挂面偏移编码）+`FourLedBlock.cs:50-74`（8 色程序化配方）；电压档反码 `ButtonBlock.cs:51-53` 〔04·15〕 |
| 地形 | 自定义整套地形生成器 | 抄 `TerrainContentsGenerator23`：实现 13 成员接口+4 个 `List<ChunkGenerationStep>`(:255-258)+构造尾 Sort(:362-365)——最简可排版的正宗结构 〔05〕 |
| 地形 | 加一个生成步骤 | TCG23:326-352 注册表样式：`new ChunkGenerationStep(order, chunk=>…)`+ShouldGenerate 开关 〔05〕 |
| 地形 | 矿脉/pocket 形状随机化 | TCG21 `CreateBrushes`(:2170-2626)：Random 固定种子→随机游走 AddBox→Compile；水/岩浆囊 :2545-2595 〔05〕 |
| 地形 | 跨区块无缝矿脉 | TCG21 `GenerateMinerals`(:991-1056)：3×3 邻域+`new Random(m_seed+i+119*j)`+burn-in 〔05〕 |
| 地形 | 洞穴蠕虫式挖掘 | TCG21 `GenerateCaves`(:1152-1266)：CavePoint 方向扰动+5 类转向概率+34 格半径出界判定+每 20 步比对防冒头 〔05〕 |
| 地形 | 植被按气候分布 | TCG21 `GenerateGrassAndPlants`(:1467-1494)+`PlantsManager.GenerateRandomPlantValue`；树密度双层噪声 :1281-1293 〔05〕 |
| 地形 | 让水面下流体自动补齐/标记顶面 | `PropagateFluidsDownwards`(:2125-2145)+`UpdateFluidIsTop`(:2147-2168) 两条自上而下扫描（平面世界复用 TCGFlat:100-102/:138-160） 〔05〕 |
| 地形 | 平面世界快速铺地形 | TCGFlat `GenerateChunkContentsPass1`(:61-98)：一重循环写整列，无中间态 〔05〕 |

## 二、新增类 · 实体 / AI / 玩法

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 组件 | 写一个完整自定义组件（契约全集） | `ComponentSpawn.cs`（61 行全文件：IUpdateable+Load 抓服务/兄弟组件（必需/可选依赖两种写法同框）+Save 条件落盘+Update 到点 RemoveEntity） 〔03〕 |
| 组件 | 运行时按模板生成实体（模板+微调） | `Managers\DatabaseManager.cs:77-92`（CreateEntity 带 ValuesDictionary overrides 重载）+批量落点照 `SubsystemCreatureSpawn.cs:1104-1135`（50 次随机偏移+适宜度>0） 〔03〕 |
| AI | 新增一个引擎级 AI 行为 | `ComponentWalkAroundBehavior.cs:6`（最简 ComponentBehavior 子类：ImportanceLevel+IsActive+Update）；调度器 `ComponentBehaviorSelector.cs` 自动收集，无需注册 〔03〕 |
| AI | 生物追逐目标并打人 | `ComponentChaseBehavior.cs:6`（只置 AttackOrder）；命中链 :180→`ComponentMiner.cs:636-715`（伤害/命中率/耐久/统计全在 Miner，绕过会丢全套管线） 〔03〕 |
| 生物 | 伤害/死亡/掉落全链 | [03页](01-引擎/03-实体与组件体系.md)"生命/伤害结算链"（Injure→Process→Die→掉落→Despawn 带行号） 〔03〕 |
| 生物 | 生物骑乘 | `ComponentRider.cs:32-39`（ParentBody 反查+0.75s 插值）；"_Saddled" 模板尾缀开关 SteedBehavior 〔03〕 |
| 生物 | 自定义 dae 生物会动 | 模板必须配 AnimationConfigPath（四足/鸟/鱼 AnimateCreature 全空实现，`ComponentFourLeggedModel.cs:188`） 〔03〕 |
| 生物 | 写生物生成规则类 | `StandardCreatureSpawnRule.cs:34-59`（继承它而非裸 CreatureType；构造签名 (SubsystemCreatureSpawn, ValuesDictionary) 是注册协议） 〔02·12〕 |
| 玩法 | 属性因子/创造免伤 | `ComponentFactors.cs:199-214`（三段时序：先结算上帧→再重建→再放行 hook）+`ComponentLevel.cs:187-189`（创造模式 ResilienceFactor=+∞） 〔03〕 |
| 玩法 | 给玩家发初始物品/默认衣 | `PlayerData.cs:632-645`（ValuesDictionary overrides 注入 Inventory/Clothing 模板覆盖，一处改全体） 〔16〕 |
| 玩法 | 自定义出生点选择算法 | `PlayerData.cs:458-533`（Score* 虚方法逐项加减分，子类重写即换算法） 〔16〕 |
| 玩法 | 出生状态机仿写 | `PlayerData.cs:142-343`（五态：FirstUpdate→PrepareSpawn→WaitForTerrain→Playing⇄PlayerDead） 〔16〕 |
| 玩法 | 世界内生成掉落物 | `Pickable.cs:129-145`（Initialize(value,count,pos,velocity,stuck,owner) 全参数；随机抛物初速在此；调优挂 MaxTimeExist/IsFireProof） 〔16〕 |
| 玩法 | 自定义伤害/护甲数值 | `ClothingData.cs:122-167`（吸收公式与耐久折算单件封装）+`Attackment.cs:66-71`（ArmorProtectionDivision 专用 mod 通道） 〔16〕 |
| 玩法 | 注册合成配方 | `Managers\CraftingRecipesManager.cs:18-56`（Initialize 钩子窗口内加 CraftingRecipe，ingredients 用 9 字符 pattern）；匹配/镜像平移穷举 :141,220 〔16〕 |
| 玩法 | 世界设置新增可存项 | `WorldSettings.cs:103-163`（Load/Save 成对、区分 live 参数，配 mod 钩子 ResetOptionsForNonCreativeMode） 〔16〕 |
| 玩法 | 玩家统计加计数器 | `PlayerStats.cs:61-133`（加一个 `[Stat]` 字段即自动持久化+UI 列举） 〔16〕 |
| 玩法 | 自定义衣物部位 | `ClothingSlot.cs:14-45`（AddClothingSlot+InitializeClothingSlots 钩子，BasicInsulation 给默认保温） 〔16〕 |
| 玩法 | 给生物接自定义 A* 寻路 | `AStar.cs:43-118`（实现 IAStarWorld 四成员+IAStarStorage 三成员即复用泛型 A*；节点池+二叉堆；后台结果用 PathfindingResult 承载） 〔16〕 |
| 端到端 | 加一只自然生成的生物 | [Mod示例-自定义生物](Mod示例-自定义生物.md)（纯数据 .xdb：新模板继承马+生成规则条目进 CreatureSpawnRules） 〔03〕 |

## 三、新增类 · 子系统 / 电学

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 子系统 | 新增子系统 | Subsystem 基类+xdb MemberSubsystemTemplate（[02页](01-引擎/02-Subsystem体系.md) 全链含 XML 片段路由） 〔02〕 |
| 子系统 | 子系统互查/顺序 | `Project.FindSubsystem`+Dependencies 声明；"全体 Load 前"窗口=`ProjectBeforeSubsystemsAndEntitiesLoad` 〔02〕 |
| 子系统 | tick 内每 N 游戏秒做一次 | `SubsystemTime.cs:147-155`（PeriodicGameTimeEvent）+用法 `ComponentHealth.cs:320`（每 2 游戏秒判溺水）——随速度倍率/睡觉加速，墙钟版见 〔01〕 〔02〕 |
| 电学 | 自定义电力元件 4 步全流程 | ElectricElement 子类（[15页](01-引擎/15-电学与机构.md) 4 步+百科 03-add-an-element）；**必须**补进 63 ID 硬编码表 `SubsystemElectricBlockBehavior.cs:8-70` 〔15〕 |
| 电学 | 最小执行元件 | `GunpowderKegElectricElement.cs:5-12`（全库最短：高数>0→调行为子系统） 〔15〕 |
| 电学 | 常量脉冲源 | `ButtonElectricElement.cs:16-39`（Press→+1 步起、+10 步回落） 〔15〕 |
| 电学 | 防抖机构执行状态机 | `TrapDoorElectricElement.cs:14-40`（10 步节流+上电复位；Door/FenceGate/SpikedPlank 同构） 〔15〕 |
| 电学 | 组合逻辑门（多输入位运算） | `XorGateElectricElement.cs:9-22`（累积异或+值变才 return true） 〔15〕 |
| 电学 | 语义方向多端口（可旋转） | `CounterElectricElement.cs:34-103`（GetConnectorDirection 分派+边沿武装+PV 持久化） 〔15〕 |
| 电学 | 持续轮询传感器（不卡 CPU） | `MotionDetectorElectricElement.cs:47-57`（周期自续+HashCode 抖动防同帧扎堆）+TestPoint 射线遮挡 :94-116 〔15〕 |
| 电学 | 模拟量分档输出 | `PressurePlateElectricElement.cs:68-94`（PressureToVoltage 8 档质量→电压阶梯表） 〔15〕 |
| 电学 | 模拟量驱动执行器 | `PistonElectricElement.cs:19-30`（电压→0-8 格长度） 〔15〕 |
| 电学 | 电控 16 级亮度灯 | `LightbulbBlock.cs:120/:266-286`（亮度存 data bit3-6）+`LightBulbElectricElement.cs:35`（Simulate 回写）；阴影联动 :122-125 〔14·15〕 |
| 电学 | 持久化内部状态（PV） | `SRLatchElectricElement.cs:11-16,:80-84`（构造读 PV+变化写 PV） 〔15〕 |
| 电学 | 显示元件（GlowPoint） | `FourLedElectricElement.cs:16-62`（OnAdded 建 4 点+按位点亮+OnRemoved 删） 〔15〕 |
| 电学 | 世界时间转电信号 | `RealTimeClockElectricElement.cs:36-49`（精确排到下一跳+5 nibble 输出） 〔15〕 |
| 电学 | 电路固定步进模拟 | `SubsystemElectricity`（0.01s 固定步进=100 步/秒）；注意 Simulate 异常 rethrow 全电路死 〔02·15〕 |

## 四、新增类 · 粒子 / 特效

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 粒子 | 新增一种粒子系统（最薄全流程） | ParticleSystem 基类 5 步（[07页](01-引擎/07-粒子系统.md)）+`BlockDebrisParticleSystem.cs:18-59`；注册 `Block.cs:499-503` 〔07〕 |
| 粒子 | 一次性爆发特效（死亡/命中风） | `KillParticleSystem.cs:14-42`+注册点 `ComponentHealth.cs:409`（构造全激活+光照取样+自毁，20 行级） 〔07〕 |
| 粒子 | 常驻共享池发射器 | `RainSplashParticleSystem.cs:28-73`+`SubsystemWeather.cs:252-253`（AddXxx 找空位+恒 false 的标准池） 〔07〕 |
| 粒子 | 跟随实体持续特效 | `OnFireParticleSystem.cs:26-77`+`ComponentOnFire.cs:60-83`（Position/Radius/IsStopped 宿主协议全套） 〔07〕 |
| 粒子 | 雨雪天气柱 | `PrecipitationShaftParticleSystem.cs:92-103`+`SubsystemWeather.cs:215`（自管批次、双纹理账本、按柱调度） 〔07〕 |
| 粒子 | 撞墙粘附粒子 | `PaintParticleSystem.cs:40-53,71-91`（切向基系构造+命中粘附/关重力） 〔07〕 |
| 粒子 | 参数化多形状爆发 | `FireworksParticleSystem.cs:37-177`（7 种 Shape 一个池子全搞定） 〔07〕 |
| 粒子 | 引信级手动管理粒子 | `SubsystemExplosivesBlockBehavior.cs:58-63,163-164`（创建/持有/手动移除全链） 〔07〕 |
| 粒子 | 需要翻页动画的粒子（火焰帧） | `FireParticleSystem.cs:51`（slot=min(9*Time/1.25,8)）——3x3 图集时间推进标准式 〔07〕 |
| 粒子 | 3D 漂浮文字/伤害数字 | `HitValueParticleSystem.cs:55-111`（FontBatch3D/VectorFontSink3D 双路）+`Attackment.cs:113-130`（ModLoader.SetHitValueParticleSystem 可整体替换） 〔07〕 |
| 特效 | 弹丸拖尾一行注册 | `SubsystemArrowBlockBehavior.cs:14`（AddTrail+SmokeTrailParticleSystem(20,0.5f,maxValue,White)） 〔07〕 |
| 特效 | 入水/入岩浆溅花+限流 | `ComponentBody.cs:591-603`（TryBeginInstantiation 100 次/帧+large 判定样板） 〔07〕 |
| 特效 | 画面叠加层（受伤闪红等） | ScreenOverlays 隐式协议：Reset 时序先清零，各组件帧内 Max() 叠入（`ComponentScreenOverlays.cs:57-71`） 〔03〕 |
| 端到端 | 自定义粒子环+位置音效 | [Mod示例-自定义特效](Mod示例-自定义特效.md)（OnBlockDug 挂点+一次性粒子系统自毁契约+PlaySound 位置系） 〔07〕 |

## 五、音效与音乐

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 音频 | 世界内 3D 一次性音效 | `SubsystemBowBlockBehavior.cs:125`（`PlaySound("Audio/Bow",1f,pitch,position,3f,true)` 标准位置系；minDistance=满音量半径） 〔08〕 |
| 音频 | 按钮/UI 点击音 | `ClickableWidget.cs:42-44`（控件设 SoundName 属性即得；无世界直通 AudioManager） 〔08〕 |
| 音频 | 3D 音源（衰减+声速延迟） | `SubsystemAudio.cs:135-141`+用法 `SubsystemSky.cs:207-220`（雷声按距离选近/远音+延迟） 〔08〕 |
| 音频 | 持续循环环境音（火/水/岩浆式） | `SubsystemAmbientSounds.cs:26-79` 全套+上报端 `ComponentOnFire.cs:68-72`（贡献聚合，勿每声源各开 source） 〔08〕 |
| 音频 | 随天气渐强的循环音（区域雨声积分） | `SubsystemWeather.cs:249-262,344-383`（雨柱按距离积分→目标音量→Lerp(5dt)） 〔08〕 |
| 音频 | 背景音乐（选曲+流式+交叉淡化） | `MusicManager.cs:61-85,131-161`（ogg StreamingSource）；游戏内音乐走 hook :107 〔08〕 |
| 音频 | 声音材质（脚步/撞击） | `SubsystemSoundMaterials.cs:17-27,29-96`（新方块只给 SoundMaterialName 即复用全套映射；映射表存世界存档） 〔08〕 |
| 音频 | 给生物挂叫声 | `ComponentCreatureSounds.cs:55-71`（PlayIdleSound）+166-188（参数表字段名） 〔08〕 |
| 音频 | 生物远程哀嚎/扇翅（行为里触发） | `ComponentHowlBehavior.cs:76-86`+`ComponentFlyAwayBehavior.cs:126-135` 〔08〕 |
| 音频 | 同一文件变调出音阶 | `ComponentLevel.cs:80-111` 〔08〕 |
| 电学 | 电压选曲高低的发音块 | `SoundGeneratorElectricElement.cs:107-151`（频率→采样档折算） 〔08·15〕 |
| 音频 | 高频事件防音效风暴 | `SubsystemPickables.cs:48-64`（每帧上限包装器，10 行抄完） 〔08〕 |

## 六、UI 与屏幕（控件 / 对话框 / 屏幕）

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| UI | 库存格子交互 | 原版 InventorySlotWidget：`InventorySlotWidget.cs:201-329`(Update)/:569(HandleDragDrop)（实为 CanvasWidget+IDragTargetWidget；必调 base.Update 清单见 [09页](01-引擎/09-UI与Widget体系.md)） 〔09〕 |
| UI | 组合控件（按钮+字+图） | `BevelledButtonWidget.cs:75-86`（XML 模板装配+Find 改装+LoadProperties，复合控件标准流程） 〔09〕 |
| UI | 带失效缓存的复杂自绘 | `BevelledRectangleWidget.cs:178-306`（cached batches+属性 setter 置脏+GlobalScale 失效） 〔09〕 |
| UI | 拖放目标与拖动宿主 | `DragHostWidget.cs:17-55`+`FurnitureSetItemWidget.cs:24-35`（BeginDrag/DragOver/DragDrop/finally EndDrag 全链） 〔09〕 |
| UI | 物品格拖抛进世界 | `ViewWidget.cs:53-75`（DragDrop 里算屏幕射线给 SubsystemPickables） 〔09〕 |
| UI | 全局输入消费（防穿透） | `SliderWidget.cs:127-162`（HitTestGlobal==子件判定+`Input.Clear()` 吞事件） 〔09〕 |
| UI | 带焦点的文本输入框 | `TextBoxWidget.cs:834-1062`（Focus 生命周期/TasksQueue 每帧任务/快捷键全集） 〔09〕 |
| UI | 血条式分格值条 | `ValueBarWidget.cs:85-211`（BarBlending/HalfBars/Flash 渐灭，别自绘） 〔09〕 |
| UI | 均衡断行（二分最小化最大行宽） | `FlexPanelWidget.cs:257-320`（CountLines 二分+拆最宽行补行数） 〔09〕 |
| UI | CSS auto 表格列协商 | `TablePanelWidget.cs:779-806`（min/max/插值三态，span 均摊 :753-773） 〔09〕 |
| UI | Markdown/HTML 渲染成界面 | `MarkdownToWidgetsBuilder.cs:27-34` 起步，复杂照 `HtmlToWidgetsBuilder.cs:48` 〔09〕 |
| UI | UI 里挂 3D 模型+动画 | `ModelWidget.cs:136-243`（AddModel/PlayAnimation/GetBoneTransform，骨变换 :576） 〔09〕 |
| UI | 分屏/刘海屏排布 | `GamesWidget.cs:14-60`（DisplayCutoutInsets×FinalUiScale+LayoutTransform 缩放） 〔09〕 |
| UI | 触摸手势解析控件（Tap/Hold/Move） | `TouchInputWidget.cs:38-91`（单指跟踪+Radius 限位输出 TouchInput） 〔09·10〕 |
| UI | 树形列表（滚动面板复用） | `TreeViewWidget.cs:56-105`（覆写 CalculateScrollAreaLength+UpdateNodes 重建行） 〔09〕 |
| UI | UI 内异步加载图片（占位→下载→上屏） | `RichContentImageLoader.cs:95-380`（占位 frame+后台下载解码+Dispatcher 回主线程+代际守卫防晚到回调） 〔09〕 |
| UI | 外部推值与用户操作双向同步（防回环） | `ModSettingItemWidget.cs:88-108`（CommitValue 查 `m_applyingExternalValue` 守卫+ApplyExternalValueCore 入口类型预检） 〔09〕 |
| 框 | 两按钮消息/确认框 | `MessageDialog.cs:18-47`（ctor 填 4 文本+handler，最通用样板；OnShowDialog 钩子=最小侵入替换点） 〔09·18〕 |
| 框 | 列表选择+定制行 | `ListSelectionDialog.cs:23-57`+`SelectGameModeDialog.cs:5-20`（itemWidgetFactory 继承定制） 〔09·18〕 |
| 框 | 文本输入框 | `TextBoxDialog.cs:19-34`（HasFocus=true+Enter 提交，一行起） 〔18〕 |
| 框 | 三按钮以上选择框 | `CommunityImportOverwriteDialog.cs:19-49`（MessageDialog 只有两按钮，多按钮自建） 〔18〕 |
| 框 | 可取消进度框 | `CancellableBusyDialog.cs:38-78`（CancellableProgress 协作取消，长任务直用） 〔09·18〕 |
| 框 | 全代码构建对话框 | `EditColorDialog.cs:19-136`（Canvas+DialogArea+Stack 结构，动态条数面板照抄）；嵌套弹框 :139-166（`ShowDialog(this, new …)` parent 传 this） 〔09·18〕 |
| 框 | 运行时组装菜单/统计行 | `GameMenuDialog.cs:475-482`（Tuple 菜单）+:520-541（AddStat 动态行） 〔18〕 |
| 框 | 滚到底才可确认 | `BulletinDialog.cs:58-63`（ScrollPosition≥80% 阈值判定） 〔09·18〕 |
| 框 | 点框外关闭 | `DownloadContentFromLinkDialog.cs:26-43`（Tap 不在框内即关） 〔18〕 |
| 框 | 每帧轮询的任务队列框 | `CommunityDownloadQueueDialog.cs:72-96`（IDownloadQueueDialogHost 抽象+Refresh 全量刷） 〔18〕 |
| 框 | 重启确认+静态便捷入口 | `RestartConfirmDialog.cs:14-51`（回调返回 true 才真重启 Window.Restart） 〔18〕 |
| 屏 | 最小设置/子菜单屏（XML+滑块+返回） | `Screen\SettingsAudioScreen.cs:5-34`（40 行含全部模板：LoadContents、Find 缓存、IsSliding 双向同步、Back 三条件） 〔17〕 |
| 屏 | Enter 收参数填详情页 | `HelpTopicScreen.cs:19-24`（参数[0]强转填 Label+滚动复位） 〔17〕 |
| 屏 | 异步加载列表不卡帧 | `Screen\PlayScreen.cs:82-118`（BusyDialog+Task.Run+Dispatcher.Dispatch 回填，跨 Enter 保留选中项） 〔17〕 |
| 屏 | 进世界流程状态机 | `Screen\GameLoadingScreen.cs:21-96`（Engine.StateMachine 四态+异常落日志框） 〔17〕 |
| 屏 | 设置页加自定义按钮 | `Screen\SettingsScreen.cs:32-43,86-115`（OnSettingsScreenCreated 钩子+AddSettingButton 奇偶分列） 〔17〕 |
| 屏 | 方块/生物专属图鉴页 | `RecipaediaScreen.cs:36-44,116-123`（Block.GetBlockDescriptionScreen/GetBlockRecipeScreen 整替注册表项） 〔17〕 |
| 屏 | 世界选项屏接入建/改世界 | `WorldOptionsScreen.cs:7,250-254`（实现 IWorldOptionsScreen，返回不重置 WorldSettings） 〔17〕 |
| 屏 | 多屏共享行为基类 | `CommunityScreenBase.cs:9-90`（ctor 订阅/Dispose 退订/单槽委托 Enter-Leave 配对） 〔17〕 |
| 屏 | 单实例多级导航 | `ModSettingsScreen.cs:19-20,59-73,233-261`（内部 (pkg,pageIds,title) 栈，规避同屏重入） 〔17〕 |
| 屏 | 屏内异步任务槽 | `CommunityScreen.cs:52-55,236-254`（TaskSlot.Start 异步+Update.TryTake 收结果） 〔17〕 |
| 端到端 | 加自己的界面 | [Mod示例-自定义界面](Mod示例-自定义界面.md)（XML 模板+OnLoadingFinished 注册+OnSettingsScreenCreated 入口按钮） 〔17〕 |

## 七、输入与相机（含 VR）

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 相机 | 环绕/跟随/自由飞行相机 | `OrbitCamera.cs:117-167`（参数化+平滑+地形钳制最全；继承 BasePerspectiveCamera 别重写） 〔10〕 |
| 相机 | 防相机穿墙 | `TppCamera.cs:127-149`（眼→期望位置 6 面不透明射线+0.5 退距）；复用 `ClampToTerrain` :29-49 〔10〕 |
| 相机 | 死亡/观战视角 | `DeathCamera.cs:50-80`（36 方位找不被地形挡的最佳点） 〔10〕 |
| 相机 | 注册自定义相机（mod 侧） | `SurvivalCraftModLoader.cs:41-61`（GetCameraList 给序号+ManageCameras 建实例挂条件委托） 〔12〕 |
| 相机 | 世界坐标↔屏幕坐标（血条/名牌） | `Camera.cs:42-46` WorldToScreen/ScreenToWorld 〔10〕 |
| 相机 | 改 FOV/投影 | `BasePerspectiveCamera.cs:233-239`（RecalculateCameraProjection 钩子 ref 改参） 〔06·10〕 |
| 输入 | 每帧响应玩家动作 | `ComponentInput.cs:134-241`（读 WidgetInput 映射名→填 PlayerInput 的完整范式） 〔10〕 |
| 输入 | 读触摸手势（拖动/长按/点按） | `WidgetInput.cs:939-990`（阈值取 SettingsManager.MinimumDragDistance/MinimumHoldDuration 可调） 〔09·10〕 |
| 输入 | 自定义虚拟摇杆/触摸控件 | `TouchInputWidget.cs:38-91`+消费范式 `ComponentInput.cs:621-639`(MoveWidget) 〔10〕 |
| 输入 | 手柄组合键/修饰键读法 | `GamePad.cs:333-397`（Once 抑制与记录）+`WidgetInput.cs:548-557` 〔10〕 |
| 输入 | 手柄键位注册（mod，含组合键） | `ModLoader.cs:1938-1947` GetGamepadMappings（组合键 ValuesDictionary 官方注释示例 :1939-1945；详见 [Mod钩子总表](Mod钩子总表.md)高频精选"手柄组合键注册"行） 〔10·12〕 |
| 输入 | 分屏本地多人输入 | `MultiKeyboard.cs`/`MultiMouse.cs` 数据结构+`WidgetInputDevice.cs` 位图+`WidgetInput.cs:99-107` 槽位轮询 〔10〕 |
| VR | VR 手柄射线拾取 | `ComponentInput.cs:60-69` CalculateVrHandRay（HMD 逆矩阵换世界系范式） 〔10〕 |
| VR | VR 传送（抛物线预览） | `ComponentInput.cs:685-819`（算弧/校验/执行三段式） 〔10〕 |
| VR | VR 双目渲染 | `VrManager.cs:264-312` RenderToEyes（FBO 状态保存恢复范式）+`ViewWidget.cs:149-190` 〔10〕 |

## 八、绘制与渲染

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 渲染 | 新增顶点格式 | `VertexPositionColorTexture.cs:3-7`（static readonly VertexDeclaration+字段顺序一致；带语义头注释照 AlphaTested.vsh:50-52） 〔06〕 |
| 渲染 | 新 Batch 类型接入 | `VectorFontBatch2D.cs` 全文+`PrimitivesRenderer2D.cs:96-130`（工厂缓存/复用/MRU+并行容器注册进 m_allBatches） 〔06〕 |
| 渲染 | 画调试线框/球/包围盒 | `FlatBatch3D.cs:12-523`（QueueSphere/QueueBoundingBox/QueueBoundingFrustum/QueueCube 现成；分段提交 BaseFlatBatch.cs:41-85） 〔06〕 |
| 渲染 | 离屏 RT/回读/Blit | `RenderTarget2D.cs:133-185`(建 FBO)/:52-78(GetData/ReadPixels)/:88-123(Blit 换格式，缓存失效置脏) 〔06〕 |
| 渲染 | 六面环境贴图 | `CubemapTexture.cs:88-108`(分配)+`CubemapRenderTarget.cs:101-129`(BindFace+SetViewport 逐面渲) 〔06〕 |
| 渲染 | 自定义混合/深度/采样状态 | `DepthStencilState.cs:9-15`+`RasterizerState.cs:11-25`+`SamplerState.cs:17-47`（各抄一个预设写法：new 完赋属性，别改锁定预设） 〔06〕 |
| 渲染 | 多纹理多采样器的着色器参数 | `GLWrapper.cs:910-1051` 纹理槽分配顺序+Shader `<Sampler/>` 元数据（AlphaTested.psh:39）；tex/sampler 必须成对声明 〔06〕 |
| 渲染 | 骨骼纹理蒙皮（超 4 关节/多骨骼） | `JointTexture.cs:32-42,93-123`（RGBA32F 矩阵纹理+normalMatrix 同算）；传统路线照 `ShaderTransforms.cs:46-74` 〔06〕 |
| 渲染 | 网格级 shader 变体宏 | `ShaderDefines.cs:334-411`（从 VertexDeclaration/ModelMeshPart 自动生成宏+稳定 hash） 〔06〕 |

## 九、修改与覆盖

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 数据 | 加一种生物换色变体 | `Content\Assets\Database.xml:707`（Horse_White 只继承 Horse 改贴图/参数）——变体=零代码纯数据 〔22〕 |
| 数据 | 调生物数值（血/攻击/掉落） | `Database.xml:46-110`（Cow 的 Health/Miner/Loot/EatPickableBehavior；ParameterSet 掉落行 `Block;min;max` 语法） 〔22〕 |
| 数据 | 刷怪蛋元数据 | `Database.xml:182-192`（AICreature 的 CreatureEggData：蛋贴图槽/显示名/营养全在这） 〔22〕 |
| 数据 | 建生物家族抽象层 | `Database.xml:602`(Creature)+:645(LandAnimal)+:176(AICreature) 三级基类——公共组件上提、特异性下放的样板 〔22〕 |
| 数据 | 加一种方块的数据表行 | `BlocksData.txt:6`（DirtBlock 行，含 # 自引用掉落；78 具名列、可只写覆盖列，见 [数据格式参考](数据格式参考.md)） 〔22〕 |
| 数据 | 加合成配方（数据表） | `CraftingRecipes.xml:64-139`（Materials 节；`a="seeds:5"` 数量、`DoughBlock:0` 数据后缀、Remains=EmptyBucketBlock 返桶样例 :69） 〔22〕 |
| 数据 | 加防具（数据表） | `Clothes.xml:2-47`（43 条 ClothingData；Slot/Insulation/Layer 全属性面） 〔22〕 |
| 数据 | 合并原版 Database（mod 侧） | `ModsManager.cs:1083-1152`（.xdb 统一 new-*/Remove 前缀 DSL，不走 Harmony 硬改） 〔12·22〕 |
| 数据 | 动画分层（走/打/骑/死） | `AnimationTemplates\Human.template.json`+`Animations\Human.json`（layer blendMode+boneMask+驱动器参数三级结构） 〔22〕 |
| 数据 | 世界恢复存根 | `RecoveryProject.xml` 全文（最小 Project.xml 只带必要 Subsystem 值） 〔22〕 |
| 数据 | 修 UI 图集 | `Atlases/Atlas.txt`+`TextureAtlasManager.cs:13-22`（纯文本子纹理表+运行期 GetSubtexture 回退） 〔22〕 |
| 方块 | 发光方块（三种姿势） | `Block.DefaultEmittedLightAmount`(:83) 或 override `GetEmittedLightAmount`(:508)；仿 `CampfireBlock.cs:146-152`（min(8+data/2,15)，字段>0 是闸门） 〔04·14〕 |
| 方块 | 零代码常亮灯 | `WickerLampBlock.cs`(15 行全文件)+`BlocksData.txt` 对应行——光 15 全靠数据表，代码只有纹理 〔14〕 |
| 方块 | 开关型装饰灯（通电亮+无影） | `ChristmasTreeBlock.cs:202-223`（bit0 开关，亮时 GetShadowStrength=-99 :209-214，顶面电输入 :228-240） 〔14〕 |
| 端到端 | 加一种可烹饪的食物 | [Mod示例-自定义食物](Mod示例-自定义食物.md)（dll 注册 FoodBlock 子类+csv 营养值+.cr 炉烤配方；营养值是 0~1 小数） 〔22〕 |

## 十、拦截与钩子（ModAPI 接入）

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| ModAPI | 注册钩子标准写法 | `SurvivalCraftModLoader.cs:15-26`（__ModInitialize 注册块，9 条 RegisterHook 一行一个，勿晚注册） 〔12〕 |
| 方块 | 拦截所有方块变更 | `SubsystemTerrain.ChangeCell:355`（总闸+TerrainChangeCell 钩子）；邻居通知延后到 `ProcessModifiedCells:66`——OnBlockAdded 里读邻居是"未通知态" 〔02·04〕 |
| ModAPI | 加按键兼容组 | `SurvivalCraftModLoader.cs:28-39`（同组键位不显示冲突） 〔12〕 |
| ModAPI | 拦截自己的资源枚举 | `ModEntity.cs:98-121`（GetFiles 先问 Loader.GetModFiles 再走 zip） 〔12〕 |
| ModAPI | 声明依赖版本范围 | `ModsManager.cs:1214-1289`（=/>/>=/</<=/^/~ 全语法） 〔12〕 |
| ModAPI | 声明模组设置页面 | `ModSettingsParser.cs:23-53`（树形 JSON 形状、Id 禁 /、类型全限定名；读值 ModSettingsManager.cs:235-263） 〔12〕 |
| ModAPI | 多语言包结构与回退 | `ModEntity.cs:167-186`+`LanguageControl.cs:266-282`（en-US 基表+语言覆盖表+英文回退） 〔12〕 |
| ModAPI | 后台任务+帧泵收尾 | `CommunityFramePump.cs:12-31`（Window.Frame 挂载+每轮 try/catch 防崩进程） 〔02·12〕 |
| ModAPI | 挡截渲染全局参数（官方预留 HookAction） | RecalculateCameraProjection(BasePerspectiveCamera.cs:233-239)、ViewFogColor(SubsystemSky.cs:376-382)、ChangeSkyColor(:983-989)、SetRainAndSnowColor(SubsystemWeather.cs:181-187)、SetShaderParameter(TerrainRenderer.cs:143-149)——参数改写不碰反射/注入 〔06〕 |

## 十一、存档与数据（序列化）

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 存档 | 自定义类型直接进存档 | `Game\FloatCurve.cs:6-13`（struct 内嵌套 `[HumanReadableConverter]`，一个文件搞定注册+字符串格式） 〔11〕 |
| 存档 | 实体引用类型转字符串（跨重载存活） | `EntityReferenceHumanReadableConverter.cs:4-9`（外部类注册，双向各一行） 〔11〕 |
| 存档 | 复杂对象↔字符串（含解析逻辑） | `EntitySystem\TemplatesDatabase\ProceduralValueStringConverter.cs:5-14` 〔11〕 |
| 存档 | 值列表打包进一个键 | `ComponentClothing.cs:290/:299`（ValuesListToString/FromString(';') 官方惯用法） 〔11〕 |
| 存档 | 自定义分号分段协议串（混合类型） | `MovingBlock.cs:89`（拼，含 ConvertToString(Vector3)）+:71-72（拆，ConvertFromString\<Vector3\>/\<Point3\>） 〔11〕 |
| 存档 | 批量 Color 解析+空串回退默认 | `WorldPalette.cs:43`（读）+:69（写，默认色写空串） 〔11〕 |
| 存档 | 存档版本迁移转换器 | `VersionConverter21To22.cs:6-30`（SourceVersion/TargetVersion+按键定位改值；注册链 VersionsManager.cs:76-93；Version 更新放最后防中间态） 〔11〕 |
| 存档 | 手写 XML 读写（与存档同 API） | `EntitySystem\XmlUtilities\XmlUtils.cs:37-46`（Set 走 HRC）+:19-30（Get+默认值）+:84-90（缩进 UTF-8 写盘） 〔11〕 |
| 存档 | 代码生成一份新存档文件 | `WorldsManager.cs:79-93`（RecoveryProject 模板+ConvertToString 填占位+SaveXmlToStream） 〔11〕 |
| 存档 | 往存档写自定义数据 | 重写 Subsystem.Save/Load；**Count>0 才落盘**，读端必须给默认值；类型硬拆箱规则见 [11页](01-引擎/11-存档持久化.md) 〔02·11〕 |
| 存档 | 卸载实体随区块重放 | `SubsystemSpawn.cs:338`(SpawnsData 紧凑字符串)/:174(重放)；区域计数防循环 `SubsystemCreatureSpawn.cs:1311` 〔02〕 |
| 存档 | 区块压缩存档格式 | TerrainSerializer23 `CompressChunkData/DecompressChunkData`(:652-724)：shaft 字节+light 位藏游程+Deflate 〔05〕 |

## 十二、媒体与动画（含 VR 后端）

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 媒体 | 加载任意格式图片并读像素 | `Engine.Media\Image.cs:144` Load（ImageSharp 嗅探一行加载）+:44-61 Pixels 惰性缓存 〔19〕 |
| 媒体 | 保存 PNG/BMP/WEBP 等 9 格式 | `Engine.Media\Image.cs:152-250` Save（每格式 encoder 参数现成，saveAlpha 控 RGBA/RGB） 〔19〕 |
| 媒体 | 手写 WAV 读写/RIFF 解析 | `Engine.Media\Wav.cs:152` Load、:164 Save、:195 ReadHeaders（未知 chunk 跳过模板） 〔19〕 |
| 媒体 | 流格式嗅探且不消耗流 | `Engine.Media\SoundData.cs:94-98`+`PeekStream.cs:31`（预读 64 字节） 〔19〕 |
| 媒体 | 生成 mipmap 链（box filter） | `Engine.Media\LegacyImage.cs:52-153` GenerateMipmaps 〔19〕 |
| 媒体 | .dae 双向导入导出+顶点去重 | `Engine.Media\Collada.cs:869/876/897`（Load/Save/IndexVertices） 〔19〕 |
| 媒体 | 位图字体自动切格+自动字距 | `Engine.Media\BitmapFont.cs:372-493`（洋红分格→裁剪→深度图 kerning） 〔19〕 |
| 媒体 | 矢量字体链+缺字回退绘制 | `Engine.Media\Fonts\VectorFont.cs:284-360`（run 切分：矢量段/位图段统一 sink） 〔19〕 |
| 动画 | glTF→自有模型结构全流程 | `Engine.Media\GltfLoader.cs:46-103`（外部资源回调+五步转换+Skip 校验） 〔19〕 |
| 动画 | 缺切线网格生成切线 | `GltfMeshConverter.cs:519-594`（w 取反对齐引擎着色器） 〔19〕 |
| 动画 | JSON 状态机动画控制器 | `Engine.Animation\AnimationConfigLoader.cs:334-426` CreateController（模板/内联双路径+校验器） 〔19〕 |
| 动画 | 1D/2D 混合空间（走跑快慢） | `Engine.Animation\BlendSpaceSource.cs:299/:334`（预分配缓冲零每帧 GC） 〔19〕 |
| 动画 | 两骨 IK 解析解 | `Engine.Animation\IK\Algorithms\TwoBoneIK.cs:12-132`（余弦定理+Hint+限位+Aim） 〔19〕 |
| 动画 | 根运动冲量（跳跃/挥击） | `Engine.Animation\AnimationController.cs:474-499`（三种测速法+父链旋转变换） 〔19〕 |
| VR | OpenXR 实例→会话→动作全启动链 | `Engine\VR\OpenXrVrBackend.cs:184-426`（软降级+双轨 init+session/swapchain/actions 全序，照抄即完整后端） 〔19〕 |
| VR | 全主流头显手柄绑定表 | `OpenXrVrBackend.cs:688-945` SuggestBindings（9 profile 现成，Quest/Vive/Index/WMR/PICO） 〔19〕 |
| VR | OpenXR 双眼帧循环 | `OpenXrVrBackend.cs:1027/1088/1135` BeginFrame/GetEyeFrame/EndFrame 〔19〕 |
| VR | recenter Y 漂移补偿 | `OpenXrVrBackend.cs:1471-1480`+`1239-1257`（事件快照+次帧差分累积模式） 〔19〕 |
| VR | 双眼 FBO 复用渲染 | `OpenXrVrBackend.cs:554-575`+`1100-1104`（每眼一 FBO、acquire 后重挂颜色附件） 〔19〕 |
| VR | 非对称 FOV 投影 | `OpenXrVrBackend.cs:1570-1592`（tangent 差值+GL clipZ[-1,1]） 〔19〕 |

## 十三、内容与资源管理

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 内容 | 注册新资产类型读取器 | `IContentReader\JsonReader.cs:20-28`(单文件最简)+注册点 `Managers\ContentManager.cs:201-203`——契约仅 3 成员，键=目标类型全名 〔20〕 |
| 内容 | mod 包内附带自定义数据文件 | `ModEntity.cs:162`(GetAssetsFile)+`ModsManager.cs:216-217`(GetInPakOrStorageFile)——Assets/ 前缀已在装载期剥掉 〔20〕 |
| 内容 | 多格式纹理自动回退（astc 优先） | `IContentReader\Texture2DReader.cs:5-19`（DefaultSuffix 顺序+astc 分支+特例固定 mipmap） 〔20〕 |
| 内容 | 双文件成对资产（vsh+psh） | `IContentReader\ShaderReader.cs:4-16`（contents[0]/[1] 配对+按文件名加宏） 〔20〕 |
| 内容 | 导入一类外部内容（校验+落盘+重名） | `CharacterSkinsManager.cs:109-123,225-235`（VerifyExternalContentName→Validate→Position=0→CopyTo 标准序） 〔20〕 |
| 内容 | 自定义包格式（单条目 zip+白名单） | `FurniturePacksManager.cs:64-78`(Create)+:109-124(Load 白名单校验)——最小可靠容器范例 〔20〕 |
| 内容 | 覆盖导入带回滚 | `ExternalContentManager.Import.cs:95-119`（TransactionalFileReplacement 同款备份-还原+不可 seek 流缓冲） 〔20〕 |
| 内容 | 归档格式失效的类型化错误 | `ScmodArchiveReader.cs:10-36`（枚举 Kind+本地化消息，替代字符串嗅探分类） 〔20〕 |
| 内容 | 后台线程枚举主线程列表 | `ExternalContentManager.Analyze.cs:138-154`（先 Dispatcher(waitUntilCompleted) 封送，竞态先例注释在此） 〔20〕 |
| 内容 | 静态配置类反射存取 XML | `SettingsManager.cs:1039-1094`(Load)+:1096-1147(Save)（属性即配置的最少代码） 〔20〕 |
| 内容 | 资源打包进世界文件（嵌入外部内容） | `WorldsManager.cs:404-439`(嵌入)+:453-461(还原)（EmbeddedContent 子目录约定） 〔20〕 |

## 十四、物理与弹道

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 物理 | 自定义弹道 | `Projectile.cs:190`(Raycast)/:300(HitBody)/:525(UpdateMovement)——独立体系不走 ComponentBody 〔13〕 |
| 物理 | 实体间挤压/击退 | `ComponentBody.cs:854-945`（HandleAxisCollision）+`InelasticCollision:1288`（非弹性碰撞系数） 〔13〕 |
| 物理 | 空间查询/射线 | `SubsystemBodies.cs:18`(FindBodiesAroundPoint)/:52(Raycast)+`BodyRaycastResult` 〔13〕 |
| 物理 | 爆炸 | `SubsystemExplosions`（压力/破坏/点燃链，见 [13页](01-引擎/13-物理与碰撞.md)） 〔13〕 |
| 物理 | 发射一颗弹道（发射器全流程） | `ComponentDispenser.cs:91-118`（CanFireProjectile 测遮挡出炮口→CreateProjectile 初速 39~41+扰动→OnDispenseShoot 钩子→FireProjectileFast） 〔13〕 |
| 物理 | 触发一次爆炸（起爆方块/纯冲击波） | `DetonatorElectricElement.cs:5-16`（TryExplodeBlock 一行起爆）+`SubsystemSky.cs:258-260`（AddExplosion 末参静音的无声波） 〔13〕 |
| 物理 | 主动击退/后坐力（施加冲量） | `Attackment.cs:193-198`（命中向+抖动+0.2 上抬配方，ImpulseFactor≤0 早退）+`SubsystemMusketBlockBehavior.cs:199`（-4×射向后坐） 〔13〕 |
| 物理 | 自定义实体碰撞箱（大小） | `ComponentBody.cs:370`（BoxSize 是模板参数，全仓无 ComponentBody 子类）+`Content\Assets\Database.xml:104`（牛 1.3,1.4,1.3）；蹲伏缩半 StanceBoxSize :122 〔13〕 |

## 十五、平台工具与排查（Engine 核心 + 浏览器）

| 域 | 我要做… | 照抄哪里（+为什么抄它） |
|---|---|---|
| 引擎 | 跨线程把结果交回主线程 | `Engine\Engine\Dispatcher.cs:38-64` Dispatch（后台线程算完 `Dispatch(()=>…)`，帧头自动执行，唯一正道） 〔21〕 |
| 引擎 | 安全写档（防写一半坏档） | `Engine\Engine\Storage.cs:204-245` MoveFileSafely（备份-替换-回滚三段式；JsonFileStore 即抄它） 〔21〕 |
| 引擎 | 玩家输入转文件名/目录名 | `Storage.cs:613-637` SanitizeFileNameSegment（保留名/超长/代理项全处理，原版三处直接调用） 〔21〕 |
| 引擎 | 跨平台读写用户数据文件 | `Storage.cs:324-341` WriteAllText/ReadAllBytes（统一 `data:` 前缀虚拟路径） 〔21〕 |
| 引擎 | 保存文件到用户磁盘（浏览器） | `Storage.cs:690-695`（ShowSaveFilePicker→句柄→字节写入三步式） 〔21·23〕 |
| 引擎 | 射线选方块/拾取 | `Engine\Engine\Ray3.cs:20-90` Intersection(BoundingBox)（slab 法带盒内提前返回） 〔21〕 |
| 引擎 | 视锥剔除 | `Engine\Engine\BoundingFrustum.cs:25-58,123-137`（矩阵→6 平面→正负顶点判定） 〔21〕 |
| 引擎 | 均匀随机方向/正态分布 | `Engine\Engine\Random.cs:61-115` NormalFloat/Vector2()/Vector3()（粒子与生物游走都用它） 〔21〕 |
| 引擎 | SIMD 批量变换 | `Engine\Engine\Vector3.cs:257-280`（全仓唯一带崩溃实证注释的范本；外门必须 AdvSimd\|\|Sse） 〔21〕 |
| 引擎 | 平滑插值/缓动 | `Engine\Engine\MathUtils.cs:213-218` Lerp/SmoothStep（UI 动画与相机过渡的标准件） 〔21〕 |
| 引擎 | 自定义日志落盘 | `Engine\Engine\StreamLogSink.cs:7-28`（实现 ILogSink 30 行完事，挂 `Log.AddLogSink`） 〔21〕 |
| 引擎 | 每 N 秒做一次/延 N 帧执行（墙钟） | `Engine\Engine\Time.cs:63-67`（PeriodicEvent，用法 `ComponentOnFire.cs:68`）+:73-75（QueueFrameIndexDelayedExecution，用法 `Window.cs:778`） 〔01〕 |
| 引擎 | 平台入口差异（Win/Android/iOS） | [01页](01-引擎/01-程序入口与主循环.md)"平台入口与启动差异"节（三形态入口+帧链收口 Program.FrameHandler） 〔01〕 |
| 浏览器 | 高频数据 JS→C# 零拷贝传输 | `Engine.Browser\InputBridge.cs:12-36`+`main.js:115-159`（共享内存双缓冲+Atomics 原子翻转协议） 〔23〕 |
| 浏览器 | 新增一种输入事件类型 | `InputEventType.cs:2-27`+`InputBridge.cs:83-110`+`main.js:121-139`（三处镜像逐字段同步） 〔23〕 |
| 浏览器 | 大文件流式下载进 WASM | `Survivalcraft.Browser\ContentFileBridge.cs:8-18`+`main.js:34-56`（共享内存+就绪头+忙等接收端） 〔23〕 |
| 浏览器 | 防 AOT/裁剪误删 delegate | `Engine.Browser\TrampolineFuncs.cs:8-11`（DynamicDependency 锚定+UnmanagedFunctionPointer 范式） 〔23〕 |
| 浏览器 | 浏览器宿主能力（文件选择器/全屏/下载） | `Engine.Browser\BrowserInterop.cs:49-56`+`main.js`（JSImport/JSExport 低频互操作契约） 〔23〕 |
| 浏览器 | P/Invoke 到自编译的 C 函数 | `Survivalcraft.Browser\Native\wasmfsHelper.c:7-16`+`Storage.cs:854-858`（NativeFileReference+同名 DllImport 一对一） 〔23〕 |
| 浏览器 | WASM 下建 OpenAL 上下文 | `Engine.Browser\ALContext.cs:6-26`+`Mixer.cs:34-35`（与桌面 Silk.NET 共存的条件别名写法） 〔23〕 |
| 浏览器 | 枚举浏览器系统字体 | `FontLocator.Browser.cs:94-163`（权限手势/缓存/去重的防御性消费） 〔23〕 |

## 回填规则

- 每完成一个深读批次 → 新范例先进本页对应大类对应域（一行一条，附〔NN〕页锚），最高频的再提炼进 [Mod开发配方.md](Mod开发配方.md) 精选表。
- 跨页重复条目合并为一行，页锚并列（如〔04·15〕）；行号必须实读。
- 超过 350 行时拆 `Mod开发配方3.md`（当前 15 类未超）。
