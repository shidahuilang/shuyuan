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
