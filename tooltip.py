import tkinter as tk
import textwrap
import cmm 
def showTip(e,justify='left', width=None, background=None, foreground=None):
        if justify not in ('left', 'right', 'center'):
            raise ValueError("justify must be 'left', 'right', or 'center'")
        text=e.widget.winfo_name()
        if text==cmm.t('保存'): text=cmm.t('保存一个文件')
        #if text=='pythonV': text= cmm.t('本软件自带python 3.12版解释器，不用设置。使用其他版本的要设置')  #在设置解释器时显示
        if cmm.language=='English':
            for it in cmm.tplLang: 
                if text==it[0]: 
                    text=it[1]
                    break
        text = textwrap.fill(text, width) if width else text  #返回格式化后的字符串
        x, y, _, _ = e.widget.bbox("insert")
        x += e.widget.winfo_rootx() + 25
        y += e.widget.winfo_rooty() + 20
        tw = tk.Toplevel(e.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes('-topmost', True)
        cmm.tw=tw
        label_options = {
            "text": text,
            "relief": 'solid',
            "borderwidth": 1,
            "font": ("arial", "10", "normal"),
            "justify": justify
        }
        if background is not None:
            label_options["background"] = background
        if foreground is not None:
            label_options["foreground"] = foreground
        label = tk.Label(tw, **label_options)
        label.pack()
def closeTip(e):
    if cmm.tw:
        cmm.tw.destroy()
        cmm.tw = None

'''
class ToolTip(object):
    def __init__(self, widget, text='Widget info', justify='left', width=None, background=None, foreground=None):
        if justify not in ['left', 'right', 'center']:
            raise ValueError("justify must be 'left', 'right', or 'center'")
        self.widget = widget
        self.text = textwrap.fill(text, width) if width else text
        self.justify = justify
        self.background = background
        self.foreground = foreground
        self.tw = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)

    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        self.tw.attributes('-topmost', True)
        label_options = {
            "text": self.text,
            "relief": 'solid',
            "borderwidth": 1,
            "font": ("arial", "10", "normal"),
            "justify": self.justify
        }
        if self.background is not None:
            label_options["background"] = self.background
        if self.foreground is not None:
            label_options["foreground"] = self.foreground
        label = tk.Label(self.tw, **label_options)
        label.pack()

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None

'''