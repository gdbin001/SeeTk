#from enum import IntEnum
#import tkinter.font as tkFont
#from tkinter import Entry, END, Label, Button
#from tkinter.ttk import Combobox
#from tkinter import colorchooser
#from tkinter.filedialog import askopenfilename

#from ScrollRows import ScrollRows
#from ScrollCols import ScrollCols
#from WidgetRedirector import WidgetRedirector
#from componentProperty import update_all_property, get_default_component_info, get_all_prop_name

CURSOR_LIST = (
    "arrow;based_arrow_down;based_arrow_up;boat;bogosity;bottom_left_corner;bottom_right_corner;"
    "bottom_side;bottom_tee;box_spiral;center_ptr;circle;clock;coffee_mug;cross;cross_reverse;crosshair;"
    "diamond_cross;dot;dotbox;double_arrow;draft_large;draft_small;draped_box;exchange;fleur;gobbler;gumby;"
    "hand1;hand2;heart;icon;iron_cross;left_ptr;left_side;left_tee;leftbutton;ll_angle;lr_angle;man;"
    "middlebutton;mouse;none;pencil;pirate;plus;question_arrow;right_ptr;right_side;right_tee;rightbutton;"
    "rtl_logo;sailboat;sb_down_arrow;sb_h_double_arrow;sb_left_arrow;sb_right_arrow;sb_up_arrow;"
    "sb_v_double_arrow;shuttle;sizing;spider;spraycan;star;target;tcross;top_left_arrow;top_left_corner;"
    "top_right_corner;top_side;top_tee;trek;ul_angle;umbrella;ur_angle;watch;xterm;X_cursor"
)
PROP_TO_VALUES = {
    "cursor":("arrow;based_arrow_down;based_arrow_up;boat;bogosity;bottom_left_corner;bottom_right_corner;"
    "bottom_side;bottom_tee;box_spiral;center_ptr;circle;clock;coffee_mug;cross;cross_reverse;crosshair;"
    "diamond_cross;dot;dotbox;double_arrow;draft_large;draft_small;draped_box;exchange;fleur;gobbler;gumby;"
    "hand1;hand2;heart;icon;iron_cross;left_ptr;left_side;left_tee;leftbutton;ll_angle;lr_angle;man;"
    "middlebutton;mouse;none;pencil;pirate;plus;question_arrow;right_ptr;right_side;right_tee;rightbutton;"
    "rtl_logo;sailboat;sb_down_arrow;sb_h_double_arrow;sb_left_arrow;sb_right_arrow;sb_up_arrow;"
    "sb_v_double_arrow;shuttle;sizing;spider;spraycan;star;target;tcross;top_left_arrow;top_left_corner;"
    "top_right_corner;top_side;top_tee;trek;ul_angle;umbrella;ur_angle;watch;xterm;X_cursor"),
    "anchor": (";n;s;w;e;nw;sw;ne;se;we;ns;center"),
    "font_anchor": (";n;s;w;e;nw;sw;ne;se;we;ns;center"),
    "labelanchor": (";n;s;w;e;nw;sw;ne;we;ns;se"),
    "justify": (";left;right;center"),
    "side": (";top;left;right;bottom"),
    "fill": (";y;x;both;none"),
    "expand": (";0;1"), 
    "undo": (";0;1"),   
    "relief": (";flat;groove;raised;ridge;solid;sunken"),
    "activerelief": (";flat;groove;raised;ridge;solid;sunken"),
    "sliderrelief": (";flat;groove;raised;ridge;solid;sunken"),
    "buttondownrelief": (";flat;groove;raised;ridge;solid;sunken"),
    "buttonuprelief": (";flat;groove;raised;ridge;solid;sunken"),
    "mode": (";determinate;indeterminate"),
    "state": (";active;disabled;normal;readonly"),
    "compound": (";bottom;center;left;none;right;top"),
    "exportselection": (";0;1"),
    "selectmode": (";browse;multiple;single;extended;none"),
    "is_show_scroll": (";0;1"),
    "is_show_scroll_x": (";0;1"),
    "is_show_scroll_y": (";0;1"),
    "is_always_show_scroll": (";0;1"),
    "orient": (";horizontal;vertical"),
    "wrap": (";none;char;word"),
    "show": (";headings;tree;tree headings"),
    'takefocus':('1;0;"";none'),
}  #下拉列表用的
PROP_COLOR_LIST = (
    "background", "activebackground", "activeforeground", "disabledforeground", "readonlybackground",
    "foreground", "highlightbackground", "highlightcolor", "insertbackground", "disabledbackground",
    "selectbackground", "selectforeground", "troughcolor", "selectcolor", "buttonbackground"
)  #颜色框用的
PROP_SELECT_LIST = (
    "bitmap", "image"
)

def btn_color_click():
        color = colorchooser.askcolor()
        if color[0] is none:
            return
        self.delete(0, END)
        self.insert(0, color[1])
def btn_select_click():
        file_path = askopenfilename(title="选择文件", filetypes=[("all files", "*")])
        if not file_path:
            return
        self.delete(0, END)
        self.insert(0, file_path)


