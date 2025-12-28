# 随机抽题机

一个基于 PyQt6 的随机抽题/抽人工具，适用于课堂提问、考试抽题、随机点名等场景。

## 功能特性

- **题库管理**：支持导入 Markdown 格式题库，可同时管理多个题库
- **名单管理**：支持导入 TXT 格式人员名单
- **随机抽取**：支持随机抽题、随机抽人，可同时进行
- **去重模式**：已抽取的题目/人员不会重复出现
- **历史记录**：自动保存抽取历史，方便查看
- **结果导出**：支持导出为 Excel 或 TXT 格式

## 安装使用

### 方式一：直接下载（推荐）

前往 [Releases](https://github.com/DunCanYounG-1/RandomQuestionGenerator/releases) 下载最新版 `随机抽题机.exe`，双击运行即可。

### 方式二：源码运行

```bash
# 克隆仓库
git clone https://github.com/DunCanYounG-1/RandomQuestionGenerator.git
cd RandomQuestionGenerator

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 题库格式

题库使用 Markdown 格式，规则如下：
- 空行分隔不同题目
- 每道题的第一行为标题
- 后续行为题目内容/要求

示例：
```markdown
# Python 基础题库

列表推导式
请写出一个列表推导式，生成1到10的平方数
要求使用一行代码完成

字典操作
请实现一个函数，合并两个字典
如果有重复的键，保留第二个字典的值

异常处理
请写一个函数，安全地将字符串转换为整数
如果转换失败，返回默认值0
```

## 名单格式

名单使用 TXT 格式，每行一个名字：

```
张三
李四
王五
```

## 截图

导入题库和名单后，点击「开始抽题」即可随机抽取题目，勾选「同时抽取人员」可以同时抽人。

## 技术栈

- Python 3.10+
- PyQt6 - GUI 框架
- SQLite - 历史记录存储
- openpyxl - Excel 导出

## 项目结构

```
├── main.py              # 程序入口
├── src/
│   ├── core/            # 核心逻辑
│   │   ├── parser.py    # Markdown 解析器
│   │   ├── bank.py      # 题库管理
│   │   ├── drawer.py    # 抽题引擎
│   │   └── roster.py    # 名单管理
│   ├── storage/         # 数据存储
│   │   ├── database.py  # SQLite 数据库
│   │   └── exporter.py  # 导出功能
│   └── ui/              # 界面组件
│       ├── main_window.py
│       ├── bank_panel.py
│       ├── draw_panel.py
│       ├── roster_panel.py
│       └── result_panel.py
├── requirements.txt
└── README.md
```

## 作者

By duncany

## 许可证

MIT License
