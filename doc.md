源阅读配置
打开源阅读，我的 -> 语音管理 -> 右上角 -> 创建语音，名称自己起，内容先粘贴这个：
```sh
https://baidu.com/api/aiyue?text={{speakText}}&voiceName=zh-CN-XiaoxiaoNeural&speed={{speakSpeed*4}},{
    "method": "GET",
    "headers": {"authorization": "Bearer TOKEN"}
}
```
将 baidu.com 改为第一步里的网址（如果是 ip+ 端口的形式还要把 https 改成 http）

zh-CN-XiaoxiaoNeural 可以改成其他语音，可以去搭好的网页上选一个（不一定所有的都能用，要先测试一下），名字就是对应的“配置名称”里括号中的英文。

如果设置了 TOKEN，在配置中把 TOKEN 这五个字母替换为你的 token，没设的不用管。

保存，测试。

打开爱阅书香，进入设置 ->听书 ->自定义语音库 ->创建

名称：任意
合成字数：建议 200
请求方式：GET
地址：第一步里获取的网址，后边加上 /api/aiyue，最终填进去的应该形如 http://baidu.com/api/aiyue，或者 https://设置好的域名(以我为例便是/baidu.com)/api/aiyue。记得点右上角的保存
参数 ->添加 ->请输入请求参数：text，内容填%@
解析字段 ->添加 ->请输入解析字段与规则：playData，内容填 ResponseData
如果在之前部署时选择了使用 TOKEN，则 Http 配置 ->自定义 HTTP 头 ->添加 ->请输入 HTTP 协议头信息：authorization，内容填 Bearer 你的token ，比如说你的 TOKEN 是 example,则内容填 Bearer example，设置完回到刚刚的页面。没有设置 TOKEN 的不用管这一步
可选：参数 ->添加 ->请输入请求参数：voiceName，内容填自己想要的人声（参考 这里），不添加这个参数的话默认 zh-CN-XiaoxiaoNeural
