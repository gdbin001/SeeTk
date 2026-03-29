import tkinter as tk
import os
from tkinter import ttk,messagebox
import bisect
import gettext

filePath=[]#列表中的值：[[filePath1,py文件内容,{所有控件属性},{所有控件对象},edited],[filePath2...],...]。
#所有控件属性是字典 {控件名1：{属性名1:[值,'string'],属性名2:[值,'string']...},控件名2:{...}...}。如果是button等控件，有'command':['','']属性。
#其中有'bind'事件绑定属性，例如'bind'：['"<Double-3>",lambda event:Entry_3_Double3(event)',...]。
#“所有控件对象”是纯粹控件，没有移动canvas(cvsGUI特殊)，是字典{控件名1:控件对象1,...}。edited直接是布尔值，表示是否编辑过界面。
lstSW=[]  #'lstSW'是选中的canvasWgt对象列表,可以有多个
ctrlPrs=0  #'ctrlPrs'是ctrl键是否按下
guiL=0  #'guiL'是当前控件的布局方式'place','pack','grid'
root=0  #'root'是根窗口
tree=0  #tree'是目录树
treeD=0  #是控件树
ctrlc=0  ##在text控件中复制了文本
#oldTabIdx=-1  #原来标签页的idx
#tabd2=0 #'tabd2'是界面结构面板frame
lstIEB=[]  #iid'是属性表中被选中的行[iid,entry,btn]
table=0  #'table'是属性表
rNB=0  #'rNB'是右边的Notebook
tw=0  #'tw'是提示框
btnBar=[]  #'btnBar'是工具栏中所有要禁用或者恢复的按钮对象
parser=0  #'parser'是ini文件对象
maxSN=0  #'maxSN'是控件最大编号
menuBar=0  #'menuBar'菜单栏对象
#copyWgt=[]  #copyWgt'复制或者剪切的canvasWgt对象列表
#iidSlt=0  #控件关系视图中当前选中的行iid
iidOld=0  #控件关系视图中原选中行iid
lblStt=0   #lblStt是下面状态栏frame中的label
icoFolder=0
icoFN=0
icoFile=0
uNB=0
#mtE=0  #属性表中的etrCbb显示
scbX=0
scbY=0
btnMC=0  #模式转换按钮
searchStr=''  #查找的字符串
replaceStr=''  #替换的字符串
#etrCbb=0  #属性值显示窗口
pw=0  #panedwindow

prmToRC=0  #menuRight模块中的prmToRC函数
refTree=0  #menuRight模块中的refTree函数
新建文件=0  #menuRight模块中的新建文件函数
newFile=0  #menuRight模块中的newFile函数
chooseL=0  #widgetPanel模块中的chooseL函数
reCreatW=0  #widgetPanel模块中的reCreatW函数
canParent=0  #widgetPanel模块中的能否做父控件的函数
adjPos=0  #widgetPanel模块中的调整控件次序的函数
regProp=0  #widgetPanel模块中的regProp的函数
mode_conversion=0  #menuBar模块中的模式转换函数
etrFocusOut=0  #widgetPanel模块中的etrFocusOut函数
showGUI=0  #menuBar模块中的showGUI函数
#copyNC=0  #menuBar模块中的copyNC函数
creatW=0  #widgetPanel模块中的creatW函数
#getAllNodes=0
handleEdit=0
打开文件=0
rcW=0  #rowconfigure、columnconfigure字符串参数解析
findText=0 
myDlg=0
moDir='./language'
tplTrans,tplKey=0,0
language=0  #当前语言
tplLang=0  #显示快捷键提示和部分菜单用
tplFL=(('en.mo','English'),('ko.mo','한국어'),('ja.mo','日本語'),('zh_TW.mo','繁体中文'))  #语言对应的文件,简体中文特殊
#pythonV=0  #选择的python编译器版本，空值是3.8版本
fontN,fontSz=0,0  #文本编辑器字体名称、大小
#timerColor=0  #代码上色定时器

#语言选择
def loadMF(lang):  #加载msgfmt编译后的.mo文件，返回GNUTranslations对象    
    for it in tplFL:  #根据语言类型确定mo文件
        if it[1]==lang:
            lang=it[0]
            break
    mo_path=0
    if os.path.exists(f"{moDir}/{lang}"): mo_path=f"{moDir}/{lang}"  #加载目标语言mo文件
    elif os.path.exists(f"{moDir}/en.mo"): mo_path=f"{moDir}/en.mo"  #目标语言不存在，加载英文mo文件
    if mo_path:
        with open(mo_path, 'rb') as f:# 打开.mo文件并解析
            return gettext.GNUTranslations(f)
    return 0   # 极端情况：英文mo文件也加载失败
def initLg(sltLg='en'):  #语言选择初始化。./是执行Python脚本时，所在的那个文件夹。简体中文不初始化
    global tplTrans,tplKey,tplLang
    mof= loadMF(sltLg) # 加载.mo文件，如果文件不存在则加载en.mo      
    if not mof:  messagebox.showerr('Fatal error','The language file en.mo is missing in the {modir} directory and cannot be initialized.！') 
    tplTrans = sorted(mof._catalog.items(), key=lambda x: x[0])  #提取翻译键值对并排序
    tplTrans =tuple([(k, v) for k, v in tplTrans if isinstance(k, str) and k])  #过滤掉gettext的内置元键（如''空键，存储文件头信息）
    tplKey =tuple([item[0] for item in tplTrans])
    if language=='English':
        tplLang=(('new_project','New Project'),('undo','Undo'),('delete','Delete'),('cut','Cut'),('copy','Copy'),('paste','Paste'),
        ('save','Save Single File'),('mode_conversion','Mode Conversion'),('run','Run'),('align_left','Align Left'),
        ('align_right','Align Right'),('align_top','Align Top'),('align_bottom','Align Bottom'),
        ('distribute_horizontally_evenly','Distribute Horizontally Evenly'),('distribute_vertically_evenly','Distribute Vertically Evenly')) 
def binary_search(target_key):       #二分查找 
    idx = bisect.bisect_left(tplKey, target_key)
    return tplTrans[idx][1] if (idx < len(tplKey) and tplKey[idx] == target_key) else 0  #其他文字
def t(key, **kwargs): #翻译核心方法       
    text=key if language=='简体中文' else (binary_search(key) or key)
    return text.format(**kwargs) if kwargs else text
def setGL(idx,pN,askGl=1):  #设置父控件内的guiL。pN父控件名,askGl=1要询问布局方式，0不要
                global guiL,filePath
                total=0
                for k,v in filePath[idx][2].items():  #计算父控件中子控件的数量及布局方式
                    if k=='cvsGUI':continue
                    if v['parent'][0]==pN:
                        total+=1
                        if v.get('pack'): guiL='pack'
                        elif v.get('grid'): guiL='grid'
                        else:guiL='place'
                        break
                if total==0 and askGl:  #主界面里没有控件，则要选择布局方式
                    groupV=tk.StringVar(value='pack') #单选按钮变量,是字符型。默认值是'pack'
                    chooseL(groupV)            
                    if groupV.get()=='end':return 0 #如果返回值是end，取消剪切
                    guiL=groupV.get()  #取得选择布局结果 
                return 1  #取得了布局
def addText(idx,funcN,delBind=0):  #在源程序中加入响应函数。delBind=1删除绑定的响应函数
    global filePath
    lst=filePath[idx][1].split('\n')
    si,ei=0,0  #起始点,结束点
    for i,it in enumerate(lst):  #找到起始点,结束点
        if "def makeGUI(self" in it: si=1  #做记号
        elif ('def ' in it or '#------' in it) and si==1 : #找到响应函数区域起始点            
            if '#------' in it and not delBind:  #类里没有任何响应函数，直接加上后退出
                lst.insert(i,f'    def {funcN}:\n        pass\n') #加入事件定义语句
                filePath[idx][1] ='\n'.join(lst)  #还原代码文本
                return 0
            si=i  #响应函数区域起始点
        elif '#------' in it: #找到响应函数区域结束点
            ei=i  #响应函数区域结束点
            break    
    if delBind:  #删除绑定的函数代码
        for i in range(ei,si-1,-1):#删除该控件绑定函数代码
            if lst[i].find('def ') and funcN in lst[i]:  
                del lst[i]  #删除函数定义行  
                while 1:   #删除函数体  
                    if lst[i].find('      ')==0:  del lst[i] #删除函数体        
                    else:break
    else:  #添加响应函数
        for i in range(si,ei+1):#查看是否已经存在响应函数
            if funcN in lst[i]: return 0  #已经存在
        else:  #不存在
            lst.insert(ei,f'    def {funcN}:\n        pass\n') #添加事件定义语句
    filePath[idx][1] ='\n'.join(lst)  #还原代码文本
def showSG():#更新控件关系树
    global iidOld,filePath
    iidOld=0
    idx=rNB.index('current')  #当前index
    #fileN=os.path.basename(filePath[idx][0])  #文件名       
    treeD.delete(*treeD.get_children()) #清空树
    #清空表父节点，同时清空了其中的子节点
    nodeOne={}  #控件名：节点ID，用于快速查找父节点  
    rootNode =treeD.insert("",'end', text='root', open=1)  # 创建根节点
    for k,v in filePath[idx][2].items():  #k是控件名。创建一级目录
        if k=='cvsGUI':continue
        if v['parent'][0]=='root':#父控件是root
            nodeOne[k]= treeD.insert(rootNode,'end',text=k,open=1)   #暂时设为文件节点
    processed=0
    lstU=[]  #无法处理的节点
    while not processed:  #创建一级目录下的所有子目录
        processed=1        
        for k,v in filePath[idx][2].items():  #k是控件名
            if k=='cvsGUI':continue
            if k in nodeOne:continue  # 跳过已处理的节点和一级目录
            if v['parent'][0] in nodeOne:# 检查父节点是否已存在
                nodeOne[k]= treeD.insert(nodeOne[v['parent'][0]],'end',text=k,open=1)  #添加子目录节点
                treeD.item(nodeOne[v['parent'][0]])#修改此节点value值为'目录'
            else: # 父节点尚未处理，记录入lstU
                processed =0
                lstU.append((k,v))
    if lstU:
        a=''
        for it in lstU: a+=f'{it[0]}--{it[1]}\n'
        messagebox.showinfo(t('提示'),t('以下节点无法处理\n{}').format(a))
    for i in range(15): #在内容下方加入15行空行
            treeD.insert('', 'end',text='')
def clearSW(): #清空之前选择的控件的列表及清除手柄
        global lstSW
        for c in lstSW:  #选择的控件
            c.widget.pack(fill='both',expand=1,padx=0,pady=0)  #控件填满边界
            c.delete('all')  #删除手柄        
        lstSW.clear() 
def menuR(event,index):
    menuR =tk.Menu(tearoff=False) 
    menuR.add_command(label=t('删除'), command=lambda :delMenu(event.widget,index))  #事件响应  
    menuR.post(event.x_root, event.y_root)     # 光标位置显示菜单 
def delMenu(wgt,index):  #删除所有菜单有关的代码
    global filePath
    lst=filePath[index][1].split('\n')
    for i in range(len(lst)-1,-1,-1): #删除在此文件中所有含有menuBar的代码
        if 'menuBar' in lst[i].strip():del lst[i]
    filePath[index][1]='\n'.join(lst)
    filePath[index][4]=1  #编辑状态
    wgt.destroy()
def hasMenu(index):  #查看是否存在菜单代码
    global filePath
    lst=filePath[index][1].split('\n')
    ist=0
    for stc in lst:
        if 'import menuBar' in stc: ist+=1
        elif 'menuBar.menu' in stc: ist+=1
    fp=os.path.dirname(filePath[index][0])+'/menuBar.py'
    if os.path.isfile(fp) and ist==2:  #检查是否存在menuBar.py
        return 1
    else:return 0






   