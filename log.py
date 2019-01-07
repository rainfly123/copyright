# -*-   coding: utf-8 -*-
import os
import logging

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
# 创建Logger
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

# 创建Handler

# 终端Handler
#consoleHandler = logging.StreamHandler()
# consoleHandler.setLevel(logging.DEBUG)

# 文件Handler
fileHandler = logging.FileHandler(os.path.join(
    ROOT_PATH, 'epg.log'), mode='w', encoding='UTF-8')
fileHandler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    '[%(asctime)s %(name)s] %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# consoleHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)

# 添加到Logger中
# LOG.addHandler(consoleHandler)
LOG.addHandler(fileHandler)

