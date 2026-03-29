import tkinter as tk
from tkinter import Menu,ttk,messagebox
import tooltip
import menuBar  #菜单模块
import menuRight
import widgetPanel
import CustomNotebook as cnb
import configparser
import cmm,sys,time,os

cmm.prmToRC=menuRight.prmToRC  #menuRight模块中的prmToRC函数
cmm.refTree=menuRight.refTree  #menuRight模块中的refTree函数
cmm.新建文件=menuRight.新建文件  #menuRight模块中的新建文件函数
cmm.newFile=menuRight.newFile #menuRight模块中的newFile函数
#cmm.getAllNodes=menuRight.getAllNodes
cmm.打开文件=menuRight.打开文件
cmm.打开文件夹=menuBar.打开文件夹
cmm.chooseL=widgetPanel.chooseL  #widgetPanel模块中的chooseL函数
cmm.reCreatW=widgetPanel.reCreatW  #widgetPanel模块中的reCreatW函数
cmm.canParent=widgetPanel.canParent  #widgetPanel模块中的能否做父控件
cmm.adjPos=widgetPanel.adjPos  #widgetPanel模块中的调整控件次序的函数
cmm.creatW=widgetPanel.creatW  #widgetPanel模块中的creatW函数
cmm.regProp=widgetPanel.regProp  #widgetPanel模块中的regProp的函数
cmm.etrFocusOut=widgetPanel.etrFocusOut  #widgetPanel模块中的etrFocusOut函数
cmm.mode_conversion=menuBar.mode_conversion  #menuBar模块中的模式转换函数
cmm.showGUI=menuBar.showGUI  #menuBar模块中的showGUI函数
cmm.handleEdit=menuBar.handleEdit
cmm.rcW=menuBar.rcW#rowconfigure、columnconfigure字符串参数解析
#cmm.copyNC=menuBar.copyNC  #menuBar模块中的copyNC函数
class mainGUI:
    def __init__(self,root):             
        style=ttk.Style()                
        style.theme_use("winnative")  #样式
        style.configure('TSizegrip',background="#a0a0a0")
        style.configure('TNotebook', borderwidth=0, tabposition='',background="#a0a0a0")
        style.configure('TNotebook.Tab', background="#a0a0a0")
        style.map("TNotebook.Tab", background= [("selected", "lightgrey")])
        style.configure('Treeview',rowheight=20,font=(cmm.t('微软雅黑'),9),background="lightgrey")#设置所有treeview表中字体、行高 
        style.configure('Treeview.Heading',background="lightgrey")
        style.map('Treeview',
                   background=[elm for elm in style.map('Treeview',query_opt='background') if elm[:2]!=('!disabled','!selected')])
        style.configure('Vertical.TScrollbar', bd=0)
        style.configure('TPanedwindow', sashwidth=8,background="#a0a0a0")
        tBar = tk.Frame(root,height=30,background="#a0a0a0") # 创建工具栏,bg='#37474f'
        tBar.pack(side='top', fill='x')  # 将工具栏放置在窗口的顶部，并水平填充
        dct={cmm.t('新建项目'):('new_project',icoNP),cmm.t('撤销'):('undo',icoCancel),cmm.t('删除'):('delete',icoDel),
             cmm.t('剪切'):('cut',icoCut),cmm.t('复制'):('copy',icoCopy),cmm.t('粘贴'):('paste',icoPaste),
             cmm.t('保存'):('save',icoSave),cmm.t('模式转换'):('mode_conversion',icoTP),cmm.t('运行'):('run',icoRun),
             cmm.t("左对齐"):('align_left',icoLeft),cmm.t("右对齐"):('align_right',icoRight),cmm.t("上对齐"):('align_top',icoUp),
             cmm.t("下对齐"):('align_bottom',icoDown),cmm.t('水平均匀分布'):('distribute_horizontally_evenly',icoHor),
             cmm.t('垂直均匀分布'):('distribute_vertically_evenly',icoVer)}     
        bi=0        
        for k,v in dct.items():
            bi+=1
            if bi>1 and bi<7:  #撤销、删除、剪切、复制、粘贴按键
                btn=tk.Button(tBar,name=k,image=v[1],command=lambda x=v[0]: menuBar.normal(x))
            else: 
                btn=tk.Button(tBar,name=k,image=v[1],command=lambda x=v[0]:getattr(menuBar,x)())
            btn.pack(side='left', padx=5)  # 将按钮放置在工具栏的左侧，并设置内边距
            if k!=cmm.t('模式转换'):  #模式转换提示文字会影响按键灵敏度
                btn.bind('<Enter>',tooltip.showTip)
                btn.bind('<Leave>',tooltip.closeTip)       
            if k==cmm.t('模式转换'): cmm.btnMC=btn  #模式转换按钮
            if k==cmm.t('撤销'):cmm.btnBar.append(btn) #要禁用或者恢复的按钮
            if bi>9:cmm.btnBar.append(btn)  #要禁用或者恢复的按钮
        pw= ttk.PanedWindow(root,orient='horizontal')  #主panedWindow,左右结构 
        pw.pack(fill='both', expand=1) #pw放到主窗口，上下左右扩展
        cmm.pw=pw        
        pw.bind('<B1-Motion>',self.sashDrag)  # 鼠标拖动时
        pwL= tk.PanedWindow(pw,orient='vertical',sashrelief='flat',sashwidth=5,bd=0)  #pwL是上下结构的窗口
        pw.add(pwL)  #pw左边窗口放入pwL
        
        noteBook=ttk.Notebook(pwL) #pwL的上方的noteBook
        cmm.uNB=noteBook
        #noteBook.pack(fill='both',expand=1)
        tab1=tk.Frame(noteBook)
        tab3=tk.Frame(noteBook)
        noteBook.add(tab1,text=cmm.t('项目资源管理器'))
        #noteBook.add(tab2,text='控件')
        noteBook.add(tab3,text=cmm.t('控件关系'))
        #cmm.tab2=tab2
        #widgetPanel.guiCtrl() #在tab2中放置界面控件按钮                
        pwL.add(noteBook)  #pwL加入上方的noteBook
        pwL.paneconfig(noteBook,height=300)               
        #style.configure('my.Treeview', background='#cce8cf')  #自定义treeview。绿豆绿色#cce8cf 
        #style.map('my.Treeview',background=[('pressed', '!disabled', ''), ('active', '')])  #使绿豆绿背景色生效，点击文字变白色
        tree = ttk.Treeview(tab1, show='tree', selectmode="browse") #在tab1创建目录树，设置为单选模式
        cmm.tree=tree
        tree.pack(fill='both', expand=1,side='left')         
        tree.bind('<Button-3>', menuRight.treeSlt) # 打开右键菜单
        tree.bind('<Double-1>', menuRight.doubleLeft) # 双击文件图标
        tree.bind('<<TreeviewOpen>>',lambda e:menuRight.openFolder(e,cmm.icoFN)) #打开文件夹事件，设置打开文件夹图标
        tree.bind('<<TreeviewClose>>',lambda e:menuRight.closeFolder(e,cmm.icoFolder)) #关闭文件夹事件，设置关闭文件夹图标         
        scbY= tk.Scrollbar(tab1,command=tree.yview)  #Y滚动条
        scbY.pack(side='right', fill='y',expand=False)
        tree.config(yscrollcommand=scbY.set)          

        tree = ttk.Treeview(tab3, show='tree', selectmode="browse") #控件关系，设置为单选模式
        cmm.treeD=tree
        tree.pack(fill='both', expand=1,side='left')        
        scbY= tk.Scrollbar(tab3,command=tree.yview)  #Y滚动条
        scbY.pack(side='right', fill='y',expand=False)
        tree.config(yscrollcommand=scbY.set)  
        tree.bind("<Button-1>",self.on_select)  #选中某个控件
        tree.bind('<Button-3>',self.menuR) # 打开右键菜单
        #tree.tag_configure('slt',background='#0079D6')    #定义行色淡蓝色背景        

        noteBD=ttk.Notebook(pwL) #pwL的下方的noteBook  
        tabd1=tk.Frame(noteBD)
        noteBD.add(tabd1,text=cmm.t('属性'))
        pwL.add(noteBD)  #pwL的下方加入控件
        pwL.paneconfig(noteBD,height=400)    
        TreeView_50 = ttk.Treeview(tabd1,columns=("序号",'编号'),show="tree headings", displaycolumns="#all",selectmode="browse") #控件的属性表
        TreeView_50.pack(fill='both',expand=1,side='left' )
        TreeView_50.tag_configure('oddColor',background='white')    #定义奇数行色   #ccebf6       
        scbYTv50 = tk.Scrollbar(tabd1,orient=tk.VERTICAL,command = TreeView_50.yview)
        scbYTv50.pack(fill='y',expand=0,side='right')
        scbYTv50.bind("<B1-Motion>",cmm.etrFocusOut) #点击纵坐标，销毁entry、cbb、button
        TreeView_50.config(yscrollcommand = scbYTv50.set)
        TreeView_50.column('#0', width=45, stretch=0)  # 将首列不随窗口变化
        TreeView_50.column('序号',width=100,anchor='w',stretch=1)   #定义列，左对齐 
        TreeView_50.column('编号',width=90,anchor='w',stretch=1)   #定义列，左对齐 
        TreeView_50.heading('#0', text=cmm.t('分类'), anchor='w')  # 可以设置首列的标题为空
        TreeView_50.heading('序号',text=cmm.t('属性'),anchor='w')   #表头
        TreeView_50.heading('编号',text=cmm.t('值'),anchor='w')   #表头         
        TreeView_50.bind("<Button-1>",widgetPanel.one)   #单击响应函数  
        TreeView_50.bind("<MouseWheel>",cmm.etrFocusOut) #绑定滚轮滚动，销毁entry、cbb、button      
        #TreeView_50.bind("<FocusOut>",cmm.etrFocusOut) #失去焦点，销毁entry、cbb、button       
        cmm.table=TreeView_50    
                
        rNB = cnb.CustomNotebook(pw,{})  #由notebook派生而来。主右窗口
        pw.add(rNB)
        cmm.rNB=rNB        
        rNB.bind("<<NotebookTabChanged>>",widgetPanel.onTabChanged) # 绑定选项卡变化事件

        sttBar = tk.Frame(root,height=15,background="#a0a0a0") # 创建状态栏。黑绿色bg='#37474f'
        sttBar.pack(side='bottom', fill='x')  # 将状态栏放置在窗口的底部，并水平填充
        lblStt=tk.Label(sttBar,background="#a0a0a0")
        lblStt.pack(side='left')
        cmm.lblStt=lblStt
        sizegrip = ttk.Sizegrip(sttBar)
        sizegrip.pack(side="bottom",anchor='e')
        
        menuRight.refTree(None,cmm.parser['default']['folderPath']) #刷新项目管理器目录        
        fileOpen=cmm.parser['default']['fileOpen']  #之前打开的文件
        sltNum=cmm.parser['default']['sltNum']  #之前选中的文件        
        if fileOpen:
            lst=fileOpen.split(',')
            for it in lst:  cmm.打开文件(it)        
        if sltNum :
            try:
                rNB.select(int(sltNum))
            except:
                pass
        root.protocol('WM_DELETE_WINDOW', self.exit)                      
    def exit(self):              
        #pageON=cmm.rNB.select()  #取得当前选中的页类名 
        #print(pageON)
        #if 'text' in pageON:  #转换后或者创建时，是文本模式        
        #    pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典的key
         #   cmm.rNB.children[pageKey].coloring=0  #停止上色            
        fileOpen,idx='',''
        for i in range(len(cmm.filePath)):#记录已经打开的文件路径
            fileOpen+=cmm.filePath[i][0]+','        
        if fileOpen: #有打开的文件
            fileOpen=fileOpen.rstrip(',')
            idx=cmm.rNB.index('current')  #当前index
        cmm.parser['default']['winW']=str(root.winfo_width()) #程序窗口宽度
        cmm.parser['default']['winH']=str(root.winfo_height()) #程序窗口高度
        cmm.parser['default']['x']=str(root.winfo_x()) #程序窗口位于屏幕x坐标
        cmm.parser['default']['y']=str(root.winfo_y()) #程序窗口位于屏幕y坐标
        cmm.parser['default']['fileOpen']=fileOpen #记录已经打开的文件路径
        cmm.parser['default']['sltNum']=str(idx) #记录选中的idx
        with open('default.ini', 'w', encoding='utf-8-sig') as cfgFile:  # 保存配置文件            
            cmm.parser.write(cfgFile)
        menuBar.关闭全部()
        root.quit()  #关闭tkinter主循环
        root.destroy()  #销毁窗口
        sys.exit(0)  #退出进程
    def sashDrag(self,e):  #拖动过程中实时重新放置bbox
        if cmm.lstIEB:
            box=cmm.table.bbox(cmm.lstIEB[0],column=1)  #取得第2列box信息   
            cmm.lstIEB[1].place(x=box[0],y=box[1],width=box[2],height=box[3])
    def on_select(self,e): #在控件关系树中，点击某个控件
        idx=cmm.rNB.index('current')  #当前index
        iidSlt =cmm.treeD.identify_row(e.y)         # 点击的iid 
        if not iidSlt: return 0
        wgtN=cmm.treeD.item(iidSlt)["text"]        
        if not wgtN:
            #cmm.treeD.selection_remove(iidSlt) 
            return 0
        pageON=cmm.rNB.select()  #取得当前选中的页类名        
        pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典的key
        if 'text' not in pageON:
            if wgtN=='root':  cmm.rNB.children[pageKey].canvasMD(0)
            else:cmm.filePath[idx][3][wgtN].master.mousedown(0)
        return iidSlt
    def menuR(self,event):  #右击控件关系树中某个控件
        iid =self.on_select(event)              
        if not iid: return 0
        wgtN=cmm.treeD.item(iid)["text"]  
        if not wgtN: return 0
        cmm.treeD.selection_set(iid)
        cmm.treeD.focus(iid)   
        mR =tk.Menu(tearoff=False)      
        piid=cmm.treeD.prev(iid) #上面的iid
        diid=cmm.treeD.next(iid) #下面的iid
        if piid: mR.add_command(label=cmm.t('上移'), command=lambda :self.moveWgt(1,wgtN,cmm.treeD.item(piid)["text"]))  #上移控件
        if diid: mR.add_command(label=cmm.t('下移'), command=lambda :self.moveWgt(2,wgtN,cmm.treeD.item(diid)["text"]))  #下移控件 
        mR.post(event.x_root, event.y_root)     # 光标位置显示菜单
    def moveWgt(self,upD,wgtN,mN):  #上移或者下移控件。默认处于文本模式 
        pageON=cmm.rNB.select()  #取得当前页类名路径 
        pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典的key 
        idx=cmm.rNB.index('current')  #当前index
        modeN=0
        if 'text' not in pageON:  #当前是图形模式
            modeN=1  
            cmm.filePath[idx][1]=menuBar.wgtToCode(idx)    #控件参数转化成文本写入filePath 1            
            lst=cmm.filePath[idx][1].split('\n')      
        else: lst=cmm.rNB.children[pageKey].get().split('\n') #当前是文本模式,文本内容从text控件中取出             
        si,ei=0,0  #界面控件语句，开始位置,结束位置
        for i,it in enumerate(lst):  #记录起止位置。其他语句要保留
            if 'def makeGUI(self,root)' in it:si=i+1   #开始位置
            elif ('def ' in it or '#------' in it) and si:  #找到结束位置
                ei=i-1  #结束位置
                break        
        lstW=[]
        for i in range(ei,si-1,-1):  #查找此控件保存代码
            if lst[i].split('.')[1] and wgtN in lst[i].split('.')[1]:  #找到此控件
                lstW.append(lst[i]) 
                del lst[i]
        if upD==1:  #上移控件
            for i in range(si,ei-len(lstW)):  #查找上面的控件
                if mN in lst[i].split('.')[1]: #找到上面的控件
                    for it in lstW: lst.insert(i,it)#在此插入此控件
                    break            
        else:  #下移控件
            for i in range(ei-len(lstW),si-1,-1):  #查找下面的控件
                if mN in lst[i].split('.')[1]: #找到下面的控件
                    for it in lstW: lst.insert(i+1,it)#在此插入此控件cmm.t("运行")
                    break        
        cmm.filePath[idx][1]='\n'.join(lst)  #还原代码文本
        if modeN:  #当前是图形模式 
            cmm.prmToRC(idx)
            for k,v in cmm.filePath[idx][3].items():  #删除界面中所有控件
                if k=='cvsGUI':continue                    
                v.master.destroy()
            cmm.showGUI(idx)
            cmm.lstSW[0]=cmm.filePath[idx][3][wgtN].master
        else:  #当前是文本模式            
            cmm.rNB.children[pageKey]._lineHash.clear()
            cmm.rNB.children[pageKey].textNow.delete('1.0','end')
            cmm.rNB.children[pageKey].insert('1.0',cmm.filePath[idx][1])  #显示文本内容            
            cmm.prmToRC(idx)
        cmm.showSG()
        cmm.filePath[idx][4]=1  #代码文本编辑标志设为已经编辑
if __name__ == "__main__":
    #sys.path.insert(0, r".\packages")  #添加搜索库路径
    cmm.parser=configparser.ConfigParser()  # 创建一个ConfigParser对象
    cmm.parser.optionxform = str          # 保持大小写
    if not cmm.parser.read('default.ini', encoding="utf-8-sig"): # 读取配置文件,windows用utf-8-sig
        messagebox.showwarning('Configuration File Error','default.ini file not found or failed to read!')
        sys.exit(0)  #退出进程
    cmm.language=cmm.parser['default']['language']  
    if cmm.language!='简体中文':  #其他文字
        cmm.initLg(cmm.language)  #之前选中的语言，空值是英文版本
    cmm.pythonV=cmm.parser['default']['pythonV']  #选择的python编译器版本，空值是3.8版本
    cmm.fontN=cmm.parser['default']['fontN']  #字体
    cmm.fontSz=cmm.parser['default']['fontSz']  #字体大小
    root = tk.Tk()
    root.title('SeeTk')   # 设置标题  
    cmm.root=root 
    root.option_add("*Font","cmm.t('微软雅黑')"+" 10")  #tk全局字体，控制基于root的控件的字体大小
    root.option_add("*Menu.font","cmm.t('微软雅黑')"+" 10")  #tk各菜单项字体     
    icoRun=tk.PhotoImage(file='ico/run.png')  #运行图标
    icoLeft=tk.PhotoImage(file='ico/left.png')  #左对齐图标
    icoRight=tk.PhotoImage(file='ico/right.png')  #右对齐图标
    icoUp=tk.PhotoImage(file='ico/up.png')  #上对齐图标
    icoDown=tk.PhotoImage(file='ico/down.png')  #下对齐图标  
    icoHor=tk.PhotoImage(file='ico/hor.png')  #下对齐图标
    icoVer=tk.PhotoImage(file='ico/ver.png')  #下对齐图标 
    icoTP=tk.PhotoImage(file='ico/textPic2.png')  #下对齐图标  
    icoSave=tk.PhotoImage(file='ico/save.png')  #保存
    icoNP=tk.PhotoImage(file='ico/newP.png')  #新建工程
    icoOF=tk.PhotoImage(file='ico/openF.png')  #打开文件
    icoCopy=tk.PhotoImage(file='ico/copy.png')  #复制文件
    icoPaste=tk.PhotoImage(file='ico/paste.png')  #粘贴文件
    icoCancel=tk.PhotoImage(file='ico/undo.png')  #
    icoDel=tk.PhotoImage(file='ico/del3.png')  #
    icoCut=tk.PhotoImage(file='ico/cut.png')  #
    cmm.icoFolder=tk.PhotoImage(file='ico/folder2.png')  #文件夹关闭图标
    cmm.icoFN=tk.PhotoImage(file='ico/folder3.png')  #文件夹打开图标
    cmm.icoFile=tk.PhotoImage(file='ico/txt.png')  #文件图标    
    cmm.myDlg=mainGUI(root)  #调用类mainGUI，创建界面  
    if cmm.parser['default']['winW']:winW=int(cmm.parser['default']['winW']) #程序窗口宽
    else: winW=1300
    if cmm.parser['default']['winH']:winH=int(cmm.parser['default']['winH']) #程序窗口高
    else: winH=740
    screenW = root.winfo_screenwidth() #屏幕宽
    screenH = root.winfo_screenheight() #屏幕高
    if cmm.parser['default']['x']:x=int(cmm.parser['default']['x'])
    else:x=(screenW-winW)//2 #x坐标
    if cmm.parser['default']['y']:y=int(cmm.parser['default']['y'])
    else:y=(screenH-winH)//2-20 #y坐标,20是标题+菜单栏的高度
    root.geometry(f'{winW}x{winH}+{x}+{y}')  #'宽度x高度+X偏移+Y偏移'
    root.resizable(width=True, height=True)  # 设置窗口是否可变长、宽（True：可变，False：不可变）
    menuBar.menu(root)   
    root.bind('<F9>',lambda e:menuBar.run())     #F9运行用户编写的程序
    root.mainloop()  #开启消息循环























