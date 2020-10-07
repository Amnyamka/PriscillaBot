from tkinter import ttk, Tk, StringVar, filedialog
from PIL import Image, ImageTk
from pathlib import Path

from .graph.canvas_design import SelectorFrame
from .graph.canvas import Drawing, CanvasMeta
from .utils import save_bunch, load_bunch, mkdir, FileFrame, FileNotebook
from .image_utils import ImageLoader


class GraphWindow(Tk):
    def __init__(self, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.reset()
        self.selector_frame = SelectorFrame(self, 'rectangle', 'blue')
        self.drawing = Drawing(self, self.selector_frame,
                               width=800, height=600, background='lightgray')
        self.create_notebook()
        self.tip_var = StringVar(self)
        self.tip_label = ttk.Label(self, textvariable=self.tip_var,
                                   foreground='blue', background='yellow')
        self.tip_var.set("Start your creation!")
        self.bind('<Motion>', self.update_info)
        self.bind_move()

    def reset(self):
        self.bunch = {}
        self.image_names = ()
        self._image_loader = None

    def update_info(self, *args):
        if not self.drawing.on:
            self.drawing.update_xy(*args)
        xy = self.drawing.x, self.drawing.y
        self.tip_var.set(xy)

    def bind_move(self):
        self.bind('<Up>', lambda event: self.move_graph(event, 0, -1))
        self.bind('<Down>', lambda event: self.move_graph(event, 0, 1))
        self.bind('<Left>', lambda event: self.move_graph(event, -1, 0))
        self.bind('<Right>', lambda event: self.move_graph(event, 1, 0))
        self.bind('<F1>', self.clear_graph)
        self.bind('<F2>', self.fill_normal)
        self.bind('<Delete>', self.delete_graph)

    def find_closest(self):
        xy = self.drawing.x, self.drawing.y
        graph_id = self.drawing.find_closest(*xy)
        return graph_id

    def find_closest_not_image(self):
        graph_id = self.drawing.find_above('image')

    def find_closest(self):
        xy = self.drawing.x, self.drawing.y
        graph_id = self.drawing.find_closest(*xy)
        return graph_id

    def delete_graph(self, *args):
        graph_id = self.find_closest()
        self.drawing.delete(graph_id)

    def clear_graph(self, *args):
        self.drawing.delete('all')

    def move_graph(self, event, x, y):
        graph_id = self.find_closest()
        self.drawing.move(graph_id, x, y)

    def create_notebook(self):
        self.notebook = ttk.Notebook(
            self.selector_frame, width=200, height=200, padding=(5, 5, 5, 5))
        # first page, which would get widgets gridded into it
        self.normal = ttk.Frame(self.notebook, width=200,
                                height=200, padding=(5, 5, 5, 5))
        self.save_normal_button = ttk.Button(
            self.normal, text='Save', command=lambda: self.save_graph('all'))
        self.load_normal_button = ttk.Button(
            self.normal, text='Load', command=self.load_normal)
        self.annotation = ttk.Frame(
            self.notebook, width=200, height=200, padding=(5, 5, 5, 5))
        self.image_frame = FileFrame(
            self.annotation, text='images', padding=(5, 5, 5, 5))
        self.next_image_button = ttk.Button(self.image_frame, text='Next')
        self.prev_image_button = ttk.Button(self.image_frame, text='Prev')
        self.annotation_frame = FileFrame(
            self.annotation, text='annotations', padding=(5, 5, 5, 5))
        self.notebook.add(self.annotation, text='Annotation')
        self.notebook.add(self.normal, text='Normal')
        self.init_command()

    def init_command(self):
        self.image_frame.load_button['command'] = self.load_images
        self.next_image_button['command'] = self.next_image
        self.prev_image_button['command'] = self.prev_image
        self.annotation_frame.save_button['command'] = lambda: self.save_graph(
            'rectangle')
        self.annotation_frame.load_button['command'] = self.load_graph

    def next_image(self):
        self.drawing.delete('image')
        self.image_loader.current_id += 1
        self.image_loader.create_image(self.drawing, 0, 0, anchor='nw')

    def prev_image(self):
        self.drawing.delete('image')
        self.image_loader.current_id -= 1
        self.image_loader.create_image(self.drawing, 0, 0, anchor='nw')

    def get_graph(self, tags):
        cats = {}
        for graph_id in self.drawing.find_withtag(tags):
            tags = self.drawing.gettags(graph_id)
            bbox = self.drawing.bbox(graph_id)
            cats[graph_id] = {'tags': tags, 'bbox': bbox}
        return cats

    def set_path(self, tags):
        if tags == 'all':
            return 'data/normal.json'
        else:
            return 'data/annotations.json'

    def save_graph(self, tags):
        graph = self.get_graph(tags)
        mkdir('data')
        path = self.set_path(tags)
        if self.image_loader:
            current_image_path = self.image_loader.current_path
            if current_image_path:
                self.bunch.update({self.image_loader.current_name: graph})
                save_bunch(self.bunch, path)
        else:
            save_bunch(graph, path)

    def load_graph(self):
        self.bunch = load_bunch('data/annotations.json')
        root = self.bunch['root']
        self.image_loader = ImageLoader(root)
        self.image_names = [
            f"{root}/{image_name}" for image_name in self.bunch if image_name != root]
        self.image_loader.current_id = 0
        self.create_image(root)
        self.draw_graph(self.bunch[self.image_loader.current_name])

    def draw_graph(self, cats):
        params = self.bunch2params(cats)
        self.clear_graph()
        for param in params.values():
            self.drawing.draw_graph(**param)

    @property
    def image_loader(self):
        return self._image_loader

    @image_loader.setter
    def image_loader(self, new):
        self._image_loader = new

    def bunch2params(self, bunch):
        params = {}
        for graph_id, cats in bunch.items():
            tags = cats['tags']
            color, shape = tags
            graph_type = shape.split('_')[0]
            bbox = cats['bbox']
            params[graph_id] = {'tags': tags, 'color': color,
                                'graph_type': graph_type, 'direction': bbox}
        return params

    def load_normal(self):
        self.bunch = load_bunch('data/normal.json')
        self.draw_graph(self.bunch)

    def fill_normal(self, *args):
        graph_id = self.find_closest()
        color = self.drawing.selector_frame._selector.color
        self.drawing.itemconfigure(graph_id, fill=color)

    def create_image(self, root):
        self.image_loader = ImageLoader(root)
        self.image_loader.create_image(self.drawing, 0, 0, anchor='nw')

    def load_images(self, *args):
        #self.image_names = filedialog.askopenfilenames(filetypes=[("All files", "*.*"), ("Save files", "*.png")])
        root = filedialog.askdirectory()
        self.bunch['root'] = root
        self.create_image(root)

    def layout(self, row=0):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.drawing.layout(row=row, column=0)
        self.selector_frame.layout(row=row, column=1)
        self.tip_label.grid(row=row+1, sticky='we')
        self.notebook.grid(row=row+2, column=0)
        self.save_normal_button.grid(row=0, column=0, padx=2, pady=2)
        self.load_normal_button.grid(row=0, column=1, padx=2, pady=2)
        self.image_frame.grid(row=0, column=0, padx=2, pady=2)
        self.prev_image_button.grid(row=1, column=0, padx=2, pady=2)
        self.next_image_button.grid(row=1, column=1, padx=2, pady=2)
        self.annotation_frame.grid(row=1, column=0, padx=2, pady=2)


class ScrollableDrawing(Drawing):
    def __init__(self, master, selector_frame, after_time=160, cnf={}, **kw):
        super().__init__(master, selector_frame, after_time, cnf, **kw)
        self._set_scroll()
        self._scroll_command()
        self.configure(xscrollcommand=self.scroll_x.set,
                       yscrollcommand=self.scroll_y.set)
        self.bind("<Configure>", self.resize)
        self.update_idletasks()

    def _set_scroll(self):
        self.scroll_x = ttk.Scrollbar(self, orient='horizontal')
        self.scroll_y = ttk.Scrollbar(self, orient='vertical')

    def _scroll_command(self):
        self.scroll_x['command'] = self.xview
        self.scroll_y['command'] = self.yview

    def resize(self, event):
        region = self.bbox('all')
        self.configure(scrollregion=region)

    def layout(self):
        self.selector_frame.pack(side='top', anchor='w')
        self.selector_frame.layout_pack()
        self.scroll_x.pack(side='top', fill='x')
        self.pack(side='top', expand='yes', fill='both')
        self.scroll_y.pack(side='left', fill='y')


class GraphDrawing(ScrollableDrawing):
    def __init__(self, master, selector_frame, after_time=160, cnf={}, **kw):
        super().__init__(master, selector_frame, after_time, cnf, **kw)
        self.page_var = StringVar()
        self.jump_stride_var = StringVar()
        self.jump_stride_var.set(1)
        self.create_notebook()
        self.image_loader = None
        self.page_num = 1
        self.info_var = StringVar()
        self.info_label = ttk.Label(
            self.selector_frame, textvariable=self.info_var)
        self.master.bind('<Return>', self.update_page)
        self.master.bind('<Control-KeyPress-s>', self.save_rectangle)
        self.master.bind('<F1>', self.clear_graph)
        self.master.bind('<Delete>', self.delete_graph)
        #self.master.bind('<1>', self.show_current_graph)
        self.master.bind('<1>', lambda event: self.select_graph(event, 'current'))
        self.bunch = {}
        self.selected_tags = ()

    def show_current_graph(self, *args):
        graph_id = self.find_withtag('current')
        clostest_graph_id = self.find_closest(self.x, self.y, start=2)
        print(self.x, self.y, graph_id, clostest_graph_id)

    def create_notebook(self):
        self.notebook = FileNotebook(
            self.selector_frame, width=200, height=100, padding=(5, 5, 5, 5))
        image_frame, image_load_button, image_save_button = self.notebook.add_frame(
            text='Image')
        graph_frame, graph_load_button, graph_save_button = self.notebook.add_frame(
            text='Graph')
        additional_frame = self.notebook.add_frame(
            text='Additional', is_init_set=False)
        prev_button = ttk.Button(
            image_frame, text='Prev', command=self.prev_page)
        next_button = ttk.Button(
            image_frame, text='Next', command=self.next_page)
        current_page_label = ttk.Label(image_frame, text='current page')
        current_page_entry = ttk.Entry(
            image_frame, width='7', textvariable=self.page_var)
        jump_label = ttk.Label(image_frame, text='jump stride')
        jump_entry = ttk.Entry(image_frame, width='7',
                               textvariable=self.jump_stride_var)
        widgets = [[prev_button, next_button], [current_page_label, current_page_entry],
                   [jump_label, jump_entry]]
        self.notebook.layout(widgets, start=1)
        image_load_button['command'] = self.load_images
        graph_save_button['command'] = lambda: self.save_graph('all')
        graph_load_button['command'] = self.load_graph

    def set_image(self):
        self.image_loader.current_id = int(self.page_var.get())
        self.image_loader.create_image(self, 0, 0, anchor='nw')

    def load_images(self, *args):
        root = filedialog.askdirectory()
        if root:
            self.image_loader = ImageLoader(root)
            self.page_num = len(self.image_loader)
            self.page_var.set(0)
            self.set_image()
            self.info_var.set(f'Total Load {self.page_num} images')
            self.bunch['root'] = root

    def get_page(self):
        return self.page_var.get(), self.jump_stride_var.get()

    def update_current_page(self, current_page):
        if isinstance(current_page, str):
            current_page = int(current_page)
        if -self.page_num < current_page < self.page_num:
            self.page_var.set(current_page)

    def update_page(self, *args):
        if self.image_loader:
            current_page, jump_stride = self.get_page()
            if '' not in [current_page, jump_stride]:
                self.update_current_page(current_page)
                self.set_image()

    def next_page(self, *args):
        current_page, jump_stride = self.get_page()
        if '' not in [current_page, jump_stride]:
            current_page = int(current_page) + int(jump_stride)
            self.update_current_page(current_page)
            self.set_image()

    def prev_page(self, *args):
        current_page, jump_stride = self.get_page()
        if '' not in [current_page, jump_stride]:
            current_page = int(current_page) - int(jump_stride)
            self.update_current_page(current_page)
            self.set_image()

    def get_graph(self, tags):
        cats = {}
        for graph_id in self.find_withtag(tags):
            tags = self.gettags(graph_id)
            bbox = self.bbox(graph_id)
            cats[graph_id] = {'tags': tags, 'bbox': bbox}
        return cats

    def set_path(self, tags):
        if tags == 'all':
            return 'data/normal.json'
        else:
            return 'data/annotations.json'

    def save_graph(self, tags):
        graph = self.get_graph(tags)
        mkdir('data')
        path = self.set_path(tags)
        if self.image_loader:
            current_image_path = self.image_loader.current_path
            if current_image_path:
                self.bunch.update({self.image_loader.current_name: graph})
                save_bunch(self.bunch, path)
        else:
            save_bunch(graph, path)

    def save_rectangle(self, *args):
        self.save_graph('rectangle')

    def load_graph(self):
        self.bunch = load_bunch('data/annotations.json')
        root = self.bunch.get()
        if root:
            
            self.image_loader = ImageLoader(root)
            self.image_names = [
                f"{root}/{image_name}" for image_name in self.bunch if image_name != root]
            self.image_loader.current_id = 0
            self.create_image(root)
            self.reload_graph(self.bunch[self.image_loader.current_name])
        else:
            self.bunch = load_bunch('data/normal.json')
            self.load_normal()

    def load_normal(self):
        self.bunch = load_bunch('data/normal.json')
        self.reload_graph(self.bunch)

    def bunch2params(self, bunch):
        params = {}
        for graph_id, cats in bunch.items():
            tags = cats['tags']
            color, shape = tags
            graph_type = shape.split('_')[0]
            bbox = cats['bbox']
            params[graph_id] = {'tags': tags, 'color': color,
                                'graph_type': graph_type, 'direction': bbox}
        return params

    def reload_graph(self, cats):
        params = self.bunch2params(cats)
        self.clear_graph()
        for param in params.values():
            self.draw_graph(**param)

    def clear_graph(self, *args):
        self.delete('all')
        
    def delete_graph(self, *args):
        xy = self.x, self.y
        graph_id = self.find_closest(*xy)
        self.delete(graph_id)

    def select_graph(self, event, tags):
        self.configure(cursor="target")
        self.update_xy(event)
        if tags == 'current':
            self.selected_tags = self.find_withtag(tags)
        else:
            self.selected_tags = tags
        print(self.selected_tags)

    def layout(self):
        self.selector_frame.pack(side='top', anchor='w')
        self.notebook.pack(side='right', anchor='w')
        self.selector_frame.info_entry.pack(side='top', anchor='w', fill='y')
        self.selector_frame._selector.pack(side='top', anchor='w', fill='y')
        self.info_label.pack(side='top', anchor='w', fill='y')
        self.scroll_x.pack(side='top', fill='x')
        self.pack(side='top', expand='yes', fill='both', anchor='w')
        self.scroll_y.pack(side='left', anchor='w', fill='y')
