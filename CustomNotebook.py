import tkinter as tk
from tkinter import ttk,messagebox 
import menuBar
import cmm 
 
class CustomNotebook(ttk.Notebook):
    __initialized = False
    def __init__(self, *abc, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__initialized = True
        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, abc[0], **kwargs)
        self._active = None
        self.orgObj=None  #按下时的对象
        self.orgFN=0
        self.bind("<Button-1>", self.on_press, True) # 按下鼠标
        self.bind("<ButtonRelease-1>", self.on_close_release) # 松开鼠标 
        self.bind('<B1-Motion>',self.onMotion)  #按着鼠标移动
    def onMotion(self, event):#当按着鼠标移动调用
        cmm.root.configure(cursor='dotbox')
    def on_press(self, event):#当按下标签时调用  
        element = self.identify(event.x, event.y)        
        try:
            self._active = self.index("@%d,%d" % (event.x, event.y))
        except :
            return  0       
        if "close" in element:  #按下了X  
            self.state(['pressed'])  #设置状态为按下    
        self._active = self.index(f"@{event.x},{event.y}")  #按下时选中的index     
        pageON=cmm.rNB.tabs()[self._active]   #按下时选中的
        pageKey=pageON[pageON.rfind('!'):]  #按下时选中的
        self.orgObj=cmm.rNB.children[pageKey]  #按下时选中的
        self.orgFN=cmm.rNB.tab(pageON, "text")  #取得当前选中的标签上的文件名 
    def on_close_release(self, event):#弹起判断 
        cmm.root.configure(cursor="arrow")  #恢复箭头鼠标
        try:
            index = self.index(f"@{event.x},{event.y}")  #弹起时选中的index
        except :
            return  0
        pageON=cmm.rNB.tabs()[index]   #弹起时选中的
        pageKey=pageON[pageON.rfind('!'):]  #弹起时选中的   
        if index ==self._active: #在相同标签             
            if not self.instate(['pressed']): return 0  #没有按下X，退出                               
            elif cmm.filePath[index][4]:  #内容编辑过 
                res=messagebox.askyesnocancel(cmm.t('确认'),cmm.t('要保存文件吗？'))
                if res==True: menuBar.保存(pageON,pageKey,index)  #保存文件                               
                elif res==None:return 0 #取消，不关闭页 
            if 'text' in pageON: #是文本模式 
                cmm.rNB.children[pageKey].coloring=0 #退出goColor定时器
            del cmm.filePath[index]  #删除cmm记录
            for i in cmm.table.get_children(): cmm.table.delete(i) #清空属性表         
            self.forget(index)       
            cmm.rNB.children[pageKey].destroy() #销毁标签页容器及内部所有控件,释放内存
            self.state(["!pressed"])  #设置状态为未按下                                     
        else:  #选择了不同标签  
            if not (0 <= index < self.index("end")):
                messagebox.showerror(cmm.t('错误'),cmm.t("索引{}超出范围").format(index))
                return 0
            cmm.rNB.insert(index,self.orgObj,text=self.orgFN)  
            cmm.filePath.insert(index,cmm.filePath.pop(self._active))      
        self._active = None 
    def __initialize_custom_style(self):
        style = ttk.Style()
        style.configure('CustomNotebook',borderwidth=0,background="#a0a0a0")  #background='#cce8cf'
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        ) 
        style.element_create("close", "image", "img_close",
                            ("active", "pressed", "!disabled", "img_closepressed"),
                            ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        #style.configure('Closable.TNotebook', tabmargins=[0,0,0,0], relief='flat')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe", 
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top", 
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top", 
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]       })     ]       })     ]     })    ])
        style.configure('CustomNotebook.Tab', background="#a0a0a0", padding=[8, 2, 2, 2], borderwidth=1)
        style.map("CustomNotebook.Tab", 
              background=[
                  ("selected", "lightgrey"),       # 选中的Tab背景色（你的原有设置）
                  ("active", "!selected", "#6c6c6c")# 鼠标悬浮、未选中 → 整个Tab背景变暗灰色
              ],
              foreground=[                         # 可选：文字颜色同步适配，增强对比度
                  ("selected", "#000000"),
                  ("active", "!selected", "#ffffff")
              ])
