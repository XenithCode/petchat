# pet-chat UI 设计规范（暗色 iOS 风格）

## 1. 整体风格

- 主题：暗色系、轻拟物 + 扁平混合风格，参考 iOS 控制中心和对话界面。
- 背景：大面积接近黑色的主背景，局部使用略亮的卡片背景制造层次。
- 圆角：统一采用中等圆角，核心可交互控件使用 10–18px 圆角。
- 动效：轻微过渡与浮动，不夸张，保证响应和稳定感。

## 2. 配色规范

### 2.1 基础颜色

| 名称              | 变量               | 颜色值   | 用途                                   |
|-------------------|--------------------|----------|----------------------------------------|
| 主色 Primary      | `Theme.PRIMARY`    | `#0a84ff` | 主按钮、选中态、高亮                  |
| 主色 Hover        | `Theme.PRIMARY_HOVER` | `#1b9aee` | 按钮悬停                               |
| 主色文字          | `Theme.PRIMARY_TEXT`  | `#f9fafb` | 主按钮文字                             |
| 次要色 Secondary  | `Theme.SECONDARY`  | `#4b5563` | 次级按钮、弱强调元素                   |
| 强调色 Accent     | `Theme.ACCENT`     | `#22c1c3` | 特殊标签、情绪高亮                     |

### 2.2 背景与边框

| 名称                | 变量                | 颜色值   | 用途                                |
|---------------------|---------------------|----------|-------------------------------------|
| 主背景              | `Theme.BG_MAIN`     | `#020617` | 应用整体背景、聊天列表背景         |
| 提升层背景          | `Theme.BG_ELEVATED` | `#020617` | 主窗口、对话框                       |
| 卡片/面板背景       | `Theme.BG_MUTED`    | `#111827` | 建议卡片、记忆卡片、输入框背景     |
| 选中/强调背景       | `Theme.BG_SELECTED` | `#111827` | Pet 卡片背景、选中状态的轻背景      |
| 边框                | `Theme.BG_BORDER`   | `#1f2937` | 所有卡片、输入、Tab 边界            |

### 2.3 文本颜色

| 名称              | 变量                  | 颜色值   | 用途                       |
|-------------------|-----------------------|----------|----------------------------|
| 主文本            | `Theme.TEXT_PRIMARY`  | `#e5e7eb` | 正文内容、标题             |
| 次文本            | `Theme.TEXT_SECONDARY` | `#9ca3af` | 辅助说明、标签、占位符     |
| 禁用文本          | `Theme.TEXT_DISABLED` | `#6b7280` | 禁用态按钮、弱提示         |

### 2.4 状态颜色

| 名称          | 变量             | 颜色值   | 用途                 |
|---------------|------------------|----------|----------------------|
| 成功          | `Theme.SUCCESS`  | `#22c55e` | 成功提示、记忆类别   |
| 警告          | `Theme.WARNING`  | `#fbbf24` | 风险提示             |
| 错误/危险     | `Theme.ERROR`    | `#f97373` | 错误信息、危险按钮   |

## 3. 栅格与间距

- 基础单位：8px
- `Theme.SPACING_XS = 4`
- `Theme.SPACING_SM = 8`
- `Theme.SPACING_MD = 16`
- `Theme.SPACING_LG = 24`
- `Theme.SPACING_XL = 32`

推荐用法：

- 水平内边距：按钮、输入框 8–16px
- 垂直间距：区域间 16–24px，控件组内 8px

## 4. 圆角与视觉元素

- `Theme.RADIUS_SM = 6`：标签、徽标、小按钮
- `Theme.RADIUS_MD = 10`：文本输入框、普通按钮、气泡
- `Theme.RADIUS_LG = 16`：卡片容器、Pet 外框

## 5. 字体与字号

采用系统字体族：

- `font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif`

字号：

- `Theme.FONT_SIZE_SM = 12`：标签、副标题、时间戳
- `Theme.FONT_SIZE_MD = 14`：正文、按钮文字
- `Theme.FONT_SIZE_LG = 16`：区域标题
- `Theme.FONT_SIZE_XL = 20`：窗口主标题（如启动模式标题）

## 6. 组件规范

### 6.1 按钮

- 默认按钮：使用全局样式（`Theme.PRIMARY`）
- 危险按钮：显式使用 `Theme.ERROR`，圆角 `RADIUS_SM`，字号 12–14
- 次级按钮（如“取消”）：使用 `Theme.SECONDARY` 背景，文字 `PRIMARY_TEXT`
- 状态：
  - `hover`：变更为 `PRIMARY_HOVER`
  - `disabled`：背景 `BG_BORDER`，文字 `TEXT_DISABLED`

### 6.2 输入框

- 背景：`Theme.BG_MUTED`
- 边框：`Theme.BG_BORDER`
- 圆角：`RADIUS_MD`
- 占位符：`TEXT_SECONDARY`
- 聚焦：边框颜色变为 `PRIMARY`

### 6.3 菜单栏与二级菜单

- 顶部 `QMenuBar`：
  - 背景：`BG_MAIN`
  - 文本：`TEXT_PRIMARY`
  - 悬停项背景：`BG_MUTED`
- 下拉菜单 `QMenu`：
  - 背景：`BG_MUTED`
  - 文本：`TEXT_PRIMARY`
  - 选中项：背景 `PRIMARY`
  - 分割线：`BG_BORDER`
- 设置菜单：
  - Host：API 配置条目可用
  - Guest：API 配置条目禁用（灰色，表达“仅 Host 可用”）

## 7. 启动界面（选择启动模式）

### 7.1 布局

- 居中标题「选择启动模式」，字号 `FONT_SIZE_XL`，加粗。
- 顶部说明文案使用 `TEXT_SECONDARY`。
- Host / Guest 单选按钮横向排列。
- Host IP 与端口输入框使用统一输入样式。

### 7.2 交互规范

- 初始角色：Host。
- 当选择 Guest：
  - Host IP 文本框启用。
- 当选择 Host：
  - Host IP 文本框禁用。
- 「取消」按钮：次级色 `SECONDARY`。
- 「确定」按钮：主色 `PRIMARY`。

## 8. 聊天界面

文件：`ui/main_window.py`

### 8.1 布局

- 左侧：Pet 区域 + 聊天列表 + 输入栏。
- 右侧：`QTabWidget`，包含「建议」和「记忆」两个标签页。
- Splitter 宽高比：左 3，右 1。

### 8.2 消息气泡

- 自己发送的消息：
  - 对齐右侧。
  - 背景：`PRIMARY`
  - 文字：`PRIMARY_TEXT`
  - 圆角：18px
- 对方/系统消息：
  - 对齐左侧。
  - 背景：`BG_MUTED`
  - 文字：`TEXT_PRIMARY`
  - 圆角：18px
- 时间戳：
  - 每条消息底部右对齐
  - 文本颜色：`TEXT_SECONDARY`，字号 11

### 8.3 时间分隔符

- 当新消息时间与上一条消息的分钟值不同（例如 10:01 到 10:02）：
  - 在消息列表中间插入一条时间分隔行：
    - 居中小条形标签，背景 `BG_MUTED`，文字 `TEXT_SECONDARY`
    - 圆角 `RADIUS_SM`
  - 时间格式：`HH:MM`

### 8.4 输入区

- 输入框使用统一输入样式（暗底白字）。
- 占位符：`TEXT_SECONDARY`。
- 按下 Enter 发送消息；输入 `/ai` 调用 AI 建议。

## 9. 建议与记忆面板

### 9.1 建议面板（`ui/suggestion_panel.py`）

- 背景：`BG_MAIN`。
- 标题「💡 AI 建议」使用 `TEXT_PRIMARY`。
- 建议卡片：
  - 背景 `BG_MUTED`
  - 边框 `BG_BORDER`
  - 圆角 `RADIUS_MD`
- 建议正文：
  - 使用 `QTextEdit` 只读模式。
  - 背景 `BG_MUTED`，边框 `BG_BORDER`。
- 「采用建议」按钮：
  - 使用 `PRIMARY` / `PRIMARY_HOVER`。

### 9.2 记忆面板（`ui/memory_viewer.py`）

- 背景：`BG_MAIN`。
- 标题「🧠 对话记忆」使用 `TEXT_PRIMARY`。
- 「清空记忆」按钮：
  - 背景：`ERROR`
  - 文字：`PRIMARY_TEXT`
- 记忆卡片：
  - 背景：`BG_MUTED`
  - 边框：`BG_BORDER`
  - 圆角：`RADIUS_MD`
- 记忆类别标签：
  - event：`PRIMARY`
  - agreement：`SUCCESS`
  - topic：`ACCENT`
  - unknown：`TEXT_DISABLED`
  - 背景透明度 0x33（约 20% 不透明度）。
- 时间戳：
  - 文本颜色 `TEXT_SECONDARY`，字号 10。

## 10. 宠物界面（PetWidget）

文件：`ui/pet_widget.py`

### 10.1 背景与容器

- 使用 `Theme.BG_HOVER` 到 `Theme.BG_SELECTED` 的纵向渐变，带 2px 边框。
- 圆角：`RADIUS_LG`。
- 容器高度：最小 180px。

### 10.2 颜色与状态

- 中性：`#9ca3af`
- 愉快：`#34d399`
- 紧张：`#fbbf24`
- 消极：`#fb7185`

### 10.3 动画与交互

- 眨眼动画：
  - 每约 3 秒一次眨眼，持续约 200ms。
- 浮动动画：
  - 愉快：幅度约 4px，节奏偏快。
  - 紧张/消极：幅度 2px，节奏略慢。

## 11. 可访问性与对比度

- 主文字与背景对比度至少接近 WCAG AA 标准。
- 避免纯灰 + 纯灰组合；重要信息使用主色或强调色。
- 禁用态采用降低对比度和饱和度，而不是仅仅改变透明度。

