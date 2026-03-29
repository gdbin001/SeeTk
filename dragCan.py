from tkinter import Canvas, ttk
import tkinter as tk
import selectedCanvas as sc
from tkinter import messagebox
import cmm 

class dragCanvas(tk.Frame):  #基础frame。在其中创建滚动条和基础canvas。然后在基础canvas上创建frm,再在frm上创建接近大小的界面canvas
    #tkinter 内建了拖曳功能：使用 scan_mark(x0, y0) 记住当前坐标 (x_0, y_0)，接着使用 scan_dragto(x1, y1, gain=10) 将 view of the canvas 拖曳到 (x_0 + gain*(x_1-x0), y_0+gain*(y_1-y_0) 位置。
    lstName=[]  #[控件1名称，控件2名称...]。类属性
    def __init__(self,idx,**kw):
        super().__init__(cmm.rNB, **kw)  #基础frame。使用super()方法来调用父类的__init__()方法，从而实现属性的初始化
        #self.canvas = Canvas(self, width=600, height=400,scrollregion=(0,0,600,400))
        self.pack(fill='both',expand=1)        
        self.startX=0
        self.startY=0
        self.idx=idx
        self.lstCopy=[]  #复制对象列表
        self.sltCvsGUI=0  #是否选中cvsGUI
        self.rect=''  # 用于存储虚线框的矩形       
        self.cvsBase=tk.Canvas(self,bg='grey',name='cvsBase')  #基础canvas,绿豆色#cce8cf
        self.cvsBase.grid(row=0, column=0, sticky="nesw")
        self.frm=tk.Frame(self.cvsBase,bd=0)   #在cvsBase创建frm控件，frm  
        self.frm.pack(fill='both',expand=1)
        self.cvsGUI=sc.SelectedCanvas(self.frm,'cvsGUI',relief='raised',bg='grey',name='cvsGUI',bd=0)#主界面canvas
        self.cvsGUI.place(x=2,y=2,width=930,height=670) #先按此参数创建，后在prmToRC()中再调整后显示 
        self.scbX = ttk.Scrollbar(self, orient="horizontal", command=self.cvsBase.xview,name='scbX')
        self.scbY = ttk.Scrollbar(self, orient="vertical", command=self.cvsBase.yview,name='scbY')
        self.scbY.grid(row=0, column=1, sticky="ns")
        self.scbX.grid(row=1, column=0, sticky="ew")         
        cmm.scbX=self.scbX
        cmm.scbY=self.scbY 
        self.cvsBase.configure(yscrollcommand=self.scbY.set, xscrollcommand=self.scbX.set)
        self.cvsBase.create_window((0,0),window=self.frm,anchor='nw')
        self.rowconfigure(0, weight=1)    #第0行，按1缩放
        self.columnconfigure(0, weight=1)  #第0列，按1缩放
        self.cvsBase.bind("<Button-1>",self.onMC)  #点击了基础canvas              
        self.cvsGUI.bind("<Button-1>",self.canvasMD)  #点击了界面canvas
        self.cvsGUI.bind('<Configure>',self.showSb)   #界面canvas尺寸变化时 
        self.cvsGUI.bind('<B1-Motion>',self.onDrag)  #拖动鼠标左键。框选控件
        self.cvsGUI.bind('<Button-3>', lambda event:self.mRight(event)) # 右击cvsGUI
        self.cvsGUI.bind('<ButtonRelease-1>',self.onRelease)  #鼠标弹起。框选控件
        self.cvsGUI.bind("<FocusOut>", self.onFocusOut)  #cvsGUI失去焦点
        self.cvsGUI.bind_all('<Control-v>',self.onPaste)  #粘贴控件        
        self.cvsGUI.bind_all('<Control-c>',self.onCopy)  #复制控件 
        self.cvsGUI.bind_all('<Control-x>',self.onCut)  #剪切控件               
        self.cvsGUI.bind_all("<Control_L>", self.onCtrlDown)  # 左Ctrl 键按下
        self.cvsGUI.bind_all("<Control_R>", self.onCtrlDown)  # 右Ctrl 键按下
        self.cvsGUI.bind_all("<KeyRelease>", self.onCtrlUp)  #Ctrl键弹起        
        self.bindWheel()  #绑定鼠标滚轮
    def mRight(self,event):  #界面空白处右键菜单
        self.canvasMD(0)
        lst=("Button","Canvas","Checkbutton","Combobox","Entry","Frame","Label","LabelFrame","Listbox","Menu",'Notebook'
        ,"PanedWindow",'Progressbar','Radiobutton','Scale','Scrollbar','Separator','Spinbox','Text','Treeview')
        menuP =tk.Menu(cmm.root,tearoff=False)  #父菜单
        menuR =tk.Menu(menuP,tearoff=False)  ##子菜单 
        menuP.add_cascade(label=cmm.t("添加控件"),menu=menuR)  #父菜单项添加级联菜单
        for i in range(len(lst)):
            menuR.add_command(label=lst[i], command=lambda x=event.x,y=event.y,a=lst[i]:cmm.creatW(0,a,x,y))   #在主界面创建控件 
        if self.lstCopy or dragCanvas.lstName:menuP.add_command(label=cmm.t('粘贴'), command=lambda e=event:self.onPaste(e))   #粘贴本控件
        menuP.post(event.x_root, event.y_root)     # 光标位置显示菜单
    def onFocusOut(self,e):  #
        tplIt=cmm.treeD.selection()  #当前选中iid元组
        if tplIt and cmm.treeD.item(tplIt[0])["text"]=='root': return 0
        self.sltCvsGUI=0
        self.cvsGUI.delete('all')  #删除手柄
    def bindWheel(self): #绑定鼠标滚轮
        self.cvsBase.bind('<MouseWheel>',self.wheel)   #鼠标滚轮控制视图  
        self.cvsGUI.bind('<MouseWheel>',self.wheel)   #鼠标滚轮控制视图 
    def wheel(self,event):  #鼠标滚轮滚动的视图
        if self.scbY.get()==(0.0,1.0):return 'break'  #当滚动条是灰色时，不响应鼠标滚轮
        self.cvsBase.yview_scroll(int(-event.delta/120), "units")  #windows系统需要除以120
        return 'break'  # 阻止事件传播
    def onCopy(self,event): #复制控件Ctrl+c
        if 'text' in cmm.rNB.select() : return  #当前是文本模式，退出 
        if not cmm.lstSW: return  #没有选控件，退出
        self.lstCopy.clear()
        self.lstCopy.extend(cmm.lstSW)
    def onPaste(self,event): #粘贴控件Ctrl+v。现在的cmm.lstSW是粘贴目标 
        if 'text' in cmm.rNB.select() : return  #当前是文本模式，退出  
        index=cmm.rNB.index("current")  #因为bind_all,所以必须要重新取得这个index
        for v in cmm.filePath[index][3].values():#可否粘贴
            if v is cmm.root.focus_get(): break #获得焦点的对象是界面中的控件，可以粘贴
        else: return #不是界面中的控件，退出 
        if (not cmm.lstSW and not self.sltCvsGUI)or len(cmm.lstSW)>1 or (not dragCanvas.lstName and cmm.lstSW==self.lstCopy): #没有选中粘贴对象或者粘贴对象过多，退出
            messagebox.showerror(cmm.t('错误'),cmm.t('请选择一个粘贴目标'))
            return 0
        lst,haveC=[],0         
        if dragCanvas.lstName:  #-------是剪切的粘贴------                       
            for it in dragCanvas.lstName:  #剪切的控件做成拖动的控件列表lst
                lst.append(cmm.filePath[index][3][it[0]].master) #最后1个it给下面用
                if cmm.filePath[index][3][it[0]].winfo_children():haveC=1#剪切的控件中有子控件                    
            if self.sltCvsGUI:  #粘贴到主界面
                cmm.filePath[index][3][it[0]].master.cutWgt(lst,1,0,event.x,event.y) #粘贴到主界面 
                self.sltCvsGUI=0               
            else:  #粘贴到控件中
                aa=cmm.filePath[index][3][it[0]].master.cutWgt(lst,0,cmm.filePath[index][3][cmm.lstSW[0].wgtName],2,2) #粘贴到控件中
                if not aa:  #不剪切,退出
                    for it in dragCanvas.lstName:#还原bg等属性
                        if len(it)==2: cmm.filePath[index][3][it[0]]['bg']=it[1] #还原bg属性
                        else: cmm.filePath[index][3][it[0]].master['bg']=it[2] #还原bg属性
                if haveC:cmm.lstSW=[cmm.filePath[index][3][cmm.lstSW[0].wgtName].master]  #有子控件，重新显示了，所以要重设cmm.lstSW
                cmm.clearSW() #cmm.lstSW要清空，否则无法选中粘贴的控件           
            lst.clear() #做成lstName 
            for it in dragCanvas.lstName: lst.append(it[0])   #做成lstName               
            cmm.filePath[index][3][it[0]].master.tail(lst,self.idx)  #收尾工作
            dragCanvas.lstName.clear()  #剪切必须要清空，原控件只能剪切1次
            return 0
        if cmm.lstSW:  #-------是复制的粘贴------
            for it in self.lstCopy:
                if not cmm.canParent(cmm.lstSW[0].wgtName,index): return 0  #不能做父控件，退出
                cmm.adjPos(it.wgtName,cmm.lstSW[0],self.idx) #调整位置        
        if not self.lstCopy : return  #剪贴板是空的，退出
        copyPN=cmm.filePath[index][2][self.lstCopy[0].wgtName]['parent'][0] #复制对象的父控件名        
        lstPCP=[]  #元素是[复制对象，新父控件名,用回原布局,x,y]  #1用原布局，0用新布局。x、y控件间的距离(place布局才用) 
        if copyPN=='root' and self.sltCvsGUI: #粘贴到复制对象的父控件中，保留原布局
            for it in self.lstCopy: lstPCP.append((it,copyPN,1)) #1用复制对象的布局
        elif cmm.lstSW and copyPN==cmm.lstSW[0].wgtName:  #粘贴到复制对象的父控件中
            for it in self.lstCopy: lstPCP.append((it,copyPN,0)) 
        elif copyPN!='root' and self.sltCvsGUI:  #粘贴到不同的父控件，父控件是root,不保留复制对象的布局
            for it in self.lstCopy: lstPCP.append((it,'root',0))  #0用新布局  
        elif copyPN!=cmm.lstSW[0].wgtName :  #粘贴到不同的父控件，父控件是lstSW[0],不保留复制对象的布局
            for it in self.lstCopy: lstPCP.append((it,cmm.lstSW[0].wgtName,0))  #0用新布局    
        wPN=lstPCP[0][1]  #粘贴目标的控件名
        lstWgt=[]  #创建的控件
        i=0
        while lstPCP:  #粘贴控件及其中的子控件
            c=lstPCP.pop(0)
            cmm.maxSN+=1
            newN=f"{c[0].wgtName.split('_')[0]}_{cmm.maxSN}"  #新控件名
            if c[1]=='root' : #在主界面中粘贴控件。不用判断布局，x、y值在pack和grid中无效                
                if i<len(self.lstCopy):
                    if event:aa=cmm.reCreatW(c[0].wgtName,self.cvsGUI,'root',index,newN,c[2],event.x+10*i,event.y+10*i)
                    else: aa=cmm.reCreatW(c[0].wgtName,self.cvsGUI,'root',index,newN,c[2],10*i+5,10*i+5)               
                else:aa=cmm.reCreatW(c[0].wgtName,self.cvsGUI,'root',index,newN,c[2]) #粘贴控件中的子控件
            else: #在控件中粘贴控件
                if i<len(self.lstCopy):aa=cmm.reCreatW(c[0].wgtName,cmm.filePath[index][3][c[1]],c[1],index,newN,c[2],i*10+5,i*10+5) 
                else:aa=cmm.reCreatW(c[0].wgtName,cmm.filePath[index][3][c[1]],c[1],index,newN,c[2])  #粘贴控件中的子控件
            if not aa:
                cmm.maxSN-=1
                return 0
            lstWgt.append(aa)
            for k,v in cmm.filePath[index][2].items(): #记录其中的子控件。k是控件名，v是控件属性
                if k=='cvsGUI':continue
                if v['parent'][0]==c[0].wgtName: 
                    cmm.guiL=next((x for x in ('pack','grid') if x in v),'place')
                    lstPCP.append((cmm.filePath[index][3][k].master,newN,cmm.guiL))
            i+=1 
        cmm.ctrlPrs=0        
        lstWgt[0].widget.focus_set() 
        for i in range(len(self.lstCopy)):
            lstWgt[i].update()
            lstWgt[i].mousedown(0) #选中最后一个新控件，并显示属性表
        cmm.filePath[self.idx][4]=1  #编辑标志设为已经编辑
        cmm.showSG()   
    def onCut(self,event):#剪切控件Ctrl+X。
        if 'text' in cmm.rNB.select(): return  #当前是文本模式，退出 
        if not cmm.lstSW:
            messagebox.showerror(cmm.t('错误'),cmm.t('请选择剪切对象'))
            return 0
        for it in cmm.lstSW: #保存剪切的控件名及纯控件或者canvas的背景色
            itc=it.widget.config()
            if 'bg' in itc:
                dragCanvas.lstName.append((it.wgtName,it.widget.cget('bg'))) #保存剪切的控件名及背景色
                it.widget['bg']='slategrey'  #当前bg设置为石板灰色
            else: 
                dragCanvas.lstName.append((it.wgtName,0,it.cget('bg'))) #保存剪切的控件名及canvas的背景色
                it['bg']='slategrey'  #当前bg设置为石板灰色
    def onCtrlDown(self, event):  #按下Ctrl键
        if 'text' in cmm.rNB.select(): return  #当前是文本模式，退出 
        cmm.ctrlPrs=1   
    def onCtrlUp(self, event):  #ctrl或者v键弹起
        #if event.keysym == 'v' or event.keysym == 'V':  #v键弹起
         #   if cmm.ctrlPrs:cmm.ctrlPrs=1
        if event.keysym == 'Control_L' or event.keysym == 'Control_R':  #ctrl键弹起
            cmm.ctrlPrs=0
    def canvasMD(self,event):  #点击了主界面canvas 
        self.cvsGUI.focus_set()
        if cmm.ctrlPrs:return 
        self.sltCvsGUI=1  #选中了cvsGUI
        if event:
            self.startX=event.x
            self.startY=event.y        
        cmm.setGL(self.idx,'root',0)  #设置guiL
        cmm.lblStt['text']=cmm.t('在父控件中的布局方式：')+cmm.guiL  #状态栏显示布局方式
        for i in range(1,len(cmm.btnBar)):
            if cmm.guiL=='place':  cmm.btnBar[i]['state']='normal' #快捷键使能 
            else: cmm.btnBar[i]['state']='disabled' #快捷键禁用
        cmm.clearSW()  #清空选择的控件列表及状态
        self.cvsGUI.drawHandle()  #画手柄。这里不能用self.cvsGUI.sltSts()
        self.cvsGUI.showHandle()   #放置手柄
        self.cvsGUI.showProp() 
        #self.clearWR()
    #def clearWR(self):  #清空关系树
     #   if cmm.lstIEBOld:cmm.treeD.item(cmm.lstIEBOld, tags=()) #清除上次选中行颜色 
      #  if cmm.treeD.selection():cmm.treeD.selection_remove(cmm.lstIEBOld)  #清除上次点击选中
       #  tplIt=cmm.treeD.selection()  #当前选中iid元组
       # if tplIt: cmm.lstIEBOld=tplIt[0]
    def onDrag(self,event):#在主界面canvas，拖动鼠标左键，绘制红色虚线框。此函数后响应，on_mouse_move先响应
        if cmm.guiL!='place':    return   #不是place布局，退出 
        #if not self.startX:return   
        if self.cvsGUI.is_sizing: return #界面canvas正在调整大小，退出
        if self.rect:  # 如果已经有一个虚线框，则删除它
            self.cvsGUI.delete(self.rect)
            self.rect=''        
        x1, y1 = min(self.startX, event.x), min(self.startY, event.y)
        x2, y2 = max(self.startX, event.x), max(self.startY, event.y)         
        self.rect = self.cvsGUI.create_rectangle(x1, y1, x2, y2, outline='red', dash=(4,4))# 绘制红色虚线框
    def onRelease(self,event):  #在主界面canvas，鼠标左键弹起，框选控件   
        if cmm.guiL!='place':return   #不是place布局，退出
        if not self.startX:return        
        for k,v in cmm.filePath[self.idx][2].items():
            if k=='cvsGUI':continue    
            if v.get('pack') or v.get('grid'):continue  #pack和grid布局的跳过 
            x1, y1 = min(self.startX, event.x), min(self.startY, event.y)  #虚线框左上角
            x2, y2 = max(self.startX, event.x), max(self.startY, event.y)  #虚线框右下角
            wx1,wy1=int(v['x'][0]),int(v['y'][0])  #控件左上角
            wx2,wy2=wx1+int(v['width'][0]),wy1+int(v['height'][0])  #控件右下角
            corners=[(wx1,wy1),(wx2,wy1),(wx1,wy2),(wx2,wy2)] #控件4个角的坐标
            for c in corners:  #c是控件4个角中的1个角的坐标
                cx,cy=c
                if x1<=cx<=x2 and y1<=cy<=y2:  #在虚线框中
                    self.showAdj(k)  #显示选中状态
                    break     
        self.cvsGUI.delete(self.rect)  #删除虚线框
        self.rect=''                
        self.startX,self.startY=0,0
        if len(cmm.lstSW)>1:#控件是2个及以上，清空属性表         
            self.cvsGUI.delete('all')  #删除cvsGUI中的手柄
            cmm.table.delete(*cmm.table.get_children())#清空表
        elif cmm.lstSW :  #只有一个控件且不是界面
            self.cvsGUI.delete('all')  #删除cvsGUI中的手柄
            cmm.lstSW[0].showProp()
    def showAdj(self,k):  #显示框选中状态并记录
        for c in self.cvsGUI.winfo_children():  #遍历cvsGUI中的各控件。c是CanvasWgt
            if c.wgtName==k:  #k是控件名
                cmm.lstSW.append(c)
                c.sltSts() #画实心手柄
    def showSb(self,event):  #界面cvsGUI尺寸变化时，frm大小和cvsBase中的scrollregion也相应变化 
        #cmm.root.update()        
        self.frm.configure(width=self.cvsGUI.winfo_width()+4,height=self.cvsGUI.winfo_height()+4)
        self.cvsBase.configure(scrollregion=(0,0,self.cvsGUI.winfo_width()+100,self.cvsGUI.winfo_height()+100))
        #cmm.smartScb(self.idx) #禁用/恢复滚动条
    def onMC(self,event):  #点击了基础canvas
        self.cvsBase.focus_set()
        cmm.guiL=''
        cmm.lblStt['text']=''  #状态栏显示布局方式  
        cmm.clearSW()
        #self.clearWR()
        self.cvsGUI.delete('all')  #删除cvsGUI中的手柄
        cmm.ctrlPrs=0
        cmm.table.delete(*cmm.table.get_children())#清空表