# Mod 示例 · 自定义界面（Screen）

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 端到端示例；XML+30 行代码做一个原版风格的模组界面，从设置页按钮进入；行号 2026-11-01 实读

## 目标

做一个模组自己的全屏界面 `MyModScreen`（原版同款布局：顶栏+返回键+正文区），在**设置页加一个按钮**点进去，按返回键回上一屏。零自定义美术、零翻译文件。

## 前置知识

- [12-ModAPI与加载链](01-引擎/12-ModAPI与加载链.md)：钩子注册窗口与 `RegisterHook` 写法
- [17-Screen屏幕族](01-引擎/17-Screen屏幕族.md)：Screen 契约（Enter/Leave/Update、切换协议）
- [09-UI与Widget体系](01-引擎/09-UI与Widget体系.md)：XML 装配与 Update 必调 base 清单

## 原理 30 秒

1. **XML 装配**：`ContentManager.Get<XElement>("Screens/名")` + `LoadContents(this, node)` 把 XML 树装进自己（原版样板 SettingsAudioScreen.cs:11-12；装配器 Widget.cs:507-517，逐属性反射赋值+递归建子树，每棵树装配完还发 `OnWidgetContentsLoaded` 钩子）。mod 的 `Assets/Screens/*.xml` 在 CombineContent 时剥掉 `Assets/` 前缀注册进 ContentManager（ModEntity.cs:290-296），同名资源即取即得。
2. **注册进屏表**：`ScreensManager.AddScreen(name, screen)`（ScreensManager.cs:47）。时机用 `OnLoadingFinished` 钩子往加载队列**尾部追加一个动作**（LoadingScreen.cs:578-583 传入队列引用；动作泵每轮先清 mod 队列 :700-711）——此刻语言/字体/内容系统全部就绪，和原版屏同等待遇。
3. **进入方式**：设置页构造时发 `OnSettingsScreenCreated` 钩子，mod 交出"按钮→动作"字典（SettingsScreen.cs:32-43），引擎用 `AddSettingButton` 奇偶分列插进左右两栏并接上点击（:68-71,86-96）——这个钩子切语言重建设置页时还会再发，按钮不丢（ModLoader.cs:1962-1965 注释明说）。
4. **切屏**：`ScreensManager.SwitchScreen(name)` 走淡入动画，Factor 过半才 Enter 新屏、Leave 旧屏（ScreensManager.cs:277-317）；`OnSwitchScreen`/`OnScreenEntered`/`OnScreenLeaved` 三个钩子在切屏链上。

## 制品

### 目录树（.scmod = zip 容器）

```
example-mymenu.scmod
├── modinfo.json
├── MyModMenu.dll                ← zip 根层（Assets/ 下的 dll 永不加载）
└── Assets/
    └── Screens/
        └── MyModScreen.xml      ← 界面布局模板（下面全文）
```

### modinfo.json（完整）

```json
{
    "Name": "示例：模组界面",
    "Version": "1.0.0",
    "ApiVersion": "1.8",
    "Author": "SC笔记示例",
    "Description": "新增原版风格设置界面并从设置页进入。演示 Screen 注册与设置页按钮钩子。",
    "PackageName": "example-mymenu",
    "LoadOrder": 10000,
    "GameplayImpactLevel": "Cosmetic"
}
```

### Assets/Screens/MyModScreen.xml（完整，逐行注明出处）

```xml
<!-- 根元素名随意（装配器只取它的属性装到 this 上），照抄原版习惯写 Screen；
     xmlns 指向 Game 命名空间=子元素标签按 Game.* 控件类名解析 -->
<Screen xmlns="runtime-namespace:Game">

  <!-- 全景背景（主菜单同款旋转地形图） -->
  <PanoramaWidget />

  <!-- 竖向骨架：顶栏 + 正文区（SettingsAudioScreen.xml 同构） -->
  <StackPanelWidget Direction="Horizontal">

    <!-- 顶栏：Style 展开=关闭键(自动 Name="TopBar.Back")+标题槽（Widgets/TopBarContents） -->
    <CanvasWidget Style="{Widgets/TopBarContents}">
      <LabelWidget Name="TopBar.Label" Text="示例面板" />
    </CanvasWidget>

    <!-- 正文区：圆角面板 + 纵向滚动 + 居中堆叠 -->
    <CanvasWidget Margin="10, 20">
      <BevelledRectangleWidget Style="{Styles/Area}" />
      <ScrollPanelWidget Direction="Vertical" HorizontalAlignment="Center" VerticalAlignment="Center" Margin="3, 3">
        <StackPanelWidget Direction="Vertical" HorizontalAlignment="Center" VerticalAlignment="Center">
          <LabelWidget Text="Hello from MyMod!" Margin="0, 10" />
          <ButtonWidget Name="MyButton" Text="点我" Size="310, 60" Margin="0, 10" />
        </StackPanelWidget>
      </ScrollPanelWidget>
    </CanvasWidget>

  </StackPanelWidget>
</Screen>
```

- `Text="示例面板"` 直接写字面量；写 `[文件名:键]` 才走语言表查找（LabelWidget.cs:19-26）——中文会经字体回退链正常渲染。
- `{路径}` 花括号=从 ContentManager 取 XML 片段当样式；`Widgets/TopBarContents` 自带返回键，`Styles/Area` 是圆角面板底。

### MyModScreen.cs（完整）

```csharp
using System.Collections.Generic;
using System.Xml.Linq;
using Engine;                                   // ContentManager 所在命名空间

namespace MyCompany.ExampleMyMenu {
    public class MyModMenuLoader : ModLoader {
        public override void __ModInitialize() {                    // 注册窗口内（ModLoader.cs:21）
            ModsManager.RegisterHook("OnLoadingFinished", this);    // 派发点 LoadingScreen.cs:578-583
            ModsManager.RegisterHook("OnSettingsScreenCreated", this); // 派发点 SettingsScreen.cs:32-43
        }

        // 装载尾段：往加载动作队列尾部追加"注册屏"动作（签名照抄 ModLoader.cs:781）
        public override void OnLoadingFinished(List<Action> actions) {
            actions.Add(() => ScreensManager.AddScreen("MyMod", new MyModScreen()));   // AddScreen 照抄 LoadingScreen.cs:611 的用法
        }

        // 设置页建好了：交出要加的按钮（签名照抄 ModLoader.cs:1968-1970）
        public override void OnSettingsScreenCreated(SettingsScreen settingsScreen, out Dictionary<ButtonWidget, Action> buttonsToAdd) {
            buttonsToAdd = new Dictionary<ButtonWidget, Action> {
                [new BevelledButtonWidget {
                    Name = "MyModMenuButton",
                    Text = "示例面板",
                    Style = ContentManager.Get<XElement>("Styles/ButtonStyle_310x60"),  // 原版设置按钮样式，同 SettingsScreen.cs:107-113
                    HorizontalAlignment = WidgetAlignment.Center,
                    VerticalAlignment = WidgetAlignment.Center,
                    Margin = new Vector2(0f, 5f)
                }] = () => ScreensManager.SwitchScreen("MyMod")     // 按名切屏，ScreensManager.cs:49
            };
        }
    }

    public class MyModScreen : Screen {
        public MyModScreen() {
            XElement node = ContentManager.Get<XElement>("Screens/MyModScreen");   // 取 XML（原版样板 SettingsAudioScreen.cs:11）
            LoadContents(this, node);                              // 装配进自己（Widget.cs:507）
        }

        public override void Update() {
            base.Update();                                         // 09 页"Update 必调 base"清单
            if (Children.Find<ButtonWidget>("MyButton").IsClicked) {
                Children.Find<LabelWidget>("TopBar.Label").Text = "点过了！";   // Find 按名字取控件（SettingsAudioScreen.cs:13）
            }
            if (Input.Back || Input.Cancel
                || Children.Find<ButtonWidget>("TopBar.Back").IsClicked) {     // 三通道返回（SettingsAudioScreen.cs:28-30）
                ScreensManager.SwitchScreen(ScreensManager.PreviousScreen);    // 回上一屏（SettingsAudioScreen.cs:31）
            }
        }
    }
}
```

## 打包清单

1. dll 在 zip 根层；扩展名小写；`__ModInitialize` 里只做 RegisterHook（12 页坑表——抛异常全模组连坐）。
2. 屏类必须 **public + 无参构造**：切语言时引擎会 `Activator.CreateInstance` 重建全部屏（ScreensManager.cs:109-112），构造失败会告警并保留旧实例（:114-116），但重建成功的屏才吃得到新语言。
3. XML 存 `Assets/Screens/`，装载后资源名=剥前缀的 `Screens/MyModScreen`，与 `Get<XElement>` 的名字一致。

## 验证

| 锚点 | 出处 |
|---|---|
| `[示例：模组界面](Version: 1.0.0) Loaded 3 resource files.`（modinfo+dll+xml） | ModEntity.cs:275 |
| 设置页出现"示例面板"按钮（左右两栏交替排布） | SettingsScreen.cs:91-96 |
| 点按钮→渐变切入"示例面板"屏 | ScreensManager.cs:51-88 |
| 切语言后再开设置页按钮仍在（钩子重发） | ModLoader.cs:1962-1965 |
| 日志 `Entered screen "MyMod"`（Verbose 级，开调试日志可见） | ScreensManager.cs:85 |

## 该示例踩的坑

- **按钮死循环报错**：`AddSettingButton` 对同一个 ButtonWidget 实例二次登记抛 `InvalidOperationException`（SettingsScreen.cs:88-91）——`OnSettingsScreenCreated` 每次设置页构造都发，字典里必须是**新建**的按钮实例，别缓存复用。
- **在 `__ModInitialize` 里直接 `AddScreen`**：此刻内容系统/字体链未就绪，屏构造函数里的 `ContentManager.Get` 会炸——必须走 `OnLoadingFinished` 追加动作的时机（本例写法）。同理别在构造函数里碰 `ScreensManager.CurrentScreen`。
- **屏不见了（退出世界再回主菜单后）**：LoadingScreen.Enter 会清掉除自己外的全部屏（LoadingScreen.cs:674-684），随后的装载动作会重放——`OnLoadingFinished` 每轮装载重发，本例写法自愈；若你在别的时机注册，重进主菜单后就没了。
- **XML 改了没生效**：检查文件是否真在 `Assets/Screens/` 下、资源名大小写是否一致；改 dll 后必须**重启整个进程**（Reboot 不卸载程序集，12 页坑表）。
- **控件点了没反应**：`Update()` 没调 `base.Update()`（09 页）；或 `Children.Find` 的名字和 XML `Name` 不一致——Find 找不到返回 null，下一行就是空引用。
- **想在世界内弹窗而不是全屏**：别用 Screen，走 Dialog 族（[18页](01-引擎/18-Dialog对话框族.md)）；两按钮确认框最小样板 `MessageDialog.cs:18-47`。

## 快查路由

| 我想… | 去/看 |
|---|---|
| 全代码构建界面（不用 XML） | `EditColorDialog.cs:19-136`（Canvas+Stack 结构样板） |
| 控件事件绑定/拖放/焦点 | [09-UI与Widget体系](01-引擎/09-UI与Widget体系.md) |
| 从世界内（游戏屏）打开 | 17 页"屏层 mod 钩子"节（OnSwitchScreen/OnScreenEntered 等） |
| 屏间传参 | `SwitchScreen(name, params)` 参数原样进 `Enter(object[])`（ScreensManager.cs:49,:307） |
| 原版各屏 XML 模板 | 源码仓库 `Survivalcraft/Content/Assets/Screens/*.xml`（41 个现成布局） |
| 异步加载列表不卡帧 | `Screen\PlayScreen.cs:82-118`（BusyDialog+Task.Run+Dispatcher 封送） |
