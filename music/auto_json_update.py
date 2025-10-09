import os
import re
import subprocess
import shutil
import sys


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

# 找文件
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

# 错误命名音乐列表
error_title_music_list = []

# 没有音乐源的音乐列表
not_exist_source = []
# 没有封面的音乐列表
not_exist_pic = []
# 没有歌词的音乐列表
not_exist_lrc = []

# 源不规范命名
not_specify_source = []
# 图片不规范命名
not_specify_pic = []
# 歌词不规范命名
not_specify_lrc = []

# 音乐列表
music_info_list = None

# 判断空
def check_null(str):
    return str is None or str == ''

# 获取音乐信息 
# music = {
#    "title": music_name,
#    "author": music_author,
#    "url": music_path + audio_files[0],
#    "pic": music_path + pic_files[0],
#    "lrc": music_path + lrc_files[0]
#}
def get_music_info():
    music_info_list = []

    music_folder = './music_info_list'
    music_path_pre = '/music/music_info_list'
    dirs = os.listdir(music_folder)

    # 判断是否按照标准命名 音乐名_作者
    valided = True

    for dir in dirs:
        
        if not ('_' in dir):
            valided = False
            error_title_music_list.append(dir)
        else: 
            infos = dir.split('_')
            music_name = infos[0]
            music_author = infos[1]
            if (check_null(music_name) or check_null(music_author)):
                valided = False
                error_title_music_list.append(dir)
            else:
                # 打印信息
                print(infos)
                music_path = music_path_pre + '/' + dir + '/'

                music_folder_real = music_folder + '/' + dir
                # 查找音频文件
                audio_files = find_files(music_folder_real, audio_extensions)
                # 查找封面
                pic_files = find_files(music_folder_real, image_extensions)
                # 查找歌词
                lrc_files = find_files(music_folder_real, lrc_extensions)

                # 存在判断 & 规范判断
                if (len(audio_files) == 0):
                    valided = False
                    global not_exist_source
                    not_exist_source.append(dir)
                else:
                    if '_' in audio_files[0]:
                        global not_specify_source
                        not_specify_source.append(dir)
                if (len(pic_files) == 0):
                    valided = False
                    global not_exist_pic
                    not_exist_pic.append(dir)
                else:
                    if '_' in pic_files[0]:
                        global not_specify_pic
                        not_specify_pic.append(dir)
                if (len(lrc_files) == 0):
                    valided = False
                    global not_exist_lrc
                    not_exist_lrc.append(dir)
                else:
                    if '_' in lrc_files[0]:
                        global not_specify_lrc
                        not_specify_lrc.append(dir)

                # music_path = music_path.replace('_', '\_')
                if valided:
                    music = {
                        "title": music_name,
                        "author": music_author,
                        "url": music_path + audio_files[0],
                        "pic": music_path + pic_files[0],
                        "lrc": music_path + lrc_files[0]
                    }
                    music_info_list.append(music)

    # 是否存在缺失文件
    if (len(not_exist_source) != 0 or len(not_exist_pic) != 0 or len(not_exist_lrc) != 0):
        print('没有音乐源：', not_exist_source)
        print('没有封面：', not_exist_pic)
        print('没有歌词：', not_exist_lrc)
        valided = False

    # 是否存在命名不规范
    if (len(not_specify_source) != 0 or len(not_specify_pic) != 0 or len(not_specify_lrc) != 0):
        print('音乐源命名不规范：', not_specify_source)
        print('封面命名不规范：', not_specify_pic)
        print('歌词命名不规范：', not_specify_lrc)
        valided = False

    if valided:
        return music_info_list
    else:
        return None

# 获取音乐列表json信息
def get_music_json_str():
    res = ''

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

# 判断规范
def check_specify():
    print('获取所有音乐信息 start--')
    global music_info_list
    music_info_list = get_music_info()
    print('获取所有音乐信息 end--')

    if music_info_list is None:
        print('存在音乐信息命名不规范，取消执行，错误命名音乐列表信息如下：')
        print(error_title_music_list)
        # 正常退出程序
        sys.exit()

check_specify()

copy_file_example()

auto_create_json_file()