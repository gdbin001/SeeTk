import tkinter as tk
from tkinter import ttk
import cmm 

class eventFunc:  #事件绑定   
    def __init__(self,wgtN): 
        cmm.root.attributes('-disabled',1)  #父窗口失效
        top =tk.Toplevel()        #创建一个顶级窗口
        top.title(cmm.t('事件绑定'))        #窗口命名
        top.transient()        #将top注册成root的临时窗口，去掉了最大最小化的按钮
        top.geometry('315x395+700+200') #设置查找框所在的位置。宽x高+x坐标+y坐标
        top.resizable(False, False) #窗口不可变
        top.attributes("-topmost", True) #总是显示在主程序窗口之上   
        top.protocol('WM_DELETE_WINDOW',lambda:self.closeW(top))
        self.wgtN=wgtN
        self.it=''  #选中的事件
        scbY= tk.Scrollbar(top,orient="vertical")  #Y滚动条
        self.listbox=tk.Listbox(top,width=20,height=19,yscrollcommand=scbY.set)  #height是字符行数，width是字符列数
        self.listbox.grid(column=0,row=0,padx=(10,0))
        self.listbox.bind('<<ListboxSelect>>',lambda e:self.onLBoxClick(dctMouse,dctKey,dctV))
        scbY.config(command =self.listbox.yview)
        scbY.grid(column=1,row=0,sticky=('n','s'))
        dctV={'Listbox':{'ListboxSelect':cmm.t('点击列表框一行')}  #虚拟事件
          ,'Combobox':{'ComboboxSelected':cmm.t('点击组合框')}
          ,'Treeview':{'TreeviewSelect':cmm.t('点击Treeview一行'),'TreeviewOpen':cmm.t('打开了文件夹'),'TreeviewClose':cmm.t('关闭了文件夹')}
          ,'Notebook':{'NotebookChange':cmm.t('点击了标签')}
          ,'Canvas':{'CanvasConfigure':cmm.t('调整长宽位置')}   
          ,'Text':{'Modified':cmm.t('内容被插入/删除/替换，modified 标志从 0→1')
                   ,'Selection':cmm.t('选区起点或终点发生移动')
                   ,'UndoStack':cmm.t('undo/redo 后,“撤销/重做”菜单灰显')}}               
        dctMouse={'Button-1':cmm.t('单击鼠标左键'),'Button-2':cmm.t('单击鼠标滚轮'),'Button-3':cmm.t('单击鼠标右键')
          ,'Double-1':cmm.t('双击鼠标左键'),'Double-2':cmm.t('双击鼠标滚轮'),'Double-3':cmm.t('双击鼠标右键')
          ,'B1-Motion':cmm.t('按住鼠标左键移动'),'B2-Motion':cmm.t('按住鼠标滚轮移动'),'B3-Motion':cmm.t('按住鼠标右键移动')
          ,'ButtonRelease-1':cmm.t('释放鼠标左键'),'ButtonRelease-2':cmm.t('鼠标滚轮弹起'),'ButtonRelease-3':cmm.t('释放鼠标右键')
          ,'Enter':cmm.t('鼠标移动到区域'),'Leave':cmm.t('鼠标离开区域'),'Motion':cmm.t('鼠标移动'),'MouseWheel':cmm.t('鼠标滚轮滚动')}          
        dctKey={'FocusIn':cmm.t('获得键盘焦点'),'FocusOut':cmm.t('失去键盘焦点'),'Key':cmm.t('任意键'),'Return':cmm.t('回车键'),'KeyRelease':cmm.t('键盘按键释放')
          ,'Configure':cmm.t('控件尺寸变化'),'Escape':cmm.t('退出键'),'Space':cmm.t('空格键'),'Tab':cmm.t('制表键')
          ,'Up':cmm.t('向上键'),'Right':cmm.t('向右键'),'Left':cmm.t('向左键'),'Down':cmm.t('向下键'),'Shitf_L':cmm.t('组合键')
          ,'Shift_R':cmm.t('组合键'),'Control_L':cmm.t('组合键'),'Control_R':cmm.t('组合键'),'Alt_L':cmm.t('组合键'),'Alt_R':cmm.t('组合键')
          ,'F1':cmm.t('功能键'),'F2':cmm.t('功能键'),'F3':cmm.t('功能键'),'F4':cmm.t('功能键'),'F5':cmm.t('功能键'),'F6':cmm.t('功能键')
          ,'F7':cmm.t('功能键'),'F8':cmm.t('功能键'),'F9':cmm.t('功能键'),'F10':cmm.t('功能键'),'F11':cmm.t('功能键'),'F12':cmm.t('功能键')}        
        self.mark(dctV,dctKey,dctMouse)  #显示所有事件
        frm=tk.Frame(top)
        frm.grid(row=0,column=2,padx=15)
        btn=tk.Button(frm,text=cmm.t('绑定'),width=10,height=1,command=lambda:self.onOK(top,dctV,dctKey,dctMouse))        
        btn.grid(row=0,column=0,pady=10,padx=(0,10),sticky='w')
        self.lbl2=tk.Label(frm,text=cmm.t('事件说明:'))
        self.lbl2.grid(row=1,column=0,sticky='w') 
        self.lbl1=tk.Label(frm,wraplength=100,justify="left")
        self.lbl1.grid(row=2,column=0,sticky='w')                     
        #btn=tk.Button(frm,text='取消',width=10,height=1,command=lambda:self.closeW(regCtrl,top))
        #btn.grid(row=3,column=0,sticky='w')        
    def mark(self,dctV,dctKey,dctMouse):  #显示所有事件并标记已有的事件绑定
        idx=cmm.rNB.index("current")        
        lst=[]  #已经绑定的事件
        self.listbox.delete(0,'end')
        if cmm.filePath[idx][2][self.wgtN].get('bind'):  #记录已经绑定的事件
            for eb in cmm.filePath[idx][2][self.wgtN]['bind']:
                if '<<' in eb: lst.append(eb[eb.find('<<')+1:eb.find('>>')])
                else : lst.append(eb[eb.find('<')+1:eb.find('>')])
        for k,v in dctV.items():  #虚拟事件
            if k in self.wgtN:
                for k1 in v.keys():
                    for it in lst:
                        if it in k1: 
                            self.listbox.insert('end',f'<<{k1}>>  bound')
                            break
                    else: self.listbox.insert('end',f'<<{k1}>>')
        dctMouse.update(dctKey)
        if dctMouse.get('Button-1') and 'Button' in self.wgtN: del dctMouse['Button-1']  #是按键控件，删除Button-1事件
        for k in dctMouse.keys():
            for it in lst:
                if it in k: 
                    self.listbox.insert('end',k+'  bound')
                    break
            else: self.listbox.insert('end',k)
    def onOK(self,top,dctV,dctKey,dctMouse):  #确定
        if not self.it:return
        idx=cmm.rNB.index("current")
        if 'bind' not in cmm.filePath[idx][2][self.wgtN]:cmm.filePath[idx][2][self.wgtN]['bind']=[]
        if '<<' in self.it:  #虚拟事件
            cmm.filePath[idx][2][self.wgtN]['bind'].append(f'"{self.it}",lambda event:self.{self.wgtN}_{self.it.replace("<<","").replace(">>","")}(event)')
        else:  #普通事件
            cmm.filePath[idx][2][self.wgtN]['bind'].append(f'"<{self.it}>",lambda event:self.{self.wgtN}_{self.it.replace("-","")}(event)')
        #content=cmm.filePath[idx][1]  #语句文本
        flag=0
        funcN=''  #事件响应函数名        
        if '<<'  in self.it:  #确定响应函数名
            funcN=f'{self.wgtN}_{self.it.replace("<<","").replace(">>","")}'
        else:
            funcN=f'{self.wgtN}_{self.it.replace("-","")}'           
        cmm.addText(idx,f'{funcN}(self,event)')  #在原程序中加入响应函数
        self.mark(dctV,dctKey,dctMouse)  
        cmm.lstSW[0].showProp()
        cmm.filePath[idx][4]=1  #代码文本编辑标志设为已经编辑
        self.closeW(top)
        cmm.模式转换(f'def {funcN}')  #转换到文本模式
    def onLBoxClick(self,dctMouse,dctKey,dctV):  #单击listbox中的一行
        index=self.listbox.curselection()
        if index:  #显示事件说明
            self.it=self.listbox.get(index)  #取得点击的文本
            if 'bound' in self.it:
                self.it=''
                return
            if '<<' in self.it:
                for k,v in dctV.items():
                    if k in self.wgtN:
                        for k1,v1 in v.items():
                            if k1 in self.it:
                                self.lbl1['text']=v1
                                return
            if dctMouse.get(self.it):
                self.lbl1['text']=dctMouse[self.it]
            else:  self.lbl1['text']=dctKey[self.it]
    def closeW(self,top):
        cmm.root.attributes('-disabled',0)  #父窗口恢复正常
        top.destroy()
        