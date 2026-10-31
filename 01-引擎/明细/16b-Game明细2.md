# Game/Community 明细（72 文件）

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(72/72，全文实读)；主页面另见 16-玩法物品与背包.md，根目录 226 文件另见 16a-Game明细.md。
>
> 前缀：`E:\SurvivalcraftAPIProject\Survivalcraft\Game\Community\`（下表省略）。分层：Domain(纯规则/状态机，26) → Infrastructure(Http/持久化/导入，35) → Models(协议与落盘模型，11)。行号`文件:行`以 2026-10-31 实读为准。

## Domain\Common（2）

| 文件 | 行 | 职责 |
|---|---|---|
| `ExternalVersionParser.cs` | 29 | Normalize 取首个数字起子串剥前缀(8)；TryParse→NuGetVersion(21)；ParseOrNull 供模型 setter"赋值即解析"，失败存 null(28) |
| `WeakEventSource.cs` | 95 | 弱引用事件源防静态事件钉死旧屏幕；多播委托 GetInvocationList 逐项登记/移除(36,57)；静态方法订阅走强引用；Raise 就地剔除死条目(68)；TargetInvocationException 还原原始异常(84) |

## Domain\Community（7，社区帖子/文件规则）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityDownloadFeedbackInfo.cs` | 9 | 纯数据 6 字段：ApiBaseUrl/Token/PostId/FileId/Platform/Version；Token 持久化前被剥离 |
| `CommunityFileRules.cs` | 33 | GetDownloadFileName(5)：filename 先 Unescape 再 Sanitize、非法转义保留原值；URL 尾段解析失败回退 `download_{Id}`(22) |
| `CommunityFilters.cs` | 121 | CommunityFileType 协议枚举(值=API 协议，9/10 均 Modpack，75)；ToExternal/FromExternal 边界互转(47,61)；JSON converter HandleNull=true 防服务端 null(112)；上传仅放行 5 类型否则抛(83)；设置非法归 Mod/Hot(93,98) |
| `CommunityLocalModMatchingRules.cs` | 57 | 文件名归一化=Unescape+取末段+OrdinalIgnoreCase(18)；IsAnyMatchingFile 存在性短路不物化列表(37)；IsModFile(54) 全项目唯一权威实现（Unknown 按版本 FileType 回退） |
| `CommunityModVersionSelector.cs` | 70 | FindBestMatch 只认 Status=1 且 Type="plugin"(15)；四元评分 Exact>兼容线>同主次>patch 距离小者(46,53) |
| `ModpackManifestParser.cs` | 376 | ZIP/JSON 双格式：单条目上限 256MB/累计 512MB(10,13)；packinfo.json 中央目录长度可伪造，解压后复核(114)；嵌入图标探测序 icon.webp>icon.png>大写兜底(18)；ZIP 名编码探测 local header bit11：UTF-8 否则 GBK(936)(298,306)；条目路径 ".." 整体拒绝(346) |
| `PostIconRules.cs` | 45 | 图标优先级 file.Icon>post.Icon>post.Cover(3)；相对路径按 API 基址 scheme+authority 补全(28)；img.suancaixianyu.cn 的 https URL 加缩略图后缀 `!/fwfh/368x238`(35) |

## Domain\LocalResources（10，本地已装 mod 规则）

| 文件 | 行 | 职责 |
|---|---|---|
| `LocalModCollectionRules.cs` | 20 | 待处理按 CreationTime 降序；HasDuplicatePackageName 按 PackageName 归组标记(OrdinalIgnoreCase) |
| `ModCompatibility.cs` | 316 | 四级 Unknown<Incompatible<Risky<Exact（同主次=Exact、主同次差1=Risky，252）；gameVersionIds 目录优先、标题/正文版本搜索兜底(93)；边界正则缓存 ConcurrentDictionary 防 Regex 静态缓存 15 条上限击穿(198)；别名前不邻数字/点防 1.2.1 命中 2.1(204)；DisplayName/CompareText 有意同源勿拆(266) |
| `ModDependencyAvailabilityRules.cs` | 69 | 五态 Missing/Incompatible/PendingRestart/Loaded/Disabled；已装但禁用≠缺失(27)；无 VersionRange 解析产物判不满足、声明文本不再二次解析(50)；包名\n版本 组合键(33) |
| `ModDependencyInfo.cs` | 25 | 不可变四要素：PackageName/VersionRangeString/VersionRange(引擎解析产物)/Link(富信息)；纯文本来源(世界存档)后两者 null |
| `ModUpdateSelector.cs` | 120 | FindBestFile 六档候选：包名+scmod 直返(49)>文件名+scmod>包名>文件名>(要求包匹配且有元数据时判null，77)>scmod>首个；版本比较 NuGetVersion 后比时间戳：InvariantCulture+AssumeUniversal 统一转 UTC(106) |
| `ModpackActivationRules.cs` | 47 | BuildEnableChanges 对全部状态以 IsManaged 判禁用(3)；BuildDisableChanges 管理中条目置禁用+备份状态原样恢复(22) |
| `ModpackModMatcher.cs` | 92 | ManagedModSet 三集合(包名/包\n版本/文件键)；NormalizeMatchKey=去扩展名(BCL 语义)+仅字母数字小写(68)；Storage 解析抛异常回退空键不匹配(77) |
| `ModpackPresenceRules.cs` | 127 | IsItemDownloaded=内嵌随包落盘或已装(45)；类型分派到快照五类键(55)；自定义数据文件走 ModpackDataFiles.IsPresent(61)；TryGetDownloadedFileName 包名表>文件名表>落盘路径三级回退(88) |
| `ModpackPresenceSnapshot.cs` | 15 | 纯数据八容器：World/Furniture/Texture/Skin/ModPackage/ModFile 六键集+LocalFileNames+ModPackageFileNames |
| `ModpackRules.cs` | 227 | TryGetPathTailName 取未解码 AbsolutePath 后统一解码一次，防 %2520 二次解码(56)；ResolveContentType 目录根词 mods/worlds/texturepacks/characterskins/furniturepacks(74)→Category 词表 world/scworld…兜底(217)；TryValidateSource：JSON 包禁相对路径、ZIP 包须嵌入命中(90)；EnsureItemFileName 缺扩展按类型补默认扩展(148) |

## Domain\Transfers（7，下载/上传传输域）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityDownloadQueueItem.cs` | 30 | 队列项 20 字段；Imported 标志(25)：进程死前已导入的项恢复时改判 Completed 避免重复导入 |
| `CommunityDownloadQueueStateMachine.cs` | 85 | 九态十命令纯转换表(52)；加载归一 Running/Pausing/Canceling→Paused(31)；Pausing 态按真实结果落 Completed/Failed、Canceling 态一律尊重取消(76)；非法转换抛 InvalidOperationException(82) |
| `CommunityDownloadSourceModels.cs` | 23 | 三值源选择枚举已收编为 SettingsManager 布尔(2)；CommunityFileDownloadResult.ExistingFilePath 类型化承载 FileAlreadyExistsException.Path，覆盖确认不嗅探错误文本(18) |
| `CommunityDownloadSourceResolver.cs` | 41 | Host 空=默认线路原站直连(4)；镜像主机填完整 URL 时取主机并回传显式端口(30)；用户输入畸形 UriBuilder 抛 UriFormatException 按 null 处理不裸抛(23) |
| `CommunityTransferProgress.cs` | 21 | 线程安全进度：Lock 内 Set/Snapshot；NaN 归 0、Clamp 0..1(11) |
| `CommunityUploadFileNaming.cs` | 27 | MakeSafeFileName 复用 Storage.SanitizeFileNameSegment；SanitizeFileName 空输入历史默认 `resource.dat`(19)；MakeSaveKey=`/{yyyy/MM/dd}/{转义名}`(22) |
| `CommunityUploadModels.cs` | 31 | 上传六阶段枚举 Preparing→Completed(2)；CommunityWorldUploadResult{Url,FileSize,Error,Canceled}；PreparedUploadFile 含 IsTemporary |

## Infrastructure 根（2）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityDownloadCacheFile.cs` | 60 | 续传缓存元数据 `<path>.meta.json`(59)：RequestUrl/ResponseUrl/ETag/LastModified/TotalLength；TryDelete 连元数据同删(14)；写入走 JsonFileStore |
| `TaskSlot.cs` | 122 | 单槽后台任务：requestId 从 1 递增、0=未启动哨兵(42)；TryTake 消费即清槽，fault 无 onFaulted 记日志按无结果、异常不冒泡 Update(71)；被弃任务 ContinueWith 观察异常防未观察(105)；全部方法须 UI 线程 |

## Infrastructure\Http（14，网络客户端）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityApiClient.cs` | 111 | 四入口 GetJsonAsync/GetStringAsync/PostJsonAsync/GetJsonResultAsync；Bearer 统一注入；带 token 收 401/403 → CommunityUnauthorizedNotifier.Notify(92)；错误体截断 512 字符(100)；空/非 JSON body(网关 200 空响应、HTML 错误页)归一化 InvalidOperationException(54,60) |
| `CommunityAuthClient.cs` | 84 | POST `/user/login`({account,password})、POST `/user/logout`(21,59)；账号密码错误由响应码承载(Code=401)不与网络故障混淆(27)；用户取消 OCE 传播，HttpClient.Timeout 抛的 OCE 不满足 when 仍归网络错误(31) |
| `CommunityDownloadFeedbackClient.cs` | 118 | GET `{api}/download/record?Action=feedback&Feedback=Success&Platform=&Version=&postId=&fileId=`(105)；Token 快照优先，fallback 仅当前服务器一致才补取——防把 B 服令牌发往 A 服外泄+误登出(84)；provider 异常按匿名上报不炸下载(91) |
| `CommunityDownloadGuard.cs` | 22 | MaxPayloadBytes=256MB(9)：Content-Length 与累计读入双重校验的统一上限（第三方清单来源防内存耗尽） |
| `CommunityHttpDownloader.cs` | 355 | 断点续传下载器：`.part` 缓存+meta ETag/LastModified/总长验证器校验(299)；416 且缓存完整(总长相等)直接读回、放宽验证器(127)；206 部分 CDN 不回显验证器：同类型验证器才可验证、总长一致放行(323)；Range 起点校验(335)、响应体与 Content-Range 完整性复核(208,342)；读空闲超时 30s linked CTS，首块前启动、每块重置(29,88)，stall 抛 CommunityReadIdleTimeoutException(is-a OCE) 区分用户取消(16)；Content-Disposition FileName 非 FileNameStar 需手工 Unescape(57)；续传读回内存前复检文件大小防外部篡改(261) |
| `CommunityModCatalogClient.cs` | 20 | GET `{api}/upload/mods?packageName=&types=5[&versionRange=]`(13,17) 按包名查已发布 mod |
| `CommunityPlayedTimeClient.cs` | 85 | POST `{api}/mod-play/record`(84)；null 字段不序列化(15)；recorded==条数且 failed==0 才算成功，调用方据此决定保留重试队列(69)；故意不广播 401/403：随自动保存周期触发，反复弹登录过期属打扰(46) |
| `CommunityTranslateClient.cs` | 66 | POST translateUrl：整篇投递由服务端 AI 保结构翻译+缓存(8)；请求键 camelCase（Nest 校验错名直接 400，52）；Shared 单例追加共享 UA(22)；翻译结果空白回退原文(44)；响应键大小写不敏感兜两种风格(15) |
| `CommunityUnauthorizedNotifier.cs` | 32 | 静态事件 UnauthorizedResponse(token)；Notify 逐订阅者 try/catch 隔离，防 UI 编组异常逃进 HTTP 调用路径(21)；IsUnauthorized=401\|403(31)；通知携带 token 供订阅方比对防误杀新会话 |
| `CommunityUploadClient.cs` | 258 | 三步发布链：POST `/upyun/credentials` 取凭证(27)→又拍云表单直传（仅 https+*.upyun.com，防签名明文/中间人，170）→POST `/upload` 登记(116)；凭证响应兼容包装/裸两种格式(53)；又拍云响应 JSON 解析失败回退 `url=` 查询串旧格式(193)；ProgressStreamContent 必须重写带 CT 的 SerializeToStreamAsync 重载否则大文件上传取消失效(234) |
| `HttpClientProvider.cs` | 28 | 三共享客户端：Community 30s / RemoteImport 100s / Upload 无限超时（大文件上传 30s 必超时，靠全程透传取消令牌兜底，15-19）；UA=`SurvivalcraftApi/{VersionsManager.Version}`(9) |
| `IModpackSourceResolver.cs` | 10 | FetchFileInfoByIdAsync + ResolveAsync（返回 data/文件名/resolvedUrl/communityFile 四元组） |
| `ModpackSourceResolver.cs` | 160 | HTTP 下载失败且有 fileId 时兜底 GET `/upload/info?id=`(68)；用户取消传播不触发兜底(29)；fileId 响应兼容包装 Data/裸 PostFileItem(87)；DownloadBytesAsync 改 ResponseHeadersRead 防 30s 总超时杀慢网体读取(114)；读空闲超时复用 CommunityHttpDownloader.ReadWithIdleTimeoutAsync(137)；Content-Disposition 转义名同款手工 Unescape(148) |
| `PostIconDecoder.cs` | 23 | ImageSharp 解码；>256 边等比缩至 256(10)；Resize 中途异常 dispose 已分配位图防泄漏(17) |

## Infrastructure\Integration（7，下载→本地导入）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityUploadFileProvider.cs` | 177 | PrepareWorld 导出 .scworld 至 DocPath 临时文件，失败清理再抛防泄漏 .tmp(20)；未加载 mod 无 ModEntity 回退 LocalFilePath(59)；整合包按 Tag is LocalModpackRecord 识别(176)；上传名缺扩展按类型补默认扩展(Modpack→.json，153) |
| `ICommunityUploadFileProvider.cs` | 7 | PrepareWorld/PrepareLocalResource/OpenRead/DeleteTemporaryFile 四方法 |
| `IModpackItemImporter.cs` | 10 | ImportExternalContent + ImportDataFile；返回 false=host 缺失无处导入，调用方必须计失败(6) |
| `ModDependencyParser.cs` | 23 | DependencyRanges→ModDependencyInfo；VersionRange.All 或空文本→VersionRangeString=null(17)；富信息(友好名/链接)走 DependencyDetails 旁路字典，键恒为 Ranges 子集(14) |
| `ModpackItemImporter.cs` | 72 | ImportExternalContent：mod 元数据校验（modinfo 缺失/包名/版本不符抛错跳过，41-69）→ExternalContentManager Prepare+Import；ImportDataFile host 缺失返回 false，导入后 IsModpackDataFilePresent 复检防空操作 host(36) |
| `PendingLocalModActions.cs` | 206 | "重启后执行"清单落盘 local-mod-pending-actions.json；Process 于启动/重启边界兑现 Delete(删 .scmod)/Disable/Enable(写 ModsManager.DisabledMods+SaveSettings)，失败条目保留下次重试(77)；includeSettingActions=false 供加载器早期只删文件(43)；读回后重建 OrdinalIgnoreCase 字典(108)；文件 IO 在锁外执行(65) |
| `PendingLocalModCompatibilityOverrideCache.cs` | 56 | 兼容性覆盖缓存容量 1024 插入序伪 LRU(26)；已存在键只更新不入队防误删(19)；key=包名或去扩展名文件名 |

## Infrastructure\Modpacks（2）

| 文件 | 行 | 职责 |
|---|---|---|
| `ModpackDataFiles.cs` | 306 | 自定义数据文件导入：受保护根名黑名单 15 项(project.xml/saves/mods…)(6)；SanitizeRelativePath 剥盘符、拒 ".."、逐段 Sanitize(239)；mod 走事务替换、本体走 Storage.MoveFileSafely(45)；启用备份三段：PrepareForActivation(78)/TryPersistChanges(109)/TryRestoreBackups(142)，恢复成功后清备份失败不报失败(181)；持久化名含 FNV-1a 路径哈希(293) |
| `ModpackPresenceManager.cs` | 83 | Capture 缓存快照：世界/家具/材质/皮肤各"名+文件名"双键；mod 走 ModsManager.ModListAll 过滤内建实体(46)；Invalidate 由导入/扫描完成事件触发 |

## Infrastructure\Persistence（10，落盘）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityCredentialStore.cs` | 429 | v4 每服一文件 `auth/<sha256(归一化地址)>.bin`(60)；魔数 SCBPAUTH4(20)；Windows=DPAPI(CurrentUser+entropy "CommunityCredentialStore.v4")，其他平台=salt16+nonce12+AES-GCM+tag16、PBKDF2-SHA256 600k、口令=机器名（威胁模型仅隔离不知机器名者，16）；原子写：备份-替换-回滚三级降级，备份建立失败仍保证一份可读(165)；payload 归属服务器与文件名不一致判未找到(130)；DPAPI blob 释放前清零防明文残留(397,407)；损坏文件作废重登重建(100) |
| `CommunityDownloadQueuePersistence.cs` | 147 | 恢复：TempFilePath 仅接受缓存目录内 `{id}_*.part` 形态，否则重建——防手工编辑路径被续传语义读+写穿任意文件(124)；Source 按名恢复、未命中回退默认线路(36)；落盘 StripToken：队列文件不走加密通道明文 Token 不落盘(81)；Imported 项恢复改判 Completed 并顺手删 .part(45) |
| `CommunityDownloadQueueStore.cs` | 20 | download-queue.json；JsonStringEnumConverter(allowIntegerValues) 字符串枚举、兼容旧数字格式(10) |
| `CommunityPlayedTimeStore.cs` | 47 | playedtime.json v1；Mods 键 PackageName；ModPlayedTimeData 含 TotalSeconds/LastPlayedAtUtc/WorldSeconds 分世界时长 |
| `CommunityStoragePaths.cs` | 20 | `DocPath/Community` 下 10 路径：state.json/local-mod-reviews.json/local-mod-pending-actions.json/local-integration-pack-state.json/playedtime.json/pending-play-reports.json/download-queue.json/auth//download-cache//integration-pack-backups/ |
| `JsonFileStore.cs` | 164 | 读：不存在/损坏/截断统一回退 default 防启动链崩溃(23)；写：临时文件 `<名>.<32位hex>.tmp`+MoveFileSafely(42)；RecoverLeftoverTempFiles 启动清扫：正式文件在→删 tmp，缺失→tmp 移回原名(55)，校验 hex 段防误伤他组件 tmp(127) |
| `LocalModReviewStore.cs` | 30 | local-mod-reviews.json；Reviews 键 OrdinalIgnoreCase 双向重建 |
| `ModpackActivationState.cs` | 124 | 静态直供；LoadResolved 探测式：RecordPath 失效→按文件名迁移目录→按 MatchesRecord 全表匹配(83)；单条记录读取失败跳过继续探测(104) |
| `ModpackRegistry.cs` | 581 | ModPacks 目录所有者：.zip/.json 主文件+`{base}.meta.json` 溯源；SaveManifest/SaveArchive 写入成功后才清理同基名旧扩展残留(68,100)；异源冲突改名 "pack (2)"：以双方 meta SourceUrl 判同源、无证据保守判异源(327,364)；解析缓存键=时间+大小+元数据时间，时间不可得时加 FNV-1a 内容哈希防同 tick 同大小替换误命中(174,465)；锁内解析防并发重复读盘(181)；ReadResources CreationTime 统一 Kind=Utc(125) |
| `ModpackStateStore.cs` | 21 | local-integration-pack-state.json；Save(null)=删文件(13) |

## Models\Api（7，线协议）

| 文件 | 行 | 职责 |
|---|---|---|
| `ApiEnvelope.cs` | 12 | {code,data,msg} camelCase JsonPropertyName 标准信封，泛型空壳继承 |
| `AuthModels.cs` | 37 | LoginResponse/LoginData{token,user}；StoredCredential v4 payload 自描述归属服务器(11)；UserData 13 字段+roles |
| `CommunityModels.cs` | 109 | PostsResponse 分页 list/total/page/limit/count；VersionListItem setter 赋值即解析 NuGetVersion+IsVersionLine（两段式版本：非预发布且 Build<0，38）；PostDownloadTrend 趋势 6 模型；FileInfoResponse=ApiEnvelope<PostFileItem> |
| `FilePublishedModels.cs` | 23 | 发布成功响应；version/file 复用 PostModels 完整模型，服务端只回子集缺省 null(20) |
| `PlayedTimeModels.cs` | 33 | ModPlayRecordRequest{list}/Item；wire 键 camelCase 契约不随本地命名改(13)；Result{recorded,failed[]{reason}} |
| `PostModels.cs` | 215 | PostItem 计数字段(like/bad/fav/postVersion/comment/heat/size)全 FlexibleString——服务端类型不稳(27)；PostVersionItem/PostFileItem setter 解析 NuGetVersion(74,118)；FlexibleInt/FlexibleString/FlexibleNullableDouble 三容错转换器 HandleNull=true；/upload/mods 的 page/limit 也 FlexibleInt(138) |
| `UploadModels.cs` | 45 | UpyunCredentials{policy,authorization,uploadUrl}；UploadRegisterRequest{path,type}；UploadFileData.Size 留 JsonElement 原始类型不归一(42) |

## Models\Persistence（4，落盘模型）

| 文件 | 行 | 职责 |
|---|---|---|
| `DownloadQueueModels.cs` | 32 | PersistedState{Version,NextId,Items}；StoredItem.Source 按名(21)、Imported 改判 Completed 语义(30) |
| `LocalModModels.cs` | 32 | ReviewsData/ReviewEntry{PostId,Rating,Text,LastText,UpdatedAt}；PendingActionsData/Entry{FilePath,PackageName,Version,ActionType}；枚举 None/Delete/Disable/Enable |
| `LocalResourceModels.cs` | 36 | LocalResourceItem 18 字段（Tag 装 LocalModpackRecord，Texture 引引擎 Texture2D，主报告 #1 归位注记 5）；LocalModCommunityStatusInfo{IsPublished,PostId,LatestVersion,HasUpdate} |
| `ModpackModels.cs` | 114 | ModpackManifest 11 字段（author/homepage/apiVersion 展示性可选旧清单显"无"，10）；ModpackItem{category,fileName,url,fileId(FlexibleString),targetPath/targetDirectory}；DownloadResult.Skipped 不算成功不算失败(43)；Progress{CustomFileBackups,顶层 Error(58),Interrupted 请求取代语义(63)}；LocalModpackRecord/ActivationState/Mod 与 File 两 StateEntry |
