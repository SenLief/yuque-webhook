# yuque-webhook
利用webhook让语雀成为后端编辑器。

> 尽量减少繁琐的事情，专注于书写

## 特点

* 利用语雀的webhook功能，无需token
* 在语雀端即可完成基本的操作，无需配置服务器
    * 文档的编辑、更新和删除
    * hugo网站的配置以及主题的更换（无法实时自定义主题）
* 支持大部分语雀编辑器的功能
    * 文本
    * 图片（利用img标签处理外链）
    * 思维导图，流程图，画板等
    * 附件（语雀更改了附件的规则，需要登录下载了）
    * B站和网易云（计划支持，主要是主题的不统一）
* 支持多知识库，多人协作

## 尝试一下 
托管于我自己的服务器上，请注意因为是webhook推送的文件，你的文档我可以看到，请不要push私密的文档。  

1. 语雀新建一个文档知识库
    - 知识库的namespace为`zjan/blog`
    - namespace可以在网页的url中获取，比如`https://www.yuque.com/zjan/bwcmnq那么知识库的namespace为zjan/bwcmnq `
2. 知识库右边有个三个点的知识库设置——更多设置——高级设置
    - 开启自动发布去掉勾
    - 自动发布无法触发wehhook
3. 知识库右边有个三个点的知识库设置——更多设置——消息推送
4. 选择其他渠道
    - 机器人名字：任意即可，比如`blog`
    - Webhook地址：`https://webhook.529213.xyz/yuque?&namespace=<user>-<repo>&code=<任意字符串>&action=new`
        - `<user>`: 上面的zjan
        - `<repo>`: 上面的bwcmnq
        - `code`: 任意的字符串，比如abc123
        - 例如：`https://webhook.529213.xyz/yuque?&namespace=zjan-bwcmnq&code=abc123&action=new ` 
    - 动态推送勾选以下几个后点击添加
        - 发布文档
        - 更新文档
        - 新增评论（用于拉起删除文档的webhook）
    - 点击已添加推送中的测试操作
    - 稍等30s  

![](https://vip1.loli.io/2022/04/12/wSEqBOmQj3YCeRv.png)

5. 访问`https://<user>-<repo>.529213.xyz`看看效果，例如我的`https://zjan-bwcmnq.529213.xyz`
6. Enjoy！不出意外已经初始化好一个hugo生成的网站了，你可以在本知识库下编写文档了，和正常书写hugo文档一样，也可以使用Front Matter，当你编写完的时候点击发布稍等就可以看到已经渲染好了。
7. 本编文档即为语雀编写，你可以看下对比的效果
    - [语雀](https://www.yuque.com/zjan/blog/tmpkh6)
    - [博客](https://senlief.xyz/posts/%E5%88%A9%E7%94%A8%E8%AF%AD%E9%9B%80webhook%E4%BD%9C%E4%B8%BA%E9%9D%99%E6%80%81%E5%8D%9A%E5%AE%A2%E7%9A%84%E5%90%8E%E7%AB%AF/)

## 安装
[](https://senlief.xyz/posts/%E5%88%A9%E7%94%A8%E8%AF%AD%E9%9B%80webhook%E4%BD%9C%E4%B8%BA%E9%9D%99%E6%80%81%E5%8D%9A%E5%AE%A2%E7%9A%84%E5%90%8E%E7%AB%AF/)