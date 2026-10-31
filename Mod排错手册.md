# Mod 排错手册（按症状查 · 前半）

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 汇编自 01-引擎 23 个主线页"坑与对策"+明细页坑列，按症状重组去重（共 250 条，本文件 1-4 类 127 条）· 后半: [Mod排错手册2.md](Mod排错手册2.md)（渲染/音频/UI/电力/世界/数值）

## 怎么用

AI 视角：先按自己观察到的现象对号入座找大类 → 逐行比对"症状"列 → 按对策处理；详址含 file:line 的直接开源码核对。详址约定：`N页` = `E:\数据\生存战争系列\SC完全学习笔记\01-引擎\N-主题.md`；源码行号省略根前缀 `E:\SurvivalcraftAPIProject\`。

## 一、加载失败类（mod 没装上 / 资源读不到 / 加载中断）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 一闪 "Loading failed" 后只剩原版内容 | 某模组 `__ModInitialize` 抛异常，HandleAssembly 失败后连坐踢掉全部非原版模组 | 日志搜 `Handle assembly failed` 定位 mod；__ModInitialize 全程 try/catch | 12页 · ModEntity.cs:406-442 |
| 日志出现 `NoModInfo`，mod 完全不加载 | zip 根无 modinfo.json，或解析失败（Name 非字符串会整份失败） | 补 modinfo.json；字段类型照 modinfo 字段表 | 12页 · ModsManager.cs:219-354 |
| 日志出现 `InvalidPackageName`，mod 完全不加载 | PackageName 空/含 `;`、`\n`/是保留字 survivalcraft、fastdebug | 包名改唯一且非保留字 | 12页 · ModsManager.cs:260-263 |
| 模组管理页标 `Duplicated` 被禁用 | 同包名同相态两实体互标；zip 内条目重名整包失败 | 升级走 ModUpdateImporter 或先删旧版；禁用记录按"包名+版本"精确匹配（大小写敏感） | 12页 · ModEntity.cs:255-268 |
| 日志出现 `DependencyError`（`is dependent on ... which is not allowed`） | 依赖缺失，或 A↔B 成环（环=双双禁用） | 补装依赖；解开环 | 12页 · ModEntity.cs:486-492 |
| dll 明明在包里，代码就是不跑 | dll 在 Assets/ 下（永不加载）/撞黑名单名（Survivalcraft、Engine、EntitySystem.dll）/后缀大写 .DLL/0 字节条目当不存在 | dll 放 zip 根、扩展名全小写、非 0 字节；日志确认有 `Handling assembly` | 12页 · ModEntity.cs:383-404 |
| 加了类但引擎没发现（Loader/Block/Reader/CreatureType 全没生效） | 发现判据=四类子类+public 无参构造；Block 缺 `public static int Index` 字段直接抛 | 补 public 无参构造；Index 用普通静态字段（const 会被跳过） | 12页 · ModEntity.cs:406-442；04页 · BlocksManager.cs:108-119 |
| 资源读取抛 `Not Found Res [X][T]` | 键大小写不符/没带对后缀（Get 按 DefaultSuffix 探测先到先得）/文件不在 Assets/ 下 | 核对键=Assets/ 剥前缀后路径；成对资产（vsh+psh、lst+png）必须全在 | 20页 · ContentManager.cs:76-129 |
| 整份 csv/方块表后半段失效或装载直接 throw | 行字段数≠表头列数抛异常（已应用行保留）；csv 写 `New-`/`Remove` 列被当陌生字段抛 | 每行列数严格对齐；csv 没有指令层，删改用 .xdb 的 new-*/Remove 协议 | 04页 · BlocksManager.cs:1047-1075 |
| 方块进世界了但属性全默认 | csv 第 1 列类名拼错，只有一行 Log.Warning 跳整行 | 验收先搜日志 Warning | 04页 · BlocksManager.cs:1056-1059 |
| 配方/掉落解析抛异常 | csv `#类名` 引用不存在的方块抛异常 | 核对类名；动态模组方块编号随存档变，代码里用 `GetBlockIndex<T>()` | 04页 · BlocksManager.cs:1078-1085 |
| 进世界失败，日志 `Error creating entity from template "X"` | 模板组件实例化抛（典型：缺 public 无参构造） | 看 inner exception；组件类补 public 无参构造 | 03页 · Project.cs:238-243 |
| 进世界失败，日志 `Error loading component 类全名.` | 组件 Load 抛异常（多为值类型硬拆箱/键缺失） | 看 inner exception 定位组件 Load | 03页 · Entity.cs:211-213 |
| 日志 `Type "X" not found in any loaded assembly.`，世界进不去 | 组件/模板 Class 解析不到且 IsOptional=false | 排错先去掉 IsOptional 让它显式抛；确认程序集已加载 | 03页 · TypeCache.cs:102-105 |
| 新加组件在实体上静默消失 | IsOptional=true 时 Class 解析不到被静默跳过 | 临时去掉 IsOptional 复现 | 03页 · Entity.cs:103 |
| 进世界失败弹 `Loading World Failed!` | 组件/子系统 Load 异常漏到 Project 构造外 | 日志搜 Error loading component / Required value | 03页 · Project.cs:93-107 |
| .json 方块模型加载直接抛"JsonModel功能暂时下线" | JsonModelReader.Load 已被下线 | 模型改用 .obj/.gltf | 12页 · JsonModelReader.cs:98 |
| .obj 模型解析失败"模型必须为三角面" | 非三角面，或 vt/vn 索引缺一 | 导出前三角化；vt/vn 成套 | 12页 · ObjModelReader.cs:141-143 |
| .xdb 合并后整个数据库加载失败 | 新节点 Guid 与已有重复 | 每个新 DatabaseObject 用新随机 Guid；定位原版节点才用原版 Guid | 02页 · ModsManager.cs:1083-1152 |
| 改/删 Database.xml 模板后子模板展开失败 | InheritanceParent 是 GUID 硬引用，删父断链 | 删改前先 grep GUID 找全部子模板 | 22页 · DatabaseObject.cs:195 |
| 皮肤/方块纹理包导入抛异常 | 图非 2 的幂或超 65536² | 导入前照 ValidateCharacterSkin/ValidateBlocksTexture 预校验 | 20页 · CharacterSkinsManager.cs:225-235 |
| 双击导入 mod 抛 FileAlreadyExistsException | 同名文件已存在，ImportMod 不覆盖 | 删旧文件或走 ModUpdateImporter 更新流程 | 12页 · ModsManager.cs:446-466 |
| 普通工具打不开 scmod / 解析抛 InvalidScmodArchiveException | 包带弱加密前缀或杂质字节（加固包=倒序/交织） | 引擎侧走 ScmodArchiveReader.OpenArchive（自动解密+截前缀）；工具打不开不等于坏包 | 20页 · ScmodArchiveReader.cs:57-92 |
| 模组键位/手柄映射只注册了一半 | 两个 Loader 返回同名键，ValuesDictionary.Add 抛，后半全丢 | 映射名加模组前缀 | 10页 · ModSettingsManager.cs:119 |
| 浏览器版启动黑屏，报 SharedArrayBuffer 缺失 | 自建托管没配 COOP+COEP 响应头，或 service-worker 旧缓存 | 复刻 wwwroot/_headers 两条响应头；改静态资产同步改 CACHE_NAME 版本戳 | 23页 · main.js:2-6 |
| 浏览器版 Content.zip 读到截断/多余流 | 只换 zip 没重编壳，FileSize 是编译期常量失配 | 重跑 UpdateContentFileSize（BeforeBuild 自动；手动拷贝发布会踩） | 23页 · ContentFileBridge.cs:8-18 |
| 浏览器版 mod 运行期崩（Harmony/Jint 缺失） | BROWSER 构建移除了 HarmonyX 与 Jint | 依赖运行时注入/JS 求值的特性必须 `#if !BROWSER` 隔离 | 12页 · Survivalcraft.Browser.csproj:13-14 |
| 世界加载卡进度后弹"无法保存"或版本错误 `Cannot find conversion path...` | 存档版本超出转换链范围（转换器只认游戏程序集内的） | 老档先在兼容版本里升档；模组兼容逻辑写在组件 Load 里 | 11页 · VersionsManager.cs:132-159 |

## 二、写了不生效类（代码/数据写了，现象没出现）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 钩子方法重写了但一次都不跑 | 错过注册窗口（启动第 5~10 步之间必须 RegisterHook）/钩子名字符串打错/该钩子本来不走钩子表（OnLoadingFinished、LoadSettings、GetKeyboardMappings 等直调） | __ModInitialize 里打日志确认；全仓 grep `HookAction("名字"` 验证派发点存在 | 12页 · ModsManager.cs:182-214 |
| 钩子跑了一次后永远不跑 | 钩子异常每 (钩子,Loader) 组合只 Log.Error 第一次，之后静默跳过 | 第一次调用就自包 try/catch；搜日志第一次的 Error | 12页 · ModsManager.cs:156-173 |
| 自己的钩子把别人的钩子拦了（或被拦） | HookAction 的 lambda return true 就地截断后续钩子 | 不拦截就返回 false | 12页 · ModsManager.cs:182-203 |
| modinfo 的 LoadOrder/NonPersistentMod/GameplayImpactLevel 没生效 | 类型陷阱：LoadOrder 必须 JSON 数字（字符串退 0，超 int32 整份失败）；NonPersistentMod 必须字面量 true；GameplayImpactLevel 大小写敏感；未知键无告警 | 按类型字面量写；对照 12 页 13 键表 | 12页 · ModsManager.cs:333-354 |
| 模组设置面板是空的 | modinfo 的 Settings 写成对象而非数组；或设置 Type 解析失败（简单名只补 `Game.` 前缀） | Settings 用数组；模组自定义类型写全限定名 | 12页 · ModSettingsParser.cs:93-102 |
| 自定义 IUpdateable.Update 逻辑没跑且无报错 | 更新异常被 SubsystemUpdate 整体 catch 静默吞掉 | 自己 try/catch+Log.Warning 自证 | 02页 · SubsystemUpdate.cs:97-99 |
| 子系统 Load 里查别的子系统拿到未初始化对象 | 加载顺序=XML 文档序+Dependencies；Load 时对方可能"已构造未 Load" | 依赖名写进 MemberSubsystemTemplate 的 Dependencies | 02页 · Project.cs:358-386 |
| mod 组件总排在全部原版组件之后 | namespace≠"Game" 的组件 LoadOrder 被强制 +10000 | 想插队用 EntityComponentsInitialized 静态事件；或写进 namespace Game | 03页 · Entity.cs:122-125 |
| ReplaceComponent 调了没效果 | 全仓空操作，不碰组件表 | 用 NoEffect 组件/同名遮蔽/EntityComponentsInitialized 换实现 | 03页 · Entity.cs:177-181 |
| 在 Initialize 里互查其他组件拿到 null | Initialize 逐个调，其余组件还没实例化 | 互查放 Load | 03页 · Entity.cs:121 |
| 地形生成步骤没跑/跑了没日志 | 步骤异常全静默（每步骤对象只报一次）；钩子挂晚了（OnProjectLoaded 后 Add 不参与 Sort） | 步骤委托内自包 try/catch+计数日志；挂 TerrainContentsGenerator24Initialize，挂晚了自己 Sort | 05页 · TCG24:2423/:352-362 |
| 地形钩子在某个世界不触发 | 生成器按 OriginalSerializationVersion 选型；老存档/平面世界没有步骤列表 | 测试地形模组新建 2.4 常规世界 | 05页 · SubsystemTerrain.cs:551-584 |
| TGWater=false 想关海洋没效果 | 死字段，只声明无读取点 | 无对策，海洋照生成 | 05页坑表 |
| override 了 GetEmittedLightAmount 方块还是不发光 | 收集闸门先看 DefaultEmittedLightAmount>0 才调 override；emitted=1 只亮自身格不进传播 | 字段给 >0 闸门值；要扩散给 >1 | 14页 · TerrainUpdater.cs:900-906 |
| 方块 DefaultIsUseable=FALSE 不生效 | 挂了 OnUse 行为的方块加载时被强制回 true | 代码侧覆写 IsUseable_ 而不是靠数据 | 04页 · SubsystemBlockBehaviors.cs:39-46 |
| 方块 Initialize 抛异常但游戏没崩、分类缺失 | 异常被吞成一条 LoadingScreen.Warning，后续 GetCreativeValues 不执行 | 搜日志 Warning；修掉异常 | 04页 · BlocksManager.cs:414-418 |
| 冬天雷暴玩法永不触发 | 冬季雷电系数=0 必不打雷 | 自己驱动视觉/事件（ManualLightningStrike 等手动入口） | 14页 · SubsystemWeather.cs:305-309 |
| Harmony patch 装了但没效果，API 升级后失效 | 游戏本体零 Harmony 调用；目标方法改签名后补丁不命中且无日志；Unpatch 语义难删 | 每次 API 升级重验 patch 目标；__ModInitialize 里 try/catch+日志；补丁内自判重（Reboot 后旧补丁仍在） | 12页HarmonyX节 |
| Harmony override CalculateGameTimeDelta 签名不匹配 | 方法名拼写就是 Dalta（CalculateGameTimeDalta） | 照抄拼写 | 14页 · SubsystemTime.cs:62 |
| Reboot/重载后改的 dll 行为没变化 | 程序集不可卸载、TypeCache 缓存不清 | 验证新代码必须重启进程 | 11页/12页 |
| UpdateInput 钩子不跑 | 没 `RegisterHook("UpdateInput", this)`；异常只报第一次 | 注册+自包 try/catch | 10页 · ComponentInput.cs:234-240 |
| 改 FOV/近远平面不生效 | 投影在 CalculateBaseProjectionMatrix，反射硬改会被覆盖 | 走 RecalculateCameraProjection 钩子改 ref result | 10页 · BasePerspectiveCamera.cs:222-241 |
| 注册的 Screen 后来消失 | LoadingScreen.Enter 清掉字典里除自己外的全部 Screen 再重跑 | 注册动作放进 OnLoadingFinished 的 actions | 09页 · LoadingScreen.cs:673-685 |
| 界面控件 XML 属性拼错，静默用默认值 | LoadProperties 对未知属性名只 Log.Warning 后跳过 | 照日志 `Property not found` 查属性归属 | 09页 · Widget.cs:558-562 |
| Style= 之前的同名属性被覆盖 | Style setter 就是 LoadContents，样式覆盖内联属性 | 要生效的属性写在 Style 之后 | 09页 · Widget.cs:464-466 |
| RichTextWidget 就地改 Spans 不刷新 | 列表引用没变引擎不感知 | 手动 MarkLayoutDirty() | 09页 · RichTextWidget.cs:56-58 |
| TreeView 增删节点不显示 | 行重建脏标记在 Draw 期消费，节点增删不自动置脏 | 手动 m_widgetsDirty=true | 09页 · TreeViewWidget.cs:48-54 |
| 合成配方匹配失败但代码判 null 没拦住 | FindMatchingRecipe 失败返回只带 Message 的假配方而非 null | 判 ResultValue 而非只判 null | 16页 · CraftingRecipesManager.cs:158-168 |
| 自己注册的配方静默消失 | 配方装载整段 try/catch，成分写错只有 Log.Error | 搜日志 Error；成分用 CraftingId 小写名 | 22页 · CraftingRecipesManager.cs:59 |
| 直接改 Database.xml（游戏本体）不生效 | 启动一次性装载，运行期不读盘 | 重开进程；运行期改走 ApplyOverrides | 22页 · LoadingScreen.cs:521 |
| 存档 XML 值解析不报错但数据不对 | XmlUtils.GetAttributeValue 捕获一切异常静默返默认值 | 核对 Value 串与 Type 的大小写/格式 | 11页 · XmlUtils.cs:22-27 |
| 存档 XML 里自己的类型值无声消失 | Type 解析不到静默 continue；模组自定义类型必须写全名 | `Type="Game.我的类"` 全名；值类型挂 HRC 转换器 | 11页 · ValuesDictionary.cs:161-164 |
| 自定义 HumanReadableConverter 注册不上 | 扫描先到先得，与已有同名类型冲突取决于程序集加载顺序 | 类型名避开冲突；不要依赖覆盖 | 11页 · HumanReadableConverter.cs:118-140 |
| 自己的粒子系统加进去没显示也不报错 | 实例已被持有（复用同一对象），AddParticleSystem 静默什么都不做 | 传 throwOnAlreadyAdded:true 或先 ContainsParticleSystem | 07页 · SubsystemParticles.cs:42-45 |
| 远处破坏方块没有碎屑 | 16 格距离门控 + DestructionDebrisScale=0 | 就近生成或调 scale | 07页 · SubsystemTerrain.cs:460-467 |
| 常驻池粒子偶尔不出现 | 池满静默丢（RainSplash/SnowSplash/Explosion 找不到空位直接放弃） | 容量给够或自行排队 | 07页坑表 |
| ParticleSystemsSimulate=false 当"关粒子"用没关掉 | 它只冻结 Simulate，Draw 照跑且系统永不移除 | 真关用 ParticleSystemsDraw | 07页坑表 |
| 改 DisabledPhysicalEffects 不彻底生效 | 运动组件每帧重置 IsGravityEnabled 等布尔属性 | 位掩码与布尔属性两个都关 | 13页 · ComponentBody.cs:375-377 |
| IsSpaceFreeToMove 跨格瞬移失败 | 只能同格判定 | 自己分段位移 | 13页 · ComponentBody.cs:673 |
| 给投掷物改 ComponentBody 物理无效 | 弹道不是实体，不走 ComponentBody | 改 Projectile 自己的 Gravity/Damping 字段 | 13页坑表 |
| 生物寻路"完成"但站着不动 | 寻路队列>10 时直接置 IsCompleted+空路径；后台单队列 | 减少并发寻路请求；查队列状态 | 02页 · SubsystemPathfinding.cs:198-222 |
| 浏览器端单帧塞大量输入事件静默丢失 | 事件缓冲 4096 字节溢出直接 return 无上报 | 控制单帧事件量；新事件类型先算字节预算 | 23页 · main.js:128-130 |
| 按扩展名读包内文件读不到（如 .CSV） | GetFiles/GetFile 扩展名比较大小写敏感；0 字节条目当不存在 | 全小写扩展名、非 0 字节 | 12页 · ModEntity.cs:98-121 |
| 代码里判 `.gitignore` 这类点文件扩展名出错 | Storage.GetExtension 把点文件整体当扩展名 | 配对用 GetExtensionBCL/GetFileNameWithoutExtensionBCL | 21页 · Storage.cs:379-398 |
| 模组加 VersionConverter 子类不生效 | 转换器只从游戏程序集反射收集 | 兼容逻辑写在组件 Load 里（按 object 取出再分支转型） | 11页 · VersionsManager.cs:52-67 |

## 三、崩溃与异常类（抛异常 / 闪退 / 静默失败）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 读档崩 `InvalidCastException: Unable to cast Single to Int32` | GetValue/TryGetValue 只硬拆箱不做数值转换 | 写读统一类型；修后按 object 读兼容旧档 | 11页 · ValuesDictionary.cs:40/:82-89 |
| 读档崩 `Required value "key" not found` | GetValue 缺键抛；Count=0 的袋子整个不存在 | 用带默认值重载；Load 不假设袋子存在 | 11页 · ValuesDictionary.cs:38-43 |
| 进世界后随机崩，弹日志对话框回主菜单 | Program.Run 顶层 catch：任何更新异常 → 回 MainMenu+弹日志+DisposeProject | 游戏内开 ViewGameLogDialog 看栈；更新逻辑自包 try/catch | 01页 · Program.cs:308-322 |
| 地形/光照/保存钩子里崩（GL 或 FindSubsystem） | OnTerrainContentsGenerated/GenerateChunkLightSources/保存第 4 步起在后台线程 | 只操作 chunk Fast 接口；碰 UI/GL 一律 Dispatcher.Dispatch | 05页/14页/11页 |
| 保存时弹"无法保存"且文件没写 | ProjectXmlSave/OnProjectXmlSaved 钩子抛异常即中止写盘 | 钩子内 try/catch；碰主线程对象用 Dispatch 包裹 | 11页 · GameManager.cs:139-157 |
| Dispatcher 里执行的动作失败但等待方无感知 | action 抛异常只记日志不外抛，waitUntilCompleted 也照样放行 | 需要结果的自己 try/catch 包住并回传状态 | 21页 · Dispatcher.cs:27-29 |
| 清空原版矿笔刷后地图生成静默异常 | 笔刷按整值比较宿主，Int(0,-1) 返 0 → m_coalBrushes[0] 越界，异常被吞全进程只报一次 | 清空同时补自己的笔刷 | 05页 · TerrainBrush.cs:214-236 |
| 自定义区块大数据读取炸 | Region 条目 1MB 上限判损坏 | 大数据别塞进单区块存档 | 05a · TerrainSerializer23.cs:494-496 |
| 存档里有 sbyte 值抛 `IHumanReadableConverter for type System.SByte not found`，char 值空串抛 IndexOutOfRange | sbyte 是唯一没有 HRC 转换器的基元；CharHumanReadableConverter `data[0]` 无保护 | 改用 byte/int；char 写前判空 | 11页坑表 |
| 弹 MessageDialog 直接抛 InvalidOperationException | 两个按钮文本都空（至少一按钮校验） | 至少给一个按钮文本 | 18页 · MessageDialog.cs:42-45 |
| SwitchScreen("名字") 抛 ArgumentNullException | m_screens 注册表查不到（忘了 AddScreen） | mod 自建 Screen 先 AddScreen 再 Switch | 01页 · ScreensManager.cs:62-64 |
| 启动早期调 Dispatcher.Dispatch 抛 InvalidOperationException | Window.Run 之前 Dispatcher 未初始化 | mod 代码只从 __ModInitialize 之后执行 | 01页 · Dispatcher.cs:39-41 |
| 对文字格 Measure(Vector2(0,∞)) 崩游戏（OOM） | 断行零推进死循环（部分路径钳 1 防护，直调不受保护） | 传 ∞ 或钳最小宽 | 09页 · FontTextWidget.cs:748-749 |
| 竖排 UniformSpacingPanel 放进竖排 StackPanel 崩整页 | 主轴 DesiredSize=∞ 污染上层，arrange 算 NaN | 均分行容器一律 Horizontal | 09页 · ModSettingItemWidget.cs:272-274 |
| 切语言后崩/界面行为错乱 | RebuildAllScreens 反射重建全部 Screen：字段状态丢、静态事件未退订 | 自定义 Screen 必须无参构造+可重入；静态事件退订放 override Dispose（Rebuild 不调 Leave） | 17页 · ScreensManager.cs:100-159 |
| 换字体后返回游戏黑屏无输入 | GameScreen 被重建成空壳（世界绑定屏不可重建） | 仿写 Rebuild 时照抄 SettingsFontScreen 的 preserve 谓词 | 17页 · SettingsFontScreen.cs:378-382 |
| Enter 里 Task.Run 回填控件崩 | 跨线程碰控件 | Dispatcher.Dispatch 回主线（PlayScreen.cs:91-115 样板） | 17页坑表 |
| 读 PlayerInput.ValuesDictionaryForMods 抛 NRE | `m_playerInput = default` 绕过 struct 初始化器，每帧变 null | 每帧判空再写 | 10页 · PlayerInput.cs:6/:72 |
| GamePad 访问抛 ArgumentOutOfRange | index 出 0..3、deadZone 不在 [0,1) | 先 IsConnected；deadZone 用 [0,1) | 10页 · GamePad.cs:294-300 |
| 改 RasterizerState 等状态对象抛 "Object was attached to a device" | LockOnFirstUse 首次绑定后锁定不可变 | 自建新状态对象一次赋值到位；别改预设 | 06页 · LockOnFirstUse.cs:2-10 |
| 着色器 Construct 抛 "Attribute has no semantic defined"/"Associated SamplerState is not set" | 缺语义头/Sampler 元数据注释 | 每个顶点属性一行 `<Semantic/>`，每个 sampler 纹理一行 `<Sampler/>`（抄 AlphaTested.vsh:50-52） | 06页 · Shader.cs:310-346 |
| GetParameter 抛 "Parameter not found" | uniform 被 GL 链接器裁掉（声明未用）或名字错 | 用 `GetParameter(name, true)` 拿 Null 参数，或确保 uniform 被读写 | 06页 · Shader.cs:47-50 |
| 抛 "Too many simultaneous textures" | 一个 Shader 的纹理 uniform 超 GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS | 合并纹理图集或减 uniform | 06页 · GLWrapper.cs:910-912 |
| ASTC 纹理调普通 SetData 抛 Invalid | 压缩纹理基类 SetData 全封死 | 读 .astc 头自解析后走专用重载；mip 离线生成 | 06页 · CompressedTexture2D.cs:62-90 |
| 第二次打开同一文件抛 IOException | Storage.OpenFile 恒 FileShare.Read | 长驻写句柄自管生命周期 | 21页 · Storage.cs:156 |
| Android 上相对路径抛异常 | ProcessPath 未知前缀（含无前缀）抛 | 跨平台路径显式 `app:`/`data:` 开头 | 21页 · Storage.cs:445-478 |
| 窗口未开时读写 Window 属性抛 InvalidOperationException | m_view==null 门禁 | 先 Window.IsCreated | 21页 · Window.cs:813-819 |
| Android 上 SIMD 批量变换抛 PlatformNotSupportedException | Vector128.IsHardwareAccelerated 在 MonoVM 恒 true 但会落进 SSE 分支 | 外门用 `AdvSimd.IsSupported || Sse.IsSupported` | 21页 · Vector3.cs:225-228 |
| InventoryBase.AddSlotItems 抛 InvalidOperationException | value 不符/超容都 throw | 批量塞格先查 GetSlotCapacity | 03页 · ComponentInventoryBase.cs:170-180 |
| 生物模板进世界抛 Required component | ComponentCreature 硬依赖六件套（Body/Health/Spawn/CreatureSounds/CreatureModel/Locomotion） | 模板挂全；CreatureModel 必须给具体子类 | 03页 · ComponentCreature.cs:42-47 |
| 建档后改 PlayerClass 抛异常 | PlayerData 已加入 PlayersData 后 setter 抛 | 建档前定好职业 | 16页 · PlayerData.cs:89-97 |
| 切语言后衣物槽 KeyNotFound | ClothingSlot.Initialize 重调，Clear 重建后旧实体引用失效 | 只补缺失部位，不 Clear | 16页 · ClothingSlot.cs:22-30 |
| 后台线程枚举内容列表崩 | 主线程列表 Clear()+Add 竞态 | Dispatcher.Dispatch(waitUntilCompleted:true) 封送 | 20页 · ExternalContentManager.Analyze.cs:138-154 |
| 多线程解析同一资产互相改流位置 | ContentInfo.Duplicate() 不是复制，只复位共享流 Position | 照 ImageReader 的 InUse 自旋+缓存回取模式 | 20页 · ContentManager.cs:35-43 |
| 旧图片工具链抛异常 | LegacyImage.GenerateMipmaps 奇数尺寸 throw；Image.Slice 宽>2×高 throw | mipmap 用 2 的幂；转换前确认尺寸或改像素循环 | 19页 · LegacyImage.cs:66-69、Image.cs:84 |
| ViewWidget 挂到非 GameWidget 父抛 InvalidOperationException | ChangeParent 校验父类型 | 只挂 GameWidget | 09a · ViewWidget.cs:24-32 |
| 含 CFF2 可变字体的环境构建字体链抛 NotSupportedException | EngineSharpAstroSource 不认 CFF2-only 字体 | 匹配期 FontLocator.Probe 拒收；建链侧已有整链降级兜底 | 19页 · EngineSharpAstroLoader.cs:55-58 |

## 四、存档数据类（存不上 / 读不回 / 串数据）

| 症状 | 根因 | 对策 | 详址 |
|---|---|---|---|
| 改了值没存上 | 本次 Save 一个键都没写（Count=0 整个子字典不落盘）；或忘调 base.Save/Load 漏父类字段 | Save 至少写一个键；Load/Save 成对调 base | 11页 · Project.cs:290-292 |
| Save 里读不到上次存档的值 | Save 的参数是新建空袋 | 从 this.ValuesDictionary 读旧值再写新袋 | 11页 · Entity.cs:218-220 |
| 同实体两个同名组件数据互相覆盖 | 存档按组件名写键，同名顶键；同类型多实例也查不出 | 组件名唯一；多实例用带名 FindComponent | 03页 · Entity.cs:222/:171 |
| 删模组后方块变空气/生物消失 | 模板或组件 Class 没了：实体模板找不到整包丢（仅警告 Ignoring invalid entity）；组件按 IsOptional 分崩/静默 | 模板 Guid 永久固定；设计 IsOptional 决定崩档还是静默；Load 带默认值 | 11页 · EntityDataList.cs:20-25 |
| 在 ProjectXmlSave 里加顶层 `<Subsystems>`/`<Entities>` 后数据丢失 | ProjectData.Save 用 FindChildElement 取文档顺序第一个同名节点，引擎那份被无视 | 钩子里只改已有节点/挂到别的子树 | 11页 · ProjectData.cs:56-65 |
| 模组设置换了存档还是旧的 | 所有模组设置合在全局 ModSettings.xml，与存档无关 | 每世界数据走 Subsystem.Save/Load | 11页坑表 |
| 读档后火焰全部重新烧 | 火焰燃烧进度 FireData 纯内存不存档 | 自己在 behavior 里持久化进度 | 02页坑表 |
| 实体卸载再回来自定义数据丢了 | Despawn 打包时不带 mod 数据 | 钩子 OnSaveSpawnData/OnReadSpawnData 读写 SpawnEntityData.Data | 02页 · SubsystemSpawn.cs:242/259 |
| 运行时改世界种子/地形参数没存上 | WorldSettings.Save(liveModifiableParametersOnly:true) 不写种子与地形参数 | 改种子只能走建档路径 | 16页 · WorldSettings.cs:134-163 |
| 覆盖导入世界/内容后档坏了 | 直接覆盖没有回滚 | 用 TransactionalFileReplacement.OverwriteWithRollback（先备份失败还原） | 20页 · ExternalContentManager.Import.cs:95-119 |
| 挂在 SettingsManager 上的临时值被写进 Settings.xml | 保存反射枚举全部 public static 可写属性 | 临时状态别做成它的 public static 可写属性 | 20页 · SettingsManager.cs:1096-1147 |
| 坏档区块"消失"被静默重生成 | LoadChunk 除 IOException 外异常吞掉并当"有档但空"处理 | 数据异常先查 chunk 序列化；重要数据别只存区块 | 05a · TerrainSerializer23.cs:626-630 |
| 手改存档/模板后枚举值不识别、bool 抛 | 枚举 Enum.Parse 大小写敏感；XML 轨 bool 只认 True/False | 照原格式大小写写 | 11页 · EnumHumanReadableConverter.cs:7 |
| 第二次进世界钩子逻辑重复执行 | EntityComponentsInitialized/BeforeSubsystemsAndEntitiesLoad 是静态事件且 Dispose 不清，N 次进世界派发 N 次 | 钩子里按 project/entity 去重或挪去 OnProjectLoaded | 11页/02页 · Project.cs:84-86 |
| 存档坏了打不开 | 引擎三级回滚：Project.xml → Project.bak → 内置 RecoveryProject 现造 | 知道机制即可；自己写档也照 MoveFileSafely 备份-替换-回滚 | 11页 · WorldsManager.cs:65-95 |
| 手改存档 XML string 键字典后对不上 | Archive 轨 string 键经 XmlConvert.EncodeLocalName 变元素名 | 特殊字符键避开或换分号协议串 | 11页 · XmlOutputArchive.cs:117 |
| 想让值跨进程重启还认得出实体 | IdToEntityMap 是空壳且加载路径传 null | 引用实体用 EntityReference（id:/name:，跨重载存活） | 11页 · EntityReference.cs |

（五~十大类与"还查不到？"路由见 [Mod排错手册2.md](Mod排错手册2.md)）
