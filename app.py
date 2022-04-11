#!/usr/bin/env python3
# coding=utf-8

import json
import uvicorn

from pathlib import Path
from loguru import logger
from fastapi import FastAPI, BackgroundTasks

from task import publish_doc, delete_doc, init_web, delete_namespace, create_namespace


# 添加日志
pwd = Path(__file__).absolute()
log_path  = Path(pwd).parent / 'logs'
log_path.mkdir(parents=True, exist_ok=True)
logger.remove()
logger.add(Path(log_path, 'yuque' + '.log'), format="{time} {level} {message}", rotation="1 MB", retention="10 days", level='INFO')


app = FastAPI()

@app.post("/yuque", status_code=200)
def yuque(data: dict, namespace: str, code: str, background_tasks: BackgroundTasks, action: str = ''):
    
    config_path = Path(pwd).parent / 'config.json'
    config = json.load(Path(config_path).open('r'))

    if 'msgtype' in data and data['msgtype'] == 'markdown':
        if action == 'debug':
            logger.remove()
            logger.add(Path(log_path, namespace + '.log'), format="{time} {level} {message}", rotation="1 MB", retention="10 days", level='DEBUG')
            logger.debug("已为{}启用DEBUG", namespace)
        elif action == 'new':
            logger.info("为{}准备新建一个网站", namespace)
            if namespace not in config:
                background_tasks.add_task(create_namespace, namespace, code)
            else:
                logger.info("{}已经有一个配置文件", namespace)
                config[namespace]['code'] = code
                json.dump(config, Path(config_path).open('w'), indent = 6)
                logger.info("{}已经配置文件已经更新", namespace)
        elif action == 'deleted':
            if namespace in config and config[namespace]['code'] == code:   
                logger.info("{}配置文件准备删除！", namespace)
                background_tasks.add_task(delete_namespace, namespace)
            else:
                logger.info("{}不匹配，不做任何操作！", namespace)
                logger.debug("namespace:{}, code:{}", namespace, code)
        else:
            logger.debug("action: {}, namespace:{}, code:{}", action, namespace, code)
    elif namespace in config and config[namespace]['code'] == code:   
        # 获取webhook内容
        logger.debug("webhook的内容是{}", data)
        req = data['data']   
        type = req['webhook_subject_type']
        format = req.get('format', '')
        if format == 'lake':
            if req['title'] == '_blog_config':
                logger.info("为{}更新网站的配置", namespace)
                background_tasks.add_task(init_web, req['body'], namespace)
            else:
                if type == 'publish':
                    background_tasks.add_task(publish_doc, req['slug'], req['body'], req['title'], namespace)
                elif type == 'update':
                    background_tasks.add_task(publish_doc, req['slug'], req['body'], req['title'], namespace)
                else:
                    logger.debug("未知的请求TYPE")
            return {"msg": "收到了Webhook的请求！"}
        elif type == 'comment_create' and req['actor_id'] == req['commentable']['user_id']:
                background_tasks.add_task(delete_doc, req['commentable']['slug'], req['commentable']['title'], namespace)
        else:
            logger.debug("目前不支持的格式")
            return {"msg": "不支持解析的格式！"}
    else:
        logger.debug("namespace:{}, code:{}",  namespace, code)
        pass


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8080)

