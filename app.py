#!/usr/bin/env python3
# coding=utf-8

import uvicorn

from pathlib import Path
from loguru import logger
from fastapi import FastAPI, BackgroundTasks

from task import publish_doc, delete_doc,  init_conf

app = FastAPI()

@app.post("/yuque", status_code=200)
def yuque(data: dict, namespace: str, background_tasks: BackgroundTasks):
    # 添加日志
    pwd = Path(__file__).absolute()
    log_path  = Path(pwd).parent / 'logs'
    log_path.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(Path(log_path, namespace + '.log'), format="{time} {level} {message}", rotation="1 MB", retention="10 days", level='INFO')
    # logger.remove()
    if 'msgtype' in data and data['msgtype'] == 'markdown':
        background_tasks.add_task(init_conf, namespace)
    else:
        # 获取webhook内容
        logger.debug("webhook的内容是{}", data)
        req = data['data']   
        type = req['webhook_subject_type']
        format = req.get('format', '')
        if format == 'lake':
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


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8080)

