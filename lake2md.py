#!/usr/bin/env python3
# coding=utf-8

import datetime
import re

from loguru import logger


# date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
# logger.add('test.log', format="{time} {level} {message}", level="INFO")

def get_pic(line):
    p_cap = re.compile(r'\[.*]', re.I)
    media_cap = re.search(p_cap, line)[0].lstrip('[').rstrip(']')
    if ' ' in media_cap:
        media_cap = media_cap.replace(' ', '')
    else:
        pass
    logger.debug("图片的信息：{media_cap}")
    if 'svg' in line:
        p_m = re.compile(r'https://cdn.nlark.com/yuque/\w+/\w{32}\.svg')
        media_url = re.search(p_m, line)[0]
        logger.debug("画板的地址：{media_url}")
    else:
        p_url = re.compile(r'https://cdn.nlark.com/yuque/\d/\d{4}/(png|jpeg|gif)/\d{6}/\w+-\w+-\w+-\w+-\w+-\w+.(png|jpeg|gif)', re.I)
        media_url = re.search(p_url, line)[0]
        logger.debug("图片的地址：{media_url}")
    # return f'<img src="{media_url}" alt="{media_cap}" referrerPolicy="no-referrer" />  '
    return media_cap, media_url


def get_attachment(line):
    if 'www.yuque.com/attachments' in line:
        logger.debug("附件的地址：{line}")
        p_cap = re.compile(r'\[.*]', re.I)
        attachment_cap = re.search(p_cap, line)[0].lstrip('[').rstrip(']')
        if ' ' in attachment_cap:
            attachment_cap = attachment_cap.replace(' ', '')
        else:
            pass
        attachment_format = 'zip|mp4|rar|html|7z|ai|mov|m4a|wmv|avi|flv|chm|wps|rtf|aac|htm|xhtml|rmvb|asf|m3u8|mpg|flac|dat|mkv|swf|m4v|webm|mpeg|mts|3gp|f4v|dv|m2t|mj2|mjpeg|mpe|ogg'
        p_url = re.compile(fr'https://www.yuque.com/attachments/yuque/\d/\d{{4}}/({attachment_format})/\d{{6}}/\w+-\w+-\w+-\w+-\w+-\w+.({attachment_format})', re.I)
        attachment_url = re.search(p_url, line)[0]
        attachment = f'[{attachment_cap}]({attachment_url})'
    else:
        attachment = line
    return attachment


def lake_to_md(doc, title):
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        if '<br />' in doc:
            d_list = doc.replace('<br />', '  \n')
            md_list = list(filter(lambda x: not x.startswith('<a'), d_list.split('\n')))
        else:
            md_list = list(filter(lambda x: not x.startswith('<a'), doc.split('\n')))
    except IndexError as e:
        logger.info("文档为空，不渲染！")
        logger.error(e)
    logger.debug("文档的内容：{md_list}")    

    doc_list = []
    file_path = ''
    for line in md_list:
        if line.startswith('path'):
            file_path = line.split(':')[1].strip()
        elif line.startswith('!['):
            img_cap, img_url = get_pic(line)
            img = f'<img src="{img_url}" alt="{img_cap}" referrerPolicy="no-referrer" />  '
            doc_list.append(img)
        elif 'www.yuque.com/attachments' in line:
            attachment_url = get_attachment(line)
            doc_list.append(attachment_url)
        else:
            doc_list.append(line)
    
    if doc_list[0] == '---':
        doc_list.insert(1, f"title: {title}")
        doc_list.insert(2, f"date: {date}")
    elif doc_list[0] == '```yaml':
        doc_list[0] = '---'
        index = doc_list[1:].index('```')
        doc_list[index+1] = '---'
        doc_list.insert(1, f"title: {title}")
        doc_list.insert(2, f"date: {date}")
    else:
        doc_list.insert(0, '---')
        doc_list.insert(1, f'title: {title}')
        doc_list.insert(2, f'date: {date}')
        doc_list.insert(3, '---')      
    
    logger.debug("Markdown的文档内容为：{}", '\n'.join(doc_list))
    return '\n'.join(doc_list), file_path


if __name__ == '__main__':
    doc = "```yaml\nauthors: Janz\ndescription: \"退格到头会闪屏\"\ntags: [Terminal, git]\nfeatured_image: \"\"\ncategories: [备忘]\ncomment: true\n```\n> 退格到头会闪屏，很影响很用的体验。\n\n<a name=\"XQshe\"></a>\n## 现象\n![2022-04-19-11-43-53.gif](https://cdn.nlark.com/yuque/0/2022/gif/243852/1650340327735-75c67282-20b0-4a2c-a65f-775cdb45e7ac.gif#clientId=u36625fcf-7cfd-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=ud9dbf4c9&margin=%5Bobject%20Object%5D&name=2022-04-19-11-43-53.gif&originHeight=724&originWidth=1420&originalType=binary&ratio=1&rotation=0&showTitle=false&size=4008225&status=done&style=none&taskId=u09b0458a-9718-46ac-9308-4b12b820982&title=)\n<a name=\"Vz1bi\"></a>\n## 解决\n`$ echo \"set bell-style none\" >> ~/.inputrc`\n<a name=\"ZfaKa\"></a>\n## 参考\n\n- [Github Issue](https://github.com/microsoft/terminal/issues/7200#issuecomment-672786518)\n"
    print(lake_to_md(doc, 'test'))
