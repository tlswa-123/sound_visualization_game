#!/usr/bin/env python3
"""
将 mp4 视频转换为 gif 动图
"""

import os
import subprocess
import sys

def convert_mp4_to_gif(input_file, output_file, fps=10, scale=640):
    """
    使用 ffmpeg 将 mp4 转换为 gif
    如果没有 ffmpeg，尝试使用 imageio
    """
    
    # 方法1：尝试使用 ffmpeg（更好的质量）
    try:
        # 检查是否有 ffmpeg
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        
        # 使用 ffmpeg 转换
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'fps={fps},scale={scale}:-1:flags=lanczos,palettegen=reserve_transparent=0',
            '-y', 'palette.png'
        ]
        subprocess.run(cmd, check=True)
        
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-i', 'palette.png',
            '-filter_complex', f'fps={fps},scale={scale}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5',
            '-y', output_file
        ]
        subprocess.run(cmd, check=True)
        
        # 清理临时文件
        if os.path.exists('palette.png'):
            os.remove('palette.png')
            
        print(f"✅ 使用 ffmpeg 成功转换: {output_file}")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ ffmpeg 不可用，尝试使用 Python 库...")
    
    # 方法2：使用 imageio-ffmpeg（Python 库）
    try:
        import imageio
        
        print("📹 正在读取视频文件...")
        reader = imageio.get_reader(input_file)
        
        print("🎨 正在转换为 GIF...")
        writer = imageio.get_writer(output_file, mode='I', fps=fps)
        
        # 每隔几帧取一帧以减少文件大小
        frame_skip = max(1, int(reader.get_meta_data()['fps'] / fps))
        
        for i, frame in enumerate(reader):
            if i % frame_skip == 0:
                # 缩放图像
                if frame.shape[1] > scale:
                    import cv2
                    height = int(frame.shape[0] * scale / frame.shape[1])
                    frame = cv2.resize(frame, (scale, height))
                
                writer.append_data(frame)
        
        writer.close()
        reader.close()
        
        print(f"✅ 使用 imageio 成功转换: {output_file}")
        return True
        
    except ImportError:
        print("❌ 需要安装 imageio: pip install imageio[ffmpeg]")
        return False
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False

def main():
    input_file = "game_screenshot.mp4"
    output_file = "game_demo.gif"
    
    if not os.path.exists(input_file):
        print(f"❌ 找不到输入文件: {input_file}")
        return
    
    print(f"🎬 开始转换 {input_file} 为 {output_file}...")
    
    success = convert_mp4_to_gif(input_file, output_file, fps=5, scale=480)
    
    if success:
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"🎉 转换完成！文件大小: {file_size:.1f} MB")
        
        if file_size > 10:
            print("⚠️ GIF 文件较大，如需优化可以降低 fps 或 scale 参数")
    else:
        print("❌ 转换失败")

if __name__ == "__main__":
    main()