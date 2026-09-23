# Windows 使用说明

本程序将麦克风听到的英语实时识别为英文字幕，并在停顿后显示简体中文翻译。识别和翻译使用项目内的本地模型；正常使用不需要 OpenAI API 或 Ollama。目前固定使用 `base.en` 识别英语，翻译方向为英语到简体中文。

## 首次安装

1. 准备 Windows 10 或 11、Python 3.10 或 3.11。安装 Python 时勾选 **Add Python to PATH**。首次安装 Python 依赖和获取模型需要网络。
2. 安装 Git for Windows 和 Git LFS。如果项目已经在本机，直接进入项目目录；如果还没有项目，可在 PowerShell 中执行：

   ```powershell
   git lfs install
   git clone https://github.com/Jin-Zhenxi/local_Translate.git
   cd local_Translate
   git lfs pull
   ```

3. 在包含 `install_windows.bat` 的项目目录运行安装脚本：

   ```powershell
   .\install_windows.bat
   ```

   脚本会在缺少 `config.ini` 时创建配置，在模型缺失时尝试通过 Git LFS 获取模型，并建立 `.venv` 安装依赖。出现 **Installation Complete!** 后再启动程序。第一次安装可能需要一些时间。

> 已有本地项目时，打开该目录的 PowerShell，直接执行第 3 步即可。请勿用缺少 Git LFS 模型文件的源码压缩包代替完整项目。

## 启动并查看字幕

1. 在项目目录运行：

   ```powershell
   .\start_windows.bat
   ```

2. 等待 **Real-Time Translator - Control Center** 控制面板打开。首次启动时，启动器还会检查 Python 依赖。
3. 打开 **Audio** 页，在 **Input Device** 中选择要使用的麦克风。若 **Auto (Default)** 对应的就是该麦克风，可以保持默认。点击右下角 **Save Settings**；界面提示保存后，请重新启动程序，使设置生效。
4. 回到 **Home** 页，点击 **▶ Launch Translator**。模型加载完成后，控制面板会最小化，屏幕右侧出现字幕悬浮窗。
5. 对麦克风说英语，例如：**Hello, this is a test.** 英文会先实时显示；说完稍作停顿后，同一条字幕下方会出现中文。英文现在是接近中文的白色，透明度略低一些。

悬浮窗可以拖动位置，右下角可以调整大小。点击 **💾 Save** 会把当前记录保存到项目目录的 `transcripts` 文件夹。点击悬浮窗中的 **⏹**，或在控制面板点击 **⏹ Stop Translator**，可停止字幕。关闭控制面板会退出程序。

## 常见问题

### 没有英文字幕

- 确认系统已允许桌面应用访问麦克风：Windows 11 在 **设置 → 隐私和安全性 → 麦克风**，Windows 10 在 **设置 → 隐私 → 麦克风**。
- 在 **Audio → Input Device** 选择正确的输入设备，点击 **Save Settings**，然后重新启动程序。设备列表没有更新时，点击旁边的 **🔄**。
- 如果已选对设备仍没有字幕，检查麦克风是否能在 Windows 的声音设置中收到声音，并查看启动窗口是否有音频设备错误。

### 有英文，没有中文

说完一句后稍作停顿，让程序形成完整语句并翻译。若始终没有中文，查看启动窗口中的报错，并确认 `models/opus-mt-en-zh-int8/model.bin` 存在且不是 Git LFS 指针文件。

### 提示模型缺失或文件太小

在项目目录运行：

```powershell
git lfs install
git lfs pull
```

然后重新运行 `install_windows.bat`。两个模型文件应分别位于 `models/faster-whisper-base.en/model.bin` 和 `models/opus-mt-en-zh-int8/model.bin`。

### 启动时提示找不到虚拟环境

先运行 `install_windows.bat`，等待依赖安装完成，再运行 `start_windows.bat`。

### 想给视频、会议或游戏声音加字幕

默认输入是麦克风。要采集电脑播放的声音，需要另外安装并配置 VB-CABLE 等虚拟音频设备，把系统声音送入虚拟输入，再在 **Audio → Input Device** 选择该输入设备。此项不是麦克风字幕的必需步骤。

## 离线使用

模型和 Python 依赖安装完成后，英语识别与中文翻译都在本机完成。启动器每次打开时仍会执行依赖检查，因此首次安装和缺少依赖时可能需要联网；日常识别和翻译不调用在线翻译服务。
