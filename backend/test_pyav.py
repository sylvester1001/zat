import subprocess
import av

proc = subprocess.Popen(
    ['adb', '-s', 'emulator-5554', 'exec-out', 'screenrecord', '--output-format=h264', '--time-limit', '3', '-'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print('打开容器...')
try:
    container = av.open(proc.stdout, format='h264')
    print(f'容器已打开: {container}')
    
    count = 0
    for frame in container.decode(video=0):
        count += 1
        print(f'帧 {count}: {frame.width}x{frame.height}')
        if count >= 5:
            break
    print(f'成功解码 {count} 帧')
except Exception as e:
    print(f'错误: {e}')
finally:
    proc.terminate()
