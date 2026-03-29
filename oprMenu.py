import tkinter as tk
from tkinter import ttk
import os
import cmm 
from tkinter import messagebox


class makeMenu:  #创建菜单   
    def __init__(self): 
        self.top =tk.Toplevel()        #创建一个顶级窗口
        self.top.title(cmm.t('创建菜单'))        #窗口命名
        self.top.transient(cmm.root)        #依附于主窗口
        self.top.geometry('1000x380+700+200') #宽x高+x坐标+y坐标
        self.top.resizable(False, False) #去掉了最大最小化的按钮
        self.top.grab_set()   # 获取模态焦点，阻止用户操作主窗口
        self.top.protocol("WM_DELETE_WINDOW",lambda: [self.top.grab_release(), self.top.destroy()])  #关闭窗口
        canvas=tk.Canvas(self.top,width=982,height=297,scrollregion=(0,0,1800,800)) #创建canvas，背景
        canvas.place(x = 0, y =0) #放置canvas的位置
        frm= tk.Frame(canvas,width=1800,height=800,bg = "#888888",relief = "flat")
        frm.pack()
        scbY= tk.Scrollbar(self.top,command=canvas.yview, orient="vertical")  #Y滚动条
        scbY.place(x=985,y=0,width=15,height=300)
        scbX= tk.Scrollbar(self.top,command=canvas.xview,orient="horizontal",)  #x滚动条
        scbX.place(x=0,y=300,width=986,height=15)
        canvas.config(yscrollcommand=scbY.set,xscrollcommand=scbX.set) 
        canvas.create_window(0,0,window=frm,anchor='nw')  #
        dctTree={}              
        btn=tk.Button(self.top,text=cmm.t('保存'),command=lambda:self.save(dctTree))        
        btn.place(x=100,y=320,width=80,height=25)         
        menubar=self.setTree(frm,dctTree)  #由menuBar代码创建菜单树，从文件中取出菜单代码放入menuText
        self.iid=''
        self.etrCbb=''
        self.content=''  #def menu(root)中的代码
        self.menuText=''  #菜单代码
        self.top.protocol('WM_DELETE_WINDOW', self.exit)    
    def addNode(self,treeview, lstMenu,dctP):  #menu文本代码转化为树视图
        for c in lstMenu:            
            if 'tk.Menu' in c:  #是否为菜单对象
                mO=c[c.find('(')+1:c.find(',')].strip()  #基于的节点对象  
                mN=c[:c.find('=')].strip() #创建的节点对象
                if mO=='menubar':dctP[mN]=''  #根节点
                else: dctP[mN]=dctP[mO]  #其他父节点
            elif  'cascade' in c:  # 是否为级联菜单
                label =c[c.find("'")+1:c.find(',')-1]  #显示的菜单文本
                mO=c[c.find('menu=')+5:].replace(')','')  #基于的节点对象            
                iid = treeview.insert(dctP[mO], 'end', text=label, open=True)  #树增加1个父节点
                dctP[label]=iid
            elif  'command' in c:     
                label =c[c.find("'")+1:c.find(',')-1]   
                mO=c[:c.find('.')].strip()  #基于的节点对象     
                treeview.insert(dctP[mO], 'end', text=label, open=1)
            elif 'add_separator' in c:
                mO=c[:c.find('.')].strip()  #基于的节点对象     
                treeview.insert(dctP[mO], 'end', text='----------')
    def makeTree(self,frm,dctTree,sn):  #创建菜单树
        trNum=int(sn)
        tree = ttk.Treeview(frm, show='tree',name=sn)  #在frm创建菜单树 
        tree.place(x=trNum*150+1*trNum,y=0,width=150,height=800)
        tree.bind('<Button-3>', lambda e:self.mRight(e,dctTree,frm)) # 打开右键菜单
        tree.bind("<Double-1>",lambda e:self.one(e,dctTree,frm))  #双击树节点响应函数
        idRoot=tree.insert("", "end",text=cmm.t('双击输入'),open=True)  # 插入根节点,返回值是根节点id字符串
        dctTree[sn]=[tree,idRoot]
    def setTree(self,frm,dctTree):  #读取menuBar.py并显示菜单树
        index=cmm.rNB.index("current")        
        filePath=os.path.dirname(cmm.filePath[index][0])+'/menuBar.py'
        if os.path.isfile(filePath):  #检查是否存在menuBar.py
            with open(filePath,'r',encoding="utf-8") as f:
                self.menuText=f.read()
        else: #不存在此文件
            self.makeTree(frm,dctTree,'0')  #创建第1列空菜单树 
            return 
        if not self.menuText:  #menuBar.py中没有内容
            self.makeTree(frm,dctTree,'0')  #创建第1列空菜单树 
            return
        lst=self.menuText.split('\n')
        for i in range(len(lst)-1,-1,-1):  #删除其中的空格行
            if not lst[i].strip():del lst[i]   
        self.menuText='\n'.join(lst)
        for i in range(len(lst)-1,-1,-1):  #root.config以下的行全部删除
            if "root.config" in lst[i]:break 
            else:del lst[i]
        si=0  # 开始删除位置
        for i in range(len(lst)-1,-1,-1):  #从tk.Menu上一行开始往上删除行
            if 'menubar=tk.Menu' in lst[i]: si=i
            if i<=si: del lst[i]
        dctP={}
        lstMenu=[]
        lc=[lst[0]]
        del lst[0]
        for l in lst:
            if 'tk.Menu(menubar' not in l: #普通节点
                lc.append(l)
            else:
                lstMenu.append(lc.copy())
                lc.clear()
                lc.append(l)
        lstMenu.append(lc)
        for j in range(len(lstMenu)): #显示菜单树
            self.makeTree(frm,dctTree,str(j)) 
            dctTree[str(j)][0].delete(dctTree[str(j)][1])
            self.addNode(dctTree[str(j)][0],lstMenu[j],dctP)
            dctTree[str(j)][1]=dctTree[str(j)][0].get_children()[0]
        self.makeTree(frm,dctTree,str(j+1)) #右边添加一空树    
    def mRight(self,event,dctTree,frm):  #右键菜单        
        self.etrFocusOut()  # 删除entry框  #前面输入的没有按下回车，输入无效
        trN=event.widget.winfo_name()  #treeview的name
        iid =dctTree[trN][0].identify_row(event.y)
        if iid:
            dctTree[trN][0].selection_set(iid)     # 设置选中
            menuR =tk.Menu(tearoff=False)            
            menuR.add_command(label=cmm.t('添加子菜单项'), command=lambda:self.addItem(trN,dctTree,iid,'+',frm,event))             
            menuR.add_command(label=cmm.t('添加菜单项'), command=lambda :self.addItem(trN,dctTree,iid,cmm.t('插入菜单项'),frm,event))
            menuR.add_separator()
            menuR.add_command(label=cmm.t('上移'), command=lambda:self.addItem(trN,dctTree,iid,cmm.t('上移'),frm,event)) 
            menuR.add_command(label=cmm.t('加分隔线'), command=lambda :self.addItem(trN,dctTree,iid,'----------',frm,event))             
            menuR.add_command(label=cmm.t('删除'), command=lambda:dctTree[trN][0].delete(iid)) 
            menuR.post(event.x_root, event.y_root)     # 光标位置显示菜单
    def addItem(self,trN,dctTree,iid,item,frm,e):  #右键菜单插入操作
        pos=dctTree[trN][0].index(iid)  #通过iid得到位置index
        parent=dctTree[trN][0].parent(iid)   #此节点的父节点
        if not parent : parent=dctTree[trN][1]  #此节点是根节点  
        if item==cmm.t('插入菜单项'):   #插入菜单项                                
            self.iid=dctTree[trN][0].insert(parent,pos,text=cmm.t('双击输入'),open=True) #插入菜单项        
        elif item=='+':  #添加子菜单项
            if '----------' in dctTree[trN][0].item(iid)['text']: return #分隔号不能加子项
            self.iid=dctTree[trN][0].insert(iid,'end',text=cmm.t('双击输入'),open=True)  #插入数据            
            parent=iid          
        elif item==cmm.t('上移'):  #上移菜单项
            content=dctTree[trN][0].item(iid)['text']
            dctTree[trN][0].delete(iid)
            self.iid=dctTree[trN][0].insert(parent,pos-1,text=content,open=True)  #插入数据 
            return
        else: #加分隔线
            dctTree[trN][0].insert(parent,pos,text=item,open=True)     
            return    
        box=dctTree[trN][0].bbox(self.iid)  #取得本框box信息。 x, y, width, height 
        box=list(box)
        box[2]=115  #宽度
        if item=='+': box[0]=e.widget.winfo_x()+40  #x坐标
        else: box[0]=e.widget.winfo_x()+20  #x坐标      
        self.setEtrCbb(dctTree,trN,frm,parent,box,'')  #显示输入框
    def etrFocusOut(self):  # entry框失去焦点，放弃更改   
        if self.etrCbb:# 如果属性表中的entry框可见
            self.etrCbb.destroy()  # 删除entry框
    def one(self,e,dctTree,frm):  #双击了菜单项
        trN=e.widget.winfo_name()  #treeview的name
        self.etrFocusOut()  # 删除entry框  #前面输入的没有按下回车，输入无效
        self.iid = dctTree[trN][0].identify_row(e.y)         # 点击的iid,相当于行号。treeview.focus()
        if not self.iid: return        
        box=dctTree[trN][0].bbox(self.iid,column='#0')  #取得本框box信息。 x, y, width, height 
        box=list(box) 
        box[0]=e.widget.winfo_x()+20
        #box[2]=115        
        parent=dctTree[trN][0].parent(self.iid)   #父节点           
        if not parent : parent=dctTree[trN][1]  #自己是根节点 
        selV=dctTree[trN][0].item(self.iid)["text"]
        self.setEtrCbb(dctTree,trN,frm,parent,box,selV)  #显示输入框         
        if selV!=cmm.t('双击输入'): self.etrCbb.insert(0, selV)  # etrCbb框插入原内容
    def etrReturn(self,dctTree,trN,frm,parent,box,selV):  #确定输入        
        cm = self.etrCbb.get().strip()  # 获取entry框内容        
        self.etrFocusOut()  #销毁entry框
        if not cm:  return
        if cm[0].isnumeric():
            messagebox.showerror(cmm.t('错误'),cmm.t("变量开头不能是数字"),parent=self.top)
            return
        dctTree[trN][0].item(self.iid,text=cm,open=1)  #更改当前节点值。如果是根或者父节点，要打开
        self.addDef(trN,cm,dctTree,selV)#在代码中添加菜单项函数定义语句
        box[1]=box[1]+20  #y坐标        
        self.iid=dctTree[trN][0].next(self.iid)
        if self.iid:  #有下一个节点            
            selV=dctTree[trN][0].item(self.iid)["text"] 
            self.setEtrCbb(dctTree,trN,frm,parent,box,selV)   #显示输入框
            if selV!=cmm.t('双击输入'):  self.etrCbb.insert(0, selV)
        else:  #新建一个节点
            self.iid=dctTree[trN][0].insert(parent, "end",text=cmm.t('双击输入'),open=True)
            self.setEtrCbb(dctTree,trN,frm,parent,box,'')   #显示输入框
            self.etrCbb.insert(0, '')
        trNum=int(trN)+1
        if len(dctTree)==trNum:  #添加根节点
            self.makeTree(frm,dctTree,str(trNum))
    def setEtrCbb(self,dctTree,trN,frm,parent,box,selV):   #显示输入框    
        self.etrCbb=tk.Entry(frm, highlightthickness=1, bg='#F3F3F4') 
        self.etrCbb.place(x=box[0], y=box[1], width=box[2], height=box[3])  # 设置self.etrCbb框位置及长宽 
        self.etrCbb.focus_set()  # etrCbb框获取焦点 
        self.etrCbb.bind("<Return>",lambda e:self.etrReturn(dctTree,trN,frm,parent,box,selV))   #table中的etrCbb框对回车的响应
        self.etrCbb.bind("<FocusOut>",lambda e:self.etrFocusOut())
    def addDef(self,trN,cm,dctTree,selV): #添加函数定义语句/修改函数名
        if dctTree[trN][0].parent(self.iid) == "":return #是根节点，退出
        if len(dctTree[trN][0].get_children(self.iid)) > 0:return #是父节点，退出    
        if not self.menuText : self.getText(dctTree)  #无文件内容#取得完整的menuText             
        lst=self.menuText.split('\n')  #有文件内容       
        si,haveS=0,0  #添加开始位置，存在旧的函数名
        for i in range(len(lst)):  #找root.config
            if "root.config" in lst[i]: si=i+1
            if f'def {selV}():' in lst[i]:  #存在旧的定义函数
                haveS=1  
                pos=i
        if haveS:lst[i]=f'def {cm}():'  #修改函数名
        else:  #添加函数定义语句
            lst.insert(si,f'def {cm}():\n    pass' )
        self.menuText='\n'.join(lst) 
    def trvTree(self,tree,idP):  #遍历菜单树，不包括根         
        for iid in tree.get_children(idP):   
            nodeN=tree.item(iid)['text']  #节点文本 
            if nodeN==cmm.t('双击输入'): continue  #根节点是“双击输入”，略过 
            pn=tree.item(idP)['text']  #父节点文本 
            if tree.get_children(iid):   #此节点是父节点                  
                self.content+=f"    {nodeN}=tk.Menu({pn},tearoff = 0)\n"  #创建节点菜单对象
                self.content+=f"    {pn}.add_cascade(label='{nodeN}', menu={nodeN})\n"  #菜单栏加入下拉菜单   
            elif nodeN=='----------':  self.content+=f"    {pn}.add_separator()\n"  #分隔线
            else : self.content+=f"    {pn}.add_command(label='{nodeN}',command=lambda:{nodeN}())\n"   #普通节点    
            self.trvTree(tree,iid)# 递归遍历子节点  
    def getCmd(self,dctTree):  #菜单树转化成菜单项代码        
        rootN=dctTree['0'][0].item(dctTree['0'][1])['text']  #0号树的根节点名
        if rootN==cmm.t('双击输入'): return 0 #0号树没有输入菜单，退出        
        self.content=''
        self.content+=f"    menubar=tk.Menu(root)\n"               
        for k,v in dctTree.items():   #生成菜单代码放入self.content 
            rootN=dctTree[k][0].item(dctTree[k][1])['text']  #树的根节点名
            if rootN==cmm.t('双击输入'): break #此树没有输入菜单，退出
            self.content+=f"    {rootN}=tk.Menu(menubar,tearoff = 0)\n" 
            self.content+=f"    menubar.add_cascade(label='{rootN}', menu={rootN})\n"  #菜单栏加入下拉菜单
            self.trvTree(v[0],v[1])     
        self.content=self.content+"    root.config(menu = menubar)\n"
        return 1
    def wrPy(self,filePath):  #写入menuBar.py文件
        with open(filePath, 'w', encoding='utf-8') as f:  #保存menuBar.py文件
            f.write('')  #清空文档
            f.write(self.menuText)
    def getText(self,dctTree,getC=1):  #取得完整的menuText
        if not self.getCmd(dctTree) :return  #菜单树转化成菜单项代码。空菜单树则退出 
        if not self.menuText:  #menuBar.py里没有代码
            self.content="import tkinter as tk\nfrom tkinter import ttk \n\ndef menu(root):  #Only command is modifiable; nothing else.\n"+self.content 
        body=self.menuText[:self.menuText.find('    menubar=tk.Menu')]+self.content
        foot=self.menuText[self.menuText.find('root.config'):]
        foot=foot[foot.find('def'):]
        self.menuText=body+foot
    def save(self,dctTree):  #保存按键        
        self.getText(dctTree)
        index=cmm.rNB.index("current")        
        filePath=os.path.dirname(cmm.filePath[index][0])+'/menuBar.py'        
        self.wrPy(filePath)        
        #--------main文件中加入menu-----------------------
        flag=0  #在cmm.filePath中加入了menuBar代码
        lst=cmm.filePath[index][1].split('\n') 
        for i in range(len(lst)):#lst中加入 import menuBar语句
            if 'import menuBar' in lst[i]:break
            if 'import' not in lst[i]:
                flag=1
                lst.insert(i,'import menuBar')
                break
        for i in range(len(lst)):    #lst中加入menuBar.menu
            if 'menuBar.menu' in lst[i]: break
            if 'mainloop' in lst[i]: 
                flag=1
                lst.insert(i,'    menuBar.menu(root)')
                break
        #-------------------------------------------------------
        if flag : cmm.filePath[index][1]='\n'.join(lst)        
        for c in cmm.filePath[index][3]['cvsGUI'].winfo_children():#查询cvsGUI有否按钮，有的话不要创建了
            if 'button' in str(c):break
        else:
            btn=tk.Button(cmm.filePath[index][3]['cvsGUI'],text='menuBar',command=lambda:makeMenu(),name='menuBtn')#向cvsGUI加入菜单按钮
            btn.place(x=200,y=0,width=60,height=15)
            btn.bind('<Button-3>',lambda event,index=index:cmm.menuR(event,index)) # 右击控件
        cmm.refTree()  #刷新菜单树#menuRight模块中的refTree函数
    def exit(self):
        self.top.grab_release()
        self.top.destroy()
    
    
