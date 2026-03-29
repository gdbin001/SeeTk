import tkinter as tk
from tkinter import messagebox
import editorPropertyList as epl
from eventRsp import eventFunc
import widgetProperty as wp
import cmm 

lstTtk=("Combobox",'Notebook','Progressbar','Separator','Treeview')  #ttk控件
class SelectedCanvas(tk.Canvas):   #生成控件大小的画布，准备之后在此画布上放置控件。此画布大小就是控件的大小  
    targetWgt=0  #粘贴目标控件Wgt对象。是纯粹控件，没有移动canvas。类属性，不是对象属性
    def __init__(self, master=None,wgtN=None, **kw):
        tk.Canvas.__init__(self, master,**kw)     #移动canvas
        self.master=master   
        self.config(bd=0,highlightthickness = 0)
        #self.create_image(0, 0, image=regCtrl['trpBg'], anchor="nw")
        self.is_sizing = 0
        self.old_width = 0
        self.old_height = 0        
        self.start_x = 0
        self.start_y = 0
        self.start_root_x = 0
        self.start_root_y = 0
        #self.on_resize_complete = None
        self.have_child=False#用以辨别是否有组件创建
        self.wgtName=wgtN  #控件名称
        self.widget=''   #移动canvas上创建的控件对象
        self.idx='' #当前index  
        self.item=0 
        #self.ctrlPrs=''  #按下ctrl键        
#--------------------移动Canvas-------------------------------------------------------------    
    def drawHandle(self,hollow=0):  #在选定的控件外画调整手柄,空心和实心的。hollow=1画空心手柄，并上色
        if hollow:  #画空心手柄
            for name in ('nw', 'w', 'sw', 'n', 's', 'ne', 'e', 'se'):     #画出调整手柄,并绑定事件。还没有放置
                if cmm.guiL=='place': self.create_rectangle(-1, -1, -2, -2, tag=name, outline='red',width=1)  #x1,y1,x2,y2。tag设置标签，可以用于查找。dash设置轮廓线为虚线，(画的像素，跳过多少像素)。outline轮廓颜色
                else: self.create_rectangle(-1, -1, -2, -2, tag=name, outline='black',width=1)
            return
        for name in ('nw', 'w', 'sw', 'n', 's', 'ne', 'e', 'se'):     #画实心手柄,并绑定事件。不可见
            if cmm.guiL=='place': self.create_rectangle(-1, -1, -2, -2, tag=name, fill='red', outline='red')  #x1,y1,x2,y2。tag设置标签，可以用于查找。dash设置轮廓线为虚线，(画的像素，跳过多少像素)。outline轮廓颜色
            else: self.create_rectangle(-1, -1, -2, -2, tag=name, fill='black', outline='black') #
            if self.wgtName=='cvsGUI' or cmm.guiL=='place':   #是cvsGUI或者place布局,有以下绑定函数
                self.tag_bind(name, "<Enter>", lambda e,a=name:self.on_mouse_enter(a,e))  #鼠标移动到手柄上方，显示相应鼠标形状
                self.tag_bind(name, "<Leave>", lambda e:self.config(cursor="arrow"))  #鼠标离开手柄区域,设置为箭头形状
                self.tag_bind(name, "<Button-1>", lambda e:self.on_mouse_click(e))  #鼠标单击手柄
                self.tag_bind(name, "<B1-Motion>", lambda e:self.on_mouse_move(e))  #鼠标按住手柄移动
                self.tag_bind(name, "<ButtonRelease-1>", lambda e:self.on_mouse_release(e))  #鼠标左键松开手柄
    def showHandle(self):  #在选定的控件四周显示调整手柄，6像素正方形   
        self.update()
        if cmm.guiL=='place' or self.wgtName=='cvsGUI':  #place布局  
            width = self.winfo_width()
            height = self.winfo_height() 
        else:  #grid、pack布局 
            width = self.widget.winfo_width()+4
            height = self.widget.winfo_height()+4
        self.coords('s', width/2-3, height-6, width/2 + 3, height)  #移动、调整已有手柄,x1,y1,x2,y2。改变xy值可以改变矩形大小      
        self.coords('se', width-6, height-6, width, height)
        self.coords('e', width-6, height/2-3, width, height/2 + 3)
        if  self.wgtName!='cvsGUI':  #点击界面canvas不显示的手柄
            self.coords('nw', 0, 0, 6, 6)   #调整已有手柄nw,x1,y1,x2,y2           
            self.coords('w', 0,height/2-3, 6, height/2 + 3)
            self.coords('sw', 0, height- 6, 6, height)
            self.coords('n', width/2-3, 0,width/2+3, 6)
            self.coords('ne',width-6, 0,width, 6)
        #self.itemconfig(name, fill='blue')
    def on_mouse_enter(self,tag_name,event):  #当鼠标在相应调整手柄上方时，设置为相应的鼠标形状
        if len(cmm.lstSW)>1:return  #超过1个控件，不显示        
        if tag_name in ("nw", "sw", "ne", "se"):
            self["cursor"] = "sizing"  #同时调整宽高的鼠标形状
        elif tag_name in ("w", "e"):
            self["cursor"] = "sb_h_double_arrow"   #左右双箭头形状
        else:
            self["cursor"] = "sb_v_double_arrow"  #上下双箭头形状
    def on_mouse_click(self, event):     #单击手柄  
        if len(cmm.lstSW)>1:return  #超过1个控件，不记录   
        self.is_sizing = 1
        self.start_x = event.x  #手柄移动初始x坐标
        self.start_y = event.y  #手柄移动初始y坐标
        self.start_root_x = event.x_root
        self.start_root_y = event.y_root
        self.old_width = self.winfo_width()
        self.old_height = self.winfo_height()
    def on_mouse_move(self,event):    #鼠标拖动手柄,调整控件大小。此函数先响应，cvsGUI中的onDrag后响应
        if len(cmm.lstSW)>1:return  #超过1个控件，不能调整
        item_ids=self.find_withtag('current')
        tag_name = self.gettags(item_ids[0])[0]
        self.__startx=event.x  #鼠标相对控件左上角初始x坐标
        self.__starty=event.y  #鼠标相对控件左上角初始y坐标
        if not self.is_sizing:  return   
        table=cmm.table
        if 'e' in tag_name:
                width = max(0, self.old_width + (event.x - self.start_x))
                self.place_configure(width=width)                
                self.hwSet('width',width) #显示宽高值
        if 'w' in tag_name:
                width = max(0, self.old_width + (self.start_root_x - event.x_root))
                to_x = event.x - self.start_x + int(self.place_info()['x'])
                self.place_configure(width=width, x=to_x)
                self.hwSet('width',width) #显示宽高值
                x=self.winfo_x()
                y=self.winfo_y()
                self.after_idle(self.showXY,x,y)  #显示x,y值
        if 's' in tag_name:
                height = max(0, self.old_height + (event.y - self.start_y))
                self.place_configure(height=height)
                self.hwSet('height',height) #显示宽高值
        if 'n' in tag_name:
                height = max(0, self.old_height + (self.start_root_y - event.y_root))
                to_y = event.y - self.start_y + int(self.place_info()['y'])
                self.place_configure(height=height, y=to_y)
                self.hwSet('height',height)  #显示宽高值
                x=self.winfo_x()
                y=self.winfo_y()
                self.after_idle(self.showXY,x,y)  #显示x,y值
        self.after_idle(self.showHandle)  #空闲时执行。显示调整手柄
    def hwSet(self,hw,val):  #显示宽高值
        cmm.filePath[self.idx][2][self.wgtName][hw][0]=str(val)  #写入filePath
        table=cmm.table        
        if not cmm.lstSW:  #选中的是cvsGUI对象
            if hw=='width':table.set(table.get_children(table.get_children()[1])[0],'#2',value=val) #显示宽值
            else:table.set(table.get_children(table.get_children()[1])[1],'#2',value=val)  #显示高值 
        else:  #选中的是其他控件
            if hw=='width':table.set(table.get_children(table.get_children()[1])[2],'#2',value=val) #显示宽值
            else:table.set(table.get_children(table.get_children()[1])[3],'#2',value=val)  #显示高值
    def on_mouse_release(self,event):  #鼠标弹起，不再调整时
        self.is_sizing = 0
        self["cursor"] = "arrow"       
#---------------------------canvas上的Wgt，有些函数属于canvas------------------------------------------------------
    def create_widget(self,widget_class,**kw):  #创建控件        
        if self.have_child==1: return        
        self.have_child=1  #如果已经创建，则忽略
        self.widget=widget_class(self,**kw)  
        self.widget.pack(fill='both',expand=1)
        self.widget.bind("<Button-1>",self.mousedown)  #单击控件,add='+'表示再绑定一个响应函数，会执行两个响应函数
        self.widget.bind("<B1-Motion>",self.dragMotion)   #拖动控件
        self.widget.bind("<ButtonRelease-1>",self.onDragEnd)   #鼠标弹起
        self.widget.bind('<Up>',self.keyUp)  #place布局，上移控件
        self.widget.bind('<Down>',self.keyDown)  #place布局，下移控件
        self.widget.bind('<Left>',self.keyLeft)  #place布局，左移控件
        self.widget.bind('<Right>',self.keyRight)  #place布局，右移控件
        self.widget.bind('<Key>',self.delW)  #删除控件,在同一父控件中的。
        self.widget.bind('<Button-3>',self.mRight) # 右击控件
        self.widget.bind('<Motion>',self.onMM)  #鼠标在控件上方移动
        self.widget.bind('<Double-1>',self.onDB)  #双击控件转去文本位置
        return self.widget
    def mousedown(self,event):  #点击了控件     
        pageON=cmm.rNB.select()  #取得当前页类名路径 
        pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典的key 
        self.idx=cmm.rNB.index('current')  #当前index        
        cmm.guiL=next((x for x in ('pack','grid') if x in cmm.filePath[self.idx][2][self.wgtName]),'place')
        cmm.lblStt['text']=cmm.t('在父控件中的布局方式：')+cmm.guiL  #状态栏显示布局方式   
        self.widget.focus_set()  #粘贴时要用，不能删除
        cmm.rNB.children[pageKey].sltCvsGUI=0  #cvsGUI选中标志清0
        for i in range(1,len(cmm.btnBar)):
            if cmm.guiL=='place':  cmm.btnBar[i]['state']='normal' #快捷键使能 
            else: cmm.btnBar[i]['state']='disabled' #快捷键禁用
        if event:  #是点击的
            self.__startx=event.x  #鼠标相对控件左上角初始x坐标
            self.__starty=event.y  #鼠标相对控件左上角初始y坐标   
            self.start_x=self.winfo_x()
            self.start_y=self.winfo_y()
        if cmm.ctrlPrs: #如果Ctrl键被按下。self.master是cvsGUI,也是SelectedCanvas   
            if  len(cmm.lstSW):   #父控件不同，不能选中  
                firstN=cmm.lstSW[0].wgtName
                if len(cmm.lstSW) and cmm.filePath[self.idx][2][self.wgtName]['parent'][0]!=cmm.filePath[self.idx][2][firstN]['parent'][0]:
                    return  
            if self in cmm.lstSW:#取消再次选择的控件选中状态
                for i,c in enumerate(cmm.lstSW):
                    if c==self:          
                        c.widget.pack(fill='both',expand=1,padx=0,pady=0) #取消选中
                        del cmm.lstSW[i]
                        break
            else:  #设置选中状态
                cmm.lstSW.append(self)       
                self.sltSts()  #设置选中状态，画实心手柄
            if len(cmm.lstSW)>1:  #控件是2个及以上，不显示属性表
                cmm.table.delete(*cmm.table.get_children())#清空表
            else:self.showProp()  #只有1个控件
        else:# 如果没有按下Ctrl键   
            self.sltSts() #画选中状态，画实心手柄 
            if self in cmm.lstSW:return  #要拖动控件移动
            cmm.clearSW()  #清空之前选择的控件及清除手柄
            cmm.lstSW.append(self)                                            
            self.showProp() 
        cmm.filePath[self.idx][3]['cvsGUI'].delete('all')  #删除cvsGUI中的手柄 
        cmm.etrFocusOut()#清除属性表中的entry和buttona及combbox
    def sltSts(self,hollow=0):  #画选中状态。hollow=1画空心手柄
        self.delete('all')  #删除手柄
        if self.wgtName!='cvsGUI':  self.widget.pack(fill='both',expand=1,padx=2,pady=2)  #缩小当前控件，留出位置显示手柄
        self.drawHandle(hollow)  #画手柄（不可见）
        self.showHandle()   #放置手柄（可见）
    def onDB(self,event):  #双击控件转去代码位置
        lstC=['Button','Checkbutton','Radiobutton','Scale','Spinbox']#控件带command属性
        dctV={'Combobox':'ComboboxSelected',"Listbox":'ListboxSelect','Notebook':'NotebookTabChanged','Treeview':'TreeviewSelect'}  #控件默认虚拟事件
        dctN={'Canvas':'Button-1','Entry':'Return',"Frame":'Enter',"Label":'Button-1',"LabelFrame":'Enter'
        ,"PanedWindow":'Configure','Text':'KeyRelease'}  #控件默认普通事件
        for it in lstC:
            if it in self.wgtName:
                cmm.mode_conversion(f'def {self.wgtName}_Click')  #转换到文本模式
                return 0         
        for k,v in dctN.items():  #查找控件
            if k in self.wgtName: 
                self.gotoPos(v)  #普通事件  
                return 0       
        for k,v in dctV.items():  #查找控件
            if k in self.wgtName: 
                self.gotoPos(v,0) #虚拟事件  
                return 0   
    def gotoPos(self,eN,typeN=1):  #双击控件，从图形模式转去文本模式，并找到代码位置
            if cmm.filePath[self.idx][2][self.wgtName].get('bind'): #有bind
                for it in cmm.filePath[self.idx][2][self.wgtName]['bind']: #查找有没有相应的事件
                    if eN in it:  #找到事件
                        if typeN:cmm.mode_conversion(f'def {self.wgtName}_{eN.replace("-","")}')  #转去文本位置
                        else:cmm.mode_conversion(f'def {self.wgtName}_{eN}')  #转去文本位置
                        return 0  #退出 
                else: #没有找到事件，则添加事件
                    if typeN:cmm.filePath[self.idx][2][self.wgtName]['bind'].append(f'"<{eN}>",lambda event:{self.wgtName}_{eN.replace("-","")}(event)') 
                    else: cmm.filePath[self.idx][2][self.wgtName]['bind'].append(f'"<<{eN}>>",lambda event:{self.wgtName}_{eN}(event)')    
            else:  #如果没有bind,则添加bind及事件
                cmm.filePath[self.idx][2][self.wgtName]['bind']=[]
                if typeN:cmm.filePath[self.idx][2][self.wgtName]['bind'].append(f'"<{eN}>",lambda event:{self.wgtName}_{eN.replace("-","")}(event)')
                else: cmm.filePath[self.idx][2][self.wgtName]['bind'].append(f'"<<{eN}>>",lambda event:{self.wgtName}_{eN}(event)')
            if typeN:cmm.addText(self.idx,f'{self.wgtName}_{eN.replace("-","")}(self,event)')  #添加响应函数 
            else:cmm.addText(self.idx,f'{self.wgtName}_{eN}(self,event)')  #添加响应函数 
            if typeN:cmm.mode_conversion(f'def {self.wgtName}_{eN.replace("-","")}')  #转去文本位置
            else:cmm.mode_conversion(f'def {self.wgtName}_{eN}')  #转去文本位置
    def onMM(self,event): #鼠标下面没有tag,显示箭头形状
        if cmm.guiL!='place':return
        #if not cmm.lstSW:return
        if cmm.lstSW and self.wgtName!=cmm.lstSW[0].wgtName:self["cursor"] = "arrow"   #当前控件不是选定的控件,显示箭头形状        
        x, y = event.x, event.y# 获取鼠标位置    
        items = self.find_overlapping(x, y, x, y)# 获取鼠标位置下的所有元素 
        if not self.gettags(items):  #鼠标下面没有tag,显示箭头形状
            self["cursor"] = "arrow"   #显示箭头形状
    def dragMotion(self,event):   #拖动当前选择的控件   
        if cmm.guiL!='place':return  #不是place布局，退出            
        if not cmm.filePath[self.idx][4]:cmm.filePath[self.idx][4]=1  #编辑标志设为已经编辑
        if len(cmm.lstSW)>1:  #选择了多个控件
            for c in cmm.lstSW:
                x=c.winfo_x()+(event.x-self.__startx)  #新x坐标
                y=c.winfo_y()+(event.y-self.__starty)  #新y坐标 
                c.place(x=x,y=y)
                cmm.filePath[self.idx][2][c.wgtName]['x'][0]=str(c.winfo_x())  #写入filePath
                cmm.filePath[self.idx][2][c.wgtName]['y'][0]=str(c.winfo_y())  #写入filePath
        else:  #选择了单个控件
            x=self.winfo_x()+(event.x-self.__startx)  #新x坐标
            y=self.winfo_y()+(event.y-self.__starty)  #新y坐标 
            self.place(x=x,y=y)
            self.after_idle(self.showXY,x,y)  #显示x,y值
        self.checkTarget()  # 判断是否重叠
    def cutWgt(self,lstCut,gui=0,st=0,xg=0,yg=0):  #剪切操作，控件名不变。st是粘贴对象。gui=1放到主界面，xg=0拖动控件，有值是剪切     
        flag,isDrag=0,0  #拖动的控件中有否子控件
        for i in range(len(lstCut)): #拖动的控件中是否有子控件            
            if lstCut[i].widget.winfo_children():#拖动的控件中有子控件
                flag=1
                break
        if not xg and not yg: #是拖动控件。否则是剪切控件
            isDrag=1
            xg=self.master.master.winfo_x()+int(cmm.filePath[self.idx][2][self.wgtName]['x'][0]) #拖动控件在界面中的x坐标
            yg=self.master.master.winfo_y()+int(cmm.filePath[self.idx][2][self.wgtName]['y'][0]) #拖动控件在界面中的y坐标
        if flag:#拖动的控件中有子控件
            if not gui and not cmm.setGL(self.idx,st.master.wgtName,1): #放到控件中
                return 0  #不放置，退出
            lstPCP=[]  #元素是(wgt,pN)拖动的控件对象，父控件名
            for c in lstCut:   #放入lstPCP
                if gui: lstPCP.append((c,'root'))  #放到主界面                   
                else: lstPCP.append((c,st.master.wgtName))  #放到控件中                    
            i=0
            while lstPCP:#修改filePath信息
                c=lstPCP.pop(0)
                if not cmm.canParent(c[1],self.idx): return 0  #不能做父控件，退出
                cmm.adjPos(c[0].wgtName,c[1],self.idx) #调整filePath中的位置
                if i<len(lstCut): #拖动的控件
                    if c[1]=='root': cmm.regProp(self.idx,c[0].wgtName,cmm.guiL,c[1],0,xg+i*10,yg+i*10) #放到界面中。修改filePath中的值
                    else: cmm.regProp(self.idx,c[0].wgtName,cmm.guiL,c[1],0,i*10+5,i*10+5) #放到控件中。修改filePath中的值
                else:  #拖动控件中的子控件 
                    if c[1]=='root': cmm.regProp(self.idx,c[0].wgtName,cmm.guiL,c[1]) #放到界面中。修改filePath中的值
                    else: cmm.regProp(self.idx,c[0].wgtName,cmm.guiL,c[1]) #放到控件中。修改filePath中的值
                for cc in c[0].widget.winfo_children(): lstPCP.append((cc,c[0].wgtName)) 
                i+=1
            for k,v in cmm.filePath[self.idx][3].items():  #删除界面中所有控件
                if k=='cvsGUI':continue                    
                v.master.destroy()
            cmm.showGUI(self.idx)  #显示所有控件
            if not gui and isDrag: #拖放到控件中。重新找回重叠目标对象
                SelectedCanvas.targetWgt=cmm.filePath[self.idx][3][st.master.wgtName] #设置重叠目标
        else:#拖动的控件中无子控件
            if not gui:  #剪切到控件中
                if not cmm.canParent(st.master.wgtName,self.idx):  #是否能做父控件
                    return 0 #不能做父控件，退出
            for i in range(len(lstCut)):
                if gui or st.master.wgtName=='cvsGUI' : #在主界面中重新创建拖动控件并显示出来
                    aa=cmm.reCreatW(lstCut[i].wgtName,cmm.filePath[self.idx][3]['cvsGUI'],'root',self.idx,0,0,xg+i*10,yg+i*10)  
                else: #在控件中重新创建拖动的控件并显示出来
                    aa=cmm.reCreatW(lstCut[i].wgtName,cmm.filePath[self.idx][3][st.master.wgtName],st.master.wgtName,self.idx,0,0,i*10+5,i*10+5)  
                if not aa:return 0  #取消操作，退出  
                if not gui:
                    cmm.adjPos(lstCut[i].wgtName,st.master.wgtName,self.idx)  #调整位置             
        for it in lstCut:it.destroy()  #删除拖动的控件
        lstCut.clear()
        cmm.showSG()  #更新控件关系树     
        return 1
    def isOut(self): #是否拖动到父控件外面了
            minX,minY=cmm.lstSW[0].winfo_x(),cmm.lstSW[0].winfo_y() #选中控件的左上(x,y)
            maxX,maxY=minX+cmm.lstSW[0].winfo_width(),minY+cmm.lstSW[0].winfo_height()#选中控件的右下(x,y)
            pN=cmm.filePath[self.idx][2][cmm.lstSW[0].wgtName]['parent'][0]  #父控件名
            pWidth=cmm.filePath[self.idx][3][pN].winfo_width()  #父控件宽度
            pHeight=cmm.filePath[self.idx][3][pN].winfo_height()  #父控件高度
            for it in cmm.lstSW:  #记录最大最小值
                x1=it.winfo_x()
                y1=it.winfo_y()
                x2=x1+it.winfo_width()
                y2=y1+it.winfo_height()
                if x2>maxX:maxX=x2
                if x1<minX:minX=x1
                if y2>maxY:maxY=y2
                if y1<minY:minY=y1
            if maxX<0 or maxY<0 or minX>pWidth or minY>pHeight:  #是否拖动到父控件外面了
                return 1  #是外面 
            else:return 0  #在里面
    def onDragEnd(self,event):#结束拖动,做剪切操作。点击一下控件也会运行此函数
        if cmm.guiL!='place':return  #不是place布局，退出  
        lstName=[]  #选中控件的名称
        for it in cmm.lstSW: lstName.append(it.wgtName)
        out=0
        if not hasattr(cmm.lstSW[0].master,'wgtName'): #在拖动前，选中的控件是某个控件的子控件                                    
            if self.isOut():  #拖动到父控件外面了
                if not self.cutWgt(cmm.lstSW,1):#剪切控件。否则退出
                    for it in cmm.lstSW: it.place(x=self.start_x,y=self.start_y) #取消剪切，放回原位
                    return 0   
                for it in lstName: cmm.lstSW.append(cmm.filePath[self.idx][3][it].master)  #重新选中控件。要拿去检测重叠
                out=1
        if self.checkTarget():  #还要继续检测有否重叠(不能用elif)
            if not self.cutWgt(cmm.lstSW,0,SelectedCanvas.targetWgt):#剪切控件。否则退出 
                if not out:  #不是从父控件中出来，可以退回原位
                    for it in cmm.lstSW: it.place(x=self.start_x,y=self.start_y) #取消剪切，放回原位
                return 0    #不能剪切控件
            if SelectedCanvas.targetWgt:
                SelectedCanvas.targetWgt.pack(fill='both',expand=1,padx=0,pady=0)
                SelectedCanvas.targetWgt.master.config(bg='SystemButtonFace')
                SelectedCanvas.targetWgt=0 #取消重叠目标控件 
            self.tail(lstName,self.idx)
        elif out: #拖动到控件外面，但没有重叠
            cmm.lstSW.clear()
            self.tail(lstName,self.idx)
    def tail(self,lstName,idx):   
        cmm.ctrlPrs=1  #设置多选
        for it in lstName:   
            cmm.filePath[idx][3][it].master.update()             
            cmm.filePath[idx][3][it].master.mousedown(0)
        cmm.ctrlPrs=0  #取消多选
        cmm.filePath[idx][4]=1  #编辑标志设为已经编辑
        cmm.showSG()
    def checkTarget(self):  # 判断是否重叠（简化的碰撞检测）
        if not len(cmm.lstSW):return
        wx1,wy1,wx2,wy2,tx1,ty1,tx2,ty2=0,0,0,0,0,0,0,0
        for c in cmm.lstSW: #检测重叠       
            wx1=c.winfo_x()  #获取选中控件的坐标
            wy1=c.winfo_y()
            wx2=wx1+c.winfo_width()
            wy2=wy1+c.winfo_height()                    
            if not SelectedCanvas.targetWgt:#当前没有重叠目标,找重叠目标
                for k,v in cmm.filePath[self.idx][3].items(): #查找重叠的控件
                    if k=='cvsGUI' :continue
                    if cmm.filePath[self.idx][2][c.wgtName]['parent'][0]!=cmm.filePath[self.idx][2][k]['parent'][0]:continue  #父控件不同，不检测
                    if k==c.wgtName: continue  #是框选的控件本身，不检测
                    else:  #要检测的控件                                            
                        tx1=v.master.winfo_x()  #获取要检测控件的坐标
                        ty1=v.master.winfo_y()
                        tx2=tx1+v.master.winfo_width()
                        ty2=ty1+v.master.winfo_height() 
                        if (wx1<tx2 and wx2>tx1 and wy1<ty2 and wy2>ty1):  #有重叠目标控件（简化的碰撞检测）
                            if not cmm.canParent(k,self.idx):return 0  #不能做父控件，退出 
                            SelectedCanvas.targetWgt=v  #设置重叠目标控件
                            v.pack(fill='both',expand=1,padx=2,pady=2)
                            v.master.config(bg='red')
                            return 1
            else:#当前已经有重叠目标
                tx1=SelectedCanvas.targetWgt.master.winfo_x()  # 获取目标的坐标
                ty1=SelectedCanvas.targetWgt.master.winfo_y()
                tx2=tx1+SelectedCanvas.targetWgt.master.winfo_width()
                ty2=ty1+SelectedCanvas.targetWgt.master.winfo_height()
                if (wx1<tx2 and wx2>tx1 and wy1<ty2 and wy2>ty1): #有重叠目标控件（简化的碰撞检测）
                    return 1 #仍然重叠
        else:  # 如果不再重叠，重置目标的边框
            if SelectedCanvas.targetWgt:
                SelectedCanvas.targetWgt.pack(fill='both',expand=1,padx=0,pady=0)
                SelectedCanvas.targetWgt.master.config(bg='SystemButtonFace')
                SelectedCanvas.targetWgt=0   #取消重叠目标控件   
    def mRight(self,event):  #右键菜单
        cmm.ctrlPrs=0
        self.idx=cmm.rNB.index('current')  #当前index  
        pageON=cmm.rNB.select()  #取得当前页类名路径 
        pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典的key
        if self not in cmm.lstSW: self.mousedown(0)  #右击的控件不在lstSW中，是选中，否则是复制多个控件
        lst=("Button","Canvas","Checkbutton","Combobox","Entry","Frame","Label","LabelFrame","Listbox",'Notebook'
        ,"PanedWindow",'Progressbar','Radiobutton','Scale','Scrollbar','Separator','Spinbox','Text','Treeview')
        menuR =tk.Menu(tearoff=False)
        menuCh =tk.Menu(menuR,tearoff=False)  ##子菜单              
        menuR.add_cascade(label=cmm.t("添加控件"),menu=menuCh)  #父菜单项添加级联菜单        
        for i in range(len(lst)):
            menuCh.add_command(label=lst[i], command=lambda x=event.x,y=event.y,a=lst[i]:self.newW(a,x,y)) #在控件中创建新控件        
        menuR.add_command(label=cmm.t('绑定事件'), command=lambda :eventFunc(self.wgtName))  #事件响应   
        menuR.add_command(label=cmm.t('复制'), command=lambda:cmm.rNB.children[pageKey].onCopy(0))   #复制控件
        menuR.add_command(label=cmm.t('剪切'), command=lambda:cmm.rNB.children[pageKey].onCut(0))  #剪切控件
        menuR.add_command(label=cmm.t('粘贴'), command=lambda:cmm.rNB.children[pageKey].onPaste(0))   #粘贴控件
        menuR.add_separator() 
        menuR.add_command(label=cmm.t('删除'), command=lambda:self.delW(0))   #删除本控件
        menuR.add_separator() 
        menuR.add_command(label=cmm.t('转去代码'), command=lambda :self.onDB(0))  #转去代码 
        menuR.post(event.x_root, event.y_root)     # 光标位置显示菜单
    def newW(self,classN,x,y):  #在控件中创建新控件
        if not cmm.canParent(self.wgtName,self.idx): return 0  #不能做父控件，退出
        wgt=cmm.creatW(0,classN,x,y,self.wgtName)#创建新控件
        if wgt:wgt.mousedown(0)  #创建了新控件
    def delW(self,event):  #删除控件,在同一父控件中的             
        if not event or event.keysym == 'Delete' :#删除1个，多个，子母控件   
            if messagebox.askyesno(cmm.t('确认'), cmm.t('删除这{}个控件，确定吗？').format(len(cmm.lstSW))):                
                lstDel=[]
                wgtPN=0  #lstSW中的父控件名
                for  obj in cmm.lstSW:                    
                    for k,v in cmm.filePath[self.idx][2].items(): #记录其中的子控件。k是控件名，v是控件属性
                        if k=='cvsGUI':continue
                        if v['parent'][0]==obj.wgtName: lstDel.append(k) #记录其中的子控件
                        if not wgtPN and k==obj.wgtName: wgtPN=v['parent'][0] #查找lstSW中的父控件名                            
                    for n in lstDel: self.delN(n)  #删除其中的子控件及filePath中的记录
                    lstDel.clear()
                    self.delN(obj.wgtName)  #删除控件本身                                               
                cmm.table.delete(*cmm.table.get_children())#清空表
                cmm.lstSW.clear()
                #cmm.etrFocusOut()
                total=0                
                if cmm.guiL=='grid' :#如果grid布局的子控件都已经全部删除，则删除父控件中的rowconfigure等
                    for k,v in cmm.filePath[self.idx][2].items():  #计算lstSW中控件的父控件中的子控件数量 
                        if k=='cvsGUI':continue
                        if v['parent'][0]==wgtPN:total+=1
                    if total==0:#grid布局的子控件都已经全部删完，则删除父控件中的rowconfigure等
                        if wgtPN=='root':wgtPN='cvsGUI'
                        if cmm.filePath[self.idx][2][wgtPN].get('rowconfigure'):
                            del cmm.filePath[self.idx][2][wgtPN]['rowconfigure']
                        if cmm.filePath[self.idx][2][wgtPN].get('columnconfigure'):
                            del cmm.filePath[self.idx][2][wgtPN]['columnconfigure']
                cmm.maxSN=0
                cmm.guiL=''
                cmm.filePath[self.idx][4]=1  #编辑标志设为已经编辑
                cmm.lblStt['text']=''  #状态栏显示布局方式
                for k in cmm.filePath[self.idx][3].keys():  #重新计算最大编号
                    if k.find('_')!=-1 and int(k.split('_')[1])>cmm.maxSN: cmm.maxSN=int(k.split('_')[1])
                cmm.showSG()  #更新控件关系树
    def delN(self,wgtN): #根据控件名销毁控件自身及其绑定事件代码        
        cmm.filePath[self.idx][3][wgtN].destroy()  #销毁canvasWgt中的wgt
        cmm.filePath[self.idx][3][wgtN].master.destroy()  #销毁canvasWgt中的canvas            
        del cmm.filePath[self.idx][3][wgtN] #在所有控件对象中删除本控件对象
        del cmm.filePath[self.idx][2][wgtN] #删除filePath中的记录  
        cmm.addText(self.idx,wgtN,1) #删除绑定响应函数                                                   
    def keyUp(self,event):  #上移控件     
        if cmm.guiL!='place':return   #不是place布局，退出
        if self.winfo_y():
            x=self.winfo_x()
            y=self.winfo_y()-1
            self.place(x=x,y=y) 
            self.after_idle(self.showXY,x,y)  #显示x,y值
    def keyDown(self,event):  #下移控件        
        if cmm.guiL!='place':return   #不是place布局，退出
        if self.winfo_y()+self.winfo_height() < self.master.winfo_height():
            x=self.winfo_x()
            y=self.winfo_y()+1
            self.place(x=x,y=y)
            self.after_idle(self.showXY,x,y) #显示x,y值
    def keyLeft(self,event):  #左移控件   
        if cmm.guiL!='place':return      #不是place布局，退出  
        if self.winfo_x():
            x=self.winfo_x()-1
            y=self.winfo_y()
            self.place(x=x,y=y)
            self.after_idle(self.showXY,x,y)  #显示x,y值
    def keyRight(self,event):  #右移控件    
        if cmm.guiL!='place':return     #不是place布局，退出  
        if self.master.winfo_width() > self.winfo_x()+self.winfo_width():
            x=self.winfo_x()+1
            y=self.winfo_y()
            self.place(x=x,y=y)
            self.after_idle(self.showXY,x,y)  #显示x,y值
    '''def saveC(self,event): #坐标写入filePath
        if len(cmm.lstSW)>1:  #选择了多个控件
            for c in cmm.lstSW: 
                cmm.filePath[self.idx][2][c.wgtName]['x'][0]=str(c.winfo_x())  #写入filePath
                cmm.filePath[self.idx][2][c.wgtName]['y'][0]=str(c.winfo_y())  #写入filePath'''
    def showXY(self,x,y):  #显示x,y值,显示对齐线
        if cmm.guiL!='place':return   #不是place布局，退出
        cmm.filePath[self.idx][2][self.wgtName]['x'][0]=str(x)  #写入filePath
        cmm.filePath[self.idx][2][self.wgtName]['y'][0]=str(y)  #写入filePath
        #if 'elected' in self.master.winfo_name():
        self.alignDash(x,y)  #显示对齐线
        table=cmm.table
        for iid in table.get_children():   #更新属性表中x,y的值
            if table.item(iid)['text']=='place':
                table.set(table.get_children(iid)[0],'#2',value=x)
                table.set(table.get_children(iid)[1],'#2',value=y)                
                break
    def showProp(self):  #显示属性表       
        table=cmm.table
        self.idx=cmm.rNB.index('current')  #当前index  
        table.delete(*table.get_children())   #清空表父节点，同时清空了其中的子节点          
        #c=self.wgtName if self.wgtName.find('_')==-1 else self.wgtName[:self.wgtName.find('_')]
        if self.wgtName=='cvsGUI':classN='cvsGUI' #显示基本属性信息
        else:classN=self.wgtName[:self.wgtName.find('_')]
        base= table.insert('','end', text=cmm.t('类'),open=1,tags='oddColor') 
        table.insert(base,'end',values=('class',classN))  #第1行的class,不在属性字典中
        table.insert(base,'end',values=('name',self.wgtName),tags='oddColor')  #第2行的name,不在属性字典中                         
        i=2
        lm=cmm.guiL  #显示布局方式属性信息
        if self.wgtName!='cvsGUI':  
            pg= table.insert('','end', text=lm,open=1,tags='oddColor')   #布局节点
            if lm=='pack' or lm=='grid':  #pack或者grid布局                
                for kp,vp in cmm.filePath[self.idx][2][self.wgtName][lm].items():  #pack或者grid字典
                    if kp=='row':
                        row=vp[0]
                        if not row:messagebox.showerror(cmm.t('错误'),cmm.t('没有row值'))
                    if kp=='column':
                        col=vp[0]
                        if not col:messagebox.showerror(cmm.t('错误'),cmm.t('没有column值'))
                    if i%2==1: table.insert(pg,'end',values=(kp,vp[0]),tags='oddColor')   #插入奇数行数据
                    else:table.insert(pg,'end',values=(kp,vp[0]))   #插入偶数行数据
                    i+=1        
                if lm=='grid':
                    parentN=cmm.filePath[self.idx][2][self.wgtName]['parent'][0]  #该控件的父控件名
                    if parentN=='root':parentN='cvsGUI'
                    ff=''
                    for kp,vp in cmm.filePath[self.idx][2][parentN].items():
                        if kp=='rowconfigure':
                            for rowStr in vp:
                                if row==rowStr[:rowStr.find(',')]:
                                    ff=rowStr
                                    break
                        if ff:break
                    table.insert(pg,'end',values=('rowconfigure',ff),tags='oddColor')   #插入奇数行数据
                    ff=''
                    for kp,vp in cmm.filePath[self.idx][2][parentN].items():
                        if kp=='columnconfigure':
                            for rowStr in vp:
                                if col==rowStr[:rowStr.find(',')]:
                                    ff=rowStr
                                    break
                        if ff:break
                    table.insert(pg,'end',values=('columnconfigure',ff))   #插入偶数行数据
                    i+=2
            else:  #place布局
                for it in ('x','y','width','height'):  #place属性
                    if i%2==1: table.insert(pg,'end',values=(it,cmm.filePath[self.idx][2][self.wgtName][it][0]),tags='oddColor')   #插入奇数行数据
                    else:table.insert(pg,'end',values=(it,cmm.filePath[self.idx][2][self.wgtName][it][0]))   #插入偶数行数据
                    i+=1        
        other= table.insert('','end', text=cmm.t('基本'),open=1,tags='oddColor')  #标准属性值信息
        if classN=='cvsGUI':
            dctOther={'width': ['', ''], 'height': ['', '']}
            i=0
        else:
            dctOther=wp.getOther(classN,lm)
            if lm=='pack' or lm=='grid':  #pack或者grid布局
                if 'padx' in dctOther:del dctOther['padx']
                if 'pady' in dctOther:del dctOther['pady']
            table.insert(other,'end',values=('parent',cmm.filePath[self.idx][2][self.wgtName]['parent'][0])) #标准属性中的parent 
            i=1                    
            dctOther = {k:dctOther[k] for k in sorted(dctOther)}
        for k,v in dctOther.items(): #显示其余标准属性            
            if k in cmm.filePath[self.idx][2][self.wgtName]:aa=cmm.filePath[self.idx][2][self.wgtName][k][0]
            else: aa=''
            if i%2==1: table.insert(other,'end',values=(k,aa),tags='oddColor')   #插入奇数行数据
            else:table.insert(other,'end',values=(k,aa) )  #插入偶数行数据
            i+=1
        if self.wgtName!='cvsGUI': table.insert('','end',values=('',''),tags='oddColor' if i%2==1 else '')   #插入一空行
        for i in range(15): #在内容下方加入15行空行
             cmm.table.insert('', 'end',text='')
    def alignDash(self,x1,y1):#显示对齐线,x1拖动的控件的左上x坐标，y1拖动控件的左上y坐标
        if not isinstance(self.master,tk.Canvas) :return  #不在界面上不显示对齐线
        x2=x1+int(cmm.filePath[self.idx][2][self.wgtName]['width'][0]) #当前控件右下x
        y2=y1+int(cmm.filePath[self.idx][2][self.wgtName]['height'][0]) #当前控件右下y
        maxLY,maxUX,maxRY,maxDX=0,0,0,0 #最长的左坚线、上横线、右竖线、下横线
        for k,v in cmm.filePath[self.idx][2].items():            
            if k=='cvsGUI':continue              
            if v['parent'][0]!=cmm.filePath[self.idx][2][self.wgtName]['parent'][0]:continue #不在同一父控件中，跳过
            if k==self.wgtName:continue  #控件本身，跳过     
            wx1=int(v['x'][0])
            wy1=int(v['y'][0])
            wx2=wx1+int(v['width'][0])
            wy2=wy1+int(v['height'][0])            
            if x1==wx1 or x1==wx2: #找到。如果有几个控件同时并排，找最大的竖线或者横线值
                if abs(wy2-y1)>maxLY or abs(y2-wy1)>maxLY:
                    if y1<wy1:maxLY=wy2-y1  #在当前控件左边画左竖线。正数表示y1小，当前控件在上方 
                    else:maxLY=wy1-y2  #负数表示wy1小，当前控件在下方                
            if y1==wy1 or y1==wy2:
                if abs(wx2-x1)>maxUX or abs(x2-wy1)>maxUX:
                    if wx2-x1>maxUX:maxUX=wx2-x1  #上横线
                    else:maxUX=wx1-x2            
            if x2==wx2 or x2==wx1:
                if abs(wy2-y1)>maxRY or abs(y2-wy1)>maxRY:
                    if y1<wy1:maxRY=wy2-y1  #右竖线
                    else:maxRY=wy1-y2 
            if y2==wy2 or y2==wy1:
                if abs(wx2-x1)>maxDX or abs(x2-wx1)>maxDX:
                    if wx2-x1>maxDX:maxDX=wx2-x1  #下横线
                    else:maxDX=wx1-x2
        if maxLY: #画线以当前控件为基准进行绘制
            self.master.delete('ly')
            if maxLY>0:self.master.create_line(x1,y1-10,x1,y1+maxLY+10,fill='red',tag='ly')  #在当前控件左边画左竖线
            else:self.master.create_line(x1,y2+10,x1,y2+maxLY-10,fill='red',tag='ly')  #在当前控件左边画左竖线
        else:self.master.delete('ly')  #删除左竖线
        if maxUX:
            self.master.delete('ux')
            if maxUX>0:self.master.create_line(x1-10,y1,x1+maxUX+10,y1,fill='red',tag='ux')  #在当前控件上方画上横线
            else:self.master.create_line(x2+maxUX-10,y1,x2+10,y1,fill='red',tag='ux')  #画上横线
        else:self.master.delete('ux')
        if maxRY:
            self.master.delete('ry')
            if maxRY>0:self.master.create_line(x2,y1-10,x2,y1+maxRY+10,fill='red',tag='ry')  #画右竖线
            else:self.master.create_line(x2,y2+maxRY-10,x2,y2+10,fill='red',tag='ry')  #画右竖线
        else:self.master.delete('ry')
        if maxDX:
            self.master.delete('dx')
            if maxDX>0:self.master.create_line(x1-10,y2,x1+maxDX+10,y2,fill='red',tag='dx')   #画下横线  
            else:self.master.create_line(x2+maxDX-10,y2,x2+10,y2,fill='red',tag='dx')   #画下横线 
        else:self.master.delete('dx')      
        '''for i,c in enumerate(lstDraw):  #遍历所有坐标
            self.master.create_line(c[0],c[1],c[2],c[3],fill='red',dash=(1,2),tag=i) 
            for i in  self.master.find_withtag("all"):  # 遍历所有线条
                if self.master.type(i)=='line':  # 确保是线段
                    self.master.delete(self.master.gettags(i))  #根据标签名删除线段'''




