from pathlib import Path
import json
from tkinter import ttk


def save_bunch(bunch, path):
    with open(path, 'w') as fp:
        json.dump(bunch, fp)


def load_bunch(path):
    with open(path) as fp:
        bunch = json.load(fp)
    return bunch


def mkdir(root_dir):
    '''依据给定名称创建目录'''
    path = Path(root_dir)
    if not path.exists():
        path.mkdir()


class FileFrame(ttk.LabelFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.save_button = ttk.Button(self, text='Save')
        self.load_button = ttk.Button(self, text='Load')
        self.layout(row=0)

    def layout(self, row=0):
        self.load_button.grid(row=row, column=0)
        self.save_button.grid(row=row, column=1)


class GridLayout:
    def __init__(self, master=None, **kw):
        pass

    def layout_row(self, row=0, *row_widget):
        '''
        row > 0
        '''
        for column, widget in enumerate(row_widget):
            widget.grid(row=row, column=column)

    def layout(self, row_widgets, start=0):
        for row, row_widget in enumerate(row_widgets):
            self.layout_row(row+start, *row_widget)



class FileNotebook(ttk.Notebook, GridLayout):
    def __init__(self, master=None, **kw):
        '''
        Example
        =============
        root = Tk()
        self = FileNotebook(root, width=200, height=100, padding=(5, 5, 5, 5))
        image_frame = self.add_frame(text='Image')
        annotation_frame = self.add_frame(text='Annotation')
        prev_button = ttk.Button(image_frame, text='Prev')
        next_button = ttk.Button(image_frame, text='Next')
        self.layout_pairs(prev_button, next_button, row=1)
        self.grid()
        root.mainloop()
        '''
        super().__init__(master, **kw)

    def add_frame(self, text, row=0, is_init_set=True, **kw):
        frame = ttk.Frame(self, **kw)
        self.add(frame, text=text)
        if is_init_set:
            load_button, save_button = self._init_set(frame, row)
            self.layout_row(0, load_button, save_button)
            return frame, load_button, save_button
        else:
            return frame

    def _init_set(self, frame, row=0):
        save_button = ttk.Button(frame, text='Save')
        load_button = ttk.Button(frame, text='Load')
        return load_button, save_button
        
