import os
import subprocess

# 定义输入文件夹和输出文件夹
# input_folder = 'C:/Users/MI/Desktop/download_flv'
# output_folder = 'C:/Users/MI/Desktop/download_flv'
input_folder = '/media/sd/Download'
output_folder = '/media/sd/Download'
# 遍历输入文件夹中的所有 FLV 文件
for filename in os.listdir(input_folder):
    if filename.endswith('.flv'):
        # 构造输入文件路径和输出文件路径
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename[:-4] + '.mp4')

        # 使用 FFMPEG 进行转换
        subprocess.run(['ffmpeg', '-i', input_path, '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-c:a', 'copy', output_path])