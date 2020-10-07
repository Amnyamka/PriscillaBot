from tkinter import StringVar, ttk

from .canvas import CanvasMeta


class GraphMeta(CanvasMeta):
    '''Set some mouse event bindings to the keyboard.
    '''

    def __init__(self, master=None, cnf={}, **kw):
        '''The base class of all graphics frames.
        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)
        self._init_set()
        self.create_info_widgets()
        self.bind('<Motion>', self.update_xy)
        self.master.bind('<F1>', self.clear_all)
        self.master.bind('<Delete>', self.delete_selected)
        self.master.bind('<Control-a>', self.select_all_graph)
        self.master.bind('<Cancel>', self.cancel_selected)
        self.bind('<1>', self.select_current_graph)
        self.tag_bind('selected', '<ButtonRelease-1>', self.tune_selected)

    def _init_set(self):
        self.xy_var = StringVar()
        self.record_bbox = ['none']*4

    def create_info_widgets(self):
        self.info_frame = ttk.Frame(self.master)
        self.xy_label = ttk.Label(self.info_frame, textvariable=self.xy_var)

    def get_canvasxy(self, event):
        return self.canvasx(event.x), self.canvasy(event.y)

    def update_xy(self, event):
        self.record_bbox[2:] = self.get_canvasxy(event)
        self.xy_var.set(f"Direction Vector: {self.record_bbox}")

    @property
    def closest_graph_id(self):
        xy = self.record_bbox[2:]
        if xy:
            return self.find_closest(*xy)

    def start_drawing(self, event):
        self.record_bbox[:2] = self.get_canvasxy(event)
        self.xy_var.set(f"Direction Vector: {self.record_bbox}")

    def clear_all(self, event):
        self.delete('all')

    def delete_selected(self, event):
        self.delete('current')

    @property
    def current_graph_tags(self):
        return self.find_withtag('current')

    def set_select_mode(self, event):
        self.start_drawing(event)
        if self.current_graph_tags:
            self.configure(cursor="target")
        else:
            self.configure(cursor="arrow")

    def select_current_graph(self, event):
        self.set_select_mode(event)
        self.addtag_withtag('selected', 'current')

    def select_all_graph(self, event):
        self.set_select_mode(event)
        self.addtag_withtag('selected', 'all')

    @property
    def strides(self):
        record_bbox = self.record_bbox
        if 'none' not in record_bbox:
            x0, y0, x1, y1 = record_bbox
            return x1 - x0, y1 - y0

    def tune_selected(self, event=None):
        self.move('selected', *self.strides)
        self.cancel_selected(event)

    def layout(self, row=1, column=0):
        self.info_frame.grid(row=row, column=column)
        self.xy_label.grid(row=0, column=0)

    def cancel_selected(self, event):
        self.dtag('selected')
        self.configure(cursor="arrow")
