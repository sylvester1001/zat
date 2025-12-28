# scrcpy 二进制文件

请从 [scrcpy releases](https://github.com/Genymobile/scrcpy/releases) 下载对应平台的预编译包，并将以下文件放置在此目录：

## Windows
- `scrcpy.exe`
- `scrcpy-server` (必须)
- `adb.exe` (可选，如果系统 PATH 中没有)

## macOS / Linux
- `scrcpy`
- `scrcpy-server` (必须)
- `adb` (可选，如果系统 PATH 中没有)

## 注意事项

1. `scrcpy-server` 是必须的，它会被 push 到 Android 设备上运行
2. 确保文件有执行权限 (Linux/macOS): `chmod +x scrcpy`
3. 打包时这些文件会被一起打包进应用
