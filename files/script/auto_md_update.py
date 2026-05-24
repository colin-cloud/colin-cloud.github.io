import os
import re
import subprocess
import shutil
import sys
from typing import Dict
from pypinyin import lazy_pinyin
from enum import Enum
import configparser

# 定义枚举类-是否已读
class FileType(Enum):
    PDF = '1',
    EPUB = '0'

# 定义枚举类-是否已读
class BookReadType(Enum):
    READ = '1',
    NOT_READ = '0'

# 书籍对象 - E:\data\blog\source\files\pdf\文学类\孤独鸽 目录层 目录名格式：书名 + 可选(国家) + 可选(作者) + 可选(已读)
class BookInfo:
    def __init__(self, bookname: str, dir: str, to_dir: str, author: str, country: str, category: str, pinyin: str, read_icon: str):
        self.bookname = bookname
        self.dir = dir
        self.to_dir = to_dir
        self.author = author
        self.country = country
        self.category = category
        self.pinyin = pinyin
        self.read_icon = read_icon
        self.book_file_list: list[BookFile] = []
    def __str__(self):
        return f"类别：{self.category} | 书名：{self.bookname} | 国家：{self.country} | 作者：{self.author} | 文件目录：{self.dir} | md目录：{self.to_dir}"

# 书籍文件 - E:\data\blog\source\files\pdf\文学类\孤独鸽\孤独鸽（上）.pdf 文件层
class BookFile:
    def __init__(self, file_name: str, file_type: str, file_book_name: str, relative_md_path: str, relative_file_path: str):
        self.file_name = file_name
        self.file_type = file_type
        self.file_book_name = file_book_name
        self.relative_md_path = relative_md_path
        self.relative_file_path = relative_file_path
        self.book_info: BookInfo = None
    def __str__(self):
        return f"文件名：{self.file_name} | 文件类型：{self.file_type} | {self.book_info}"

## 路径
from_root_location = 'E:\\data\\blog\source\\files\\pdf'
from_root_location_prefix = 'E:\\data\\blog\source'
to_root_location = 'E:\\data\\blog\\source\\book\\book_list'
to_root_location_index = 'E:\\data\\blog\\source\\book'

# 默认md文件名
md_file_name = 'index.md'
config_file_name = 'config.ini'

# md文件内容格式
md_content = """---
title: %s
top_img: 
cover:
toc:
toc_number:
copyright:
mathjax:
katex:
hide: true
series: %s
password: Zhc%s0725
message: 请输入密码查看~~
---

<link rel="stylesheet" href="/book/css/book.css">



<div class="pdf-container">
  <iframe
    class="pdf-viewer"
    src="/pdfjs/web/viewer.html?file=%s#toolbar=0">
  </iframe>
</div>

"""
# 目录index.md
index_md_content = """---
title: 电子书
date: 2025-10-27 00:00:00
top_img: /files/img/1_20250928231115_27_10.jpg
cover:
toc: true
toc_number:
copyright:
mathjax:
katex:
hide:
aside: true  # 关闭右侧栏
---

<link rel="stylesheet" href="/book/css/book_list.css">

"""

# 表单格式
title_content = """
### %s
"""
table_head_content = """
| **书名** | **国籍** | **作者** | **预览** | **PDF** |
| -------- | :--: | :-----------: | :---------------------| :-------------------------|
"""
line_content = """| %s | %s | %s | %s | %s |
"""
line_md_content = """&#x1f4d6;[%s](%s)"""
line_file_content = """📙[%s](%s)"""

# 汉字转首字母
def get_first_letter(chinese):
    pinyin_list = lazy_pinyin(chinese)
    return ''.join([item[0].lower() for item in pinyin_list])


# 根据文件名获取书对应信息
def get_book_info(file_path, file_name):
    # 判断文件存在再读取
    if os.path.exists(file_path):
        # 读取
        cfg = configparser.ConfigParser()
        cfg.read(file_path, encoding="utf-8")
        return cfg.get("info", "name"), cfg.get("info", "country"), cfg.get("info", "author"), cfg.get("info", "read_icon")

    # 匹配：书名 + 可选(国家) + 可选(作者) + 可选(已读)
    pattern = r"^([^()]+?)(?:\((.*?)\))?(?:\((.*?)\))?(?:\((.*?)\))?$"
    match = re.match(pattern, file_name.strip())
    
    if not match:
        return file_name.strip(), "", "", BookReadType.NOT_READ.value
    
    book = match.group(1).strip()
    country = (match.group(2) or "").strip()
    author = (match.group(3) or "").strip()
    is_read = (match.group(4) or BookReadType.NOT_READ.value).strip()
    
    return book, country, author, '❎'

# 获取书信息
def find_book_info(from_dir, to_dir, ext = ['.pdf']):
    # 定义字典，key：类别，value：[BookInfo]
    dic: dict[str, list[BookInfo]] = {}
    # 定义数组，category - 保证顺序
    category_set: set[str] = set()
    # 定义字典，key：书名，value：[BookInfo]
    book_dic: dict[str, BookInfo] = {}
    # 递归遍历所有文件和子文件夹
    for root, dirs, files in os.walk(from_dir):
        # ✅ 强制按字母顺序 排序 子目录
        dirs.sort()
        # ✅ 强制按字母顺序 排序 文件
        files.sort()
        # 遍历所有文件
        for file in files:
            if file.lower().endswith(tuple(ext)):
                # 文件全名
                file_path = os.path.join(root, file)
                # 相对路径
                relative_location = file_path.replace(from_dir, '').replace(file, 'index.md')
                relative_dir = file_path.replace(from_dir, '').replace(f"\\{file}", '')
                # 最终路径
                to_path = to_dir + relative_dir
                # 拆分目录层级
                dirs = os.path.normpath(root).split(os.sep)
                # 取倒数第二个目录 - 类别目录
                category = dirs[-2]
                # 取倒数第一个目录 - 书籍信息目录
                bookinfo = dirs[-1]
                # print(relative_dir)
                # config.ini 文件获取书籍信息
                config_file_path = os.path.join(root, config_file_name)
                book_name, country, author, read_icon = get_book_info(config_file_path, bookinfo)
                # 获取拼音信息
                bookname_pinyin = get_first_letter(book_name)
                category_pinyin = get_first_letter(category)
    
                # 类别字典
                if not category in dic:
                    dic[category] = []
                # 获取书籍信息
                book = None
                # 书籍字典
                if not book_name in book_dic:
                    to_dir = root.replace(from_root_location, to_root_location)
                    book = BookInfo(book_name, root, to_dir, author, country, category, bookname_pinyin, read_icon)
                    book_dic[book_name] = book                 
                    dic[category].append(book)
                else:
                    book = book_dic[book_name]

                # 书籍对象添加文件对象
                # 获取文件名
                file_book_name = os.path.splitext(file)[0]
                file_suffix = os.path.splitext(file)[1]
                file_ext = file_suffix.lstrip(".").upper()
                # 文件路径变为相对路径，并将\变为/
                relative_file_path = file_path.replace(from_root_location_prefix, '').replace('\\', '/')
                md_file_path = os.path.join(book.to_dir, file_book_name)
                relative_md_path = md_file_path.replace(to_root_location_index, '').replace('\\', '/').lstrip("/")  
                book_file = BookFile(file, file_ext, file_book_name, relative_md_path, relative_file_path)
                book_file.book_info = book
                book.book_file_list.append(book_file)

                # 数组添加对象
                category_set.add(category)
                # print(f"{book_file}")
    return dic, book_dic, category_set

# 写入文件
def create_md_book(book_dic: Dict[str, BookInfo]):
    # 定义数组，category - 保证顺序
    incremental_book_list: set[str] = set()
    # 遍历字典
    for name, book in book_dic.items():
        for book_file in book.book_file_list:
            # md文件路径
            md_file_path = os.path.join(book.to_dir, book_file.file_book_name + '.md')
            # 如果不存在md目录，则创建目录
            if not os.path.exists(book.to_dir):
                os.makedirs(book.to_dir)
            # 如果文件不存在，则创建文件
            if not os.path.exists(md_file_path):
                incremental_book_list.add(book.bookname)
                with open(md_file_path, "w", encoding="utf-8") as f:
                    # md文件内容
                    content = md_content % (book_file.file_book_name, book_file.file_book_name, book.pinyin, book_file.relative_file_path)
                    # 写入文件
                    f.write(content)
    return incremental_book_list



# 写入index.md文件
def create_md_index(category_dic: Dict[str, list[BookInfo]], category_list: list[str] = []):
    # 如果不存在目录，则创建目录
    if not os.path.exists(to_root_location_index):
        os.makedirs(to_root_location_index)
    # index.md文件路径
    md_file_path = os.path.join(to_root_location_index, md_file_name)
    with open(md_file_path, "w", encoding="utf-8") as f:
        # 1.写入文件头部信息
        f.write(index_md_content)
        # 遍历数组
        for category in category_list:
            # 获取书籍信息
            book_category_list = category_dic[category]
            # 写入index.md文件
            # 2.写入表格
            ## 2.1 写入标题
            title = title_content % (category)
            f.write(title)
            ## 2.2 写入表格头
            f.write(table_head_content)
            ## 2.3 写入表格行
            for book in book_category_list:
                cur_line_md_content = ''
                cur_line_file_content = ''
                file_len = len(book.book_file_list)
                for index, book_file in enumerate(book.book_file_list):
                    # 是否添加br标签
                    br_check = index == file_len - 1
                    br_content = '' if br_check else '<br/>'
                    # 书名
                    book_content = book.bookname if file_len == 1 else book_file.file_book_name
                    md_content_file = line_md_content % (book_content, book_file.relative_md_path)
                    cur_line_md_content = f"{cur_line_md_content}{md_content_file}{br_content}"
                    file_content_file = line_file_content % (book_content, book_file.relative_file_path)
                    cur_line_file_content = f"{cur_line_file_content}{file_content_file}{br_content}"
                # 写入文件
                line = line_content % (book.read_icon + book.bookname, book.country, book.author, cur_line_md_content, cur_line_file_content)   
                f.write(line)   


if __name__ == "__main__":
    category_dic, book_name_dic, category_set = find_book_info(from_root_location, to_root_location)
    # 中文首字母排序
    category_list = sorted(list(category_set), key=lambda x: x)
    # print(category_list)
    # 创建md文件
    incremental_book_list = create_md_book(book_name_dic)
    print(f"增加书籍{len(incremental_book_list)}本：{list(incremental_book_list)}")
    # 创建index.md文件
    create_md_index(category_dic, category_list)
    print(f"总书籍{len(book_name_dic)}本")

