#!/usr/bin/env python3
# coding=utf-8

import datetime
import re

from loguru import logger

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

def get_third(line):
    pattern = re.compile(r'\(https\S+\)')
    third_url = re.search(pattern, line)[0].lstrip('(').rstrip(')')

    padding = '75%'
    if 'player.bilibili.com' in line:
        url = third_url + '&high_quality=1'
    elif 'music.163.com' in line:
        padding = '12%'
        url = third_url
    else:
        url = third_url
    html = f'<div style="position:relative; width:100%; padding-bottom:{padding};" ><iframe class="responsive-iframe" src="{url}"  scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" style="position:absolute; height:100%; width:100%;" ></iframe></div>'
    
    return html

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
    logger.debug("文档的内容：{}", md_list)    

    doc_list = []
    file_path = ''
    for line in md_list:
        if line.startswith('path'):
            file_path = line.split(':')[1].strip()
        elif line.startswith('!['):
            img_cap, img_url = get_pic(line)
            img = f'<img src="{img_url}" alt="{img_cap}" referrerPolicy="no-referrer" />'
            doc_list.append(img)
            doc_list.append('\n')
        elif 'www.yuque.com/attachments' in line:
            attachment_url = get_attachment(line)
            doc_list.append(attachment_url)
            doc_list.append('\n')
        elif '点击查看' in line or 'doc_embed' in line:
            html = get_third(line)
            # new_line = f'{{{{< iframe url={third_url} >}}}}'
            doc_list.append(html) 
            doc_list.append('\n')
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
    doc = "```yaml\nauthors: Janz\ndescription: \"渲染的文档支持的情况\"\ntags: [yuque]\nfeatured_image: \"\"\ncategories: [备忘]\ncomment: true\n```\n<a name=\"n3o4h\"></a>\n## Markdown语法支持\n<a name=\"nfG7E\"></a>\n### 引用\n> 这是引用\n\n<a name=\"bK2Zv\"></a>\n### 标题\n<a name=\"M9CEv\"></a>\n# H1\n<a name=\"xw2h7\"></a>\n## H2\n<a name=\"Zstha\"></a>\n### H3\n<a name=\"WK1GK\"></a>\n### 段落和换行\n这是第一段<br />这是第二段<br />只是第三段\n<a name=\"t80ib\"></a>\n### 强调\n**粗体**<br />_斜体_\n<a name=\"Y7su0\"></a>\n### 有序列表\n\n1. list1\n1. list2\n1. list3\n<a name=\"oIjar\"></a>\n### 无序列表\n\n- 1\n- 2\n- 3\n<a name=\"tKqBt\"></a>\n### 行内代码\n`$ import this`\n<a name=\"yI4zy\"></a>\n### 代码块\n```python\n$ import this\n```\n<a name=\"Gj0Wn\"></a>\n### 分割线\n\n---\n\n\n<a name=\"BFYHs\"></a>\n### 链接\n[语雀](https://www.yuque.com)\n<a name=\"X4p2o\"></a>\n### 图片（目前语雀图片可以外链）\n![image.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1650354661417-899a0b51-affe-477a-bf4c-7119ec759efd.png#clientId=u65d4eb71-e486-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=ufc2e3c2b&margin=%5Bobject%20Object%5D&name=image.png&originHeight=635&originWidth=847&originalType=url&ratio=1&rotation=0&showTitle=false&size=1577767&status=done&style=none&taskId=u173a44da-fa07-49ff-8a7f-bbd5d55228d&title=)\n\n<a name=\"TDv5x\"></a>\n### 表格(不支持合并和颜色)\n| A | B | C |\n| --- | --- | --- |\n| 1 | 2 | 3 |\n| 4 | 5 | 6 |\n\n\n<a name=\"G87GM\"></a>\n## 特色卡片支持（图片）\n<a name=\"dfPR6\"></a>\n### 画板\n![](https://cdn.nlark.com/yuque/0/2022/jpeg/243852/1650355235302-512596f2-78b8-4534-be1b-b5924979fcc1.jpeg)\n<a name=\"fVSMK\"></a>\n### 思维导图\n![](https://cdn.nlark.com/yuque/0/2022/jpeg/243852/1650355236275-7c134b90-03f4-4f43-8729-79720bde69f5.jpeg)\n<a name=\"ARLFH\"></a>\n### 流程图\n![](https://cdn.nlark.com/yuque/0/2022/jpeg/243852/1650355237366-9584f5ed-6f25-4ddc-96c3-baea0d4e891e.jpeg)\n<a name=\"ImA2b\"></a>\n### UML图\n![](https://cdn.nlark.com/yuque/0/2022/jpeg/243852/1650355239314-0893616d-b888-4862-8f32-2eed4c4734f1.jpeg)\n<a name=\"rfcpb\"></a>\n### 文本绘图\n![](https://cdn.nlark.com/yuque/__puml/78ca87890f92981264a9de6efca9185c.svg#lake_card_v2=eyJ0eXBlIjoicHVtbCIsImNvZGUiOiJAc3RhcnR1bWxcbkFsaWNlIC0-IEJvYjogQXV0aGVudGljYXRpb24gUmVxdWVzdFxuQm9iIC0tPiBBbGljZTogQXV0aGVudGljYXRpb24gUmVzcG9uc2VcblxuQWxpY2UgLT4gQm9iOiBBbm90aGVyIGF1dGhlbnRpY2F0aW9uIFJlcXVlc3RcbkFsaWNlIDwtLSBCb2I6IEFub3RoZXIgYXV0aGVudGljYXRpb24gUmVzcG9uc2VcbkBlbmR1bWwiLCJ1cmwiOiJodHRwczovL2Nkbi5ubGFyay5jb20veXVxdWUvX19wdW1sLzc4Y2E4Nzg5MGY5Mjk4MTI2NGE5ZGU2ZWZjYTkxODVjLnN2ZyIsImlkIjoiVGxNTTgiLCJtYXJnaW4iOnsidG9wIjp0cnVlLCJib3R0b20iOnRydWV9LCJjYXJkIjoiZGlhZ3JhbSJ9)<a name=\"rokIN\"></a>\n### 公式\n![](https://cdn.nlark.com/yuque/__latex/146ac92b6071bbb19ade94ed5065f040.svg#card=math&code=%5Csum_%7Bi%3D0%7D%5En%20i%5E2%20%3D%20%5Cfrac%7B%28n%5E2%2Bn%29%282n%2B1%29%7D%7B6%7D&id=mBKfT)\n<a name=\"KQwTO\"></a>\n## 第三方内容（利用iframe嵌入支持）\n<a name=\"AmNdp\"></a>\n### 语雀内容\n[利用语雀webhook作为静态博客的后端](https://www.yuque.com/zjan/blog/tmpkh6?view=doc_embed)\n<a name=\"c1B2H\"></a>\n### B站\n[点击查看【bilibili】](https://player.bilibili.com/player.html?aid=55895675)\n<a name=\"dhw4w\"></a>\n### 网易云音乐\n[点击查看【music163】](https://music.163.com/outchain/player?type=2&id=1420830402&auto=0&height=66)\n<a name=\"E8zz2\"></a>\n### 优酷\n[点击查看【youku】](https://player.youku.com/embed/XNDc1NDU1MTQwOA==)\n<a name=\"d2Ss8\"></a>\n### Processon\n[点击查看【processon】](https://www.processon.com/embed/5d006c43e4b071ad5a206ed2)\n<a name=\"zDpXJ\"></a>\n### 高德地图\n[点击查看【amap】](https://ditu.amap.com/)\n\n<a name=\"PpPZL\"></a>\n### 墨刀\n[点击查看【modao】](https://free.modao.cc/app/2cd26580a6717a147454df7470e7ec464093cba3/embed/v2#screen=sk71k6d1dfxulzx)\n<a name=\"rVvEZ\"></a>\n## Enjoy\n"
    print(lake_to_md(doc, 'test'))
