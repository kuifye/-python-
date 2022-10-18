#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
from PyInstaller.__main__ import run
#  -F:打包成一个EXE文件
#  -w:不带console输出控制台，window窗体格式
#  --paths：依赖包路径
#  --icon：图标
#  --noupx：不用upx压缩
#  --clean：清理掉临时文件
 
if __name__ == '__main__':
    opts = ['-F',
            #'--paths=D:\\Program Files\\Python\\Lib\\site-packages\\PyQt5\\Qt\\bin',
            #'--paths=D:\\Program Files\\Python\\Lib\\site-packages\\jpype',
            #'--noupx',
            #'--clean',
            #'--hidden-import=numpy',
            'Minions.py']
    run(opts)
