#!/usr/bin/env python3
# coding=utf-8

import os
import subprocess
import json

from pathlib import Path
from loguru import logger

from lake2md import lake_to_md
from dotenv import dotenv_values

user_config = dotenv_values(".env")

class Config:
    def __init__(self, prefix):
        self.prefix = prefix
        try:
            pwd = Path(__file__).absolute()
            file_path = Path(pwd).parent / 'config.json'
            with open(file_path, 'r') as f:
                config = json.load(f)

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
    else:
        logger.info("{}存在一个配置文件，没有更新", prefix)
        pass


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
    # init_doc('zjan-bwcmnq') 
    init_conf('cccc')   