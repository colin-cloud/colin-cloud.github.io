import os
import re
import subprocess
import shutil


file_head = "title:\ndate:\ntags:\ncategories:\nkeywords:\ndescription:\ntop_img:\ncomments:\ncover:\ntoc:\ntoc_number:\ncopyright:\nmathjax:\nkatex:\nhide:\naplayer: true\n"

file_import_resource = [
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/aplayer@1.10/dist/APlayer.min.css">',
    '<script src="https://cdn.jsdelivr.net/npm/aplayer@1.10/dist/APlayer.min.js"></script>',
    '<link rel="stylesheet" href="/music/css/custom.css">'
]

json_head = '{% aplayerlist %}'

tab = '    '
json_body_start = '{\n'+tab+'"narrow": false,\n'+tab+'"autoplay": false,\n'+tab+'"mode": "order",\n'+tab+'"showlrc": 3,\n'+tab+'"mutex": true,\n'+tab+'"theme": "#e6d0b2",\n'+tab+'"preload": "metadata",\n'+tab+'"listmaxheight": "513px",\n'+tab+'"music": [\n'
json_body_end = ']\n}\n{% endaplayerlist %}'
json_start = '{\n'
json_end = '}' 
tab_2 = '            '

music_info_list = []


def find_files(dir, extensions):
    """
    查找指定目录及其子目录中的指定文件
    
    参数:
        dir(str): 要搜索的目录路径
        extensions(arr): 后缀
        
    返回:
        list: 文件列表
    """
    
    files_list = []
    
    # 递归遍历目录
    for root, dirs, files in os.walk(dir):
        for file in files:
            # 获取文件扩展名（小写）
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                files_list.append(file)
    
    return files_list

# 定义常见的音频文件扩展名
audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', 
                    '.aac', '.wma', '.alac', '.ape', '.opus'}
# 定义常见的图片文件扩展名（小写）
image_extensions = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
    '.tiff', '.webp', '.svg', '.ico', '.jfif'
}
# 定义歌词扩展名
lrc_extensions = {
    '.lrc'
}

def get_music_info():
    music_info_list = []

    music_folder = './music_info_list'
    music_path_pre = '/music/music_info_list'
    dirs = os.listdir(music_folder)
    print(dirs)
    for dir in dirs:

        infos = dir.split('_')
        print(infos)
        music_name = infos[0]
        music_author = infos[1]
        music_path = music_path_pre + '/' + dir + '/'

        music_folder_real = music_folder + '/' + dir
        # 查找音频文件
        audio_files = find_files(music_folder_real, audio_extensions)
        # 查找封面
        pic_files = find_files(music_folder_real, image_extensions)
        # 查找歌词
        lrc_files = find_files(music_folder_real, lrc_extensions)
        music = {
            "title": music_name,
            "author": music_author,
            "url": music_path + audio_files[0],
            "pic": music_path + pic_files[0],
            "lrc": music_path + lrc_files[0]
        }
        music_info_list.append(music)
    return music_info_list


def get_music_json_str():
    res = ''

    print('获取所有音乐信息 start--')
    music_info_list = get_music_info()
    print('获取所有音乐信息 end--')

    list_len = len(music_info_list)
    print('音乐数：' + str(list_len))

    for i in range(list_len):
        music_info = music_info_list[i]
        json_str = json_start + tab_2 + '"title": "' + music_info['title'] + '",\n' + tab_2 + '"author": "' + music_info['author'] + '",\n' + tab_2  + '"url": "' + music_info['url'] + '",\n' + tab_2  + '"pic": "' + music_info['pic'] + '",\n' + tab_2  + '"lrc": "' + music_info['lrc'] + '"\n' + json_end
        res += json_str
        if i != list_len - 1:
            res += ','
        res += '\n'
    return res


# 创建文件
def auto_create_json_file():
    try:
        # 打开文件并写入内容
        with open(f"index.md", "w", encoding="utf-8") as file:
            # 写入md头
            print("写入文件头 start---")
            file.write(f"---\n{file_head}---\n")
            print("写入文件头 end---")

            # 写入引入资源
            print("引入资源 start---")
            for i in range(len(file_import_resource)):
                resource_line = file_import_resource[i]
                file.write(f"\n{resource_line}\n")
            print("引入资源 end---")

            # 写入json头
            print("写入json头 start---")
            file.write(f"\n{json_head}")
            print("写入json头 end---")

            # 写入json body
            print("写入json body start---")
            file.write(f"\n{json_body_start}")

            print("获取音乐json信息 start---")
            json_str = get_music_json_str()
            print("获取音乐json信息 end---")

            file.write(f"{json_str}")
            file.write(f"{json_body_end}")
            print("写入json body start---")
        
        print(f"成功创建 Markdown 文件: index.md")
        
    except Exception as e:
        print(f"创建文件时出错: {e}")

# 备份文件
def copy_file_example():
    # 源文件路径
    source = "index.md"
    # 目标文件路径
    destination = "index-copy.md"
    
    
    # 1. 基本复制（仅复制内容，不保留元数据）
    try:
        shutil.copy(source, destination)
        print("备份成功~")
    except Exception as e:
        print(f"备份失败: {e}")


copy_file_example()

auto_create_json_file()