import copy
# 默认值, 属性类型
PROP_CONFIGURE = {
    "activebackground": {
        "Button": ("", "string",),
        "Checkbutton": ("", "string",),
        "Label": ("", "string",),
        "Radiobutton": ("", "string",),
        "Scale": ("", "string",),
        "Scrollbar": ("", "string",),
        "Spinbox": ("", "string",),
    },
    "activeforeground": {
        "Button": ("", "string",),
        "Checkbutton": ("", "string",),
        "Label": ("", "string",),
        "Radiobutton": ("", "string",),
    },
    "activerelief": {
        "Scrollbar": ("", "string",),
    },    
    "anchor": {
        "Button": ("", "string",),
        "Canvas": ("", "string",),
        "Checkbutton": ("", "string",),
        "Entry": ("", "string",),
        "Message": ("", "string",),
        "Radiobutton": ("", "string",),
        "Label": ("", "string",),
    },
    "aspect": {
        "Message": ('', "int",),
    },
    "autoseparators": {
        "Text": ('', "bool",),
    },
    "background": {
        "Button": ("", "string",),
        "Checkbutton": ("", "string",),
        "Canvas": ("", "string",),
        "Entry": ("", "string",),
        "Frame": ("", "string",),
        "Label": ("", "string",),
        "LabelFrame": ("", "string",),
        "Listbox": ("", "string",),
        "Message": ("", "string",),
        "PanedWindow": ("", "string",),
        "Radiobutton": ("", "string",),
        "Scale": ("", "string",),
        "Scrollbar": ("", "string",),
        "Spinbox": ("", "string",),
        "Text": ("", "string",),
        "Toplevel": ("", "string",),
    },
    "bigincrement": {
        "Scale": ('', "int",),
    },
    "borderwidth": {
        "Button": ('', "int",),
        "Canvas": ('', "int",),
        "Checkbutton": ('', "int",),
        "Entry": ('', "int",),
        "Frame": ('', "int",),
        "Label": ('', "int",),
        "LabelFrame": ('', "int",),
        "Listbox": ('', "int",),
        "Message": ('', "int",),
        "PanedWindow": ('', "int",),
        "Radiobutton": ('', "int",),
        "Scale": ('', "int",),
        "Scrollbar": ('', "int",),
        "Spinbox": ('', "int",),
        "Text": ('', "int",),
        "Toplevel": ('', "int",),
    },
    "buttonbackground": {
        "Spinbox": ("", "string",),
    },
    "buttoncursor": {
        "Spinbox": ("", "string",),
    },
    "buttondownrelief": {
        "Spinbox": ("", "string",),
    },
    "buttonuprelief": {
        "Spinbox": ("", "string",),
    },    
    "columns": {
        "Treeview": ("", "",),
    },
    "compound": {
        "Label": ("", "string",),
        "Button": ("", "string",),
        "Checkbutton": ("", "string",),
        "Radiobutton": ("", "string",),
    },
    "command": {
        "Button": ('', "",),
        "Checkbutton": ('', "",),
        "Radiobutton": ('', "",),
        "Scale": ('', "",),
        "Spinbox": ('', "",),
    },
    "confine": {
        "Canvas": ('', "bool",),
        "ScrollCanvas": ('', "bool",),
    },
    "cursor": {
        "Button": ("arrow", "string",),
        "Canvas": ("arrow", "string",),
        "Checkbutton": ("arrow", "string",),
        "Combobox": ("xterm", "string",),
        "Entry": ("xterm", "string",),
        "Frame": ("arrow", "string",),
        "Label": ("arrow", "string",),
        "LabelFrame": ("arrow", "string",),
        "Listbox": ("arrow", "string",),
        "Message": ("arrow", "string",),
        "PanedWindow": ("arrow", "string",),
        "Progressbar": ("arrow", "string",),
        "Radiobutton": ("arrow", "string",),
        "Scale": ("arrow", "string",),
        "Scrollbar": ("arrow", "string",),
        "Spinbox": ("arrow", "string",),
        "Text": ("xterm", "string",),
        "Toplevel": ("arrow", "string",),
        "Treeview": ("arrow", "string",),        
    },    
    "digits": {
        "Scale": ('', "int",),
    },
    "disabledforeground": {
        "Button": ("", "string",),
        "Checkbutton": ("", "string",),
        "Label": ("", "string",),
        "Radiobutton": ("", "string",),
        "Spinbox": ("", "string",),
    },
    "disabledbackground": {
        "Spinbox": ("", "string",),
    },
    "exportselection": {
        "Combobox": ('', "int",),
        "Entry": ('', "int",),
        "Listbox": ('', "int",),
        "Spinbox": ('', "int",),
        "Text": ('', "int",),
    },
    "elementborderwidth": {
        "Scrollbar": ('', "int",),
    },
    "font": {
        "Button": ("", "font",),
        "Checkbutton": ("", "font",),
        "Entry": ("", "font",),
        "Label": ("", "font",),
        "LabelFrame": ("", "font",),
        "Listbox": ("", "font",),
        "Message": ("", "font",),
        "Radiobutton": ("", "font",),
        "Scale": ("", "font",),
        "Spinbox": ("", "font",),
        "Text": ("", "font",),
        "Combobox": ("", "font",),
    },
    "font_anchor": {
        "Button": ("", "string",),
        "Checkbutton": ("", "string",),
        "Label": ("", "string",),
        "Radiobutton": ("", "string",),
    },
    "foreground": {
        "Button": ("", "string",),
        "Checkbutton": ("", "string",),
        "Combobox": ("", "string",),
        "Entry": ("", "string",),
        "Label": ("", "string",),
        "LabelFrame": ("", "string",),
        "Listbox": ("", "string",),
        "Message": ("", "string",),
        "Radiobutton": ("", "string",),
        "Scale": ("", "string",),
        "Spinbox": ("", "string",),
        "Text": ("", "string",),
    },
    "handlepad": {
        "PanedWindow": ('', "int",),
    },
    "handlesize": {
        "PanedWindow": ('', "int",),
    },   
    "highlightbackground": {
        "Button": ("", "string",),
        "Canvas": ("", "string",),
        "Checkbutton": ("", "string",),
        "Entry": ("", "string",),
        "Frame": ("", "string",),
        "Label": ("", "string",),
        "LabelFrame": ("", "string",),
        "Listbox": ("", "string",),
        "Message": ("", "string",),
        "Radiobutton": ("", "string",),
        "Scale": ("", "string",),
        "Scrollbar": ("", "string",),
        "Spinbox": ("", "string",),
        "Text": ("", "string",),
        "Toplevel": ("", "string",),
    },
    "highlightcolor": {
        "Button": ("", "string",),
        "Canvas": ("", "string",),
        "Checkbutton": ("", "string",),
        "Entry": ("", "string",),
        "Frame": ("", "string",),
        "Label": ("", "string",),
        "LabelFrame": ("", "string",),
        "Listbox": ("", "string",),
        "Message": ("", "string",),
        "Radiobutton": ("", "string",),
        "Scale": ("", "string",),
        "Scrollbar": ("", "string",),
        "Spinbox": ("", "string",),
        "Text": ("", "string",),
        "Toplevel": ("", "string",),
    },
    "highlightthickness": {
        "Button": ('', "int",),
        "Canvas": ('', "int",),
        "Checkbutton": ('', "int",),
        "Entry": ('', "int",),
        "Frame": ('', "int",),
        "Label": ('', "int",),
        "LabelFrame": ('', "int",),
        "Listbox": ('', "int",),
        "Message": ('', "int",),
        "Radiobutton": ('', "int",),
        "Scale": ('', "int",),
        "Scrollbar": ('', "int",),
        "Spinbox": ('', "int",),
        "Text": ('', "int",),
        "Toplevel": ('', "int",),
    },
    "image": {
        "Button": ("", "",),
        "Checkbutton": ("", "",),
        "Label": ("", "",),
        "Radiobutton": ("", "",),
    },
    "increment": {
        "Spinbox": ('', "float",),
    },
    "indicatoron": {
        "Checkbutton": ('', "bool",),
        "Radiobutton": ('', "bool",),
    },
    "insertbackground": {
        "Canvas": ("", "string",),
        "Entry": ("", "string",),
        "Spinbox": ("", "string",),
        "Text": ("", "string",),
    },
    "insertborderwidth": {
        "Canvas": ('', "int",),
        "Entry": ('', "int",),
        "Spinbox": ('', "int",),
        "Text": ('', "int",),
    },
    "insertofftime": {
        "Canvas": ('', "int",),
        "Entry": ('', "int",),
        "Spinbox": ('', "int",),
        "Text": ('', "int",),
    },
    "insertontime": {
        "Canvas": ('', "int",),
        "Entry": ('', "int",),
        "Spinbox": ('', "int",),
        "Text": ('', "int",),
    },
    "insertwidth": {
        "Canvas": ('', "int",),
        "Entry": ('', "int",),
        "Text": ('', "int",),
        "Spinbox": ('', "int",),
    },    
    "justify": {
        "Button": ("", "string",),
        "Checkbutton": ("", "string",),
        "Combobox": ("", "string",),
        "Entry": ("", "string",),
        "Label": ("", "string",),
        "Message": ("", "string",),
        "Radiobutton": ("", "string",),
        "Spinbox": ("", "string",),
    },
    "jump": {
        "Scrollbar": ('', "bool",),
    },
    "label": {
        "Scale": ("", "string",),
    },
    "labelanchor": {
        "LabelFrame": ("", "string",),
    },
    "length": {
        "Progressbar": ('', "int",),
        "Scale": ('', "int",),
    },
    "maxundo": {
        "Text": ('', "int",),
    },
    "maximum": {
        "Progressbar": ('', "int"),
    },
    "mode": {
        "Progressbar": ("", "string"),
    },

    "offvalue": {
        "Checkbutton": ('', "int",),
    },
    "onvalue": {
        "Checkbutton": ('', "int",),
    },
    "opaqueresize": {
        "PanedWindow": ('', "bool",),
    },
    "orient": {
        "PanedWindow": ("", "string",),
        "Progressbar": ("", "string",),
        "Scale": ("", "string",),
        "Scrollbar": ("", "string",),
        "Separator": ("", "string",),
    },
    "padx": {
        "Button": ('', "int",),
        "Checkbutton": ('', "int",),
        "Label": ('', "int",),
        "LabelFrame": ('', "int",),
        "Message": ('', "int",),
        "Radiobutton": ('', "int",),
        "Text": ('', "int",),
    },
    "pady": {
        "Button": ('', "int",),
        "Checkbutton": ('', "int",),
        "Label": ('', "int",),
        "LabelFrame": ('', "int",),
        "Message": ('', "int",),
        "Radiobutton": ('', "int",),
        "Text": ('', "int",),
    },
    "readonlybackground": {
        "Spinbox": ("", "string",),
    },
    "relief": {
        "Button": ("", "string",),
        "Canvas": ("", "string",),
        "Checkbutton": ("", "string",),
        "Entry": ("", "string",),
        "Frame": ("", "string",),
        "Label": ("", "string",),
        "LabelFrame": ("groove", "string",),
        "Listbox": ("", "string",),
        "Message": ("", "string",),
        "PanedWindow": ("", "string",),
        "Radiobutton": ("", "string",),
        "Scale": ("", "string",),
        "Scrollbar": ("", "string",),
        "Spinbox": ("", "string",),
        "Text": ("", "string",),
        "Toplevel": ("", "string",),
    },
    "repeatdelay": {
        "Button": ('', "int",),
        "Scale": ('', "int",),
        "Scrollbar": ('', "int",),
        "Spinbox": ('', "int",),
    },
    "repeatinterval": {
        "Button": ('', "int",),
        "Scale": ('', "int",),
        "Scrollbar": ('', "int",),
        "Spinbox": ('', "int",),
    },
    "resolution": {
        "Scale": ('', "float",),
    },
    "sashcursor": {
        "PanedWindow": ("", "string",),
    },
    "sashpad": {
        "PanedWindow": ('', "int",),
    },
    "sashrelief": {
        "PanedWindow": ("", "string",),
    },
    "sashwidth": {
        "PanedWindow": ('', "int",),
    },
    "showhandle": {
        "PanedWindow": ('', "bool",),
    },
    "showvalue": {
        "Scale": ('', "bool",),
    },
    "sliderlength": {
        "Scale": ('', "int",),
    },
    "sliderrelief": {
        "Scale": ("", "string",),
    },
    "state": {
        "Button": ("", "string",),
        "Canvas": ("", "string",),
        "Checkbutton": ("", "string",),
        "Combobox": ("", "string",),
        "Entry": ("", "string",),
        "Label": ("", "string",),
        "Listbox": ("", "string",),
        "Radiobutton": ("", "string",),
        "Scale": ("", "string",),
        "Spinbox": ("", "string",),
        "Text": ("", "string",),
        "Treeview": ("", "string",),
    },
    "selectbackground": {
        "Canvas": ("", "string",),
        "Entry": ("", "string",),
        "Listbox": ("", "string",),
        "Spinbox": ("", "string",),
        "Text": ("", "string",),
    },
    "selectborderwidth": {
        "Canvas": ('', "int",),
        "Entry": ('', "int",),
        "Listbox": ('', "int",),
        "Spinbox": ('', "int",),
        "Text": ('', "int",),
    },
    "selectcolor": {
        "Checkbutton": ("", "string",),
        "Radiobutton": ("", "string",),
    },
    "selectforeground": {
        "Canvas": ("", "string",),
        "Entry": ("", "string",),
        "Listbox": ("", "string",),
        "Spinbox": ("", "string",),
        "Text": ("", "string",),
    },
    "selectmode": {
        "Listbox": ("", "string",),
        "Treeview": ("", "string",),
    },
    "show": {
        "Treeview": ("", "string",),
    },
    "spacing1": {
        "Text": ('', "int",),
    },
    "spacing2": {
        "Text": ('', "int",),
    },
    "spacing3": {
        "Text": ('', "int",),
    },
    "takefocus": {
        "Button": ('', "bool",),
        "Canvas": ('', "bool",),
        "Checkbutton": ('', "bool",),
        "Combobox": ('', "bool",),
        "Entry": ('', "bool",),
        "Frame": ('', "bool",),
        "Label": ('', "bool",),
        "LabelFrame": ('', "bool",),
        "Listbox": ('', "bool",),
        "Progressbar": ('', "bool",),
        "Radiobutton": ('', "bool",),
        "Scale": ('', "bool",),
        "Scrollbar": ('', "bool",),
        "Separator": ('', "bool",),
        "Spinbox": ('', "bool",),
        "Text": ('', "bool",),
        "Treeview": ('', "bool",),
    },
    "tickinterval": {
        "Scale": ('', "int",),
    },
    "to": {
    },
    "troughcolor": {
        "Scale": ("", "string",),
        "Scrollbar": ("", "string",),
    },
    "undo": {
        "Text": ('', "bool",),
    },
    "value": {
        "Progressbar": ('', "int"),
    },
    "values": {
        "Combobox": ("", "string",),
    },
    
    "wrap": {
        "Text": ("char", "string",),
    },
    "wrapspinbox": {
        "Spinbox": ('', "bool",),
    },
    "wraplength": {
        "Button": ('', "int",),
        "Checkbutton": ('', "int",),
        "Label": ('', "int",),
        "Radiobutton": ('', "int",),
    },
    'xscrollincrement':{
        "Canvas": ('', "",),
    },
    'yscrollincrement':{
        "Canvas": ('', "",),
    },    
}  #xscrollincrement设置水平滚动条的步长
PROP_FIRST={    
    "text": {
        "Button": ("Button", "string",),
        "Checkbutton": ("", "string",),
        "Label": ("", "string",),
        "LabelFrame": ("", "string"),
        "Message": ("", "string",),
        "Radiobutton": ("", "string",),
    },
}
dctGrid={'grid':{'row':['','int'],'column':['','int'],'columnspan':['','int'],'rowspan':['','int'],
          'sticky':['nesw','string'],'padx':['2',''],'pady':['2',''],'ipadx':['10','int'],'ipady':['10','int']}}
dctPack={'pack':{'anchor':['','string'],'side':['','string'],'fill':['','string'],'expand':['','bool'],
        'padx':['2',''],'pady':['2',''],'ipadx':['10','int'],'ipady':['10','int']}}
def getBase(component_type,typeL,clr=0):  #取得全部基础属性
    if typeL=='place':  #place
        property_dict = {'parent':['root',''],'text':['','string'],'x':['','int'],'y':['','int'],'width':['','int'],'height':['','int']}
    elif typeL=='pack':
        property_dict = {**copy.deepcopy(dctPack),**{'parent':['root',''],'text':['','string']}}#deepcopy防止指向同一个引用
    else:   #grid
        property_dict = {**copy.deepcopy(dctGrid),**{'parent':['root',''],'text':['','string']}}  
    if clr and (typeL=='pack' or typeL=='grid'):  #清空预设值
        for v in property_dict[typeL].values(): v[0]=''
    for k,v in PROP_FIRST.items():  #是否删除text属性
        if component_type in v:break
    else:del  property_dict['text']
    return property_dict
def getOne(classN,propN,typeL):  #取得一个属性空值及类型（基础属性以外）
    if propN=='width' or propN=='height':#基础属性中已经有width和height
        if typeL=='grid' :
            if classN in ('Combobox',"Entry",'Progressbar','Scale','Scrollbar','Separator','Spinbox','Treeview'):
                if propN=='width':return ['','int']
            elif classN in ('Treeview','Progressbar','Separator'):
                if propN=='height':return ['','int']
            else:  return ['','int']
        else:  #pack布局
            if classN in ("Entry",'Scale','Scrollbar','Spinbox'): #只有width
                if propN=='width':return ['','int']
            elif classN in ('Treeview','Progressbar','Separator'):return 0  #全无
            else:  return ['','int']  #width和height都有
    else: #基础属性中,其他属性
        for k,v in PROP_CONFIGURE[propN].items():
            if k==classN: return list(v)  #元组转换成列表是生成新的列表，每个控件的属性都不会指向同一个引用，从而避免了不同控件相同值的问题
    return 0
def getOther(classN,typeL):  #取得其余属性        
    property_dict={}
    for k,v in PROP_CONFIGURE.items():
        if classN in v:property_dict[k] = list(v[classN])    
    for k,v in PROP_FIRST.items():
        if classN in v:property_dict[k] = list(v[classN])
    if typeL=='grid':
        if classN in ('Combobox',"Entry",'Progressbar','Scale','Scrollbar','Separator','Spinbox','Treeview'):
            property_dict['width']=['','int']
        elif classN in ('Progressbar','Separator','Treeview',):
            property_dict['height']=['','int']
        else:  property_dict.update({'width':['','int'],'height':['','int']})
    elif typeL=='pack':
        if classN in ("Entry",'Scale','Scrollbar','Spinbox'): #只有width
            property_dict['width']=['','int']
        elif classN in ('Treeview','Progressbar','Separator'):return property_dict  #全无
        else:  property_dict.update({'width':['','int'],'height':['','int']})  #width和height都有
    return property_dict







