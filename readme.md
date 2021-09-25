# Weibo Spider

## Introduction

本项目爬取微博数据信息，包含

- 用户身份信息：昵称，性别，年龄
- 用户关系信息：followers以及fans
- 用户社交信息：发博，评论，点赞等

## How it works

微博站点分为三种

- WAP站: weibo.cn
- 移动站：m.weibo.cn
- 桌面站点: weibo.com

本项目通过微博移动站相关api获取社交数据信息并使用tkinter可视化展示

## Get started

1. 安装依赖 python -r requirements
2. 获取cookie信息 替换config.py中cookies字段
3. 启动可视化 python visualize.py

# Reference

    https://github.com/nghuyong/WeiboSpider
