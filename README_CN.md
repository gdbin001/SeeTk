
SeeTk

基于 Python + Tkinter 3.8 开发的可视化界面快速开发工具，支持拖拽生成 UI、控件属性编辑、事件绑定与项目管理，零代码 / 低代码快速生成桌面应用界面。
功能特性

    🖱️ 可视化拖拽编辑：直接拖动控件到画布，所见即所得
    🧩 丰富控件面板：支持按钮、文本框、标签、容器等常用组件
    ⚙️ 属性可视化配置：宽高、颜色、字体、位置一键修改
    📁 项目管理：新建、保存、打开项目，方便持续开发
    📝 自动生成代码：编辑完成可导出对应 Python 界面代码
    🌍 多语言支持：支持界面语言切换
    🎯 右键菜单 / 快捷键：提升开发效率

技术栈

    语言：Python
    UI 框架：Tkinter
    模式：可视化拖拽 + 代码生成

快速运行

    克隆本项目

bash
运行

git clone https://github.com/gdbin001/SeeTk.git
cd SeeTk

    启动主程序

bash
运行

python main.py

项目结构
plaintext

SeeTk/
├── main.py                 # 程序入口
├── CustomNotebook.py       # 自定义标签页
├── codeTxt.py              # 代码编辑/展示
├── editorPropertyList.py   # 属性列表
├── eventRsp.py             # 事件响应
├── menuBar.py              # 主菜单
├── newPrj.py               # 新建项目
├── widgetPanel.py          # 控件面板
├── widgetProperty.py       # 控件属性
├── default.ini                # 配置文件
├── ico/                    # 图标资源
├── cmm.py       # 公共文件
├── dragCan.py       # 界面文件
├── menuRight.py       # 右键菜单
├── oprMenu.py       # 制作菜单
├── selectedCanvas.py       # 控件组件
├── tooltip.py       # 按钮提示
└── language/               # 语言文件

使用说明

    打开软件 → 新建项目→输入项目名称，选好存放文件夹→点击模式转换按钮（有2个相反箭头的大按钮），转换成图形模式
    右击界面空白处→添加控件→点击控件→选择布局方式，添加到编辑区
    左侧修改控件属性
    右击控件→绑定事件
    转换成文本模式可以编写代码
    保存项目 

适用场景

    快速制作 Tkinter 界面原型
    学习 Python GUI 开发
    小型桌面工具快速开发
    教学演示可视化编程

版本更新

    修复新建项目相关问题
    优化控件创建与交互逻辑

作者
gdbin001项目地址：https://github.com/gdbin001/SeeTk