#!/usr/bin/env python3
# coding=utf-8

import os
import re
import subprocess
import json
import zipfile
import requests

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
    commamd = ["git", "clone", var_dict['theme_url'], Path(config.workdir, 'themes', var_dict['theme'])]
    subprocess.call(commamd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

    # 处理配置文件
    conf_list = list(filter(None, doc_list[1].split('\n')))
    if conf_list[0] == '```yaml':
        Path(config.workdir, 'config.yaml').write_text('\n'.join(conf_list[1:-1]))
    else:
        Path(config.workdir, 'config.toml').write_text('\n'.join(conf_list[1:-1]))
    
    # 处理静态文件
    static_path = Path(config.workdir, var_dict['staticdir'])
    # attachment_format = 'zip|mp4|rar|html|7z|ai|mov|m4a|wmv|avi|flv|chm|wps|rtf|aac|htm|xhtml|rmvb|asf|m3u8|mpg|flac|dat|mkv|swf|m4v|webm|mpeg|mts|3gp|f4v|dv|m2t|mj2|mjpeg|mpe|ogg'
    # p_url = re.compile(fr'https://www.yuque.com/attachments/yuque/\d/\d{{4}}/({attachment_format})/\d{{6}}/\w+-\w+-\w+-\w+-\w+-\w+.({attachment_format})', re.I)
    # attachment_url = re.search(p_url, list(filter(None, doc_list[2].split('\n')))[0])[0]
    # logger.debug(attachment_url)
    # resp = requests.get("https://www.yuque.com/attachments/yuque/0/2022/zip/243852/1649585814297-a951d6bc-7e3e-4977-b8de-4ea15bdfa424.zip?_lake_card=%7B%22src%22%3A%22https%3A%2F%2Fwww.yuque.com%2Fattachments%2Fyuque%2F0%2F2022%2Fzip%2F243852%2F1649585814297-a951d6bc-7e3e-4977-b8de-4ea15bdfa424.zip%22%2C%22name%22%3A%22static.zip%22%2C%22size%22%3A299481%2C%22type%22%3A%22application%2Fx-zip-compressed%22%2C%22ext%22%3A%22zip%22%2C%22status%22%3A%22done%22%2C%22taskId%22%3A%22u704c20a9-49d1-4dbc-98cc-192bef5e96e%22%2C%22taskType%22%3A%22upload%22%2C%22id%22%3A%22u2fb9b168%22%2C%22card%22%3A%22file%22%7D", stream=True)
    # file_name = Path(config.workdir, static_path, 'static.zip')
    # with open(file_name, 'wb') as f:
    #     for chunk in resp.iter_content(chunk_size=1024): #边下载边存硬盘
    #         if chunk:
    #             f.write(chunk)
    # # Path(config.workdir, static_path, 'static.zip').write_bytes(resp.content)
    # zip_file = zipfile.ZipFile(Path(config.workdir, static_path, 'static.zip'))
    # zip_extract = zip_file.extractall()
    # zip_extract.close()
    config.deploy()

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
    # init_conf('cccc')  
    init_web("```bash\ngen=hugo\ntheme=LoveIt\ntheme_url=https://github.com/dillonzq/LoveIt.git\nstaticdir=themes\n```\n\n---\n\n```toml\nbaseURL = \"http://example.org/\"\n# [en, zh-cn, fr, ...] 设置默认的语言\ndefaultContentLanguage = \"zh-cn\"\n# 网站语言, 仅在这里 CN 大写\nlanguageCode = \"zh-CN\"\n# 是否包括中日韩文字\nhasCJKLanguage = true\n# 网站标题\ntitle = \"我的全新 Hugo 网站\"\n\n# 更改使用 Hugo 构建网站时使用的默认主题\ntheme = \"LoveIt\"\n\n[params]\n# LoveIt 主题版本\nversion = \"0.2.X\"\n\n[menu]\n[[menu.main]]\nidentifier = \"posts\"\n# 你可以在名称 (允许 HTML 格式) 之前添加其他信息, 例如图标\npre = \"\"\n# 你可以在名称 (允许 HTML 格式) 之后添加其他信息, 例如图标\npost = \"\"\nname = \"文章\"\nurl = \"/posts/\"\n# 当你将鼠标悬停在此菜单链接上时, 将显示的标题\ntitle = \"\"\nweight = 1\n[[menu.main]]\nidentifier = \"tags\"\npre = \"\"\npost = \"\"\nname = \"标签\"\nurl = \"/tags/\"\ntitle = \"\"\nweight = 2\n[[menu.main]]\nidentifier = \"categories\"\npre = \"\"\npost = \"\"\nname = \"分类\"\nurl = \"/categories/\"\ntitle = \"\"\nweight = 3\n\n# Hugo 解析文档的配置\n[markup]\n# 语法高亮设置 (https://gohugo.io/content-management/syntax-highlighting)\n[markup.highlight]\n# false 是必要的设置 (https://github.com/dillonzq/LoveIt/issues/158)\nnoClasses = false\n\n```\n\n---\n\n[static.zip](https://www.yuque.com/attachments/yuque/0/2022/zip/243852/1649585814297-a951d6bc-7e3e-4977-b8de-4ea15bdfa424.zip?_lake_card=%7B%22src%22%3A%22https%3A%2F%2Fwww.yuque.com%2Fattachments%2Fyuque%2F0%2F2022%2Fzip%2F243852%2F1649585814297-a951d6bc-7e3e-4977-b8de-4ea15bdfa424.zip%22%2C%22name%22%3A%22static.zip%22%2C%22size%22%3A299481%2C%22type%22%3A%22application%2Fx-zip-compressed%22%2C%22ext%22%3A%22zip%22%2C%22status%22%3A%22done%22%2C%22taskId%22%3A%22u704c20a9-49d1-4dbc-98cc-192bef5e96e%22%2C%22taskType%22%3A%22upload%22%2C%22id%22%3A%22u2fb9b168%22%2C%22card%22%3A%22file%22%7D)\n","zjan-bwcmnq") 