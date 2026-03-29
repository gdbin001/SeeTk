import tkinter as tk
from tkinter import ttk,messagebox
import selectedCanvas as sc
from oprMenu import makeMenu
from tkinter.filedialog import askdirectory,asksaveasfilename,askopenfilename
import os,shutil,codeTxt,dragCan,newPrj,threading,subprocess,cmm,sys,ast


lstTtk=("Combobox",'Notebook','Progressbar','Separator','Treeview')  #ttk控件
lstWxy=('x','y','width','height')
dctBool={'1':1,'0':0,'""':"",'None':None}
lstPlace=('x','y','width','height')
dctErr={}  #{出错文件名：[行号，。。。]}  #运行文件出错信息
lstMsg=[]  # 全局列表：子线程将输出消息放入列表，主线程定时读取并更新GUI
p=0

def menu(root):
    menubar=tk.Menu(root)  # 创建菜单栏对象
    cmm.menuBar=menubar
    文件=tk.Menu(menubar,tearoff = 0) # 创建文件菜单对象
    menubar.add_cascade(label=cmm.t("文件"),menu=文件)  # 将菜单对象添加到菜单栏中
    文件.add_command(label='New Project' if cmm.t("新建项目")=='new_project' else cmm.t("新建项目"),command=lambda:new_project())
    文件.add_command(label=cmm.t("打开文件"),command=lambda:打开文件())
    文件.add_command(label=cmm.t("打开文件夹"),command=lambda:打开文件夹())    
    文件.add_command(label='Save' if cmm.t("保存")=='save' else cmm.t("保存"),command=lambda:save())    
    文件.add_command(label=cmm.t("保存全部"),command=lambda:保存全部())  
    文件.add_command(label=cmm.t("另存为"),command=lambda:另存为())   
    文件.add_separator()   
    文件.add_command(label=cmm.t("关闭全部"),command=lambda:关闭全部())  
    编辑=tk.Menu(menubar,tearoff = 0) # 创建编辑菜单对象
    menubar.add_cascade(label=cmm.t("编辑"),menu=编辑)  # 将菜单对象添加到菜单栏中
    编辑.add_command(label='Undo' if cmm.t("撤销")=='undo' else cmm.t("撤销"),accelerator='Ctrl+Z',command=lambda:handleEdit('undo'))    
    编辑.add_separator()   
    编辑.add_command(label='Cut' if cmm.t("剪切")=='cut' else cmm.t("剪切"),accelerator='Ctrl+X',command=lambda:handleEdit('cut'))
    编辑.add_command(label='Copy' if cmm.t("复制")=='copy' else cmm.t("复制"),accelerator='Ctrl+C',command=lambda:handleEdit('copy'))
    编辑.add_command(label='Paste' if cmm.t("粘贴")=='paste' else cmm.t("粘贴"),accelerator='Ctrl+V',command=lambda:handleEdit('paste'))
    编辑.add_separator() 
    编辑.add_command(label=cmm.t("全选"),accelerator='Ctrl+A',command=lambda:handleEdit('全选'))
    编辑.add_separator()
    编辑.add_command(label=cmm.t('查找/替换'),accelerator='Ctrl+F',command=lambda:newPrj.findText())  
    工具=tk.Menu(menubar,tearoff = 0) # 创建工具菜单对象
    menubar.add_cascade(label=cmm.t("工具"),menu=工具)  # 将菜单对象添加到菜单栏中
    工具.add_command(label='Run' if cmm.t("运行")=='run' else cmm.t("运行"),command=lambda:run())
    #工具.add_command(label=cmm.t("安装包"),command=lambda:package())
    工具.add_separator()    
    工具.add_command(label=cmm.t("设置"),command=lambda:设置())   
    帮助=tk.Menu(menubar,tearoff = 0) # 创建帮助菜单对象 
    menubar.add_cascade(label=cmm.t("帮助"),menu=帮助)  # 将菜单对象添加到菜单栏中
    帮助.add_command(label=cmm.t('关于 SeeTk'),command=lambda:aboutV())
    root.config(menu = menubar)
def aboutV():  #关于 SeeTk
    top=tk.Toplevel()
    top.resizable(0,0)  #不能最大化
    top.wm_attributes("-toolwindow", 1)  #只保留关闭按钮
    top.grab_set()  # 设置窗口为模态（阻止用户操作主窗口）
    newPrj.helpGUI(top,设置)   #打开设置窗口    
def errCode():  #出错行设置红底色。aa是出错行号数字字符串。仅在主线程中执行：给Text控件添加错误tag
    tpl=cmm.rNB.tabs()  #取得所有页类名
    for i,it in enumerate(cmm.filePath):
        if it[0] in dctErr and 'dragtext' in tpl[i]:
            pageKey=tpl[i][tpl[i].rfind('!'):]  #从页类名中取得页字典的key 
            textObj=cmm.rNB.children[pageKey].textNow   
            textObj.tag_remove('err', '1.0', "end") #移除所有的出错标记效果            
            try:  # 校验行号是否有效（避免非数字行号）
                for sn in dctErr[it[0]]:   # 遍历错误行号，添加tag
                    lineNum=int(sn)
                    textObj.see(f'{lineNum}.0')#滚动到这行
                    textObj.tag_add('err',f'{lineNum}.0',f'{int(lineNum)+1}.0') #加tag  
            except ValueError:  #忽略不存在的行号
                continue
def updateOW(event):  #主线程读取队列，更新输出信息窗口（tkinter安全操作）
    while lstMsg: 
        msgType,msg=lstMsg.pop(0)
        if msgType=='errorLine': errCode() # 2. 处理错误行高亮
        else:
            for window in cmm.root.winfo_children():  
                if isinstance(window,tk.Toplevel) and window.title()==cmm.t('输出'):  #存在信息输出窗口
                    if msgType=='output' or msgType=='error':  #1.更新输出窗口
                        msgBox.tx.insert('end', f'{msg}\n')
                        msgBox.tx.see('end')            
                    elif msgType=='returnCode':  # 3. 处理子进程返回码                
                        if msg==0: tip=cmm.t('正常退出')
                        elif msg == -1:  tip = cmm.t('运行超时 {}').format(msg)
                        elif msg == 1:   tip = cmm.t('一般错误 {}').format(msg)
                        else:  tip = cmm.t('其他异常 {}').format(msg)
                        msgBox.tx.insert('end', tip + '\n')
                        msgBox.tx.see('end')
                    break
def getMsg():#只负责读取子进程输出，发送自定义事件，不直接操作GUI
    global p
    if not p or p.stdout is None:  # 前置检查：p为空，或者 p.stdout is None表示不存在输出管道        
        lstMsg.append(('error', cmm.t('无子进程对象或没有输出管道')))
        cmm.root.event_generate('<<MsgEvent>>')
        return 0
    try:
        dctErr.clear()
        while p.poll() is None:  # 逐行读取输出（用readline避免管道阻塞）。p.poll() is None 进程正在运行中,关闭时是0
            strL=p.stdout.readline()  #如果管道内无内容，则会卡住（阻塞）
            strL=strL.strip()
            if strL: #有输出
                lstMsg.append(('output',strL)) 
                cmm.root.event_generate('<<MsgEvent>>')  #发送输出消息事件
                lst=strL.split('\n')   # 2. 解析错误行号（仅处理数据，不操作GUI）
                for i in range(len(lst)):
                    if not lst[i].find('File "'): #发现File "在开头位置。记录文件路径和行号                                        
                        aa=lst[i].find('", line ')  #找出错行号标志位置   
                        if aa!=-1:  #找到                
                            bb=lst[i].find(',',aa+8)  #出错行号起始位置           
                            if bb!=-1: bb=lst[i][aa+8:bb]  #出错行号数字串
                            else: bb=lst[i][aa+8:] #出错行号数字串
                            key=lst[i][6:lst[i].find('", line')].replace('\\','/') #文件路径
                            if key not in dctErr: dctErr[key]=[]      
                            dctErr[key].append(bb) #记录文件路径和行号
        if dctErr: lstMsg.append(('errorLine','')) 
        returnCode=p.wait()  # 等待子进程退出，获取返回码
        lstMsg.append(('returnCode',returnCode))         
    except Exception as e:
        lstMsg.append(('error',str(e)))
    finally:
        cmm.root.event_generate('<<MsgEvent>>')  # 发送返回码消息
        p.stdout.close()
        p=0  #可以代替del p
def run():  #运行代码 
    global msgBox,p       
    if not cmm.rNB.index("end"): # 检查是否有打开的py文件
        messagebox.showerror(cmm.t('错误'),cmm.t('请先打开py文件'))
        return 0
    if p and p.poll() is None:  # 终止正在运行的子进程
        try:
            p.kill()
            p.wait()
            if p.stdout:  p.stdout.close()
        except Exception as e:
            messagebox.showerror(cmm.t('错误'),str(e))
            return 0
        finally:
            p=0  #可以代替del p
    tpl=cmm.rNB.tabs()  #取得所有页类名
    for i,it in enumerate(cmm.filePath):  #移除旧的出错标记效果
            if it[0] in dctErr and 'text' in tpl[i]:             
                pageKey=tpl[i][tpl[i].rfind('!'):]  #从页类名中取得页字典的key
                textObj=cmm.rNB.children[pageKey].textNow   
                textObj.tag_remove('err', '1.0', "end") #移除所有的出错标记效果      
    保存全部()
    idx=cmm.rNB.index("current")
    filePath=cmm.filePath[idx][0]          
    for window in cmm.root.winfo_children():#如果运行结果窗口已经存在，清空窗口
        if isinstance(window, tk.Toplevel) and window.title() == cmm.t('输出'):
            window.winfo_children()[0].delete("1.0","end")  #清空消息窗口
            break
    else:msgBox=newPrj.myDialog(cmm.t('输出')) #创建运行结果窗口    
    if getattr(sys, 'frozen', False): #打包成exe后，用自带的解释器
        if cmm.parser['default']['pythonV'] and os.path.isfile(cmm.parser['default']['pythonV']):  #用户选择python运行版本
            cmd=[cmm.parser['default']['pythonV'],'-u',filePath]
        else:
            messagebox.showerror(cmm.t('错误'),cmm.t('请设置python解释器路径'))
            return 0
    else:  cmd= [sys.executable,'-u',filePath]  #未打包，用win10安装的python解释器
    try:  #创建进程。creationflags避免子进程挂起
        p=subprocess.Popen(cmd, bufsize=1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=1,encoding='utf-8',
          creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0) 
    except Exception as e:
        messagebox.showerror(cmm.t('错误'),str(e)) 
        p=0
        return 0
    try:    # 启动子线程读取输出（仅处理数据）
        threading.Thread(target=getMsg,daemon=1).start()  #创建线程，获取出错消息
        cmm.root.unbind('<<MsgEvent>>')  # 移除旧的绑定（避免重复绑定）
        cmm.root.bind('<<MsgEvent>>', updateOW)  # 绑定自定义事件到处理函数
    except Exception as e:
        messagebox.showerror(cmm.t('错误'),str(e)) 
        p.kill()
        p.wait()
        if p.stdout: p.stdout.close()
        p=0   
def normal(k):  #点击工具栏的处理函数
    pageON=cmm.rNB.select()  #取得当前选中的页类名
    pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典的key
    if k in ('copy','paste','undo','cut'):
        if 'text' in pageON:  handleEdit(k) #文本模式        
        elif k=='copy': cmm.rNB.children[pageKey].onCopy(0) #图形模式 
        elif k=='paste': cmm.rNB.children[pageKey].onPaste(0) #图形模式 
        elif k=='cut': cmm.rNB.children[pageKey].onCut(0) #图形模式 
    else:  #删除
        if 'text' in pageON: #文本模式
            try: #删除选中的文本
                cmm.rNB.children[pageKey].textNow.delete('sel.first', 'sel.last')   
            except tk.TclError: # 没有任何选区时，会抛出 TclError，删除单个字符
                nextPos=cmm.rNB.children[pageKey].textNow.index(f"{tk.INSERT} + 1 chars")
                cmm.rNB.children[pageKey].textNow.delete('insert', nextPos) 
        else: cmm.lstSW[0].delW(0)  #图形模式
def handleEdit(actType):  #点击菜单的处理函数。撤销、剪切、复制、粘贴、全选
    pageON=cmm.rNB.select()  #取得当前页类名
    pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典key  
    if actType=='undo': 
        cmm.rNB.children[pageKey].undo() #撤销
        cmm.rNB.children[pageKey].textNow.edit_modified(1)
        cmm.rNB.children[pageKey]._changeDt=1
    elif actType=='cut': cmm.rNB.children[pageKey].cCopy(cmm.t('剪切'))  #剪切
    elif actType=='copy': cmm.rNB.children[pageKey].cCopy(cmm.t('复制'))  #复制
    elif actType=='paste': cmm.rNB.children[pageKey].cPaste() #粘贴 
    elif actType=='全选': cmm.rNB.children[pageKey].textNow.event_generate("<<SelectAll>>")  #全选'''
def save(pageON='',pageKey='',idx=''): #保存一个文件。点击了保存或者在CustomNotebook中点击了X号，会传入pageON等参数。正常调用则为空
    if not pageON:  #点击了保存
        pageON=cmm.rNB.select()  #取得当前页类名
        pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典key  
        idx=cmm.rNB.index("current")
    if 'dragtext' in pageON: #当前是文本模式
        content=cmm.rNB.children[pageKey].get() #读取text控件中的文本内容        
    else:  #当前是图形模式
        content=wgtToCode(idx)  #把界面代码转化成文本文件,加入原代码中
    cmm.filePath[idx][1]=content  #写入filePath    
    with open(cmm.filePath[idx][0], 'w', encoding='utf-8') as f:  #用utf-8编码方式保存到文件
        f.write(content)
    cmm.filePath[idx][4]=0  #代码文本编辑标志设为未编辑
def 保存全部():
    for i,pon in enumerate(cmm.rNB.tabs()): #一个个取出所有页类名
        save(pon,pon[pon.rfind('!'):],i)
def 另存为(): 
    idx=cmm.rNB.index("current")   
    filePath=asksaveasfilename(
        defaultextension=".py",
        filetypes=[("Python files", "*.py"), ("All files", "*.*")]
    )   # 让用户选择保存路径
    if filePath:  # 如果用户选择了路径
        oldFP=cmm.filePath[idx][0]
        shutil.copyfile(oldFP, filePath)
        cmm.filePath[idx][0]=filePath  #更改filePath中的文件路径
        cmm.rNB.tab(cmm.rNB.select(),text=f"{os.path.basename(filePath)}")#更改notebook标签文本
        cmm.filePath[idx][4]=0  #编辑标志设为未编辑
def 关闭全部():    
    cmm.table.delete(*cmm.table.get_children())    #清空表
    lstPon=cmm.rNB.tabs()
    for i in range(len(lstPon)-1,-1,-1): #
        if cmm.filePath[i][4]:
            if messagebox.askyesno(cmm.t('确认'),cmm.t("是否要将更改保存到{}？").format(f"'\n'{cmm.filePath[i][0]}")): 
                save(lstPon[i],lstPon[i][lstPon[i].rfind('!'):],i)  
        #cmm.rNB.forget(i)  #删除该页
        pageKey=lstPon[i][lstPon[i].rfind('!'):]  #从页类名路径中取得页字典的key 
        cmm.rNB.children[pageKey].destroy()  #销毁其中的控件
        #cmm.rNB.event_generate("<<NotebookTabClosed>>") #
        del cmm.filePath[i]  #删除文件记录             
def 设置():  #打开设置窗口
    设置.langCh=0  #函数属性
    top=tk.Toplevel()
    top.resizable(0,0)  #不能最大化
    top.grab_set()  # 设置窗口为模态（阻止用户操作主窗口）
    newPrj.setupGUI(top,设置)   #打开设置窗口
    if 设置.langCh:  #当语言设置发生了变化    
        filePath=f'{os.getcwd()}\\main.py'     
        subprocess.Popen([sys.executable,filePath], creationflags=subprocess.CREATE_NO_WINDOW) #重新运行seetk
        cmm.myDlg.exit()
def new_project():  #打开新建项目窗口
    cmm.root.attributes('-disabled',1)  #父窗口失效
    top=tk.Toplevel()
    top.resizable(False,False)
    top.transient(cmm.root)  #将top注册成root的临时窗口，去掉了最大最小化的按钮
    newPrj.newProject(top,)
def 打开文件夹(folderPath=0):   
    if not folderPath:  folderPath=askdirectory()
    cmm.refTree('',folderPath)  #menuRight模块中的refTree函数
    cmm.parser['default']['folderPath']=folderPath  # 修改默认文件夹路径  
def 打开文件():
    filePath=askopenfilename(title=cmm.t('请选择文件'),filetypes=[('py files', '*.py'), ('All files', '*.*')])
    if not filePath: return         # 用户点了“取消”
    cmm.打开文件(filePath)        
def distribute_horizontally_evenly():  #水平均匀分布
    if cmm.guiL!='place':return
    align_top()
    idx=cmm.rNB.index('current')  #当前index
    max,min=0,100000
    lstX=[]  #控件x坐标。元素[x坐标，控件对象,width]
    if len(cmm.lstSW)>2:
        for c in cmm.lstSW:
            w=int(cmm.filePath[idx][2][c.wgtName]['width'][0])
            x=int(cmm.filePath[idx][2][c.wgtName]['x'][0])
            if x>max:max=x
            if x<min:min=x+w
            lstX.append([x,c,w])  #控件x坐标
    else:  #以界面为范围水平均匀分布
        return
    lstX.sort(key=lambda x:x[0])
    lpp=max-min  #等分步长
    for i in range(1,len(lstX)-1): lpp-=lstX[i][2]  #等分步长
    lpp=lpp//(len(lstX)-1)  #等分步长
    for i in range(1,len(lstX)-1):  #处理中间控件,i是次数
        x=lstX[0][0]+lstX[0][2]+i*lpp  #要移动控件的x坐标
        wd=0
        for j in range(1,i):
            wd=wd+lstX[j][2]
        x+=wd
        cmm.filePath[idx][2][lstX[i][1].wgtName]['x'][0]=str(x)
        lstX[i][1].place({'x':x})
def distribute_vertically_evenly():  #垂直均匀分布
    if cmm.guiL!='place':return
    align_left()
    idx=cmm.rNB.index('current')  #当前index
    max,min=0,100000
    lst=[]  #控件y坐标。元素[y坐标，控件对象,height]
    if len(cmm.lstSW)>2:
        for c in cmm.lstSW:
            h=int(cmm.filePath[idx][2][c.wgtName]['height'][0])
            y=int(cmm.filePath[idx][2][c.wgtName]['y'][0])
            if y>max:max=y
            if y<min:min=y+h
            lst.append([y,c,h])  #控件x坐标
    else:return
    lst.sort(key=lambda x:x[0])
    lpp=max-min
    for i in range(1,len(lst)-1):lpp-=lst[i][2]
    lpp=lpp//(len(lst)-1)
    for i in range(1,len(lst)-1):  #处理中间控件,i是次数
        y=lst[0][0]+lst[0][2]+i*lpp  #要移动控件的y坐标
        wd=0
        for j in range(1,i):
            wd=wd+lst[j][2]
        y+=wd
        cmm.filePath[idx][2][lst[i][1].wgtName]['y'][0]=str(y)
        lst[i][1].place({'y':y})
def align_left():  #左对齐选定的控件
    if cmm.guiL!='place':return
    idx=cmm.rNB.index('current')  #当前index
    minX=100000
    for c in cmm.lstSW:  #找出最左边的x值
        x1=int(cmm.filePath[idx][2][c.wgtName]['x'][0]) 
        if x1<minX:minX=x1  
    for c in cmm.lstSW:  #设置
        cmm.filePath[idx][2][c.wgtName]['x'][0]=str(minX)
        c.place({'x':minX})
def align_top():  #上对齐选定的控件
    if cmm.guiL!='place':return
    idx=cmm.rNB.index('current')  #当前index
    minY=100000
    for c in cmm.lstSW:  #找出最上边的y值
        y1=int(cmm.filePath[idx][2][c.wgtName]['y'][0]) 
        if y1<minY:minY=y1  
    for c in cmm.lstSW:  #设置
        cmm.filePath[idx][2][c.wgtName]['y'][0]=str(minY)
        c.place({'y':minY})
def align_right():  #右对齐选定的控件
    if cmm.guiL!='place':return
    idx=cmm.rNB.index('current')  #当前index
    maxX=0
    for c in cmm.lstSW:  #找出最左边的x值
        x1=int(cmm.filePath[idx][2][c.wgtName]['x'][0])
        width=int(cmm.filePath[idx][2][c.wgtName]['width'][0])
        x2=x1+width
        if x2>maxX:maxX=x2  
    for c in cmm.lstSW:  #设置
        width=int(cmm.filePath[idx][2][c.wgtName]['width'][0])
        cmm.filePath[idx][2][c.wgtName]['x'][0]=str(maxX-width)
        c.place({'x':maxX-width})
def align_bottom():  #下对齐选定的控件
    if cmm.guiL!='place':return
    idx=cmm.rNB.index('current')  #当前index
    maxY=0
    for c in cmm.lstSW:  #找出最下边的y值
        y1=int(cmm.filePath[idx][2][c.wgtName]['y'][0])
        height=int(cmm.filePath[idx][2][c.wgtName]['height'][0])
        y2=y1+height
        if y2>maxY:maxY=y2  
    for c in cmm.lstSW:  #设置
        height=int(cmm.filePath[idx][2][c.wgtName]['height'][0])
        cmm.filePath[idx][2][c.wgtName]['y'][0]=str(maxY-height)
        c.place({'y':maxY-height})
def mode_conversion(fStr=0): #本页内模式转换，fStr是光标要移动到的目标函数名  
    pageON=cmm.rNB.select()  #取得当前页类名路径 
    if not pageON:
        messagebox.showerror(cmm.t('错误'),cmm.t('请先打开py文件'))
        return 0
    pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典的key 
    index=cmm.rNB.index("current")
    fileN=cmm.rNB.tab(pageON, "text")  #取得当前选中的标签上的文件名    
    #保存(pageON,pageKey,index)#保存当前文件
    if 'text' in pageON:  #文本模式转换成图形模式 
        cmm.rNB.children[pageKey].coloring=0 #退出goColor定时器
        cmm.filePath[index][1]=cmm.rNB.children[pageKey].get()  #文本内容从text控件中取出放入filePath中的1 
        try: 
            cmm.prmToRC(index)  #界面代码转化成属性写入filePath。menuRight模块中的prmToRC函数  
            cmm.rNB.children[pageKey].destroy()  #
            canvasObj=dragCan.dragCanvas(index)  #创建图形界面
            if index<len(cmm.rNB.tabs()):  #页插入指定位置
                cmm.rNB.insert(index,canvasObj, text=fileN)              
            else:#在末尾加入页
                cmm.rNB.add(canvasObj, text=fileN)  
            cmm.rNB.select(canvasObj)
            showGUI(index)  #从filePath中转化成图形控件   
            if cmm.hasMenu(index):  #检查是否存在菜单代码
                btn=tk.Button(cmm.filePath[index][3]['cvsGUI'],text='menuBar',command=lambda:makeMenu(),name='menuBtn')#cvsGUI加入菜单按钮
                btn.place(x=200,y=0,width=100,height=15)
                btn.bind('<Button-3>',lambda event,index=index:cmm.menuR(event,index)) # 右击控件
            #cmm.smartScb(index) #禁用/恢复滚动条
            cmm.showSG()#显示界面结构     
        except Exception as e:
            messagebox.showerror(cmm.t('错误'),e) 
        cmm.pw.sashpos(0,280)  #缩小左边窗口宽度。分割线索引（从0开始），位置
    else:  #图形模式转换成文本模式  
        cmm.lstSW.clear()   
        #cmm.uNB.tab(1, state="disabled")  #控件面板不可用
        if len(cmm.filePath[index][2])==1 and 'cvsGUI' in cmm.filePath[index][2]:  #主界面是空的,只修改winW、winH值，不做wgtToCode
            lst=cmm.filePath[index][1].split('\n')
            aa=0
            for i in range(len(lst)): #设置winW、winH值
                aa=lst[i].strip()
                if not aa.find('winW=') and aa[int(aa.find('='))+1:]!=cmm.filePath[index][2]['cvsGUI']['width'][0]:
                    lst[i]=f"    winW={cmm.filePath[index][2]['cvsGUI']['width'][0]}"
                elif not aa.find('winH=') and aa[int(aa.find('='))+1:]!=cmm.filePath[index][2]['cvsGUI']['height'][0]:
                    lst[i]=f"    winH={cmm.filePath[index][2]['cvsGUI']['height'][0]}"
            cmm.filePath[index][1]='\n'.join(lst)
        else: #主界面中有控件
            try:
                cmm.filePath[index][1]=wgtToCode(index)    #控件参数转化成文本写入filePath 1
            except Exception as e:
                messagebox.showerror(cmm.t('错误'),e)
        cmm.rNB.children[pageKey].destroy()  #销毁其中的基础cavans控件
        textObj=codeTxt.dragText()#创建文本界面
        if index<len(cmm.rNB.tabs()):  #页插入指定位置
            cmm.rNB.insert(index,textObj, text=fileN)  
        else:
            cmm.rNB.add(textObj, text=fileN)  
        cmm.rNB.select(textObj)  
        textObj.insert('1.0',cmm.filePath[index][1])  #显示文本内容
        if fStr:  #查找字符串并定位
            sPos = textObj.textNow.search(fStr,'1.5',stopindex='end')  #起始位置
            if sPos:  #找到了字符串
                ePos=f"{sPos}+{len(fStr)}c"  #结束位置
                textObj.textNow.see(sPos)  #代码框滚动到匹配位置
                sPos=str(int(sPos[:sPos.find('.')])+1)+'.13'
                textObj.textNow.mark_set('insert',sPos)  #光标移动到匹配位置,sPos的值已经更换
                textObj.textNow.focus_set()  #文本框成为焦点光标才会闪烁
        cmm.table.delete(*cmm.table.get_children())#清空表
        cmm.pw.sashpos(0,25)  #缩小左边窗口宽度。分割线索引（从0开始），位置
def rcW(it):#rowconfigure、columnconfigure字符串参数解析
    lstIt=it.split(',')
    rc=int(lstIt[0])
    lstIt=lstIt[1].split('=')
    w={lstIt[0]:lstIt[1]}
    return rc,w
def showGUI(index):#从filePath[index][2]列表中转化成图形控件    
    dctIco={}  #放ico对象
    pageON=cmm.rNB.select()  #取得当前页类名
    pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典key
    cmm.filePath[index][3].clear()  #清空控件对象字典
    for k,v in cmm.filePath[index][2].items():  #k是控件名
        if k=='cvsGUI':
            cmm.filePath[index][3]['cvsGUI']=cmm.rNB.children[pageKey].cvsGUI  #cvsGUI对象写入filePath
            for kp,vp in v.items(): 
                if kp=='rowconfigure':
                    for it in vp: 
                        r,w=rcW(it)
                        cmm.rNB.children[pageKey].cvsGUI.rowconfigure(r,**w) 
                    continue      
                elif kp=='columnconfigure':
                    for it in vp: 
                        col,w=rcW(it)
                        cmm.rNB.children[pageKey].cvsGUI.columnconfigure(col,**w) 
                    continue
                cmm.filePath[index][3]['cvsGUI'].place({kp:int(vp[0])})    #根据参数设置界面cvsGUI对象                          
            continue 
        if v['parent'][0]=='root':#父控件是root,同时确定主界面布局方式
            canvasWgt=sc.SelectedCanvas(cmm.rNB.children[pageKey].cvsGUI,k)#创建移动canvas，此画布大小就是控件的大小 
            if not cmm.guiL:  #确定主界面布局方式
                cmm.guiL=next((x for x in ('pack','grid') if x in v),'place')
        else:   #父控件是其他  
            for kp,vp in cmm.filePath[index][3].items():  #找到父控件对象，创建移动canvas
                if kp==v['parent'][0]:
                    canvasWgt=sc.SelectedCanvas(vp,k)#创建移动canvas，此画布大小就是控件的大小 
                    break
        classN=k[:k.find('_')]  #取得类名                
        if classN in lstTtk:   #在移动canvas中创建ttk控件    
            cmm.filePath[index][3][k]=canvasWgt.create_widget(getattr(ttk,classN))  
        else:   #在移动canvas中创建tk控件  
            cmm.filePath[index][3][k]=canvasWgt.create_widget(getattr(tk,classN))   
        for kp,vp in v.items(): #设置控件。kp是属性名
            if kp=='parent' or kp=='bind':continue      
            if kp=='rowconfigure' or kp=='columnconfigure': 
                for x in vp: 
                    rc,w=rcW(x)
                    getattr(canvasWgt,kp)(rc,**w)
                continue
            if kp=='pack' or kp=='grid':  #pack或者grid布局
                argDct={}
                for kpp,vpp in vp.items(): #取得控件pack或者grid中的属性值
                    if vpp[0]: 
                        if vpp[1]=='string' :argDct[kpp]=vpp[0]
                        elif '(' in vpp[0]: argDct[kpp]=ast.literal_eval(vpp[0])
                        else: argDct[kpp]=int(vpp[0])
                getattr(canvasWgt,kp)(**argDct) #显示效果            
            elif kp=='image': 
                if vp[0][1:2]==':': dctIco[k]=tk.PhotoImage(file=vp[0])  #绝对路径
                else: dctIco[k]=tk.PhotoImage(file='ico/ff.png')  #方块代替
                canvasWgt.widget[kp]=dctIco[k]
                canvasWgt.image =dctIco[k]   
            elif vp[0]:  #有属性值
                if vp[1]=='int':val=int(vp[0])
                elif vp[1]=='bool':val=dctBool[vp[0]]
                elif vp[1]=='float':val=float(vp[0])
                else: val=vp[0]
                if (kp in lstPlace) and cmm.filePath[index][2][k].get('x'):  #是控件canvas位置长宽,且是place布局
                    canvasWgt.place({kp:val})
                elif kp=='font': #是字体
                    try:
                        dct=ast.literal_eval(vp[0])  #字符串‘{...}’转化成字典。不行就用ast.literal_eval()
                    except :
                        messagebox.showerror(cmm.t('错误'),cmm.t("字符串'{}'转化成字典失败。请修改后再做").format(vp[0]))
                        return
                    canvasWgt.widget[kp]=tk.font.Font(**dct)
                else:    
                    canvasWgt.widget[kp]=val #其他属性 
def wgtToCode(index):  #filePath[index][2]列表转化成文本
    content=cmm.filePath[index][1] 
    lst=content.split('\n')
    for i in range(len(lst)-1,-1,-1):  #删除其中的空行元素
        if not lst[i].strip():del lst[i]
    si,ei=0,0 #起始位置，结束位置
    for i,it in enumerate(lst):  #删除原界面代码
        if 'def makeGUI(self,root)' in it:si=i+1 #开始位置
        elif ('def ' in it or '#------' in it) and si:
            ei=i #结束位置
            break
        if si and i>=si: lst[i]=''  #原控件代码都设置为空
    if not ei:return 
    for i in range(len(lst)-1,-1,-1):  #删除原控件代码
        if not lst[i]:del lst[i]           
    lstBind=[]  #绑定事件语句列表       
    lstRCfg=[] #rowconfigure语句列表
    lstCCfg=[]  #columnconfigure语句列表
    for k,v in cmm.filePath[index][2].items():  #{k:v,...},k是控件名，v是{kp:vp,...}，v中kp是各属性名，vp是[值,值类型]            
            if k=='cvsGUI':  #界面canvas
                for i in range(len(lst)-1,-1,-1): #设置界面宽高及删除rowconfigure等语句
                    if ('rowconfigure' in lst[i]) or ('columnconfigure' in lst[i]):  #删除rowconfigure等语句
                        del lst[i]
                    elif 'winH=' in lst[i]: 
                        lst[i]='    winH='+str(v['height'][0])                    
                    elif 'winW=' in lst[i]: 
                        lst[i]='    winW='+str(v['width'][0])
                        break
                i+=1
                if v.get('rowconfigure'):
                    for x in v['rowconfigure']:  #添加语句    
                        i+=1 
                        lst.insert(i,f'    root.rowconfigure({x})')
                if v.get('columnconfigure'):
                    for x in v['columnconfigure']:#加语句  
                        i+=1 
                        lst.insert(i,f'    root.columnconfigure({x})')
                continue            
            stcF=''  #字符设置语句  content=tk.font.Font(**content) 
            stcN=''  #创建控件的语句
            stcP=''  #place、pack、grid语句             
            stcImg=''  #image有关语句
            lstBind.clear()
            lstRCfg.clear()
            lstCCfg.clear()
            for kp,vp in v.items(): #kp是属性名，vp是属性值和属性类型
                if kp=='parent':
                    if vp[0]=='root' or not vp[0]:  #root是父控件,parent属性值为空默认为root
                        if k[:k.find('_')] in lstTtk: stcN='        self.'+k+"=ttk."+k[:k.find('_')]+"(root,)"  #创建ttk控件
                        else: stcN='        self.'+k+"=tk."+k[:k.find('_')]+"(root,)"  #创建tk控件
                    else:  #父控件是其他
                        if k[:k.find('_')] in lstTtk: stcN=f'        self.{k}=ttk.{k[:k.find("_")]}(self.{vp[0]},)'  #创建ttk控件
                        else: stcN=f'        self.{k}=tk.{k[:k.find("_")]}(self.{vp[0]},)' #创建tk控件
                    continue                
                if kp=='bind':  #绑定事件                     
                    for i in range(len(vp)):
                        lstBind.append(f'        self.{k}.bind({vp[i]})')
                elif kp=='pack'or kp=='grid':  #pack、grid布局
                    for kpp,vpp in vp.items():
                        if not stcP:stcP=f'        self.{k}.{kp}()'
                        if vpp[0]:
                            if vpp[1]=='string': 
                                stcP=f"{stcP[:stcP.rfind(')')]}{kpp}='{vpp[0]}',)"
                            else: stcP=f'{stcP[:stcP.rfind(")")]}{kpp}={vpp[0]},)'
                elif kp=='rowconfigure':                    
                    for x in vp:
                        lstRCfg.append(f'        self.{k}.rowconfigure({x})') 
                elif kp=='columnconfigure':                     
                    for x in vp:
                        lstCCfg.append(f'        self.{k}.columnconfigure({x})')                
                elif kp in lstWxy and v.get('x'):#大小位置等属性，且是place布局
                    if not stcP:stcP='        self.'+k+'.place()'
                    stcP=stcP[:stcP.find(')')]+kp+'='+vp[0]+',)'
                elif kp=='font':  #字体属性
                    stcF='        self.'+k+'Ft=tk.font.Font(**' +vp[0]+')'
                    stcN=f'{stcN[:stcN.find(",)")+1]}{kp}=self.{k}Ft,)'                 
                elif kp=='image': #image有关语句 
                    if vp[0][1:2]==':': stcImg=f'        self.ico{k}=tk.PhotoImage(file="{vp[0]}");        self.{k}.image=self.ico{k}' #绝对路径
                    else: stcImg=f'        self.ico{k}=tk.PhotoImage(file={vp[0]});        self.{k}.image=self.ico{k}'  #有f'{}'                           
                    stcN=f'{stcN[:stcN.find(",)")+1]}{kp}=self.ico{k},)' 
                elif vp[0]: #其他属性有值   
                    if vp[1]=='string':stcN=stcN[:stcN.rfind(')')]+kp+"='"+vp[0]+"',)"
                    else: stcN=stcN[:stcN.find(',)')+1]+kp+"="+vp[0]+',)'
            if stcF:  #控件字体语句
                stcF=stcF.replace(',)',')',1)
                lst.insert(si,stcF)  
                si+=1
            if stcImg:#ico语句
                lst.insert(si,stcImg[:stcImg.find(';')])  
                si+=1
            stcN=stcN.replace(',)',')',1)#创建控件的语句
            lst.insert(si,stcN)  
            si+=1 
            if stcImg: #image相关语句
                lst.insert(si,stcImg[stcImg.find(';')+1:])  
                si+=1
            for i in range(len(lstBind)):  #bind语句
                lst.insert(si,lstBind[i])
                si+=1
            if stcP:#控件放置语句
                stcP=stcP.replace(',)',')',1)
                lst.insert(si,stcP)  
                si+=1            
            for x in lstRCfg:  #rowconfigure语句,在GUI类中                
                lst.insert(si,x)
                si+=1
            for x in lstCCfg:  #columnfigure语句,在GUI类中
                lst.insert(si,x)
                si+=1
    if ei-si==1:lst.insert(si,'        pass')   #没有控件
    return '\n'.join(lst)