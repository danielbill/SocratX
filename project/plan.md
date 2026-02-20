## 快速原型 Rapid Prototype 

### RP - 001 ： 启动桌面
- 启动SocratX
- 出现独立的、非浏览器窗口的桌面应用窗口
- 应用应该已经有了基础样式
- 窗口中至少有一个对话框
- 应用窗口应该是完全定制的样式，不得出现windows原生的header

### RP - 002 : 完成一次对话
- 完成AI调用配置： 当前配置GLM-4.7 
- 启动SocratX，用户输入：你好
- SocratX 注入系统提示
- AI回复：你好，我是SocratX
- 要求：
  - 创建后台统一的logger，单例，后台统一使用
  - 建立三个log文件
    - SocratX.log 记录SocratX及系统的信息
    - conversation 记录通话内容
    - ai.log 单独记录云端AI的信息



