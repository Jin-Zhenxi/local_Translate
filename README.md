# realtime-subtitle

完全本地的实时英文语音转简体中文字幕工具。

```text
麦克风
→ faster-whisper base.en
→ 实时英文字幕
→ 本地 OPUS-MT en→zh
→ CTranslate2 INT8
→ 简体中文字幕
→ PyQt6 Overlay
```

项目基于 [Vanyoo/realtime-subtitle](https://github.com/Vanyoo/realtime-subtitle) 做最小修改，保留原有音频采集、实时字幕、异步处理、Dashboard 和 Overlay 结构。

## 当前状态

### Windows 第一阶段：已完成

已在 Windows 10/11、Python 3.10 环境验证：

```text
[PASS] faster-whisper base.en 英文识别
[PASS] 英文 partial 字幕实时刷新
[PASS] final transcription
[PASS] OPUS-MT 英文到简体中文翻译
[PASS] CTranslate2 INT8 本地推理
[PASS] 中文字幕 Overlay
[PASS] 字幕无明显重复或疯狂跳动
[PASS] 项目内本地模型加载
[PASS] 强制离线模式启动
```

当前版本不依赖：

```text
OpenAI API
Ollama
DeepL
Google Translate
远程 LLM
其他在线翻译服务
```

当前固定使用 `base.en`，不准备或开发 `small.en`。

### Apple Silicon Mac 第二阶段：待实机验证

下一阶段只将当前 Windows 成功版本迁移到 Apple Silicon Mac，并完成原生环境、麦克风、ASR、翻译、Overlay 和离线运行验证。

这一阶段不进行 `.app` 或 `.dmg` 打包。

## 核心实现

### 音频与字幕数据流

```text
sounddevice.InputStream
→ AudioCapture.generator()
→ Pipeline 累积音频
→ faster-whisper base.en
→ partial 英文通过 PyQt signal 更新 Overlay
→ 检测到停顿后形成 final transcription
→ Translator.translate()
→ 本地 OPUS-MT / CTranslate2 INT8
→ 同一条 Overlay 项更新为中文字幕
```

partial transcription 不调用翻译模型。翻译只在 final transcription 形成后异步执行，因此不会每增加一个英文单词就重新翻译。

### 本地模型目录

```text
models/
├── faster-whisper-base.en/
└── opus-mt-en-zh-int8/
```

`models/` 被 Git 忽略。仅执行 `git clone` 不会得到模型，迁移机器时必须单独复制这两个运行模型目录。

模型转换期间产生的目录不需要迁移：

```text
models/.downloads/
```

### 关键配置

`config.ini` 是本机配置并被 Git 忽略。核心设置应保持：

```ini
[translation]
target_lang = Chinese
model_path = models/opus-mt-en-zh-int8
device = cpu
compute_type = int8
threads = 1

[transcription]
backend = whisper
whisper_model = base.en
device = cpu
compute_type = int8
source_language = en
transcription_workers = 1
```

## Windows 使用

### 环境安装

推荐 Python 3.10 或 3.11：

```powershell
cd D:\Pyprojection\Translate\realtime-subtitle
.\install_windows.bat
```

### 准备模型

如果项目中已经存在两个完整的运行模型目录，不需要重复下载。

首次准备翻译模型：

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\scripts\requirements-model.txt
.\.venv\Scripts\python.exe .\scripts\prepare_translation_model.py
```

首次准备 `base.en`：

```powershell
.\.venv\Scripts\python.exe .\scripts\prepare_asr_model.py base.en
```

### 启动

```powershell
.\start_windows.bat
```

在 Dashboard 中点击 `Launch Translator`，然后选择或确认麦克风输入设备。

## 第二阶段：Apple Silicon Mac 迁移

### 本阶段目标

仅实现并验证：

```text
English speech
→ 项目内 faster-whisper base.en
→ English partial/final text
→ 项目内 OPUS-MT en→zh
→ CTranslate2 INT8
→ Simplified Chinese Overlay
```

### 严格边界

不要在本阶段进行：

```text
重写 ASR
切换 whisper.cpp
切换 MLX backend
下载 small.en
更换翻译模型
加入在线翻译或 LLM
UI 重构
系统音频捕获
PyInstaller
.app / .dmg
codesign / notarization
GitHub Actions
新语言或中文到英文
```

如果 Mac 出现兼容问题，只做能保持 Windows 路径正常的最小修复。

### 1. 冻结并确认 Windows checkpoint

在 Windows 成功版本上执行：

```bash
git status
git log -1 --oneline
```

如果成功版本尚未提交：

```bash
git add .
git commit -m "working offline realtime en-zh subtitle on Windows"
```

不要修改历史 commit。后续 Mac 修改全部基于这个 checkpoint。

### 2. 复制到 Mac

需要复制：

```text
realtime-subtitle/
├── 源代码
├── .git/
├── config.ini
├── requirements.txt
├── scripts/
├── install_mac.sh
├── start_mac.sh
└── models/
    ├── faster-whisper-base.en/
    └── opus-mt-en-zh-int8/
```

不要从 Windows 复制：

```text
.venv/
venv/
__pycache__/
*.exe
*.dll
Windows Python
Windows 原生扩展
Windows 打包输出
models/.downloads/
```

Mac 必须创建自己的 arm64 Python 环境。

### 3. 检查 Mac 环境

```bash
uname -m
python3 --version
python3 -c "import platform; print(platform.machine())"
```

期望架构：

```text
arm64
```

优先使用 Python 3.10 或 3.11。确认 `python3` 指向兼容版本后再运行安装脚本。

### 4. Mac Codex 开始前必须阅读

先完整阅读：

```text
install_mac.sh
start_mac.sh
config.py
transcriber.py
audio_capture.py
translator.py
requirements.txt
main.py
launcher.py
overlay_window.py
```

并搜索：

```bash
rg -n "platform\.system|sys\.platform|Darwin|MLX|CoreAudio|sounddevice|ctranslate2" .
```

在修改任何代码前，先报告：

```text
Mac 启动路径
Mac ASR backend
Mac 音频输入路径
Mac Translator 加载路径
包含原生二进制的依赖
发现的实际兼容问题
```

当前预期路径是：

```text
start_mac.sh
→ reloader.py
→ launcher.py
→ dashboard.py
→ main.Pipeline
```

当前 Mac 第一轮必须继续使用：

```text
backend = whisper
whisper_model = base.en
device = cpu
compute_type = int8
```

即使 `install_mac.sh` 安装了 `mlx-whisper`，也不要主动把 backend 切换成 MLX。

### 5. 预期的 Mac 原生依赖

以下依赖包含或可能包含平台原生二进制，Mac 必须安装自己的 arm64 版本：

```text
Python
PyQt6 / Qt
numpy
sounddevice / PortAudio
ctranslate2
sentencepiece
faster-whisper
onnxruntime
tokenizers
PyAV
```

不能复用 Windows `.venv`。

Whisper 和 OPUS-MT 目录是模型数据，优先直接复用 Windows 已准备的副本。只有实测证明格式不兼容时才重新准备模型。

### 6. 创建 Mac 原生环境

先阅读 `install_mac.sh`，确认它仍符合当前文件内容，然后执行：

```bash
chmod +x install_mac.sh start_mac.sh
./install_mac.sh
```

原脚本可能仍安装当前默认路径不使用的兼容依赖。除非它们造成安装失败，不要为了清理依赖而扩大修改范围。

麦克风测试不要求 BlackHole。若脚本只警告 BlackHole 缺失，可以继续；本阶段不测试系统音频捕获。

## Mac 分阶段验证

不要一开始就运行完整 GUI。严格按照 A 到 D 的顺序验证。

### Test A：Python 与原生依赖

```bash
./.venv/bin/python -c "import platform; print(platform.machine())"
./.venv/bin/python -c "import PyQt6, sounddevice, numpy, ctranslate2, sentencepiece, faster_whisper; print('core imports: OK')"
./.venv/bin/python -c "import ctranslate2; print(ctranslate2.__version__)"
./.venv/bin/python -c "from faster_whisper import WhisperModel; print('faster-whisper import: OK')"
./.venv/bin/python -c "import sounddevice as sd; print(sd.query_devices())"
```

必须确认 Python 进程为 `arm64`，而不是通过 Rosetta 使用 x86_64 环境。

### Test B：完全本地翻译

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
./.venv/bin/python -c "from translator import Translator; print(Translator().translate('Today we are testing the translation system.'))"
```

预期得到合理的简体中文。此过程不得访问 OpenAI、Ollama 或任何远程 HTTP 服务。

也可以运行内置的两句验收：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
./.venv/bin/python translator.py
```

### Test C：项目内 base.en 加载

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
./.venv/bin/python -c "from transcriber import Transcriber; t=Transcriber(backend='whisper', model_size='base.en', device='cpu', compute_type='int8', language='en'); t.warmup(); print('base.en offline load: OK')"
```

日志中的模型路径应指向：

```text
models/faster-whisper-base.en
```

不应重新下载模型或访问 Hugging Face。

随后用 Mac 麦克风说：

```text
Hello, this is a test.
```

确认 `base.en` 能得到合理英文文本。

### Test D：完整程序

```bash
./start_mac.sh
```

在 Dashboard 中选择麦克风，点击 `Launch Translator`，验证：

```text
麦克风
↓
英文实时 partial subtitle
↓
停顿后 final transcription
↓
本地 OPUS-MT
↓
简体中文字幕
↓
Overlay
```

首次访问麦克风时，macOS 可能弹出权限提示。若程序正常启动但没有音频，先检查：

```text
System Settings
→ Privacy & Security
→ Microphone
```

先区分权限问题和 PortAudio/sounddevice 问题，不要立即修改 `AudioCapture`。

### Test E：离线启动

不必真的拔网线。使用：

```bash
PIP_NO_INDEX=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_OFFLINE=1 \
./start_mac.sh
```

确认 ASR 与翻译均从项目内模型目录加载。日志中不应出现：

```text
huggingface.co 下载
OpenAI 请求
Ollama 请求
其他远程 HTTP 请求
```

## Mac 修改规则

每次修改前，Mac Codex 必须先说明：

```text
问题是什么
Windows 为什么正常
Mac 为什么失败
准备修改哪个文件
预计修改多少行
是否影响 Windows
是否存在更小的修复
```

优先 1～10 行平台判断或兼容修复。必要时使用：

```python
if platform.system() == "Darwin":
    ...
```

不要直接替换已经通过验证的 Windows 路径。

已知历史问题：旧版 `transcriber.py` 的 MLX 初始化附近曾有无意义的 `sssss`。当前 Windows checkpoint 已删除该字符。Mac Codex 仍应先查看实际文件，不要凭旧说明重复修改。

## Mac 验收结果模板

完成后必须按以下格式报告：

```text
Mac 测试结果

[PASS/FAIL] Apple Silicon arm64 Python
[PASS/FAIL] 程序启动
[PASS/FAIL] 麦克风
[PASS/FAIL] base.en 本地加载
[PASS/FAIL] 英文实时字幕
[PASS/FAIL] final transcription
[PASS/FAIL] OPUS-MT 本地翻译
[PASS/FAIL] 简体中文字幕
[PASS/FAIL] Overlay
[PASS/FAIL] 离线运行
```

随后列出：

```text
修改过哪些文件
每个文件为什么修改
Windows 是否受影响
Mac 安装命令
Mac 启动命令
```

全部通过后停止开发，不进入打包阶段。

## Mac Codex 还必须创建 `使用说明.md`

Mac 实机验证全部通过后，在仓库根目录创建：

```text
使用说明.md
```

这份文档面向普通用户，不是开发日志，至少包括：

```text
1. 支持的 Mac 与 macOS/Apple Silicon 要求
2. 首次安装步骤
3. 如何启动程序
4. 如何授权麦克风
5. 如何选择输入设备
6. 如何开始和停止字幕
7. 两句快速验收语音
8. 如何确认离线运行
9. 常见问题：无声音、无字幕、权限、模型缺失
10. 当前仅支持英文语音到简体中文
11. 当前固定使用 base.en
12. 不需要 OpenAI API 或 Ollama
```

文档中的命令和界面名称必须来自 Mac 实机验证结果，不能在 Windows 上猜测。

## 第三阶段路线：封装成 Mac 小软件

Mac 第二阶段全部通过后，可以单独进入第三阶段，目标是：

```text
当前可运行源码
→ 可双击启动的 realtime-subtitle.app
→ 可选的 .dmg 安装镜像
```

理想交付体验：

```text
普通用户不需要安装 Python
双击 .app 即可启动
模型随应用或资源目录一起分发
首次启动提示麦克风权限
运行期间完全离线
```

`.app` 必须在 macOS 上使用 Mac 原生依赖构建，不能直接使用 Windows 产物。打包阶段需要单独处理资源路径、模型目录、Qt 插件、麦克风权限描述、签名和 Gatekeeper 行为。

当前阶段只记录这一目标，不执行：

```text
PyInstaller
.app
.dmg
codesign
notarization
Apple Developer 配置
```

等 Mac 源码版全部通过后，再为打包阶段单独制定方案。

## License

MIT License。原项目版权信息见 [LICENSE](LICENSE)。
