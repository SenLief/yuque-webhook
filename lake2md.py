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
            img = f'<img src="{img_url}" alt="{img_cap}" referrerPolicy="no-referrer" />  '
            doc_list.append(img)
        elif 'www.yuque.com/attachments' in line:
            attachment_url = get_attachment(line)
            doc_list.append(attachment_url)
        elif '点击查看' in line or 'doc_embed' in line:
            html = get_third(line)
            # new_line = f'{{{{< iframe url={third_url} >}}}}'
            doc_list.append(html) 
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
    doc = "```yaml\ntags: [test, yuque]\n```\n下面是b站<br />[点击查看【bilibili】](https://player.bilibili.com/player.html?bvid=BV1tq4y1e7RW)<br />下面是musicdfsggsdfg fdsgd  dsfasfdsdfsadfsdfsdafsd  <br />[点击查看【music163】](https://music.163.com/outchain/player?type=2&id=1420830402&auto=0&height=66)<br />下面是附件sdfsdfsdfsdfasdfsdfsdf   fsdfsadfsaf<br />[favicon_package_v0.16.zip](https://www.yuque.com/attachments/yuque/0/2022/zip/243852/1648913657004-5f256593-4400-4b63-a139-fdf0e5f3e6af.zip?_lake_card=%7B%22src%22%3A%22https%3A%2F%2Fwww.yuque.com%2Fattachments%2Fyuque%2F0%2F2022%2Fzip%2F243852%2F1648913657004-5f256593-4400-4b63-a139-fdf0e5f3e6af.zip%22%2C%22name%22%3A%22favicon_package_v0.16.zip%22%2C%22size%22%3A247603%2C%22type%22%3A%22application%2Fx-zip-compressed%22%2C%22ext%22%3A%22zip%22%2C%22status%22%3A%22done%22%2C%22taskId%22%3A%22ueddaf3ee-1665-4f3b-bafb-d74835d8b14%22%2C%22taskType%22%3A%22upload%22%2C%22id%22%3A%22u4f63386d%22%2C%22card%22%3A%22file%22%7D)<br />下面是导图<br />![](https://cdn.nlark.com/yuque/0/2022/jpeg/243852/1648914842615-69be76e4-6e4a-4bd4-965a-6f0ae1b77930.jpeg)<br />下面是文本绘图asdfsadfsd   sdfasdsd  sdfasdfs    dsfsdfssdfasdfsdfsadfsdf  sfdsadfsadfs\n![](https://cdn.nlark.com/yuque/__puml/9f5560730e769f3fe0fe8387247e9beb.svg#lake_card_v2=eyJ0eXBlIjoicHVtbCIsImNvZGUiOiJAc3RhcnR1bWxcblA6IFBFTkRJTkdcblA6IFBlbmRpbmcgZm9yIHJlc3VsdFxuXG5OOiBOT19SRVNVTFRfWUVUXG5OOiBEaWQgbm90IHNlbmQgdGhlIEtZQyBjaGVjayB5ZXQgXG5cblk6IEFQUFJPVkVEXG5ZOiBLWUMgY2hlY2sgc3VjY2Vzc2Z1bFxuXG5SOiBSRUpFQ1RFRFxuUjogS1lDIGNoZWNrIGZvdW5kIHRoZSBhcHBsaWNhbnQncyBcblI6IGluZm9ybWF0aW9uIG5vdCBjb3JyZWN0IFxuXG5YOiBFWFBJUkVEXG5YOiBQcm9vZiBvZiBBZGRyZXNzIChQT0EpIHRvbyBvbGRcblxuWypdIC0tPiBOIDogQ2FyZCBhcHBsaWNhdGlvbiByZWNlaXZlZFxuTiAtLT4gUCA6IFN1Ym1pdHRlZCB0aGUgS1lDIGNoZWNrXG5QIC0tPiBZXG5QIC0tPiBSXG5QIC0tPiBYIDogUHJvb2Ygb2YgQWRkcmVzcyAoUE9BKSB0b28gb2xkXG5QIC0tPiBYIDogZXhwbGljaXRseSBieSBLWUNcblkgLS0-IFsqXVxuUiAtLT4gWypdXG5YIC0tPiBbKl1cbkBlbmR1bWwiLCJ1cmwiOiJodHRwczovL2Nkbi5ubGFyay5jb20veXVxdWUvX19wdW1sLzlmNTU2MDczMGU3NjlmM2ZlMGZlODM4NzI0N2U5YmViLnN2ZyIsImlkIjoiaXdUVFQiLCJtYXJnaW4iOnsidG9wIjp0cnVlLCJib3R0b20iOnRydWV9LCJjYXJkIjoiZGlhZ3JhbSJ9)nwr123<br />[点击查看【canva】](https://www.canva.cn/design/DAD3c63mhHU/view?embed)<br />[点击查看【processon】](https://www.processon.com/embed/5d006c43e4b071ad5a206ed2)<br />[重构内容解析](https://www.yuque.com/zjan/bwcmnq/buhn9d?view=doc_embed)\n"
    print(lake_to_md(doc, 'test'))
