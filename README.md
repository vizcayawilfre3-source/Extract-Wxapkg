# wxapkg-
通过低版本微信获取小程序wxapkg后解包出源码

先安装低版本微信https://github.com/tom-snow/wechat-windows-versions/releases/tag/v3.9.12.57  
使用这个启动器启动https://github.com/Skyler1n/WeChat3.9-32bit-Compatibility-Launcher  

打开低版本微信加载小程序，先打开需要解包的小程序，然后看  
C:\Users\你的用户名\Documents\WeChat Files\Applet  
这个文件夹，里面文件格式是  

Applet/  
  ├── publicLib/          ← 公共库（所有小程序共享）  
  │     └── {版本号}/  
  │           └── clientPublicLib.wxapkg  
  │  
  └── {小程序AppID}/      ← 每个小程序一个文件夹  
        └── {版本号}/  
              └── __APP__.wxapkg    ← 小程序主包  

如果不知道小程序appid就在微信的设置清空缓存，再打开目标小程序，这个文件夹里面仅剩的wx开头的文件夹里面就是这个小程序的wxapkg文件  

wxid（密钥）是小程序文件夹的名称，例如 C:\Users\xiaomao\Documents\WeChat Files\Appletwx8c1d34a9ecc36262，这个文件夹里面的wxapkg文件密钥就是wx8c1d34a9ecc36262  

解包后内容格式  

output/  
  ├── app-config.json         ← 小程序配置（页面路由、窗口样式等）  
  ├── app-service.js          ← 全局业务逻辑  
  ├── app.js.js               ← App() 入口  
  ├── app.json                ← 原始配置  
  ├── page-frame.html         ← 页面框架模板  
  ├── @babel/runtime/helpers/ ← babel 转译辅助函数  
  ├── pages/                  ← 各页面（.html + .js.js + .json）  
  ├── components/             ← 自定义组件（如有）  
  ├── utils/                  ← 工具函数  
  ├── images/                 ← 图片资源  
  ├── miniprogram_npm/        ← npm 依赖  
  └── weui-miniprogram/       ← WeUI 组件库  
