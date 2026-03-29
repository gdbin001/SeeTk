from tkinter import  ttk,Text,font,messagebox
import tkinter as tk
import newPrj,time,hashlib,re,cmm,threading

class dragText(ttk.Frame):   #带滚动条的Text
    def __init__(self, **kw):
        super().__init__(cmm.rNB,**kw)               
        self.textNow = Text(self,undo=0,wrap='none',background='black',border=0,foreground='#eeeeee',font=(f"{cmm.fontN}",int(cmm.fontSz)),insertbackground='white')
        self.scbY = ttk.Scrollbar(self, orient="vertical", command=self.textNow.yview,cursor="arrow")
        self.scbX = ttk.Scrollbar(self, orient="horizontal", command=self.textNow.xview,cursor="arrow")
        self.textNow.configure(yscrollcommand=self.scbY.set, xscrollcommand=self.scbX.set) #set函数可以使滑块移动后固定在当前位置
        self.textNow.bind("<Return>",self.onReturn)   #回车后，自动缩进
        self.textNow.bind('<Button-3>',self.rightEdit)  #部分编辑功能。绑定右键点击事件
        self.textNow.bind('<Control-f>',lambda event:newPrj.findText()) #快捷键查找/替换
        self.textNow.bind('<Control-c>',lambda event:self.cCopy('复制'))  #复制功能
        self.textNow.bind('<Control-x>',lambda event:self.cCopy(cmm.t('剪切')))  #剪切功能
        self.textNow.bind('<Control-v>',lambda event:self.cPaste())  #粘贴功能
        self.textNow.bind('<Control-z>',lambda event:self.undo())  #撤销功能
        self.scbX.grid(row=1, column=0, sticky="ew") 
        self.scbY.grid(row=0, column=1, sticky="ns")
        self.textNow.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)    #第0行，按1缩放
        self.grid_columnconfigure(0, weight=1)  #第1列，按1缩放 
        self.undoStk=[]  # 撤销栈：存储每一步操作的反向操作（用于撤销）
        self.isUndoing=0  # 标记是否处于撤销状态（避免递归记录）
        #self.idx=0
        #----------语法高亮-------     
        self.createTags()   # 为每种语法元素定义标签  
        self.patt()   # 定义语法模式 
        self.textNow.bind('<KeyRelease>',self.keyRls)  #键盘键弹起（包括回车弹起）
        self._lineHash=[]  # 存储每行的哈希值 [[行索引,行内容hash],...]
        self._changeDt=1
        self.textNow.edit_modified(1)
        self.coloring=11  #0是停止上色 
        self.timerID=None  #上色定时器ID            
        self.textNow.tag_config('err',background='#bb0000')    #出错行高亮                
        #----------行号显示与代码折叠------   
        self.folded_blocks = {}  # 存储折叠状态：{内容起始行: 内容结束行}      
        self.textNow.bind('<KeyPress>',self.keyPrs)  #键盘键按下（包括鼠标键按下）
        self.textNow.bind("<1>", self.mousePrs)#鼠标左键按下绑定事件     
        self.textNow.bind("<ButtonRelease-1>", self.mouseRls)#鼠标左键弹起绑定事件                 
        self.textNow.tag_configure('readonly', background='#37474f',foreground='#eeeeee') #只读区背景色,不要换成bgc
        self.textNow.tag_configure("bgc", background='#37474f')#折叠标题行背景色,不要换成readonly                    
        self.textNow.tag_configure("elided", elide=True)# 关键：定义隐藏标签（elide=True 表示隐藏文本）
        self.textNow.tag_configure('foldCH',foreground='#ffee00')   #"⊞⊟"符号颜色。
        self.textNow.tag_bind('foldCH', "<Enter>",lambda e: self.textNow.config(cursor="hand2")) #"⊞"符号手柄
        self.textNow.tag_bind('foldCH', "<Leave>",lambda e: self.textNow.config(cursor="ibeam")) #离开标签后恢复编辑形状                      
        #搜索一遍，如果光标在readonly区，则要放到文本区
    def insert(self,ins,content):  #向textNow中加入文本，并设置=号颜色
        lst=[]
        for i,it in enumerate(content.split('\n'),1):  #每行前面加上5个字符
            it=(4-len(str(i)))*' '+str(i)+' '+it
            lst.append(it)
        content='\n'.join(lst)
        self.textNow.insert(ins,content) #放入内容          
        self.textNow.mark_set('insert','1.5')  #放置光标
        self.textNow.focus_set()  #文本框成为焦点光标才会闪烁
        for i in range(1,len(lst)+1):  #设置背景色
            self.textNow.tag_add('readonly',f'{i}.0',f'{i}.5')        
        self.auto_add_folding_symbols()  #代码折叠
        self.textNow.edit_reset()  #清空操作记录
        self.goColor()   #开始上色 
    def recON(self,opN,idx1,idx2=0,content=0):  #记录操作。Del要idx1,idx2。Ins要idx1,content
        if self.isUndoing==11: return 0
        if 'Del' in opN:  #删除
            delContent = self.textNow.get(idx1, idx2)  # 获取被删除的内容
            if opN[0].isdigit(): self.undoStk.append((f'{opN[0]}Ins', idx1, delContent)) #复合操作
            else: self.undoStk.append(('Ins', idx1, delContent))  #单纯操作  
        else:  #'Ins'，插入                        
            if opN[0].isdigit(): self.undoStk.append((f'{opN[0]}Del', idx1, f"{idx1}+{len(content)}c", content))           
            else: self.undoStk.append(('Del', idx1, f"{idx1}+{len(content)}c", content))  
    def undo(self):  #撤销功能
        if not self.undoStk: return 0
        self.isUndoing=11
        tpl = self.undoStk.pop()  # 取出最后一步操作的反向操作
        if tpl[0][0].isdigit(): lp=int(tpl[0][0])
        else: lp=1
        for i in range(lp):
            if 'Del' in tpl[0]:  # 反向操作是删除，对应原操作是插入
                self.textNow.delete(tpl[1], tpl[2])           
            else:  # 反向操作是'Ins'，对应原操作是删除
                self.textNow.insert(tpl[1], tpl[2])
            if lp>1 and i<lp-1: tpl = self.undoStk.pop()
        self.isUndoing =0
    def rightEdit(self,event):  #文本模式右键菜单
        popMenu=tk.Menu(self.textNow, tearoff=0)  # 创建一个弹出菜单.tearoff=0表示不显示可分离的菜单项        
        popMenu.add_command(label=cmm.t("剪切"), command=lambda: self.cCopy('cut'))
        popMenu.add_command(label=cmm.t("复制"), command=lambda: self.cCopy('copy'))
        #popMenu.add_command(label="粘贴", command=lambda: self.textNow.event_generate("<<Paste>>"))
        popMenu.add_command(label=cmm.t("粘贴"), command=lambda: self.cPaste())
        popMenu.post(event.x_root, event.y_root)  # 显示弹出菜单在右键点击的位置    
    def get(self):  #从textNow读取文本
        ct=self.textNow.get('0.0','end')  #文本内容从text控件中取出
        lst=ct.split('\n')
        for i,it in enumerate(lst):  #过滤掉每行前面5个字符 
            it=it[5:]
            lst[i]=it
        return '\n'.join(lst) 
    def cCopy(self,typeN):  #复制、剪切功能。在text控件中的复制要设置cmm.ctrlc
        wgt=cmm.root.focus_get()        
        if wgt:
            if 'dragtext' in wgt._w :  cmm.ctrlc=11  #在text控件中复制。wgt._w获取控件的名称字符串
            else: cmm.ctrlc=0  #在text控件外复制
        self.textNow.event_generate("<<Copy>>")
        if typeN=='cut': 
            tplSel=self.textNow.tag_ranges("sel")  #鼠标框选的区域
            self.recON('Del',tplSel[0],tplSel[1]) #记录操作 
            self.textNow.delete('sel.first', 'sel.last') 
    def cPaste(self):  #粘贴功能
        try:
            clipText =cmm.root.clipboard_get()  #获取剪贴板内容
        except tk.TclError:
            return ''
        tplSel=self.textNow.tag_ranges("sel")  #粘贴时，鼠标框选了区域
        if tplSel: #有框选,删除选中
            self.recON('Del',tplSel[0],tplSel[1]) #记录操作 
            self.textNow.delete('sel.first', 'sel.last') 
        if cmm.ctrlc!=11: clipText=clipText.replace('\n','\n     ')  #在text控件外复制，回车后面加5个空格
        if tplSel: self.recON('2Ins',tplSel[0],0,clipText) #有框选
        else: self.recON('Ins',self.textNow.index('insert'),0,clipText) #没有框选
        self.textNow.insert('insert', clipText)  #将处理后的内容插入到 Text 控件的光标位置
        self.textNow.edit_modified(1)
        self._changeDt=1
        return 'break'    
    def keyPrs(self, event):#键盘按键按下。(不响应鼠标)
        index=self.textNow.index('insert')  #当前光标位置
        col=int(index.split('.')[1])  #当前列数。退格键、删除键位置准
        row=int(index.split('.')[0])  #当前行数。退格键、删除键位置准  
        tplSel=self.textNow.tag_ranges("sel")  #鼠标框选的区域    
        if tplSel:  #有框选
            row0,col0=map(int,str(tplSel[0]).split('.'))  #鼠标框选的区域的一端
            row1,col1=map(int,str(tplSel[1]).split('.'))  #鼠标框选的区域的另一端       
        if event and event.keysym == 'BackSpace':  #退格键。col位置准
            if not tplSel:  #之前没有框选
                if col==5:  #在代码区行首
                    if index.split('.')[0]=='1': self.textNow.mark_set('insert','1.5')  #在代码区第1行首
                    else:  #在行首
                        bb=self.textNow.get(f"{row-1}.0",f"{row-1}.end") #上一行的内容
                        aa=self.textNow.get(index,f"{index.split('.')[0]}.end")   #光标后面的内容   
                        self.recON('Ins',self.textNow.index(f"{row-1}.end"),0,aa) #记录操作                     
                        self.textNow.insert(f"{row-1}.end",aa)  #内容上移一行到上一行的末尾                              
                        self.textNow.mark_set('insert',f"{row-1}.{len(bb)}")  #放置光标  
                        self.recON('2Del',f"{index.split('.')[0]}.0",f"{row+1}.0") #记录操作,2是做了Ins和Del的复合操作   
                        self.textNow.delete(f"{index.split('.')[0]}.0",f"{row+1}.0")#删除本行   
                else:  #在行中间
                    self.recON('Del',self.textNow.index(f"{index}-1c"),index) #记录操作 
                    self.textNow.delete(self.textNow.index(f"{index}-1c"),index)                  
            else:  #之前有框选
                self.recON('Del',tplSel[0],tplSel[1]) #记录操作 
                self.textNow.delete('sel.first', 'sel.last') 
            self.textNow.see('insert')
            return 'break'        
        elif event and event.keysym == 'Delete':  #del键。按住del键一直删除。col位置准
            if col>4 and not tplSel: #之前没有框选，而是按住del键一个个删除
                aa=self.textNow.get(index,f"{index.split('.')[0]}.end")  #光标后面的内容
                if aa: #在行中间删除
                    self.recON('Del',index,self.textNow.index(f"{index}+1c")) #记录操作 
                    self.textNow.delete(index,self.textNow.index(f"{index}+1c"))                    
                else:  #按住del键删除，在行末尾
                    bb=self.textNow.get(f"{row+1}.5",f"{row+1}.end") #下一行的代码区内容
                    self.recON('Ins',self.textNow.index(f"{row}.end"),0,bb) #记录操作
                    self.textNow.insert(f"{row}.end",bb)  #内容放到本行末尾
                    self.textNow.mark_set('insert',index)  #放置光标
                    self.recON('2Del',f"{row+1}.0",f"{row+2}.0") #记录操作 
                    self.textNow.delete(f"{row+1}.0",f"{row+2}.0")#删除下一行
            elif col>4:  #之前有框选
                self.recON('Del',tplSel[0],tplSel[1]) #记录操作 
                self.textNow.delete('sel.first', 'sel.last')
            return 'break'  #不能共享   
        if event and event.keysym =='Left':  #左方向键
            if row==1 and col<5: self.textNow.mark_set('insert',f"{row}.5")  #放本行代码区行首
            elif col<5 : self.textNow.mark_set('insert',f"{row-1}.end")  #放到上一行代码区列尾
        elif event and event.keysym =='Right':  #右方向键
            if col<5: self.textNow.mark_set('insert',f"{row}.5")  #放本行代码区行首 
        else:  #光标位置。col位置是上一次的            
            tagN=self.textNow.tag_names(index)
            if tagN and tagN[0]=='readonly': #在只读区
                self.textNow['insertwidth']=0
                return 'break'          # 禁止输入
            else:self.textNow['insertwidth']=2  #在代码区        
    def onReturn(self,event):  #按下回车键，再执行响应函数        
        tplSel=self.textNow.tag_ranges("sel")  #鼠标框选的区域 
        selDel=0  #有否选区删除操作                         
        if tplSel: #先删除鼠标框选的区域
            row0,col0=map(int,str(tplSel[0]).split('.'))  #鼠标框选的区域的一端
            row1,col1=map(int,str(tplSel[1]).split('.'))  #鼠标框选的区域的另一端
            self.recON('Del',tplSel[0],tplSel[1]) #记录操作 
            self.textNow.delete('sel.first', 'sel.last')  #删除框选的区域
            selDel=11
        index = self.textNow.index('insert')#点击。获取光标的位置 
        row=index.split('.')[0]  #行号
        aa=self.textNow.get(index,f"{row}.end")   #光标后面的内容
        preN=len(aa)+1
        if 'bgc' in self.textNow.tag_names(f"{row}.5") and not aa:#在已经折叠的标题行尾按下回车
            num=self.folded_blocks[int(row)]+1  #要插入行的行号（数值）
            aa=f'     \n'  #要插入的内容
        else:  #普通回车     
            num=int(row)+1  #要插入行的行号（数值）
            strLine=self.textNow.get(f"{row}.5",f"{row}.end")   #代码区整行内容，包括回车
            count=len(strLine)-len(strLine.lstrip(' '))  #计算回车之前的行开头有多少空格                    
            for st in ('if','while','for','else','elif','def'): #句子开头是否有这些命令
                if strLine.strip().startswith(st): 
                    aa=f"         {' '*count}{aa}\n"  #要插入的内容
                    break
            else:  aa=f"     {' '*count}{aa}\n"  #不是那些命令 
            self.recON('Del',index,self.textNow.index(f"{row}.end")) #记录操作            
            self.textNow.delete(index,f"{row}.end")  #删除光标后面的内容
        if selDel==11:self.recON('3Ins',f'{num}.5',0,aa)
        else:self.recON('2Ins',f'{num}.5',0,aa)
        self.textNow.insert(f'{num}.0',aa)  #insert操作会自动更新tag范围
        self.textNow.mark_set('insert',f'{num}.{len(aa)-preN}') 
        self.textNow.see('insert')
        return 'break'
    def updateDC(self,num,lastNum=0):#更新行号框,num是当前行数
        total=int(self.textNow.index('end-1c').split('.')[0]) #总行数
        if not lastNum:lastNum=total
        for i in range(num,lastNum+1):#从num到末尾更新行号
            aa=(4-len(str(i)))*' '+str(i)+' '
            self.textNow.replace(f'{i}.0',f'{i}.5',aa)
            self.textNow.tag_add('readonly',f'{i}.0',f'{i}.5')  #设置背景色tag   
    def threeD(self):  # 单独对三点字符串上色
        pat = re.compile(r'(\"\"\"|\'\'\').*?(\"\"\"|\'\'\')', re.S)
        for match in pat.finditer(self.textNow.get('1.0','end')):  # 单独对三点字符串上色            
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c" 
            for tag in self.colors: 
                if tag!='COMMENT' or tag!='readonly':self.textNow.tag_remove(tag,start_index,end_index)  # 删除所有标签名，除了注释 
            orgTag=self.textNow.tag_names(start_index)
            if orgTag and (orgTag[0]=='COMMENT' or orgTag[0]=='readonly'): continue #start_index处的tag是注释,转下一个  
            self.textNow.tag_add('LSTRING', start_index, end_index)#上色   
        lineCount=int(self.textNow.index('end-1c').split('.')[0]) #总行数
        for i in range(1,lineCount+1):  #移除字符串颜色   
            self.textNow.tag_remove('LSTRING',f'{i}.0',f'{i}.5')
    def createTags(self): # 为每种语法元素定义标签  
        self.colors = {      # 定义颜色方案   
            'COMMENT': '#bbe8c2',  # 注释#99c786#bbe8c2
            'KEYWORD': '#c695c6',  #关键字#ff7701
            'PRMN': '#ffc882', #参数名
            'INT&F':'#ffee00',   #小数和整数
            'OPR': '#ff7c1c',  #运算符
            'STRING': '#11dd11',  # 字符串
            'LSTRING': '#11dd11',  # 字符串
            'DEFINITION': '#68abdd',  #函数名
            'BUILTIN': '#88bbdd',    # 魔术方法、内置常量、特殊变量。匹配像 __init__, __str__, __name__ 这样的魔术方法
            'SPV':'#ff3333'  # 特殊变量
        }     
        for tag, color in self.colors.items():# 为每种语法元素创建标签
            self.textNow.tag_configure(tag, foreground=color)                
        self.textNow.tag_configure("sel", background="#d0d0d0")# 设置选择文本的背景颜色   
    def patt(self):  # 定义语法模式          
        self.patterns = (
            (r'#.*', 'COMMENT'),  # 注释
            (r'(\').*?(\')', 'STRING'),  # 字符串
            (r'(\").*?(\")', 'STRING'),  # 字符串
            (r'(\"\"\"|\'\'\').*?(\"\"\"|\'\'\')', 'LSTRING'),  # 字符串
            (r'\b(__\w+__|__\w+)\b', 'BUILTIN'),  # 魔术方法。匹配像 __init__, __str__, __name__ 这样的魔术方法
            (r'\b(None|True|False|Ellipsis|NotImplemented)\b', 'BUILTIN'),  # 内置常量
            (r'\b(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b', 'KEYWORD'),  # 关键字
            (r'\b(self|cls)\b', 'SPV'),  # 特殊变量                        
            (r'\b([A-Za-z_][A-Za-z0-9_]*)\b(?=\s*\()', 'DEFINITION'),  # 函数名
            (r'(?<=\() *(\w+) *(?==)','PRMN'),  #参数名
            #(r'^def\s+\w+\s*\(([^)]*)\)','PRMN'),  #参数名            
            (r'(?<!\w)\s*(\d+|\d+\.\d+)(?![a-zA-Z_])','INT&F'), #小数和整数
            (r'(/|\+|-|\*|%|\||<|>|!|&|\^|~|=)','OPR'),  #运算符规则。=号另外处理
            )                      
    def keyRls(self,event):  #设置高亮标志。按键弹起
        self.textNow.edit_modified(1)
        self._changeDt=1       
        #下面是对行号的操作------
        index=self.textNow.index('insert')  #当前光标位置
        col=int(index.split('.')[1])  #列数
        row=int(index.split('.')[0])  #行数
        if event and event.keysym =='Left':  #左方向键
            if row==1 and col<5: self.textNow.mark_set('insert',f"{row}.5")  #放本行代码区行首
            elif col<5 : self.textNow.mark_set('insert',f"{row-1}.end")  #放到上一行代码区列尾
        elif event and event.keysym =='Right':  #右方向键
            if col<5: self.textNow.mark_set('insert',f"{row}.5")  #放本行代码区行首 
        if event: cmm.filePath[cmm.rNB.index('current')][4]=1  #设置为已经编辑过
    def goColor(self):  #更新发生变化的行，设置控制标志
        if not self.coloring:  #停止上色
            try:                
                if self.timerID is not None:
                    self.after_cancel(self.timerID)
                    #print(f"关闭  {cmm.filePath[cmm.rNB.index('current')][0]}")
            except Exception as e:# 防止定时器已执行/被取消导致的异常            
                messagebox.showerror(cmm.t('错误'),cmm.t("取消上色定时器失败: {}").format(e))
            finally:
                self.timerID = None
                return 0
        try:
            #print(cmm.filePath[cmm.rNB.index('current')][0])
            #pageON=cmm.rNB.select()  #取得当前选中的页类名 
            #print(pageON)
            if self._changeDt and self.textNow.edit_modified() and self.textNow: #有变化,上色   
                self._updateCL()
                self.textNow.edit_modified(0)
                self._changeDt=0
        except:
            return 0
        self.timerID=self.after(20,self.goColor)  #20ms后再次运行
    def _updateCL(self):  #只更新发生变化的行
        changedL=[]
        lineCount=int(self.textNow.index('end-1c').split('.')[0]) #总行数
        for lineNum in range(1,lineCount+1):  #将行内容转化成hash值,然后进行比较
            stIdx=f'{lineNum}.5'  #行开始位置 
            endIdx=f'{lineNum}.5 lineend'  #行结束索引  
            content=self.textNow.get(stIdx,endIdx) #取得一行的内容
            contentHash=hashlib.md5(content.encode()).hexdigest() #行内容转化成hash
            for i,it in enumerate(self._lineHash):  #当前hash与_lineHash中的hash进行比较
                if it[0]==stIdx:  #找到此行索引
                    if it[1]!=contentHash: #其中的hash已经改变
                        changedL.append((stIdx,content))
                        self._lineHash[i][1]=contentHash  #更换hash
                        break
                    else:break
            else:  #无此行索引
                changedL.append((stIdx,content))  #记录改变行
                self._lineHash.append([stIdx,contentHash])   #添加进_lineHash
        for stIdx,content in changedL:   #更新发生变化的行         
            self.colorize(stIdx,content)
        self.threeD()  # 单独对三点字符串上色        
        if changedL:  #当行有变化时，更新行号框一次
            num=changedL[0][0].split('.')[0]  #起始行
            #lastNum=int(changedL[len(changedL)-1][0].split('.')[0])  #结束行
            if len(changedL)==1: #在一行中有变化。不更新行号
                if changedL[0][1].startswith(('class ', 'def ')) or changedL[0][1].startswith('    def') :  # 排除已有符号和缩进行                                
                    self.textNow.replace(f'{num}.4',f'{num}.5',"⊟")#行号列末尾添加 ⊟ 符号
                    self.textNow.tag_add('foldCH',f'{num}.4',f'{num}.5')  #添加前景色标签。包头不包尾   
                    self.textNow.tag_add('readonly',f'{num}.4',f'{num}.5')  #添加背景色标签。包头不包尾 
                #else:self.updateDC(int(num),int(num)) #更新一行                    
                return 0
            self.updateDC(1) #2行及以上有变化，要更新行号
            self.auto_add_folding_symbols()     
            for k in self.folded_blocks: self.textNow.tag_add("elided", f"{k+1}.0", f"{k+1}.end+1c") #重新添加elide,消除错误  
    def colorize(self,stIdx,code):  #上色
        endIdx = f"{stIdx} lineend"
        for tag in self.colors:# 移除所有现有的语法标签
            self.textNow.tag_remove(tag,stIdx,endIdx)        
        for pattern, tagN in self.patterns:# 应用模式
            for match in re.finditer(pattern,code):
                start_index = f"{stIdx}+{match.start()}c"
                end_index = f"{stIdx}+{match.end()}c" 
                orgTag=self.textNow.tag_names(start_index)
                if (orgTag and (orgTag[0]=='bgc' or orgTag[0]=='elided')) or not orgTag: #start_index位置处有bgc或者elided或者不存在tag,则添加tag
                    self.textNow.tag_add(tagN, start_index, end_index)# 加标签 
    def auto_add_folding_symbols(self):  #自动给顶格的类或函数添加折叠符号
        self.folded_blocks.clear()  #清空折叠记录
        content = self.textNow.get("1.0", "end-1c")
        for i,it in enumerate(content.split('\n'), 1): #在行号列中添加⊟，并更新折叠记录                         
            if 'bgc' in self.textNow.tag_names(f'{i}.5'):  self.folded_blocks[i]=self.find_code_block(i) #更新折叠记录
            if (it[5:].startswith(('class ', 'def ')) or it[5:].startswith('    def')) and not it[5:].startswith('\t') :  # 排除已有符号和缩进行                                
                self.textNow.replace(f'{i}.4',f'{i}.5',"⊟")#行号列末尾添加 ⊟ 符号
                self.textNow.tag_add('foldCH',f'{i}.4',f'{i}.5')  #添加前景色标签。包头不包尾   
                self.textNow.tag_add('readonly',f'{i}.4',f'{i}.5')  #添加背景色标签。包头不包尾  
        for k in self.folded_blocks:#已经折叠的标题行加背景色和换符号。查self.folded_blocks
            self.textNow.tag_add('bgc',f"{k}.5",f'{k}.end')  #给已经折叠的标题行加背景色
            self.update_symbol(k, "⊞")  # 更新符号为 ⊞（表示可展开）
    def mousePrs(self, event): #点击折叠号，更新折叠号（不响应键盘）
        index = self.textNow.index(f"@{event.x},{event.y}")  #点击的位置，行.列
        line_num = int(index.split('.')[0])  #点击的行号。标题行号(数值)
        line_content = self.textNow.get(index, f'{index}+1c')   #得到此字符内容
        if line_content=='⊞' or line_content== '⊟': #切换折叠状态
            if line_num in self.folded_blocks: self.unfold_code(line_num)  #展开代码
            else:  self.fold_code(line_num)  #折叠代码    
        self.textNow.tag_remove('err', '1.0', "end") #移除所有的出错标记效果
        tagN=self.textNow.tag_names(index)
        if tagN and tagN[0]=='readonly': #在只读区
            self.textNow['insertwidth']=0  #隐藏光标
            self.textNow.mark_set('insert',f"{index.split('.')[0]}.5")  #放置光标
            self.textNow['insertwidth']=2  #显示光标 
            return 'break' 
    def mouseRls(self,event):
        index = self.textNow.index(f"@{event.x},{event.y}")  #点击的位置，行.列
        tagN=self.textNow.tag_names(index)
        if tagN:
            for it in tagN: 
                if it=='readonly':#在只读区
                    self.textNow['insertwidth']=0  #隐藏光标
                    self.textNow.mark_set('insert',f"{index.split('.')[0]}.5")  #放置光标
                    self.textNow['insertwidth']=2  #显示光标 
                    return 'break'
    def find_code_block(self, start_line): #找到代码块范围（基于缩进）。返回结束行号。start_line是标题行号(数值)
        total_lines = int(self.textNow.index('end-1c').split('.')[0])  #全文行数
        current_line = start_line + 1  #内容开始行号(数值)
        end_line = start_line  #内容结束行号(数值)             
        base_indent = self.get_indent_level(start_line)# 获取标题行的缩进        
        while current_line <= total_lines:            
            line_content = self.textNow.get(f"{current_line}.5", f"{current_line}.end").strip()  #取出行内容
            if not line_content:# 跳过空行                
                end_line = current_line
                current_line += 1
                continue                        
            current_indent = self.get_indent_level(current_line)   # 计算当前行的缩进        
            if current_indent <= base_indent :break # 若缩进小于等于基础缩进，代码块结束
            end_line = current_line
            current_line += 1
        return  end_line
    def fold_code(self, start_line): #折叠代码（用elide标签隐藏内容）。start_line是点击的行号(数值)，标题行号(数值)
        end_line= self.find_code_block(start_line) #找到代码结束行号(数值)       
        if start_line== end_line:  return  # 没有可折叠的内容       
        self.textNow.tag_add('bgc',f"{start_line}.5",f'{start_line}.end')  #给已经折叠的标题行加背景色         
        for line in range(start_line+ 1, end_line+ 1): # 标记从start_line+1到end_line的内容为隐藏（添加elided标签）
            self.textNow.tag_add("elided", f"{line}.0", f"{line}.end+1c")  #给整行添加隐藏标签。+1c包含换行符 
        self.folded_blocks[start_line] = end_line  # 记录折叠范围              
        self.update_symbol(start_line, "⊞")  # 更新符号为 ⊞（表示可展开）
    def unfold_code(self, start_line):  #展开代码（移除elide标签）。start_line是标题行号(数值)
        if start_line not in self.folded_blocks: return  # 没有可折叠的内容      
        end_line_num = self.folded_blocks[start_line]  #(数值)        
        for line in range(start_line + 1, end_line_num + 1):# 移除隐藏标签，显示内容
            if '⊞'==self.textNow.get(f"{line}.4", f"{line}.5"): 
                self.update_symbol(line, "⊟")# 更新符号为 ⊟（表示可折叠）
                self.textNow.tag_remove('bgc',f"{line}.5",f'{line}.end')  #给已经折叠的标题行去除背景色
            self.textNow.tag_remove("elided", f"{line}.0", f"{line}.end+1c")  #+1c包含换行符              
        del self.folded_blocks[start_line]      # 删除折叠记录          
        self.textNow.tag_remove('bgc',f"{start_line}.5",f'{start_line}.end')  #给已经折叠的标题行去除背景色  
        self.update_symbol(start_line, "⊟")# 更新符号为 ⊟（表示可折叠）
    def get_indent_level(self, line_num): #获取行的缩进级别
        line_content = self.textNow.get(f"{line_num}.5", f"{line_num}.end") #获得行的内容    
        return len(line_content) - len(line_content.lstrip())    # 计算缩进（空格数）
    def update_symbol(self, line_num, new_symbol): #更新符号
        self.textNow.replace(f'{line_num}.4',f'{line_num}.5',new_symbol)#添加⊞或⊟号
        self.textNow.tag_add('foldCH',f'{line_num}.4',f'{line_num}.5')  #添加标签本身的颜色。包头不包尾
        self.textNow.tag_add('readonly',f'{line_num}.4',f'{line_num}.5')  #添加标签背景颜色。包头不包尾