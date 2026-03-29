import tkinter as tk
from tkinter import messagebox
import os
from shutil import rmtree,copy,copy2,copytree  #删除文件夹,复制文件
import re
import widgetProperty as wp
import codeTxt
import cmm 
import win32clipboard
import ctypes
from ctypes import wintypes
import pythoncom

iidSlt=0  #选中的文件或者文件夹
lstOpen=[] #已经打开的文件夹的名称
nowPath=0  #当前文件夹路径
lstLM=('.place','.pack','.grid','.rowconfigure','.columnconfigure')

def refTree(sltFileN=None,folderPath=None):  #刷新目录树  
        global lstOpen,nowPath        
        cmm.tree.delete(*cmm.tree.get_children())#清空目录树
        if not folderPath and not nowPath: 
            nowPath=os.getcwd()     #当前文件夹     
        elif folderPath:  
            if os.path.exists(folderPath):  #文件夹是否存在
                nowPath=folderPath  #当前文件夹
            else:nowPath= os.getcwd()    #当前文件夹
        root=cmm.tree.insert('', 'end',text=os.path.split(nowPath)[-1],open=1,image=cmm.icoFN,values=['目录',nowPath])  #根文件夹
        load_tree(root,nowPath,sltFileN)  #显示树 
        for i in range(15): #在内容下方加入15行空行
            cmm.tree.insert('', 'end',text='')
def load_tree(parent,nowPath,sltFileN=None):  #显示树。递归
        for fileName in os.listdir(nowPath):
            absPath = nowPath+'/'+fileName
            if os.path.isdir(absPath):  #该路径是文件夹
                #if itemC==os.path.basename(absPath): #该文件夹是选中的就打开，否则关闭
                if fileName in lstOpen:#该文件夹原来是打开状态就打开，否则关闭
                    treeF = cmm.tree.insert(parent, 'end',text=fileName,image=cmm.icoFN,values=['目录',nowPath],open=1) #文件夹是打开的
                else: treeF =cmm.tree.insert(parent, 'end',text=fileName,image=cmm.icoFolder,values=['目录',nowPath]) #文件夹是关闭的
                load_tree(treeF,absPath)
            else:  #该路径是文件
                treeF =cmm.tree.insert(parent, 'end',text=fileName,image=cmm.icoFile, values=['文件',nowPath]) 
                if fileName==sltFileN : 
                    cmm.tree.selection_set(treeF)  #该项设置为选中状态
#--------------------------------右击菜单---------------------------------------------
def treeSlt(event):  #右击了树
        global iidSlt
        iid = cmm.tree.identify_row(event.y)
        if iid:
            iidSlt=iid
            if not cmm.tree.item(iid)["text"]: return 0
            cmm.tree.selection_set(iid)                   # 设置选中
            pastePath = pathWin()# 获取剪贴板中的文件路径             
            if cmm.tree.item(iid)['values'][0]== '目录':
                folderR =tk.Menu(tearoff=False)
                folderR.add_command(label=cmm.t('新建文件夹'), command=lambda:newFolder())
                folderR.add_command(label=cmm.t('新建界面文件'), command=lambda:newFile())             
                folderR.add_command(label=cmm.t('新建空白文件'), command=lambda:newFile(1))                                     
                folderR.add_separator()
                folderR.add_command(label=cmm.t('复制'), command=lambda:copyFile())  
                #if not cmm.tree.parent(iidSlt):folderR.entryconfig("复制", state="disabled")  #
                folderR.add_command(label=cmm.t('重命名'), command=lambda:renFolder(event))
                if pastePath: folderR.add_command(label=cmm.t('粘贴'), command=lambda:pasteFile())
                folderR.add_command(label=cmm.t('刷新'), command=lambda:refTree())
                folderR.add_separator()                
                folderR.add_command(label=cmm.t('删除'), command=lambda:delFolder())
                if not cmm.tree.parent(iidSlt):folderR.entryconfig(cmm.t("删除"), state="disabled")  #不能删除根目录  
                folderR.post(event.x_root, event.y_root)     # 光标位置显示菜单
            elif cmm.tree.item(iid)['values'][0]== '文件':
                fileR = tk.Menu(tearoff=False)
                fileR.add_command(label=cmm.t('打开'), command=lambda:doubleLeft(event,))                             
                fileR.add_command(label=cmm.t('复制'), command=lambda:copyFile())  
                fileR.add_command(label=cmm.t('另存为'), command=lambda:saveAs())   
                fileR.add_command(label=cmm.t('重命名'), command=lambda:renFile())
                fileR.add_separator()  
                fileR.add_command(label=cmm.t('删除'), command=lambda:delFile())     
                fileR.post(event.x_root, event.y_root)
def getNowPath(item): #获取Treeview中的路径，还只是相对路径
    path = []    
    while item:# 从当前item开始，不断追溯其父节点       
        path.append(cmm.tree.item(item, "text")) # 获取当前item的文本        
        item = cmm.tree.parent(item)# 获取父节点ID    
    return "/".join(reversed(path))# 倒序排列，并连接成字符串
def newFolder():  #新建文件夹
        folderN = tk.simpledialog.askstring(title=cmm.t('新建文件夹'), prompt=cmm.t('新建文件夹名：'))
        if folderN!=None:
            if cmm.tree.item(iidSlt)['values'][1]==nowPath:
                folderPath=cmm.tree.item(iidSlt)['values'][1]+'/'+folderN
            else:
                folderPath=cmm.tree.item(iidSlt)['values'][1]+'/'+cmm.tree.item(iidSlt)["text"] #选中的目录
                folderPath=folderPath+'/'+folderN
            try:
                os.makedirs(folderPath)
            except Exception as e:
                messagebox.showerror(cmm.t('错误'),cmm.t("新建文件夹{}失败{}").format(folderPath,e))
            else: refTree()                
class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt",     wintypes.POINT),
        ("fNC",    wintypes.BOOL),
        ("fWide",  wintypes.BOOL),
    ]  #DROPFILES结构体
def copyFile():  #复制文件或文件夹到剪贴板
    if cmm.tree.parent(iidSlt): srcPath=cmm.tree.item(iidSlt)['values'][1]+'/'+cmm.tree.item(iidSlt, "text") #子目录 
    else: srcPath=cmm.tree.item(iidSlt)['values'][1]  #根目录  
    data = (srcPath+ '\0').encode('utf-16-le')# 转换路径为宽字符(UTF-16)
    drop = DROPFILES()
    drop.pFiles = ctypes.sizeof(DROPFILES)
    drop.fWide  = True
    blob = bytes(drop) + data + b'\x00\x00'  # 组合数据：DROPFILES结构体 + 路径字节 + 最终的null终止符                  
    win32clipboard.OpenClipboard()# 打开剪贴板
    try:                
        win32clipboard.EmptyClipboard()# 清空剪贴板                
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP,blob)# 设置CF_HDROP格式数据
    finally:                
        win32clipboard.CloseClipboard()    # 确保关闭剪贴板 
def pathWin():  #"""从windows系统剪贴板获取复制的路径"""        
        try:
            pythoncom.CoInitialize()# 初始化COM。一定要有    
            win32clipboard.OpenClipboard()    
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):# 检查剪贴板有CF_HDROP格式数据
                files = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                return files
            return 0
        except Exception as e:
            messagebox.showerror(cmm.t('错误'),cmm.t("获取剪贴板内容错误: {}").format(e))
            return 0
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass   # 如果没打开成功，忽略即可
            pythoncom.CoUninitialize()# 释放COM
def pasteFile():#"""粘贴文件或文件夹到当前目录""" 
        pastePath = pathWin()# 获取剪贴板中的文件路径
        if not pastePath:  return  #没有要粘贴的文件      
        success_count = 0# 复制文件数量
        error_count = 0  #无法复制数量
        error_files = []  #  
        fdPath=getNowPath(iidSlt)
        for srcPath in pastePath:
            try:                
                fileN = os.path.basename(srcPath)# 获取文件名
                if cmm.tree.parent(iidSlt):tp=cmm.tree.item(iidSlt)['values'][1]+'/'+cmm.tree.item(iidSlt,"text") #目标是子目录                           
                else: tp=cmm.tree.item(iidSlt)['values'][1]  # 目标是根目录
                dstPath=tp+'/'+fileN
                counter = 1# 处理文件重名
                while os.path.exists(dstPath):  #如果存在同名文件，则加序号，直到不重名为止
                    name, ext = os.path.splitext(fileN)
                    fileN=f"{name}({counter}){ext}"
                    dstPath = tp+'/'+fileN  #加序号
                    counter += 1                                
                if os.path.isdir(srcPath):# 复制整个文件夹
                    copytree(srcPath, dstPath)
                else:# 复制文件
                    copy2(srcPath, dstPath)                
                success_count += 1
            except Exception as e:
                error_count += 1
                error_files.append(f"{srcPath}：\n{str(e)}")         
        if cmm.tree.item(iidSlt,'text') not in lstOpen:lstOpen.append(cmm.tree.item(iidSlt,'text'))
        refTree()  #刷新目录树  
        search_file(fdPath,fileN)
        if error_count > 0:
            result_msg=cmm.t('成功复制{}个文件，失败{}个文件\n').format(success_count,error_count)
            result_msg+=cmm.t("失败的文件:") + "\n".join(error_files[:5])
            if len(error_files) > 5:
                result_msg += cmm.t("\n... 还有 {} 个错误").format(len(error_files)-5)        
            messagebox.showinfo(cmm.t("粘贴失败"), result_msg)
def getAllNodes(tree,parent=""):#"""递归获取Treeview中所有节点的ID，返回列表"""    
    nodes = []    
    children = tree.get_children(parent)# 获取当前父节点下的直接子节点
    for child in children:
        nodes.append(child)        
        nodes.extend(getAllNodes(tree,child))# 递归获取子节点的后代节点
    return nodes
def search_file(folderPath,fileN):#根据文件名搜索并选中文件"""（复制后显示选中的文件）      
    f=0
    for iid in getAllNodes(cmm.tree):#查找全部
        if cmm.tree.item(iid)['values'][0]== '目录':  #是文件夹            
            if folderPath==getNowPath(iid):  #找到文件夹                
                for it in getAllNodes(cmm.tree,iid):  #查找其中所有的文件
                    if fileN==cmm.tree.item(it)["text"]:  #找到文件
                        cmm.tree.selection_set(it)
                        cmm.tree.focus(it)
                        cmm.tree.see(it)  # 滚动到可见位置
                        f=1
                        break
        if f: break        
    else:
        messagebox.showerror(cmm.t('错误'),cmm.t("未找到文件{}").format(fileN)) 
def saveAs():  #另存为
    oldN=cmm.tree.item(iidSlt)["text"]
    fileN = tk.simpledialog.askstring(title=cmm.t('另存为'), prompt=cmm.t('新文件名：'),initialvalue=oldN)
    if not fileN or oldN==fileN:return            
    dstPath=cmm.tree.item(iidSlt)['values'][1]+'/'+fileN
    if not os.path.exists(dstPath):   #不存在同名文件    
        srcPath=cmm.tree.item(iidSlt)['values'][1]+'/'+oldN
        copy(srcPath,dstPath)
        refTree(fileN)
    else:messagebox.showerror(cmm.t('错误'),cmm.t("无法另存为。文件{}已经存在。").format(fileN))
def openFolder(e,icoFN):  #设置目录打开的图标
        global lstOpen
        iid=e.widget.selection()
        if iid and cmm.tree.item(iid)['values'][0]=='目录':
            cmm.tree.item(iid,image=icoFN)            
            lstOpen.append(cmm.tree.item(iid,'text'))  #记录打开状态的文件夹名
def closeFolder(e,icoFolder):  #设置目录关闭的图标
        global lstOpen
        iid=e.widget.selection()
        if cmm.tree.item(iid)['values'][0]=='目录':
            cmm.tree.item(iid,image=icoFolder)
            for i in range(len(lstOpen)):  #删除打开状态的文件夹名
                if lstOpen[i]==cmm.tree.item(iid,'text'):
                    del lstOpen[i]
                    break
def delFolder():  #删除文件夹
        folderPath=cmm.tree.item(iidSlt)['values'][1]+'/'+cmm.tree.item(iidSlt)["text"] #选中的目录
        if messagebox.askyesno(cmm.t('删除文件夹'), cmm.t("要删除文件夹 {} 吗 ?").format(cmm.tree.item(iidSlt)['text'])):
            try:
                rmtree(folderPath)
            except Exception as e:
                messagebox.showerror(cmm.t('错误'),e)
                return 0
            if cmm.tree.item(iidSlt)["text"] in lstOpen:
                for i in range(len(lstOpen)):  #删除打开状态的文件夹名
                    if lstOpen[i]==cmm.tree.item(iidSlt,'text'):
                        del lstOpen[i]
                        break
            refTree()
def renFolder(event):  #文件夹重命名
        cmm.tree.selection_remove(cmm.tree.selection()) # 取消表格选取
        oldN=cmm.tree.item(iidSlt)["text"]        
        folderN = tk.simpledialog.askstring(title=cmm.t('文件夹重命名'), prompt=cmm.t('新文件夹名：'),initialvalue=oldN)
        if not folderN:return
        dst=cmm.tree.item(iidSlt)['values'][1]+'/'+folderN
        if dst!=None:
            if not os.path.exists(dst):            
                src=cmm.tree.item(iidSlt)['values'][1]+'/'+cmm.tree.item(iidSlt)["text"]
                try:
                    os.rename(src,dst)
                except Exception as e:
                    messagebox.showerror(cmm.t('错误'),cmm.t("无法重命名。文件夹{}已经存在。").format(folderN))
                else: 
                    refTree()   
def 新建文件(filePath,blank=0):  #新建文件
        fileN=os.path.basename(filePath)
        if os.path.exists(filePath):  #已经存在文件名或者文件夹名
            messagebox.showerror(cmm.t('错误'),cmm.t('文件已经存在。请用其他文件名。'))
            return
        baseN,ext=os.path.splitext(fileN)  #得到文件名和扩展名
        if baseN.isdigit():baseN=''
        else:
            for i in range(len(baseN)):  #删除开头是数字的字符
                if not baseN[i].isdigit():
                    baseN=baseN[i:]
                    break
        baseN+='UI'
        with open(filePath, 'w', encoding='utf-8') as f:
            if blank:f.write('')
            else:
                f.write(
                "import tkinter as tk\nimport tkinter.font\nfrom tkinter import ttk \n"
                '#Auto-generated by the system. Do NOT modify the makeGUI() function arbitrarily--------Do not delete this line----\n'
                'class '+baseN+':\n    def __init__(self,root):\n        self.makeGUI(root)\n'
                '    def makeGUI(self,root):\n        pass\n'
                '#-------------------------------------------------------Do not delete this line------------\n'
                "if __name__ == \"__main__\":  #Do NOT modify the content below without authorization-----\n"
                '    root = tk.Tk()\n    root.option_add("*Font",' +'"'+cmm.t("微软雅黑")+' 10")  #Global font: controls the font size of root-based widgets\n'
                '    root.option_add("*Menu.font", '+'"'+cmm.t("微软雅黑")+' 10")  #Font for menu items\n'
                "    root.title('')\n    myDlg="+baseN+"(root)\n    winW=600\n    winH=400\n    screenW = root.winfo_screenwidth()\n"
                "    screenH = root.winfo_screenheight()\n    mainWin ='%dx%d+%d+%d'%(winW,winH,(screenW-winW)//2,(screenH-winH)//2)\n"
                "    root.geometry(mainWin)\n    root.resizable(width=True, height=True)\n    root.mainloop()\n    "
                )
        refTree()  #刷新工程资源管理器
        打开文件(filePath)
def 打开文件(filePath):
    for i in range(len(cmm.filePath)):
        if filePath == cmm.filePath[i][0]:
            messagebox.showinfo(cmm.t('提示'), cmm.t('该文件已经打开'))
            cmm.rNB.select(i)
            return 0    
    try:
        with open(filePath,'r',encoding="utf-8") as f:
            content=f.read().rstrip()
    except:  #上面出错 ，执行下面这句
        messagebox.showerror(cmm.t('错误'),cmm.t('无法打开文件。请检查文件是否存在或者是否“utf-8”格式'))
        return 0      
    cmm.filePath.append([filePath,'',{},{},0])  #‘’文件内容,{}控件内容，{}创建的所有控件,0是没有编辑过
    for it in cmm.filePath:  #文件内容放入filePath
        if filePath == it[0]:
            it[1]=content
            break    
    fileN=os.path.basename(filePath)  #文件名
    for pon in cmm.rNB.tabs():  #查找是否有相同的标签文本
        if cmm.rNB.tab(pon,'text').strip()==fileN:
            fileN=f'{fileN}——{os.path.dirname(filePath).replace(":","")}'
            break
    if len(fileN)<15:fileN=fileN.ljust(15)  #限制为15个字符宽度
    textObj=codeTxt.dragText()
    cmm.rNB.add(textObj, text=fileN)  #添加text页
    cmm.rNB.select(textObj)  #选择当前Tab
    textObj.insert('1.0',content)    
    cmm.table.delete(*cmm.table.get_children())#清空表    
    index=cmm.rNB.index("current")    
    #textObj.idx=index
    if '#Auto-generated by the system' in content and 'Do not delete this line-' in content:  #是本软件格式的文件
        try:
            prmToRC(index)  #打开文件时，控件属性写入filePath字典
        except Exception as e:
            messagebox.showerror(cmm.t('错误'),e)
    else: cmm.btnMC['state']='disabled'  #禁用模式转换功能    
    #cmm.uNB.tab(1, state="disabled")  #禁用控件面板
    #cmm.uNB.tab(1, state="normal")  #控件关系面板可用
def newFile(blank=0):  #新建文件。blank=0是页面文件，1是空白文件
        global iidSlt        
        fileN= tk.simpledialog.askstring(title=cmm.t('新建文件'), prompt='File Name (*.py)：')        
        if fileN:
            if fileN.find('.')==-1:fileN=fileN+'.py' 
            if not iidSlt:iidSlt=cmm.tree.get_children()[0] #得到根节点
            baseFolderN=os.path.basename(cmm.tree.item(iidSlt)['values'][1])
            sltFolderN=cmm.tree.item(iidSlt)['text']
            if baseFolderN==sltFolderN:  #在project下新建
                filePath=cmm.tree.item(iidSlt)['values'][1]+'/'+fileN
            else:  #在其他文件夹下新建
                filePath=cmm.tree.item(iidSlt)['values'][1]+'/'+sltFolderN+'/'+fileN         
            新建文件(filePath,blank)
            refTree(fileN)   
def doubleLeft(event,):  # 双击文件图标,打开文件
        global iidSlt
        iid = cmm.tree.identify_row(event.y)
        if iid:
            iidSlt=iid
            cmm.tree.selection_set(iid)           # 设置选中
            if cmm.tree.item(iid)['values'][0]== '文件':
                #filePath=os.path.join(cmm.tree.item(iid)['values'][1],cmm.tree.item(iid)["text"])
                filePath=cmm.tree.item(iid)['values'][1]+'/'+cmm.tree.item(iid,"text")
                打开文件(filePath)
def delFile():  #删除文件
        #filePath=os.path.join(cmm.tree.item(iidSlt)['values'][1],cmm.tree.item(iidSlt)["text"])  #选中的文件
        filePath=cmm.tree.item(iidSlt)['values'][1]+'/'+cmm.tree.item(iidSlt)["text"]
        if messagebox.askyesno(cmm.t('删除文件'), cmm.t("要删除文件 {} 吗 ?").format(cmm.tree.item(iidSlt)['text'])):
            os.unlink(filePath)  #删除文件
            refTree()  #刷新目录树
            for i in range(len(cmm.filePath)):  #删除已经打开的文件
                if cmm.filePath[i][0]==filePath:                    
                    pon=cmm.rNB.tabs()[i]  #页类名路径
                    pageKey=pon[pon.rfind('!'):]  #从页类名路径中取得页字典的key 
                    cmm.rNB.children[pageKey].destroy()  #销毁其中的控件
                    del cmm.filePath[i]  #删除文件记录
                    break        
def renFile():  #文件重命名
        oldN=cmm.tree.item(iidSlt)["text"]
        x, y, width, height = cmm.tree.bbox(iidSlt,column='#0')
        x+=32
        entry = tk.Entry(cmm.tree,bg='white')
        entry.place(x=x, y=y, width=width,height=height)
        entry.insert(0,oldN)
        entry.focus()
        def saveN(e,oldN):
            fileN = entry.get().strip()            
            entry.destroy()
            if not fileN or oldN==fileN:return            
            dstPath=cmm.tree.item(iidSlt)['values'][1]+'/'+fileN
            if not os.path.exists(dstPath):   #不存在同名文件 
                cmm.tree.item(iidSlt, text=fileN)  #修改节点内容     
                srcPath=cmm.tree.item(iidSlt)['values'][1]+'/'+oldN
                os.rename(srcPath, dstPath)
                refTree(fileN)
                for i,pon in enumerate(cmm.rNB.tabs()):
                    tabN=cmm.rNB.tab(pon,'text').strip()  #取得标签名
                    if tabN==oldN:
                        cmm.filePath[i][0]=dstPath  #filePath更新路径名
                        cmm.rNB.tab(pon,text=fileN)  #更改标签名
                        break    
            else:messagebox.showerror(cmm.t('错误'),cmm.t("无法重命名。文件{}已经存在。").format(fileN))
        entry.bind("<Return>", lambda e,oldN=oldN:saveN(e,oldN))
        entry.bind("<FocusOut>", lambda e: entry.destroy())        
def prmToRC(index):  #界面代码文本转化成属性写入filePath[index][2]列表
    lst=cmm.filePath[index][1].split('\n')
    for i in range(len(lst)-1,-1,-1):  #删除其中的空格行
        lst[i]=lst[i].strip()  #去掉前后空格
        if not lst[i]:del lst[i]   #删除其中的空行
        elif '.bind' in lst[i]: lst[i]=lst[i][5:]  #去掉前面1个self.即可，后面的self.保留
        else:lst[i]=lst[i].replace('self.','')  #去掉所有self.    
    si,ei=0,0  #界面控件语句，开始位置,结束位置
    for i,it in enumerate(lst):  #记录起止位置。其他语句要保留，后面有用
        if 'def makeGUI(self,root)' in it:si=i+1   #开始位置
        elif ('def ' in it or '#------' in it) and si:  #找到结束位置
            ei=i  #结束位置
            break
    if not si:return #不是此系统生成的代码文件，退出 
    cmm.filePath[index][2].clear()  #清空控件属性字典  
    cmm.filePath[index][2]['cvsGUI']={'width':['600','int'],'height':['400','int']}
    #p1=re.compile(r"[,\(] *(\w+) *=(\(\d+,\d+\))") 
    p1=re.compile(r"[,\(] *(\w+) *='?\"?(\(\d+,\d+\)|[#:\w\u4e00-\u9fff]+)\"?'?")  #找 属性名=属性值，[\u4e00-\u9fff]近似匹配常用中文字符
    pT=re.compile(r"[,\(] *(text) *='?\"?([^'^\"]*)\"?'?")  #找text属性及内容。 属性名=属性表达式。（）外的都是非捕获组，只是匹配时要用
    nameImg,lm,lmRoot,flag=0,0,0,0  #lm当前控件布局方式，lmRoot主界面布局方式
    for i in range(si,ei):
        flag=0
        if lst[i]=='pass':continue        
        if lst[i][0]=='#':continue
        if lst[i].strip().find('ico')==0:  #ico语句（image属性用）
            nameImg=lst[i][3:lst[i].strip().find('=')]+'.image'
            if lst[i].find('=f')>-1:icoPath=icoPath=lst[i][lst[i].strip().find('file=')+5:].rstrip(')') #主要要找是这个
            else:icoPath=lst[i][lst[i].strip().find('file=')+6:].rstrip('")')  #主要要找是这个 
            continue        
        if nameImg and lst[i].find(nameImg)==0:  #button.image语句
            nameImg=0  #完成image,下个循环放行
            continue
        if lst[i].find('.bind')>-1: wgtN=lst[i][:lst[i].find('.bind')].strip()  #bind句中取得控件名   
        elif '(' not in lst[i][:lst[i].find('=')]: #创建、字体句中取得控件名 
            wgtN=lst[i][:lst[i].find('=')].strip()         
            if 'Ft' in wgtN : wgtN=wgtN.replace('Ft','')  #字体句中的控件名
        elif lst[i][lst[i].find('.'):lst[i].find('(')].strip() in lstLM: #在布局语句中取得控件名
            wgtN=lst[i][:lst[i].find('.')].strip()     
        parentN=re.search(r'(?<=\()([a-zA-Z]+\w*)(?=[,\)])',lst[i]) #找父控件
        if not cmm.filePath[index][2].get(wgtN): #创建该控件字典及取得布局方式
            classN=wgtN[:wgtN.find('_')]  #取得控件类名            
            k=1
            while 1: #确定此控件的布局方式
                if lst[i+k][:lst[i+k].find('=')].find(wgtN)>-1:  #是此控件的语句
                    for j in lstLM:  #确定此控件的布局方式lmRoot
                        if lst[i+k].find(j)>-1:
                            lm=j[1:]  #当前布局方式
                            if not lmRoot:lmRoot=lm  #主界面布局方式
                            flag=1
                            break                    
                    if flag: break
                    k+=1
                else:  #此控件的语句已经搜索完毕，没有找到布局方式
                    messagebox.showerror(cmm.t('错误'),cmm.t("{} 没有布局方式").format(wgtN))
                    break
            cmm.filePath[index][2][wgtN]=wp.getBase(classN,lm,1)  #创建该控件字典。加入该控件基础属性,1是清空所有预设值  
        if 'Ft' in lst[i][:lst[i].find('=')]:  #是字体语句 
            cmm.filePath[index][2][wgtN]['font']=[lst[i][lst[i].find('{'):lst[i].find('}')+1],'font'] #字体属性 
            continue    
        if 'bind' in lst[i]:  #是绑定语句
            cmm.filePath[index][2][wgtN]['bind']=[]
            cmm.filePath[index][2][wgtN]['bind'].append(lst[i][lst[i].find('(')+1:lst[i].rfind(')')])
            continue          
        if 'rowconfigure' in lst[i]:#是rowconfigure语句
            if 'rowconfigure' not in cmm.filePath[index][2][wgtN]:cmm.filePath[index][2][wgtN]['rowconfigure']=[]
            cmm.filePath[index][2][wgtN]['rowconfigure'].append(lst[i][lst[i].find('(')+1:lst[i].find(')')])
            continue
        if 'columnconfigure' in lst[i]: #是columnconfigure语句
            if 'columnconfigure' not in cmm.filePath[index][2][wgtN]:cmm.filePath[index][2][wgtN]['columnconfigure']=[]
            cmm.filePath[index][2][wgtN]['columnconfigure'].append(lst[i][lst[i].find('(')+1:lst[i].find(')')])
            continue
        matches=p1.findall(lst[i])  #是创建和布局语句。找出属性值对[('属性'，'值')...]，不包括parent
        for it in matches: #是创建或者布局语句，属性写入filePath
            if it[0]=='font':continue
            if it[0]=='command': cmm.filePath[index][2][wgtN][it[0]]=[f"{it[1].replace(':',':self.')}()",'']
            elif it[0]=='text':  #text属性重新匹配
                mt=pT.findall(lst[i])
                cmm.filePath[index][2][wgtN][it[0]][0]=mt[0][1]
            elif (lm=='pack' or lm=='grid') and lm in lst[i]:  #此句是pack或者grid布局语句
                if cmm.filePath[index][2][wgtN][lm][it[0]][1]=='string':
                    cmm.filePath[index][2][wgtN][lm][it[0]][0]=it[1].replace("'",'').replace('"','')
                else:cmm.filePath[index][2][wgtN][lm][it[0]][0]=it[1]
            elif it[0] in cmm.filePath[index][2][wgtN]: #基础属性中有此属性
                if cmm.filePath[index][2][wgtN][it[0]][1]=='string':  #是string值
                    cmm.filePath[index][2][wgtN][it[0]][0]=it[1].replace("'",'').replace('"','')
                else:cmm.filePath[index][2][wgtN][it[0]][0]=it[1]  #不是string值
            else:  #基础属性以外的属性
                valueP=wp.getOne(classN,it[0],lm)
                if valueP:  #有此属性
                    cmm.filePath[index][2][wgtN][it[0]]=valueP
                    if it[0]=='image':
                        cmm.filePath[index][2][wgtN][it[0]][0]=icoPath
                    elif valueP[1]=='string':  #是string值 
                        cmm.filePath[index][2][wgtN][it[0]][0]=it[1].replace("'",'').replace('"','')
                    else:cmm.filePath[index][2][wgtN][it[0]][0]=it[1]  #不是string值
                else: messagebox.showerror(cmm.t('错误'),cmm.t("控件 {} 没有 {} 属性").format(wgtN,it[0]))  #无此属性        
        if parentN and parentN.group()!='root':  #修改父控件
            cmm.filePath[index][2][wgtN]['parent'][0]=parentN.group()     
    for i in range(ei,len(lst)):  #cvsGUI界面长宽值        
        if 'winW=' in lst[i]: cmm.filePath[index][2]['cvsGUI']['width'][0]=lst[i][lst[i].find('=')+1:].strip()
        elif 'winH=' in lst[i]:cmm.filePath[index][2]['cvsGUI']['height'][0]=lst[i][lst[i].find('=')+1:].strip()
    if lmRoot=='grid':cmm.filePath[index][2]['cvsGUI'].update({'rowconfigure':[],'columnconfigure':[]})
    for i in range(len(lst)): #rowconfigure,columnconfigure
        if 'root.rowconfigure'in lst[i] :
            rc=lst[i][lst[i].find('(')+1:lst[i].find(')')]
            cmm.filePath[index][2]['cvsGUI']['rowconfigure'].append(rc)
        if 'root.columnconfigure'in lst[i]:
            rc=lst[i][lst[i].find('(')+1:lst[i].find(')')]
            cmm.filePath[index][2]['cvsGUI']['columnconfigure'].append(rc)

