import tkinter as tk
from tkinter import ttk,messagebox
from tkinter.filedialog import askopenfilename
from tkinter import colorchooser
from tkfontselector import ask_font
import selectedCanvas as sc
import widgetProperty as wp
import editorPropertyList as epl
import copy,cmm,ast,threading

lstTtk=("Combobox",'Notebook','Progressbar','Separator','Treeview')  #ttk控件
lstPG=('Frame','Canvas','LabelFrame','Notebook','PanedWindow','Toplevel','Treeview')  #能做父控件的控件
lstPlace=('x','y','width','height')
dctBool={'1':1,'0':0,'""':"",'None':None}
mtE=0

#def guiCtrl():  #在控件面板放置各控件按钮
 #   lst=("Button","Canvas","Checkbutton","Combobox","Entry","Frame","Label","LabelFrame","Listbox","Menu",'Notebook'
 #       ,"PanedWindow",'Progressbar','Radiobutton','Scale','Scrollbar','Separator','Spinbox','Text','Treeview')    
  #  for i in range(len(lst)):        
   #     B=tk.Button(cmm.tab2,text=lst[i])       
    #    B.grid(row=i//3,column=i%3,sticky='EW',padx=2,pady=4)
     #   B.bind("<ButtonRelease-1>", lambda event:creatW(event))  #点击按钮事件
def creatW(e=0,nameFrom=0,wx=0,wy=0,parentN='cvsGUI'):  #创建控件。wx和wy右击cvsGUI的坐标。parentN是父控件名       
    pageON=cmm.rNB.select()  #取得当前页类名
    if not pageON or 'text' in pageON:return        
    idx=cmm.rNB.index("current")   
    cmm.filePath[idx][4]=1  #编辑了界面,保存标志置1 
    if parentN=='cvsGUI':aa='root'  
    else: aa=parentN
    if not cmm.setGL(idx,aa):return 0  #取消创建
    cmm.lblStt['text']=cmm.t('在父控件中的布局方式：')+cmm.guiL  #状态栏显示布局方式  
    if e:classN=e.widget.cget('text')  #在界面控件面板中，取得按钮上面的文字 
    else: classN=nameFrom  #在控件中点击右键菜单         
    if classN=="Menu":  #菜单控件
        if cmm.hasMenu(idx):#查看是否存在菜单控件
            messagebox.showerror(cmm.t('错误'),cmm.t('已经存在菜单控件'))
        else:
            from oprMenu import makeMenu
            makeMenu()  #创建菜单     
        return 0
    cmm.maxSN+=1
    wgtN=f"{classN}_{cmm.maxSN}"
    canvasWgt=sc.SelectedCanvas(cmm.filePath[idx][3][parentN],wgtN)#创建移动canvas，此画布大小就是控件的大小
    if classN in lstTtk:   #在移动canvas中创建基本ttk控件并记录在filePath中   
        cmm.filePath[idx][3][wgtN]=canvasWgt.create_widget(getattr(ttk,classN)) 
    else:   #在移动canvas中创建基本tk控件并记录在filePath中   
        cmm.filePath[idx][3][wgtN]=canvasWgt.create_widget(getattr(tk,classN))  
    regProp(idx,wgtN,cmm.guiL,0,0,wx,wy,aa)  #根据布局模式设置控件属性
    for k,v in cmm.filePath[idx][2][wgtN].items(): #显示效果     
        if k=='pack' or k=='grid':showWgt(k,0,idx,wgtN,canvasWgt)  #显示1个属性的效果，grid、pack属性是多个
        else:showWgt(k,v[0],idx,wgtN,canvasWgt)
    if classN in wp.PROP_CONFIGURE['command']:  #此控件有command属性
        cmm.filePath[idx][2][wgtN]['command']=wp.getOne(classN,'command',cmm.guiL)  #取得1个属性
        cmm.filePath[idx][2][wgtN]['command'][0]=f'lambda:self.{wgtN}_Click()'
        cmm.addText(idx,f'{wgtN}_Click(self)')  #在原程序中加入响应函数    
    cmm.showSG()
    canvasWgt.update()  #要在属性表中看到坐标或者长宽值就要更新，如果只是看效果则不用更新 
    canvasWgt.mousedown(0)   #这里做了 cmm.lstSW.append(canvasWgt)，还刷新属性表
    return canvasWgt
def one(e,):  #单击属性表中的单元格 
    table=cmm.table  
    etrFocusOut()  #销毁entry、cbb、button    
    if cmm.lstSW: cmm.lstSW[0].sltSts(1)  #控件显示空心手柄
    iid = table.identify_row(e.y)         # 点击的iid    
    if not iid or not table.parent(iid): return
    propN=table.item(iid, 'value')[0]  #属性名   
    if propN=='class' or propN=='name':return  #class和name属性不能更改
    selV = table.item(iid, 'value')[1]  # 原单元格内容,属性值
    box=table.bbox(iid,column=1)  #取得第2列box信息     
    if not box: return
    cmm.lstIEB.clear()
    for k,v in epl.PROP_TO_VALUES.items():  #有关属性显示combobox
        if propN==k: 
            etrCbb =ttk.Combobox(table, background='#F3F3F4',state='readonly')  #创建combobox框
            etrCbb['values']=v.split(';')
            etrCbb.bind("<<ComboboxSelected>>",lambda e:etrReturn())   #选中了另一属性，之前设置的属性值有效
            etrCbb.bind('<Return>',lambda e:etrReturn())
            etrCbb.bind('<FocusOut>',etrFocusOut)
            etrCbb.bind('<1>',setM)
            etrCbb.set(selV)  #列表框放入原选定值
            etrCbb.place(x=box[0], y=box[1], width=box[2], height=box[3])  # 设置etrCbb框位置及长宽   
            cmm.lstIEB.extend([iid,etrCbb]) 
            etrCbb.focus_set() 
            break
    else:#其他属性显示entry及button
        if propN in epl.PROP_COLOR_LIST :  #是颜色有关属性
            cEtrCbb(table,iid,box,selV,1,'color')            
        elif propN in epl.PROP_SELECT_LIST:  #是图片属性
            cEtrCbb(table,iid,box,selV,1,'img')            
        elif propN=='font':  #是字体属性
            cEtrCbb(table,iid,box,selV,1,'font')
        elif propN=='rowconfigure' or propN=='columnconfigure':  #
            cEtrCbb(table,iid,box,selV,1,'rcCfg',propN)
        else:cEtrCbb(table,iid,box,selV,0)   #剩余属性只显示entry框     
def setM(e):
    global mtE
    mtE=1   
def cEtrCbb(table,iid,box,selV,withB,k=0,propN=0):  #创建entry框及按钮
    etrCbb=tk.Entry(table, highlightthickness=1, bg='#F3F3F4')  #创建entry框
    etrCbb.bind("<Return>",lambda e:etrReturn())   #table中的etr框对回车的响应
    etrCbb.bind("<FocusOut>",etrFocusOut)   #销毁entry、cbb、button     
    etrCbb.insert(0, selV)  # etrCbb框插入原内容
    if withB:  #创建按钮
        etrCbb.place(x=box[0], y=box[1], width=box[2]-20, height=box[3])  # 设置etrCbb框位置及长宽 
        btn=tk.Button(table,text='...',command=lambda a=k,propN=propN,selV=selV:btnClick(a,propN,selV))
        btn.place(x=box[0]+box[2]-19, y=box[1], width=20, height=box[3])
        cmm.lstIEB.extend([iid,etrCbb,btn]) 
    else:
        etrCbb.place(x=box[0], y=box[1], width=box[2], height=box[3])  # 设置etrCbb框位置及长宽     
        cmm.lstIEB.extend([iid,etrCbb]) 
    etrCbb.focus_set()  # etrCbb框获取焦点
def btnClick(a,propN=0,selV=0): #点击了entry旁边的按钮
    global mtE
    mtE=1
    cmm.lstIEB[1].delete(0,'end')  #清空内容
    if a=='color': #是颜色有关属性        
        color = colorchooser.askcolor()
        if color[0] is None: #取消修改
            cmm.lstIEB[1].insert(0, selV)  # etrCbb框插入原内容
            return  
        cmm.lstIEB[1].insert(0, color[1]) #在etrCbb中插入输入的值
    elif a=='img': #是图片属性
        filePath = askopenfilename(title=cmm.t("选择文件"), filetypes=[("All files", "*")])
        if not filePath: #取消修改
            cmm.lstIEB[1].insert(0, selV)  # etrCbb框插入原内容
            return
        cmm.lstIEB[1].insert(0,filePath)  #在etrCbb中插入输入的值
    elif a=='font': #是字体
        cFont = ask_font(title=cmm.t("字体"))
        if not cFont: #取消修改
            cmm.lstIEB[1].insert(0, selV)  # etrCbb框插入原内容
            return
        for k in list(cFont.keys()):
            if not cFont[k]:del cFont[k]
        cmm.lstIEB[1].insert(0, cFont)   #在etrCbb中插入输入的值
    elif a=='rcCfg':  #'rowconfigure' or 'columnconfigure'
        groupV=tk.StringVar(value='') #单选按钮变量,是字符型。默认值是''
        chooseL(groupV,propN,selV)  #打开选择界面
        if groupV.get()=='end':  #取消修改
            cmm.lstIEB[1].insert(0, selV)  # etrCbb框插入原内容
            return 
        if groupV.get()=='clear':cmm.lstIEB[1].insert(0,'') #在etrCbb中插入输入的值
        else:cmm.lstIEB[1].insert(0, groupV.get()) #在etrCbb中插入输入的值
    etrReturn()
def canParent(parentN,idx):#是否能做父控件。wgtN是子控件名，parentN是父控件名
    if parentN=='root' or parentN=='cvsGUI':return 1
    vc,flag=0,0
    for i,k in enumerate(cmm.filePath[idx][2].keys()):
        if k==parentN:  #找到父控件
            classN=parentN[:parentN.find('_')]  #父控件类名
            if classN not in lstPG: return 0   #不能做父控件
            break            
    else:  #不存在父控件 
        return 0
    return 1
def adjPos(wgtN,parentN,idx):#在filePath中，调整控件位置。wgtN是子控件名，parentN是父控件名
    if parentN=='root' or parentN=='cvsGUI':return 1
    vc,flag=0,0
    for i,k in enumerate(cmm.filePath[idx][2].keys()):#调整位置
        if k==parentN:  #找到父控件
            for ic,kc in enumerate(cmm.filePath[idx][2].keys()):  #移动子控件到父控件后面
                if kc==wgtN:  #找到子控件
                    if ic<i:  #子控件在此控件的前面,记录子控件字典值
                        vc=cmm.filePath[idx][2].pop(kc)
                        cmm.filePath[idx][2][kc]=vc  #移动子控件到最后面
                    flag=1
                    break
            if flag:break
    else:  #不存在父控件 
        return 0
    return 1
def convertStr(typeN,arg):  #转换成相应类型
    if not typeN:return 0 #没有类型
    if typeN=='int' :  #int类型
        try:
            arg=int(arg)
        except :
            messagebox.showerror(cmm.t('错误'),cmm.t('输入值不是有效整数'))
            return 
    elif typeN=='bool':    #bool类型        
            arg=dctBool[arg]
    elif typeN=='float':   #float类型
        try:
            arg=float(arg)
        except :
            messagebox.showerror(cmm.t('错误'),cmm.t('输入值不是有效浮点数'))
            return
    elif typeN=='font':   #字体类型
        try:            
            arg=tk.font.Font(**ast.literal_eval(arg)) 
        except :
            messagebox.showerror(cmm.t('错误'),cmm.t('输入值不是有效字体属性'))
            return
    return arg
def haveWgt(r,col,idx,parent): #grid布局查看此位置是否有控件
    for k,v in cmm.filePath[idx][2].items():
        if k=='cvsGUI':continue
        if v['parent'][0]==parent and v.get('grid'):
            if v['grid']['row'][0]==r and v['grid']['column'][0]==col:
                messagebox.showerror(cmm.t('错误'),cmm.t('此位置有控件'))
                return 1
def etrReturn(): #输入完毕按下回车。检查content,并保存到相应filePath，显示效果。
    propN=cmm.table.item(cmm.lstIEB[0])['values'][0] #取得属性名    
    if cmm.lstSW:  #界面中的控件
        wgtN=cmm.lstSW[0].wgtName  #取得控件名
        classN=wgtN[:wgtN.find('_')]  #取得控件类名
    else:  wgtN='cvsGUI'
    idx=cmm.rNB.index('current')  #当前index    
    cmm.filePath[idx][4]=1  #编辑标志设为已经变化 
    content = cmm.lstIEB[1].get().strip()  # 获取entry或者combobox的内容      
    propPN=cmm.table.item(cmm.table.parent(cmm.lstIEB[0]))['text']  #属性表中属性的父节点名 
    if not content:#输入为空
        if wgtN=='cvsGUI':
            messagebox.showerror(cmm.t('错误'),cmm.t('界面尺寸不能为空'))
            return 
        if propPN=='grid' or propPN=='pack': 
            if propN=='row' or propN=='column':return
            if propN=='rowconfigure' or propN=='columnconfigure':
                parentN=cmm.filePath[idx][2][wgtN]['parent'][0]  #该控件的父控件名
                if parentN=='root':parentN='cvsGUI'  #主界面控件名
                if propN=='rowconfigure':rc=cmm.filePath[idx][2][wgtN][propPN]['row'][0]  #行值
                else:rc=cmm.filePath[idx][2][wgtN][propPN]['column'][0]  #列值
                if propN in cmm.filePath[idx][2][parentN]:  #删除父控件中的rowconfigure等语句
                    for i,it in enumerate(cmm.filePath[idx][2][parentN][propN]):
                        if rc==it[:it.find(',')]:del cmm.filePath[idx][2][parentN][propN][i]
            else:cmm.filePath[idx][2][wgtN][propPN][propN][0]='' #在grid或者pack基础属性中
        elif propN in wp.getBase(classN,cmm.guiL): #在基础属性中
            if cmm.filePath[idx][2][wgtN][propN][1]=='int':cmm.filePath[idx][2][wgtN][propN][0]='0'
            elif cmm.filePath[idx][2][wgtN][propN][1]=='':cmm.filePath[idx][2][wgtN][propN][0]='0'
            else:cmm.filePath[idx][2][wgtN][propN][0]=''  
        elif propN in cmm.filePath[idx][2][wgtN]: del cmm.filePath[idx][2][wgtN][propN] #不在基础属性中
    else:  #输入有值
        if (propN=='ipadx' or propN=='ipady') and not content[0].isdigit():
            messagebox.showerror(cmm.t('错误'),cmm.t('请输入数字'))
            return
        if propN in cmm.filePath[idx][2][wgtN] : #属性值没有变化。grid和pack在下面
            if content==cmm.filePath[idx][2][wgtN][propN][0]: 
                etrFocusOut()  #销毁entry、cbb、button
                return  #属性值没有变化 
        if propN=='parent' :#要修改父控件
            if not canParent(content,idx): #能否做父控件                
                messagebox.showerror(cmm.t('错误'),cmm.t('此控件不能做父控件，或者不存在'))   
                return  0
            adjPos(wgtN,content,idx)  #可以做父控件，调整字典中的位置 
        elif propN=='height' or propN=='width':
            if propN not in cmm.filePath[idx][2][wgtN]:cmm.filePath[idx][2][wgtN][propN]=['','int'] 
            cmm.filePath[idx][2][wgtN][propN][0]=content   #要修改width或者height属性值
        elif propN=='rowconfigure' or propN=='columnconfigure':  #属性值没有变化在chooseL中已经处理，这里不用响应
            if content.find(',')!=-1:  #打到值 
                parentN=cmm.filePath[idx][2][wgtN]['parent'][0]  #该控件的父控件名
                if parentN=='root':parentN='cvsGUI'
                if propN not in cmm.filePath[idx][2][parentN]:  #创建rowconfigure等属性
                    cmm.filePath[idx][2][parentN][propN]=[]  #父控件中的这个属性只负责存放，不在属性表中显示
                for i,it in enumerate(cmm.filePath[idx][2][parentN][propN]):
                    if it[:it.find(',')]==content[:content.find(',')]:
                        cmm.filePath[idx][2][parentN][propN][i]=content
                        break
                else: cmm.filePath[idx][2][parentN][propN].append(content) #保存属性值到filePath,有多个则用“,”号隔开。例如rowconfigure:['0,weight=1','1,weight=2']
        elif propPN=='grid' or propPN=='pack': #要修改pack或者grid的属性
            if content==cmm.filePath[idx][2][wgtN][propPN][propN][0]: #属性值没有变化 
                etrFocusOut()  #销毁entry、cbb、button
                return  
            if propN=='row': #grid布局查看此位置是否有控件
                col=cmm.filePath[idx][2][wgtN]['grid']['column'][0]
                r=content
                if haveWgt(r,col,idx,cmm.filePath[idx][2][wgtN]['parent'][0]):return  #此位置上已有控件，退出
            elif propN=='column': #grid布局查看此位置是否有控件
                r=cmm.filePath[idx][2][wgtN]['grid']['row'][0]
                col=content
                if haveWgt(r,col,idx,cmm.filePath[idx][2][wgtN]['parent'][0]):return  #此位置上已有控件，退出
            cmm.filePath[idx][2][wgtN][propPN][propN][0]=content  #保存属性值到filePath            
        elif len(cmm.lstIEB)==3: #要修改color、image、字体等值 
            if propN not in cmm.filePath[idx][2][wgtN]:  
                cmm.filePath[idx][2][wgtN][propN]=wp.getOne(classN,propN,propPN)
            cmm.filePath[idx][2][wgtN][propN][0]=content  #保存属性值到filePath。如果是image,则保存图片路径，后面再进行转换  
        else:  #要修改其他etrCbb能显示的值 
            if propN not in cmm.filePath[idx][2][wgtN]:
                cmm.filePath[idx][2][wgtN][propN]=wp.getOne(classN,propN,propPN)  #保存属性值到filePath 
            cmm.filePath[idx][2][wgtN][propN][0]=content  #保存属性值到filePath      
    if propN=='row' or propN=='column':cmm.filePath[idx][3][wgtN].master.showProp()  #刷新属性表，重新显示rowconfigure等值
    else:cmm.table.set(cmm.lstIEB[0],1,content)#修改属性表
    etrFocusOut()  #销毁entry、cbb、button
    if propN=='parent':  #更换父控件(创建新控件，删除原控件)                       
        tmp=cmm.lstSW[0]  #暂存原来的canvasWgt控件  
        if content=='root':cmm.lstSW[0]=reCreatW(wgtN,cmm.filePath[idx][3]['cvsGUI'],content,idx)  #在界面重新创建控件并显示出来
        else:   #在子控件中重新创建控件并显示出来 
            for k,v in cmm.filePath[idx][3].items():  #在所有控件中根据控件名查找父控件对象。v是父控件对象，下面要用
                if k==content: break
            cmm.lstSW[0]=reCreatW(wgtN,v,content,idx)             
        if cmm.lstSW[0]:  #修改成功
            tmp.destroy()  #删除原来的canvasWgt控件 
        else:  #没有修改
            cmm.lstSW[0]=tmp  #还原来的canvasWgt控件 
        cmm.showSG()  #更新控件关系树
    elif propN!='command':
        try:
            if cmm.lstSW:showWgt(propN,content,idx,wgtN,cmm.lstSW[0])  #显示选定控件的1个属性的效果
            else: showWgt(propN,content,idx,wgtN)  #显示cvsGUI的属性的效果  
        except Exception as e:
            messagebox.showerror(cmm.t('属性不正确，请检查'),cmm.t("错误：{} - {}").format(type(e).__name__,e)) 
    if not content:cmm.lstSW[0]=cmm.filePath[idx][3][wgtN].master  #lstSW指向新生成的控件。必须放这里
    if cmm.lstSW:  
        cmm.lstSW[0].update()
        cmm.lstSW[0].sltSts() #控件画选中状态            
    else: #cvsGUI画选中状态  
        cmm.filePath[idx][3][wgtN].update()
        cmm.filePath[idx][3][wgtN].sltSts()          
def showWgt(propN,content,idx,wgtN,canvasWgt=0):    #显示1个属性的效果,但parent、command、bind等略过   
    if propN=='command' or propN=='parent' or propN=='bind':return 0
    if canvasWgt and (propN=='pack' or propN=='grid' or ((cmm.guiL=='pack' or cmm.guiL=='grid') and propN in cmm.filePath[idx][2][wgtN][cmm.guiL])): #第2个and后是修改了1个pack或者grid属性
        argDct={}
        for kpp,vpp in cmm.filePath[idx][2][wgtN][cmm.guiL].items():  #取得控件pack或者grid中的属性值
            if vpp[0]: 
                if vpp[1]=='string' :argDct[kpp]=vpp[0]
                elif '(' in vpp[0]: argDct[kpp]=ast.literal_eval(vpp[0])
                else: argDct[kpp]=int(vpp[0])
        getattr(canvasWgt,cmm.guiL)(**argDct) #显示效果
        return 0
    if content and (propN=='rowconfigure' or propN=='columnconfigure') :  #content有内容 
        pN=cmm.filePath[idx][2][wgtN]['parent'][0]
        if pN=='root':pN='cvsGUI'
        rc,w=cmm.rcW(content)
        getattr(cmm.filePath[idx][3][pN],propN)(rc,**w)
        return 0
    if content:  arg=convertStr(cmm.filePath[idx][2][wgtN][propN][1],content)  #转换成相应类型
    if not content : #content无内容。则要删除所有控件，再重新显示
        for k,v in cmm.filePath[idx][3].items():  #删除界面中所有控件
            if k=='cvsGUI':continue                    
            v.master.destroy()
        if (propN=='rowconfigure' or propN=='columnconfigure') and cmm.filePath[idx][2][wgtN]['parent'][0]=='root':
            cmm.filePath[idx][3]['cvsGUI'].destroy()
            pageON=cmm.rNB.select()  #取得当前页类名
            pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典key
            cmm.rNB.children[pageKey].cvsGUI=sc.SelectedCanvas(cmm.rNB.children[pageKey].frm,'cvsGUI',relief='raised',bg='grey',name='cvsGUI',bd=0)#主界面canvas
            cmm.rNB.children[pageKey].cvsGUI.place(x=2,y=2,width=930,height=670) #先按此参数创建，后在prmToRC()中再调整后显示 
        cmm.showGUI(idx) #重新显示所有控件
    elif propN=='image' : 
        if content[1:2]==":":  abc=tk.PhotoImage(file=content) #绝对地址
        else: abc=tk.PhotoImage(file='ico/ff.png')  #用f'{}'表示的地址，用自带的小方块代替 
            
        canvasWgt.widget[propN]=abc #显示效果       
        canvasWgt.image=abc
    elif (propN in lstPlace) and cmm.guiL=='place':  #是位置长宽,且是place布局
        if canvasWgt: canvasWgt.place({propN:arg})  #界面中的控件
        else: cmm.filePath[idx][3][wgtN].place({propN:arg})  #cvsGUI 
    else:  #是其他属性#cmm.lstSW[0].config({propN:arg})
        if wgtN=='cvsGUI':  cmm.filePath[idx][3]['cvsGUI'].place_configure(**{propN:content})
        else:canvasWgt.widget[propN]=arg  #显示效果    
def gridRC(idx,wgtN=0,rePN=0):#grid布局确定行列值
    mr=0  #mr最大行数
    for k,v in cmm.filePath[idx][2].items(): #找最大行数、列数和满格情况下的控件总数
        if k=='cvsGUI':continue
        if v['parent'][0]==rePN:       
            if v['grid']['row'][0] and int(v['grid']['row'][0])>mr: 
                mr=int(v['grid']['row'][0])
    return mr+1
def regProp(idx,reCN,layoutM,rePN='',newN='',wx=0,wy=0,rightWN=0):  #记录属性值。rePN父控件名,rightWN右击的控件名。wx和wy右击cvsGUI的坐标
    classN=reCN[:reCN.find('_')]  #原控件类名
    if newN :#粘贴操作
        cmm.filePath[idx][2][newN]=copy.deepcopy(cmm.filePath[idx][2][reCN])
        reCN=newN
    if layoutM=='place':  #当前为place布局方式                                   
        if rePN: #更换父控件或者粘贴。确定本控件的xywh值       
            dct=copy.deepcopy(cmm.filePath[idx][2][reCN])  
            if 'pack' in cmm.filePath[idx][2][reCN] or 'grid' in cmm.filePath[idx][2][reCN]: #该控件原来是pack或者grid
                cmm.filePath[idx][2][reCN]=wp.getBase(classN,layoutM)
                if wx or wy: x,y,w,h=wx,wy,90,25  #从pack或者grid到place
                else: x,y,w,h=5,5,90,25                              
            else:   #该控件原来是place
                w,h=int(cmm.filePath[idx][2][reCN]['width'][0]),int(cmm.filePath[idx][2][reCN]['height'][0])     
                if wx or wy: x,y=wx,wy
                else: x,y=5,5                                       
            for k,v in dct.items():
                if k not in ('pack','grid','width','height','parent'):cmm.filePath[idx][2][reCN][k]=v 
            cmm.filePath[idx][2][reCN]['parent'][0]=rePN  #修改parent  
        else:  #新建
            if wx and wy: x,y,w,h=wx,wy,90,25  #x坐标,y坐标#宽高 
            else:  x,y,w,h=cmm.maxSN*5,cmm.maxSN*5,90,25  #没有传值过来的情况下，x坐标,y坐标#宽高
            cmm.filePath[idx][2][reCN]=wp.getBase(classN,layoutM)  #是新建，记录该控件基础属性
            if rightWN!='root' : cmm.filePath[idx][2][reCN]['parent'][0]=rightWN  #修改父控件名
            if 'text' in cmm.filePath[idx][2][reCN]: cmm.filePath[idx][2][reCN].update({'text':[reCN,'string']}) #设置text属性
        cmm.filePath[idx][2][reCN].update({'x':[str(x),'int'],'y':[str(y),'int'],'width':[str(w),'int'],'height':[str(h),'int']})  #保存控件对象
    elif layoutM=='pack':  #当前为pack布局方式
        if rePN : #更换父控件，reCN是原控件名。粘贴，reCN是新控件名           
            if cmm.filePath[idx][2][reCN].get('grid') or cmm.filePath[idx][2][reCN].get('x'): #该控件原来是place或者grid
                dct=copy.deepcopy(cmm.filePath[idx][2][reCN])
                cmm.filePath[idx][2][reCN]=wp.getBase(classN,layoutM) 
                for k,v in dct.items():
                    if k not in ('grid','x','y','width','height','parent'):cmm.filePath[idx][2][reCN][k]=v
            cmm.filePath[idx][2][reCN]['parent'][0]=rePN  #修改parent                            
        else:  #新建
            cmm.filePath[idx][2][reCN]=wp.getBase(classN,layoutM)  #是新建，记录该控件基础属性
            if rightWN!='root' : cmm.filePath[idx][2][reCN]['parent'][0]=rightWN  #修改父控件名
            if 'text' in cmm.filePath[idx][2][reCN]: cmm.filePath[idx][2][reCN]['text'][0]=reCN #设置text属性
    else:  #当前为grid布局方式
        if rePN :#更换父控件，reCN是原控件名。粘贴，reCN是新控件名
            if cmm.filePath[idx][2][reCN].get('pack') or cmm.filePath[idx][2][reCN].get('x'): #原控件是pack或者place
                dct=copy.deepcopy(cmm.filePath[idx][2][reCN])
                cmm.filePath[idx][2][reCN]=wp.getBase(classN,layoutM) 
                for k,v in dct.items():
                    if k not in ('pack','x','y','width','height','parent'):cmm.filePath[idx][2][reCN][k]=v 
            cmm.filePath[idx][2][reCN]['parent'][0]=rePN  #修改parent  
        else:  #新建
            cmm.filePath[idx][2][reCN]=wp.getBase(classN,layoutM)  #是新建，记录该控件基础属性 
            if rightWN!='root' : cmm.filePath[idx][2][reCN]['parent'][0]=rightWN  #修改父控件名
            if 'text' in cmm.filePath[idx][2][reCN]: cmm.filePath[idx][2][reCN]['text'][0]=reCN #text属性
        if rePN:r=gridRC(idx,reCN,rePN)  #更换父控件和粘贴。确定行值 
        else: r=gridRC(idx,reCN,rightWN)  #新建。确定行值            
        cmm.filePath[idx][2][reCN]['grid'].update({'row':[str(r),'int'],'column':['0','int']})
def reCreatW(reCN,reP,content,idx,newN=0,reGL=0,xg=0,yg=0):  #reCN是原控件名。reP是新父控件对象,content是新父控件名,newN新控件名,reGL=1是用回原布局 
    global lstTtk 
    if not reGL:  #要询问布局
        if not cmm.setGL(idx,content):return 0 #没有取得布局则退出    
    classN=reCN[:reCN.find('_')]  #原控件类名
    if newN: wgtN=newN  #粘贴新控件        
    else: wgtN=reCN  #修改父控件
    canvasWgt=sc.SelectedCanvas(reP,wgtN)#创建移动canvas，此画布大小就是控件的大小  
    if classN in lstTtk:   #在移动canvas上创建ttk控件    
        cmm.filePath[idx][3][wgtN]=canvasWgt.create_widget(getattr(ttk,classN))
    else:   #在移动canvas上创建tk控件  
        cmm.filePath[idx][3][wgtN]=canvasWgt.create_widget(getattr(tk,classN))
    regProp(idx,reCN,cmm.guiL,content,newN,xg,yg) #记录控件所有属性。   
    if newN:   #粘贴的控件，处理有command和bind命令的内容
        if cmm.filePath[idx][2][newN].get('command'):  #更换command中的控件名,添加command定义语句
            cmm.filePath[idx][2][newN]['command'][0]=cmm.filePath[idx][2][newN]['command'][0].replace(reCN,newN)
            cmm.addText(idx,f'{newN}_Click(self,)')  #加入命令定义语句
        if 'bind' in cmm.filePath[idx][2][newN]:  #更换bind中的控件名
            cmm.filePath[idx][2][newN]['bind'][0]=cmm.filePath[idx][2][newN]['bind'][0].replace(reCN,newN)
    for k,v in cmm.filePath[idx][2][wgtN].items(): #显示效果
        if k=='pack' or k=='grid':showWgt(k,0,idx,wgtN,canvasWgt)  #显示1个属性的效果，grid、pack属性是多个
        else: showWgt(k,v[0],idx,wgtN,canvasWgt)  #不是所有的属性都要showWgt
        if k not in ('pack','grid') and not v[0]: canvasWgt=cmm.filePath[idx][3][wgtN].master #属性值为空会销毁所有控件，重新创建，所以要重新指向
    return canvasWgt
def etrFocusOut(e=0):  #销毁entry、cbb、button.
    global mtE
    if not mtE and cmm.lstIEB:        
        aa=str(type(cmm.lstIEB[1]))
        if 'Entry' in aa or 'Combobox' in aa:# 如果属性表中的entry或者cbb框可见
            cmm.lstIEB[1].destroy()  # 删除entry或者cbb框            
        if len(cmm.lstIEB)==3:
            cmm.lstIEB[2].destroy()
        cmm.lstIEB.clear()
    mtE=0
def onTabChanged(e): #创建新页时触发。模式转换触发。选定页时触发。
    pageON=cmm.rNB.select()  #取得当前选中的页类名     
    cmm.guiL=''
    cmm.lblStt['text']=''
    if not pageON: return    
    cmm.table.delete(*cmm.table.get_children())#清空表 #清空原表内容        
    for c in cmm.lstSW:  #取消原页面中的控件选中状态
        if c.winfo_exists():
            c.widget.pack(fill='both',expand=1,padx=0,pady=0) 
            c.delete('all')
    tabN=cmm.rNB.tab(pageON, "text")  #取得当前选中的标签上的名称
    idx=cmm.rNB.index("current")  #取得当前的tabId
    for i,po in enumerate(cmm.rNB.tabs()):  #遍历标签页，启动或者停止上色
        if 'text' in po: #是文本模式          
            pageKey=po[po.rfind('!'):]
            if i==idx: #是当前标签页
                if not cmm.rNB.children[pageKey].coloring: 
                    cmm.rNB.children[pageKey].coloring=11   #启动上色
                    cmm.rNB.children[pageKey].textNow.edit_modified(1)
                    cmm.rNB.children[pageKey]._changeDt=1
                    cmm.rNB.children[pageKey].goColor()  #启动上色
            else: cmm.rNB.children[pageKey].coloring=0  #停止上色 
    if 'text' in pageON:  #转换后或者创建时，是文本模式        
        pageKey=pageON[pageON.rfind('!'):]  #从页类名中取得页字典的key
        cmm.rNB.children[pageKey].keyPrs(0)  #光标如果在行号框则不显示
        if '#Auto-generated by the system' in cmm.filePath[idx][1] and 'Do not delete this line-' in cmm.filePath[idx][1]: #是本软件格式的文件
            cmm.menuBar.entryconfig(cmm.t("编辑"), state="normal")  #菜单栏中的"编辑"菜单使能
            for i in range(len(cmm.btnBar)):
                if i>0:  cmm.btnBar[i]['state']='disabled' #快捷键禁用
                else:  cmm.btnBar[i]['state']='normal' #快捷键使能
            cmm.btnMC['state']='normal'  #模式转换功能使能
        else:cmm.btnMC['state']='disabled'  #禁用模式转换功能
    else:  #转换后是图形模式
        cmm.btnMC['state']='normal'  #模式转换功能使能
        cmm.setGL(idx,'root',0) #设置父控件内的guiL
        cmm.lblStt['text']=cmm.t('在父控件中的布局方式：')+cmm.guiL  #状态栏显示布局方式
        cmm.menuBar.entryconfig(cmm.t("编辑"), state="disabled")  #禁用菜单栏中的"编辑"菜单
        for i in range(len(cmm.btnBar)):
            if i==0:  cmm.btnBar[i]['state']='disabled' #快捷键禁用
            elif cmm.guiL=='place':  cmm.btnBar[i]['state']='normal' #快捷键使能  
            else: cmm.btnBar[i]['state']='disabled' #快捷键禁用              
    cmm.lstSW.clear()
    #cmm.copyWgt.clear()
    cmm.showSG()  #更新控件关系树
    cmm.ctrlPrs=0 #清空原界面ctrl键
    cmm.maxSN=0    
    cmm.refTree(tabN.strip(),cmm.parser['default']['folderPath'])  #menuRight模块中的refTree函数    
    for k in cmm.filePath[idx][3].keys():  #计算当前最大编号
        if k.find('_')!=-1 and int(k.split('_')[1])>cmm.maxSN: cmm.maxSN=int(k.split('_')[1])
def chooseL(groupV='',propN='',selV=0):  #确定布局、rowconfigure等
    top =tk.Toplevel()        #创建一个顶级窗口
    top.grab_set()  # 设置窗口为模态（阻止用户操作主窗口）          
    top.resizable(0,0)  #去掉最大化和最小化按钮
    xp=cmm.root.winfo_x()  #父窗口x坐标
    yp=cmm.root.winfo_y()  #父窗口y坐标
    hp=cmm.root.winfo_height()  #父窗口高度
    wp=cmm.root.winfo_width()  #父窗口宽度
    top.geometry(f'300x200+{int((wp-300)/2)+xp}+{int((hp-200)/2)+yp}') #设置框所在的位置。宽x高+x坐标+y坐标
    top.resizable(False, False) #窗口不可变
    top.attributes("-topmost", 1) #总是显示在主程序窗口之上                        
    if groupV.get():  #是选择布局
        top.title(cmm.t('选择布局'))
        tk.Radiobutton(top,text='pack  ',variable=groupV,value='pack').pack(pady=(30,0))  
        tk.Radiobutton(top,text='grid  ',variable=groupV,value='grid').pack() 
        tk.Radiobutton(top,text='place ',variable=groupV,value='place').pack()  #,font=('微软雅黑',11)
        tk.Button(top,text=cmm.t('确定'),width=10,height=1,command=lambda:top.destroy()).pack(pady=(10,0))         
        top.bind('<Return>',lambda e:top.destroy())
    else:  #是rowconfigure等
        idx=cmm.rNB.index("current")
        wgtName=cmm.lstSW[0].wgtName
        for kp,vp in cmm.filePath[idx][2][wgtName]['grid'].items():  #grid字典
            if kp=='row':r=vp[0]
            if kp=='column': col=vp[0]
        dct={}
        if selV:
            aa=selV
            aa=aa[aa.find(',')+1:]  #删除第1个值 
            lstV=aa.split(',')
            for pair in lstV:
                k,v=pair.split('=')
                dct[k]=v
        top.title('grid-'+propN)
        tk.Label(top,text=propN[:3]).grid(row=0,column=0,sticky='e',pady=(30,0),padx=(70,0))
        etr1=tk.Entry(top,)
        etr1.grid(row=0,column=1,pady=(30,0))
        if propN=='rowconfigure':etr1.insert(0,r)
        else:etr1.insert(0,col)
        etr1['state']='readonly'
        tk.Label(top,text='weight').grid(row=1,column=0,sticky='e') #窗口调整大小时如何分配额外的空间,weight
        etr2=tk.Entry(top,)
        etr2.grid(row=1,column=1)
        if dct.get('weight'):etr2.insert(0,dct['weight'])
        etr2.focus_set()
        tk.Label(top,text='minsize').grid(row=2,column=0,sticky='e') #指定行或者列的最小宽度,minsize
        etr3=tk.Entry(top,)
        etr3.grid(row=2,column=1)  #,font=('微软雅黑',11)
        if dct.get('minsize'):etr3.insert(0,dct['minsize'])
        tk.Label(top,text='pad').grid(row=3,column=0,sticky='e') #指定行或者列的内部填充,pad
        etr4=tk.Entry(top,)
        etr4.grid(row=3,column=1)  #,font=('微软雅黑',11)
        if dct.get('pad'):etr4.insert(0,dct['pad'])
        frm=tk.Frame(top,bd=0, highlightthickness=0)
        frm.grid(row=4,column=1)
        tk.Button(frm,text=cmm.t('确定'),width=6,height=1,command=lambda:rcRes(groupV,selV,etr1,etr2,etr3,etr4)).pack(side='left',padx=5,pady=3) 
        tk.Button(frm,text=cmm.t('清除设置'),width=10,height=1,command=lambda:closeW(1)).pack(side='left',padx=5,pady=3)   
        top.bind('<Return>',lambda e:rcRes(groupV,0,etr1,etr2,etr3,etr4)) 
    def rcRes(groupV=0,selV=0,etr1=0,etr2=0,etr3=0,etr4=0):  #确定
        aa=''
        tpl=('','weight','minsize','pad')
        for i,it in enumerate((etr1,etr2,etr3,etr3,etr4),1):
            bb=it.get().strip()
            if bb: aa=f'{aa}{tpl[i-1]}{"" if not(i-1) else "="}{bb},'
        if aa==selV:groupV.set('end')  #取消更改
        else:groupV.set(aa.strip(','))
        top.destroy()    
    def closeW(a=0):#这个函数在find_text内部定义的话，较为简单
        if a:groupV.set('clear')
        else:groupV.set('end')
        top.destroy() #然后再销毁窗口
    top.protocol('WM_DELETE_WINDOW', closeW)
    top.focus_set()
    top.wait_window()  #停止主窗口事件循环。等待模态窗口关闭


