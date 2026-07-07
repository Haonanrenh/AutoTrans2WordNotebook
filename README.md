# AutoTrans2WordNotebook

Windows 离线选词翻译工具，可将查询结果保存到本地 Word 单词本。

程序常驻系统托盘。用户用鼠标选中英文单词或短语后，点击浮动提示即可查看中文释义和音标，并可一键保存到 `.docx` 单词本。

## 功能

- 离线英汉查询，内置 ECDICT 词典。
- 鼠标选词触发翻译提示，无需快捷键。
- 保存原文、释义、音标和时间到 Word 单词本。
- 自动跳过重复单词或短语。
- 过滤无效选区并清洗词典文本。

## 运行

以下命令均在项目根目录执行：

```text
AutoTrans2WordNotebook/
```

### 运行 exe

适合普通用户。下载 Release 附件或本地构建后，直接运行：

```text
dist/AutoTrans2WordNotebook.exe
```

首次启动时，在设置窗口中选择 Word 单词本 `.docx` 路径。支持续写覆盖原有doc。

### 运行 Python app

适合开发和调试。进入项目根目录后安装依赖并启动根目录的 `app.py`：

```powershell
cd path\to\AutoTrans2WordNotebook
python -m pip install -e ".[dev]"
python app.py
```

## 使用

1. 选中英文单词或短语。
2. 点击鼠标旁的“翻译”提示。
3. 在结果窗口中查看释义，或保存到单词本。

## 词典

项目使用 [ECDICT](https://github.com/skywind3000/ECDICT) 作为离线词典数据源。仓库包含可直接使用的 SQLite 词典：

```text
src/resources/builtin_dictionary.sqlite3
```

如需更新词典：

```powershell
python tools/build_ecdict.py
```

开发时可使用较小的 mini 词典：

```powershell
python tools/build_ecdict.py --mini
```

## 构建 exe

先进入项目根目录：

```powershell
cd path\to\AutoTrans2WordNotebook
```

更新内置离线词典：

```powershell
python tools/build_ecdict.py
```

运行 PowerShell 打包脚本：

```powershell
.\scripts\build_exe.ps1
```

输出文件：

```text
dist/AutoTrans2WordNotebook.exe
```

## 项目结构

```text
AutoTrans2WordNotebook/
├── app.py                         # Python app 启动入口
├── pyproject.toml                 # 项目依赖和工具配置
├── packaging/                     # PyInstaller 打包配置
├── scripts/                       # 构建脚本
├── src/
│   ├── app.py                     # 应用主流程
│   ├── clipboard.py               # 鼠标选词和剪贴板读取
│   ├── config.py                  # 本地配置
│   ├── dictionary.py              # 离线词典查询
│   ├── notebook.py                # Word 单词本写入
│   ├── resources/                 # 内置词典资源
│   └── ui/                        # PySide6 界面组件
├── tests/                         # 单元测试
└── tools/                         # 词典构建和导入工具
```

## 开发

```powershell
pytest
ruff check .
```

## 安全与隐私

- 默认离线查询，不上传选中文本。
- 不执行剪贴板、词典或 Word 文档中的动态内容。

## License

本项目使用 [MIT License](LICENSE)。
