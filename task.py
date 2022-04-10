#!/usr/bin/env python3
# coding=utf-8

import os
import re
import subprocess
import json
import shutil
import requests

from pathlib import Path
from loguru import logger

from lake2md import lake_to_md, get_pic
from dotenv import dotenv_values

user_config = dotenv_values(".env")

class Config:
    def __init__(self, prefix):
        try:
            pwd = Path(__file__).absolute()
            file_path = Path(pwd).parent / 'config.json'
            with open(file_path, 'r') as f:
                config = json.load(f)
            self.config = config
            if prefix in config.keys():
                self.basedir = config[prefix].get('basedir', user_config.get('BASEDIR', Path.home()))
                self.desdir = config[prefix].get('desdir', user_config.get('DESDIR', Path.home()))
                self.workdir = config[prefix].get('workdir', user_config.get('WORKDIR', Path.home()))
                self.cmd = config[prefix]['cmd']
                self.conf = config[prefix]['conf']
            else:
                logger.debug("配置不正确")
        except OSError as e:
            logger.exception(e)

    def deploy(self):
        if self.cmd != '':
            os.chdir(self.workdir)
            return subprocess.Popen(self.cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
        else:
            logger.debug("命令为空")


def init_cmd(gen, workdir, desdir):
    if gen == 'hugo':
        if Path(workdir).exists():
            os.chdir(Path(workdir))
        else:
            workdir.mkdir(parents=True, exist_ok=True)
            os.chdir(Path(workdir))
        subprocess.call("hugo new site .",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
        Path(desdir).mkdir(parents=True, exist_ok=True)
        logger.info("初始化一个HUGO博客")
        theme_url = 'https://github.com/AmazingRise/hugo-theme-diary.git'
        command = ["git", "clone", theme_url, Path(workdir, 'themes', 'diary')]
        subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        Path(workdir, 'config.toml').write_text(Path(workdir, 'themes', 'diary', 'exampleSite', 'config.toml').read_text())
        os.chdir(Path(workdir))
        subprocess.call(["hugo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    else:
        logger.info("没有初始化命令")
        pass
    
    
def init_conf(prefix):
    gen = user_config.get('GEN', '')
    basedir = user_config.get('BASEDIR', Path.home())
    workdir = user_config.get('WORKDIR', Path(basedir, prefix))
    desdir = user_config.get('DESDIR', Path(basedir, prefix, 'content', 'posts'))
    conf = {
        prefix: {
            "basedir": str(basedir),
            "desdir": str(desdir),
            "workdir": str(workdir),
            "cmd": gen,
            "conf": {
                "html": True,
                "shortcode": False
            } 
        }
    }
    pwd = Path(__file__).absolute()
    file_path = Path(pwd).parent / 'config.json'
    config = Path(file_path).read_text(encoding='utf-8')
    config_dict = json.loads(config)
    if prefix not in config_dict:
        config_dict.update(conf)
        json.dump(config_dict, file_path.open('w+'), indent = 6)
        logger.info("为{}初始化一个配置文件", prefix)
        init_cmd(gen, workdir, desdir)
        logger.info("网站部署完成")
    else:
        logger.info("{}存在一个配置文件，没有更新", prefix)
        pass


def init_web(doc, prefix):
    doc_list = doc.split('---')
    
    config = Config(prefix) 
    # # 处理主题 
    var_list = list(filter(None, doc_list[0].split('\n')))[1:-1]
    # logger.debug(var_list)
    var_dict = {}
    for line in var_list:
        v = line.split('=')
        var_dict.update({v[0]: v[1]})
    theme_dir = Path(config.workdir, 'themes', var_dict['theme'])
    if Path(theme_dir).exists():
        logger.info("主题文件存在，不处理")
    else:
        logger.info("下载主题{}", var_dict['theme'])
        command = ["git", "clone", var_dict['theme_url'], Path(config.workdir, 'themes', var_dict['theme'])]
        subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

    # 处理配置文件
    conf_list = list(filter(None, doc_list[1].split('\n')))
    if conf_list[0] == '```yaml':
        Path(config.workdir, 'config.yaml').write_text('\n'.join(conf_list[1:-1]))
    else:
        Path(config.workdir, 'config.toml').write_text('\n'.join(conf_list[1:-1]))
    
    # 处理静态文件
    logger.info("静态文件夹为{}", var_dict['staticdir'])
    static_path = Path(config.workdir, var_dict['staticdir'])
    static_list = list(filter(None, doc_list[2].split('\n')))
    logger.debug(static_list)
    if len(static_list) == 0:
        pass
    else:
        for line in static_list:
            cap, url = get_pic(line)
            resp = requests.get(url)
            Path(static_path, cap).write_bytes(resp.content)
    config.deploy()
    logger.info("部署网站配置完成！")

def delete_namespace(namespace):
    pwd = Path(__file__).absolute()
    file_path = Path(pwd).parent / 'config.json'
    with open(file_path, 'r') as f:
        config = json.load(f)
    if namespace in config:
        try:
            shutil.rmtree(Path(config[namespace]['workdir']))
            del config[namespace]
            json.dump(config, Path(file_path).open('w+'), indent = 6)
            logger.info("{}已经删除了", namespace)
        except IOError as e:
            logger.exception(e)
    else:
        pass
        logger.info("{}不存在", namespace)

def publish_doc(slug, doc, title, prefix):
    config = Config(prefix)
    try:
        md_doc = lake_to_md(doc, title)
        Path(config.desdir, title + '.md').write_text(md_doc)
        logger.info("写入了一篇新的文章：{}", title)
    except IOError as e:
        logger.exception(e)
    
    if Path(config.workdir, prefix + '.json').exists():
        conf = Path(config.workdir, prefix + '.json').read_text(encoding='utf-8')
        conf_dict = json.loads(conf)
        logger.debug("配置文件为:{}", conf_dict)
        if slug not in conf_dict:
            conf_dict.update({slug: title })
            json.dump(conf_dict, Path(config.workdir, prefix + '.json').open('w+'), indent = 6)
            logger.info("知识库{}发布了一遍名为<<{}>>的文章并已部署！", prefix, title)
        else:
            pass
            logger.info("知识库{}更新了一遍名为<<{}>>的文章并已部署！", prefix, title)
    else:
        conf_dict = {slug: title}
        json.dump(conf_dict, Path(config.workdir, prefix + '.json').open('w+'), indent = 6)
        logger.info("配置文件为空,设置为新的文件") 
    config.deploy()


def delete_doc(slug, title, prefix):
    config = Config(prefix)
    try:
        conf = Path(config.workdir, prefix + '.json').read_text(encoding='utf-8')
        conf_dict = json.loads(conf)
        logger.debug("配置文件为:{}", conf_dict)
    except IOError as e:
        logger.exception(e)
        conf_dict = {}
        logger.info("配置文件为空,设置为新的文件")

    if slug in conf_dict:
        file_path = Path(config.desdir, conf_dict[slug] + '.md')
        Path(file_path).unlink()
        del conf_dict[slug]
        json.dump(conf_dict, Path(config.workdir, prefix + '.json').open('w+'), indent = 6)
        logger.info("知识库{}删除了一篇名为<<{}>>的文章!", prefix, title)
    else:
        logger.info("文档可能已经移动，无法获取位置")
    config.deploy()

   
if __name__ == '__main__':
    init_conf(os.environ['NAMESPACE']) 
    # init_conf('cccc')  
    # init_web("```bash\ngen=hugo\ntheme=LoveIt\ntheme_url=https://github.com/dillonzq/LoveIt.git\nstaticdir=themes\n```\n\n---\n\n```toml\nbaseURL = \"http://example.org/\"\n# [en, zh-cn, fr, ...] 设置默认的语言\ndefaultContentLanguage = \"zh-cn\"\n# 网站语言, 仅在这里 CN 大写\nlanguageCode = \"zh-CN\"\n# 是否包括中日韩文字\nhasCJKLanguage = true\n# 网站标题\ntitle = \"我的全新 Hugo 网站\"\n\n# 更改使用 Hugo 构建网站时使用的默认主题\ntheme = \"LoveIt\"\n\n[params]\n# LoveIt 主题版本\nversion = \"0.2.X\"\n\n[menu]\n[[menu.main]]\nidentifier = \"posts\"\n# 你可以在名称 (允许 HTML 格式) 之前添加其他信息, 例如图标\npre = \"\"\n# 你可以在名称 (允许 HTML 格式) 之后添加其他信息, 例如图标\npost = \"\"\nname = \"文章\"\nurl = \"/posts/\"\n# 当你将鼠标悬停在此菜单链接上时, 将显示的标题\ntitle = \"\"\nweight = 1\n[[menu.main]]\nidentifier = \"tags\"\npre = \"\"\npost = \"\"\nname = \"标签\"\nurl = \"/tags/\"\ntitle = \"\"\nweight = 2\n[[menu.main]]\nidentifier = \"categories\"\npre = \"\"\npost = \"\"\nname = \"分类\"\nurl = \"/categories/\"\ntitle = \"\"\nweight = 3\n\n# Hugo 解析文档的配置\n[markup]\n# 语法高亮设置 (https://gohugo.io/content-management/syntax-highlighting)\n[markup.highlight]\n# false 是必要的设置 (https://github.com/dillonzq/LoveIt/issues/158)\nnoClasses = false\n\n```\n\n---\n\n![avatar.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1649596432324-692f5c93-1f8c-4a86-94f6-bb0f48c2da6a.png#clientId=udebfdf32-6ca6-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u9f1e44df&margin=%5Bobject%20Object%5D&name=avatar.png&originHeight=640&originWidth=640&originalType=binary&ratio=1&rotation=0&showTitle=false&size=34002&status=done&style=none&taskId=u2cc0debc-cb3f-46b2-a20e-3faab5dc9a1&title=)\n\n![uTools_1648054722512.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1649596451630-f3824cbb-946a-412a-8984-646531584981.png#clientId=udebfdf32-6ca6-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u2ded442e&margin=%5Bobject%20Object%5D&name=uTools_1648054722512.png&originHeight=857&originWidth=1693&originalType=binary&ratio=1&rotation=0&showTitle=false&size=73815&status=done&style=none&taskId=u2a545784-171f-4889-ba02-175b6e348aa&title=)\n","zjan-bwcmnq") 