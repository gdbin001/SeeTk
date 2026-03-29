import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory,askopenfilename
from tkinter import messagebox
import os,cmm,tooltip
#import matplotlib.pyplot as plt
#import matplotlib.font_manager as fm

class newProject:  #新建项目的界面
    def __init__(self,top,):
        top.title(cmm.t("新建项目"))
        self.top=top
        import ctypes
        user32 = ctypes.windll.user32
        sw = user32.GetSystemMetrics(0)  #获取屏幕宽度
        sh = user32.GetSystemMetrics(1)  #获取屏幕高度
        sx = 0
        sy = 0
        dw=400  #界面宽度
        dh=200  #界面高度
        top.geometry('%dx%d+%d+%d'%(dw,dh,sx+(sw-dw)/2,sy+(sh-dh)/2))  #界面放到屏幕中央
        top['background'] = '#efefef'
        #top.grid_rowconfigure(, weight=1)    #第0行，按1缩放
        top.grid_columnconfigure(1, weight=1)  #第1列，按1缩放

        Label_17 = tk.Label(top,text=cmm.t("名称"))
        Label_17.grid(row=0, column=0, sticky="e",ipady=30,padx=10)
        self.Entry_14 = tk.Entry(top,relief = "sunken")
        self.Entry_14.grid(row=0, column=1, sticky="ew")
        self.Entry_14.bind("<Return>",lambda e: self.ok())  #回车键
        self.Entry_14.focus_set()

        tk.Label(top,text=cmm.t("保存到")).grid(row=1, column=0, sticky="e",padx=10)
        self.Entry_18 = tk.Entry(top,relief = "sunken")
        self.Entry_18.bind("<Return>",lambda e: self.ok())  #回车键
        self.Entry_18.grid(row=1, column=1, sticky="ew")
        #self.Entry_18.insert(0,os.getcwd().replace('\\','/')+'/Project')  #默认项目路径
        tk.Button(top,text=cmm.t("清空"),command=lambda:self.cancel()).grid(row=2, column=1, sticky="w",ipadx=15,pady=10,padx=30)
        tk.Button(top,text=cmm.t("确定"),command=lambda:self.ok()).grid(row=2, column=1, sticky="e",ipadx=15,pady=10,padx=30)        
        tk.Button(top,text=cmm.t("浏览"),command=lambda:self.browser()).grid(row=1, column=2, sticky="e",ipadx=15,padx=10)
        
        top.protocol('WM_DELETE_WINDOW', self.exit)

    def exit(self):
        cmm.root.attributes('-disabled',0)  #父窗口恢复正常
        self.top.destroy()
    def ok(self):  #确定
        if not self.Entry_14.get():
            messagebox.showerror(cmm.t('错误'),cmm.t('请输入项目名称'))
            return
        if not self.Entry_18.get():
            messagebox.showerror(cmm.t('错误'),cmm.t('请选择保存路径'))
            return
        folderPath=self.Entry_18.get()+'/'+self.Entry_14.get()
        try:
            os.makedirs(folderPath)
        except Exception as e:
            messagebox.showerror(cmm.t('错误'),cmm.t("新建文件夹{}失败{}").format(folderPath,e))
        else:               
            cmm.打开文件夹(folderPath)
            cmm.新建文件(folderPath+'/main.py')
            cmm.refTree()
        #getattr(sys.modules['menuBxxr'],'refTree')(regCtrl, self.Entry_18.get()) #刷新项目资源管理器                
        self.exit()
    def browser(self):  #浏览
        location = askdirectory()
        if not location: return
        self.Entry_18.delete(0, "end")
        self.Entry_18.insert(0, location)
    def cancel(self):  #清空
        self.Entry_14.delete(0,'end')
        self.Entry_18.delete(0,'end')

class helpGUI:  #帮助的界面
    def __init__(self,top,funcRef):
        top.title('SeeTk')
        import ctypes
        user32 = ctypes.windll.user32
        sw = user32.GetSystemMetrics(0)  #获取屏幕宽度
        sh = user32.GetSystemMetrics(1)  #获取屏幕高度
        sx = 0
        sy = 0
        dw=400  #界面宽度
        dh=200  #界面高度        
        top.geometry('%dx%d+%d+%d'%(dw,dh,sx+(sw-dw)/2,sy+(sh-dh)/2))  #界面放到屏幕中央
        top['background'] = '#efefef'
        Label_4Ft=tk.font.Font(**{'family': 'Arial', 'size': 22, 'weight': 'bold', 'slant': 'roman'})
        tk.Label(top,text='SeeTk',font=Label_4Ft).pack(padx=2,pady=2,ipadx=10,ipady=10)
        tk.Label(top,text='Version: 0.5  (Build 20260302)\nRelease Date: 2026-03-02\nCopyright:© 2026 Lxbin. All rights reserved.\nContact: 1013056018@qq.com',justify='left').pack(padx=2,pady=2,ipadx=10,ipady=10)

class setupGUI:  #设置卡的界面
    def __init__(self,top,funcRef):
        top.title(cmm.t("设置"))
        self.top=top
        self.funcRef=funcRef
        import ctypes
        user32 = ctypes.windll.user32
        sw = user32.GetSystemMetrics(0)  #获取屏幕宽度
        sh = user32.GetSystemMetrics(1)  #获取屏幕高度
        sx = 0
        sy = 0
        dw=400  #界面宽度
        dh=400  #界面高度        
        top.geometry('%dx%d+%d+%d'%(dw,dh,sx+(sw-dw)/2,sy+(sh-dh)/2))  #界面放到屏幕中央
        top['background'] = '#efefef'

        lbF1=tk.LabelFrame(top,text=cmm.t('全局'))
        lbF1.pack(padx=2,pady=2,ipadx=10,ipady=10)
        tk.Label(lbF1,text=cmm.t("解释器")).grid(row=1, column=0, sticky="e",padx=10)  #解释器行
        self.Entry_18 = tk.Entry(lbF1,relief = "sunken",name='pythonV',width=4) 
        self.Entry_18.bind("<Return>",lambda e: self.ok())  #回车键
        self.Entry_18.grid(row=1, column=1, sticky="ew")
        if cmm.parser['default']['pythonV']: self.Entry_18.insert(0,cmm.parser['default']['pythonV'])  #解释器路径
        #else: self.Entry_18.insert(0,cmm.t('python 3.8请留空。使用其他版本的请选择'))
        #self.Entry_18.bind('<Enter>',tooltip.showTip)
        #self.Entry_18.bind('<Leave>',tooltip.closeTip)
        tk.Button(lbF1,text=cmm.t("浏览"),command=lambda:self.browser(),width=4).grid(row=1, column=2, sticky="e",ipadx=15,padx=10)        
        tk.Label(lbF1,text=cmm.t("语言")).grid(row=2, column=0, sticky="e",padx=10)  #语言行
        self.Combobox_1 = ttk.Combobox(lbF1,state="readonly") 
        #self.Combobox_1 .bind("<Return>",lambda e: self.ok())  #回车键
        self.Combobox_1 .grid(row=2, column=1, sticky="ew")
        lst=['简体中文']
        i,sltLan=1,0
        for fn in os.listdir('language'):  # 遍历文件夹
            filePath = os.path.join(os.getcwd(),'language', fn)  #取得文件路径
            if os.path.isfile(filePath):  #是文件
                for it in cmm.tplFL:
                    if it[0]==fn: 
                        lst.append(it[1]) # 只添加文件（排除子文件夹）
                        if cmm.language and it[1]==cmm.language: sltLan=i
                        i+=1
                        break
        self.Combobox_1['values']=lst
        self.Combobox_1.current(sltLan)

        lbF1=tk.LabelFrame(top,text=cmm.t('文本编辑器'))
        lbF1.pack(padx=2,pady=2,ipadx=10,ipady=10)
        tk.Label(lbF1,text=cmm.t("字体")).grid(row=4, column=0, sticky="e",padx=10)  #字体行
        self.Combobox_2 = ttk.Combobox(lbF1,state="readonly") 
        self.Combobox_2 .grid(row=4, column=1, sticky="ew")
        lstFont= list(tk.font.families())
        self.Combobox_2['values']=lstFont
        pageKey=cmm.rNB.select()[cmm.rNB.select().rfind('!'):]  #从页类名中取得页字典key  
        #textFont = cmm.rNB.children[pageKey].textNow.cget('font')  #取得字体名及大小
        #print(textFont)
        #fontN=textFont[1:textFont.find('}')]  #字体名称
        for i,fn in enumerate(lstFont):
            if fn ==cmm.fontN: 
                self.Combobox_2.current(i)
                break
        tk.Label(lbF1,text=cmm.t("字体大小")).grid(row=5, column=0, sticky="e",padx=10)  #字体大小行
        self.Entry_19 = tk.Entry(lbF1,relief = "sunken",name='fontSz') 
        self.Entry_19.bind("<Return>",lambda e: self.ok())  #回车键
        self.Entry_19.grid(row=5, column=1, sticky="ew")
        #fontSz=textFont[textFont.find('}')+1:].strip()  #字体大小
        self.Entry_19.insert(0,cmm.fontSz)
        tk.Label(lbF1,text="     ").grid(row=5, column=2, sticky="e",padx=33)  #占位

        tk.Button(top,text=cmm.t("确定"),command=lambda:self.ok(),width=4).pack(padx=2,pady=1,ipadx=15,ipady=1)
        top.protocol('WM_DELETE_WINDOW', self.exit)
        cmm.root.wait_window(top)  #停止主窗口事件循环。等待模态窗口关闭 
    def exit(self):
        cmm.root.attributes('-disabled',0)  #父窗口恢复正常
        self.funcRef.langCh= self.Combobox_1.get() != cmm.language
        self.top.destroy()
    def browser(self):  #浏览
        filePath=askopenfilename(title=cmm.t("选择py编译程序"), filetypes=[("All files files", "*"),],initialdir=self.Entry_18.get())
        if not filePath: return
        self.Entry_18.delete(0, "end")
        self.Entry_18.insert(0, filePath)
    def ok(self,):  #确定            
        cmm.parser['default']['pythonV']=self.Entry_18.get().strip()  # 修改编译器版本    
        cmm.parser['default']['language']=self.Combobox_1.get()  # 修改语言
        flag=0
        fontSz=self.Entry_19.get().strip()
        if not fontSz:  
            messagebox.showerror(cmm.t('错误'),cmm.t('输入无效'))
            self.Entry_19.focus_set()
            return 0
        try:# 第一步：尝试转为整数        
            dg=int(fontSz)
        except ValueError:
            messagebox.showerror(cmm.t('错误'),cmm.t('输入无效'))
            self.Entry_19.focus_set()
            return 0
        if  cmm.fontSz!=fontSz:  # 修改字体大小
            cmm.fontSz=fontSz  
            cmm.parser['default']['fontSz']=fontSz     
            flag=11
        if cmm.fontN!=self.Combobox_2.get():# 修改字体
            cmm.fontN=self.Combobox_2.get()  
            cmm.parser['default']['fontN']=self.Combobox_2.get()
            flag=11
        if flag==11:  # 修改编辑器字体、大小
            for i,po in enumerate(cmm.rNB.tabs()):  #遍历标签页
                if 'text' in po: #是文本模式          
                    pageKey=po[po.rfind('!'):]
                    cmm.rNB.children[pageKey].textNow['font']=(f'{cmm.fontN}',dg)  
        with open('default.ini', 'w', encoding='utf-8-sig') as configfile:# 将更改写回到配置文件中
            cmm.parser.write(configfile)  #立即写入        
        self.exit()
    #def cancel(self):  #取消
     #   self.Entry_18.delete(0,'end')

class myDialog:  #显示错误信息
    def __init__(self,tt):
        top=tk.Toplevel()
        top.title(tt)
        sx = 0
        sy = 0
        dw=300  #界面宽度
        dh=520  #界面高度
        screenW = cmm.root.winfo_screenwidth() #屏幕宽
        top.geometry('%dx%d+%d+%d'%(dw,dh,screenW-dw-20,0))  #界面位置
        top.rowconfigure(0,weight=1)
        top.columnconfigure(0,weight=1)
        self.tx=tk.Text(top,width=8,height=1,background='black',foreground='#eeeeee',insertbackground="white",insertwidth=3,insertofftime=0,insertontime=0)# 创建一个Text控件        
        self.tx.grid(row=0,column=0,sticky='nesw',padx=(5,0),pady=0,ipadx=0,ipady=0)
        Scrollbar_2=tk.Scrollbar(top,width=8)
        Scrollbar_2.grid(row=0,column=1,sticky='nesw',padx=(0,5),pady=0,ipadx=2)
        Scrollbar_2 .config(command = self.tx.yview)
        self.tx.config(yscrollcommand =Scrollbar_2.set)
        sizegrip = ttk.Sizegrip(top)
        sizegrip.grid(row=1,column=1,padx=0,ipadx=0)
        #self.tx.insert('1.0', msg)  # 正确访问initial_text属性
def findText(event=None):  #查找/替换功能。要运行完才能显示出界面。非模态窗口    
    pageText,tabT=0,0 
    findText.sPos=0
    def getWgt():
        nonlocal pageText,tabT
        pageON=cmm.rNB.select()  #取得当前页类名
        pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典key 
        if 'dragtext' in pageON: #当前打开的是text控件
            aa=cmm.rNB.tab(pageON,'text')  #标签页上的名称
            if aa!=tabT:  #点击了新标签页
                if pageText:
                    pageText.tag_delete('yellow')  #删除加到codeTxt中的标签的定义
                    pageText.tag_delete('match')  #删除加到codeTxt中标签的定义
                pageText=cmm.rNB.children[pageKey].textNow       
                pageText.bind('<1>',lambda e:dycb(pageText))  #单击text,删除黄色标记和回到点击位置。鼠标点击更换单击响应函数                
                if 'yellow' not in pageText.tag_names():pageText.tag_config('yellow',foreground='black', background='#ffbb00') #tag加到codeTxt中
                if 'match' not in pageText.tag_names():pageText.tag_config('match', foreground='black',background='lightgrey') #tag加到codeTxt中
                tabT=aa
                findText.sPos=0
        else:return    
    getWgt()    
    top =tk.Toplevel()        #创建一个顶级窗口
    top.title(cmm.t('查找/替换'))        #窗口命名
    top.transient(cmm.root)        #将top注册成root的临时窗口，去掉了最大最小化的按钮
    top.geometry('340x115+700+500') #设置查找框所在的位置
    top.resizable(0,0) #窗口不可变
    top.attributes("-topmost",1)  #总是让搜索框显示在主程序窗口之上    
    findText.sKey=0  #要查找的字符串。函数属性,被函数共享           
    findText.selNum=0  #查找次数。函数属性,被函数共享
    tk.Label(top,text=cmm.t('查找')).grid(row=0,column=0,sticky='e',padx=(25,0)) #设置标签提醒
    entryS =tk.Entry(top,width=22) #设置输入框
    entryS.grid(row=0,column=1,padx=(1,0),pady=2,sticky='w') #布局
    entryS.focus_set()  
    entryS.insert(0,cmm.searchStr)
    entryS.bind('<Return>',lambda e:searchResult(pageText,entryS.get(),ignCase.get()))
    tk.Button(top,text=cmm.t("查找"),width=6,command=lambda :searchResult(pageText,entryS.get(),ignCase.get()) 
           ).grid(row=0, column=2, sticky='e' + 'w', padx=2, pady=2)  #设置查找按钮，但是要回事件的，中间常常的参数是要传入到search_result函数中的变量
    tk.Label(top,text=cmm.t('替换为')).grid(row=1,column=0,sticky='e',padx=(25,0)) 
    entryR =tk.Entry(top,width=22) #设置输入框
    entryR.grid(row=1,column=1,padx=(1,0),pady=2,sticky='w') #布局  
    entryR.insert(0,cmm.replaceStr)  
    tk.Button(top,text=cmm.t("替换"),width=6,command=lambda :replaceS(pageText,entryR.get(),entryS.get(),ignCase.get())  
           ).grid(row=1, column=2, sticky='e' + 'w', padx=2, pady=2)
    ignCase =tk.IntVar(value=1)  #这里的整型变量只在这个函数内部使用   
    tk.Checkbutton(top,text=cmm.t('忽略大小写'),variable=ignCase).grid(row=2,column=1,sticky='e',padx=2,pady=2)  #设置是否忽略大小写的按钮    
    def closeW():#这个函数在find_text内部定义的话，较为简单
        pageText.unbind('<1>')  #更换回codeTxt鼠标单击响应函数
        pageText.bind('<1>',pageText.master.mousePrs)
        pageText.tag_delete('yellow')  #删除标签的定义
        pageText.tag_delete('match')  #删除标签的定义
        top.destroy() #然后再销毁窗口          
    def dycb(pt): #删除黄色标记和回到点击位置
        pt.tag_remove('yellow', '1.0', "end")
        #findText.sKey=key
        findText.selNum=-1
        findText.sPos=pt.index('insert')
    def searchResult(pageText,key,ignCase):  #查找。嵌套函数可以直接访问外层函数的局部变量（只要不修改，修改需要nonlocal） 
        getWgt()
        for k in list(pageText.master.folded_blocks):  #把已经折叠的行都打开
            pageText.master.unfold_code(k)
        if findText.sPos!=pageText.index('insert') or key!=findText.sKey:  #光标位置或者搜索词发生了变化
            findText.sKey=key
            findText.selNum=0
            findText.sPos=pageText.index('insert')
            searchFP(key,ignCase,findText.sPos)
        else:findText.selNum+=1  #没有变化 
        matchNum = 0   #匹配成功总数
        if key:             #如果输入了要匹配的数据，进行接下来的操作
            tplSel=pageText.tag_ranges("sel")  #鼠标框选的区域
            if tplSel: #有框选区域
                startPos,ep=tplSel[0],tplSel[1]
            else:startPos,ep='1.5','end'
            while 1:            
                startPos = pageText.search(key,startPos, nocase=ignCase, stopindex=ep) #返回第一个匹配的位置
                if not startPos: break  #没有找到则退出
                endPos = f'{startPos}+{len(key)}c'  #把匹配结束的位置记下来
                tn=pageText.tag_names(startPos)  #该位置下的tag
                if not tn or tn[0]!='readonly': #不是行号               
                    if matchNum==findText.selNum  :  #选中
                        pageText.tag_remove('match', startPos, endPos) #去掉已有的标记
                        pageText.tag_add('yellow', startPos, endPos)  #黄色移动到当前匹配词
                        pageText.see(startPos)  # 文本滚动到匹配位置
                    else :  #没选中
                        pageText.tag_remove('match', startPos, endPos) #去掉已有的标记
                        pageText.tag_remove('yellow', startPos, endPos) #去掉已有的标记
                        pageText.tag_add('match', startPos, endPos)  #对其他匹配到的内容配灰色
                    matchNum += 1  #匹配的内容计数+1            
                startPos = endPos  #重设起始位置        
        if findText.selNum+1==matchNum: #黄色移动到最后一个匹配词
            pageText.mark_set('insert', '1.0') 
            findText.sKey=0
        cmm.searchStr=key
    def replaceS(pageText,r,key,ignCase):  #替换
        if not r:return 0  #没有替换内容，退出
        pos=pageText.tag_ranges('yellow')[:2] #取得2个标签的位置（开始，结束）
        if not pos:return 0
        cmm.replaceStr=r
        if pos:
            pageText.delete(pos[0],pos[1])  #删除标记的文本
            pageText.insert(pos[0],r)   #插入替换文本
            pageText.tag_remove('yellow',pos[0],pos[1])  #删除标记（背景色）
            findText.selNum-=1
            searchResult(pageText,key,ignCase)  #重新搜索并标记
            cmm.filePath[cmm.rNB.index('current')][4]=1  #编辑了界面    
            pageText.master.keyRls(0)  #语法上色
    def searchFP(key,ignCase,ePos):  #从开头到光标位置查找
        pageText.tag_remove('match','1.0', "end") #去掉已有的标记
        pageText.tag_remove('yellow', '1.0', "end") #去掉已有的标记
        if key:             #如果输入了要匹配的数据，进行接下来的操作
            startPos = '1.5'  #文首位置
            while 1:            
                startPos = pageText.search(key,startPos, nocase=ignCase, stopindex=ePos) #返回第一个匹配的位置
                if not startPos: break  #没有找到则退出
                endPos = f'{startPos}+{len(key)}c'  #把匹配结束的位置记下来
                pageText.tag_add('match', startPos, endPos)  #对匹配到的内容配灰白色
                startPos = endPos  #重设起始位置
    top.protocol('WM_DELETE_WINDOW', closeW)
    return "break"  #到此为止，防止向下级传播







