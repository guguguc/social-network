import tkinter as tk
import queue
from tkinter import ttk
import threading
from main import Network


# 主线程为ui线程
# 线程a构建社交网络

class ThreadedTask(threading.Thread):
    def __init__(self, q: queue.Queue):
        super().__init__()
        self.queue = q

    def run(self):
        net = Network.construct(uid=self.queue.get(), max_depth=2)
        self.queue.put(net)


class Gui(tk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.main_pane = tk.PanedWindow(bg='black', sashwidth=1)
        self.main_pane.pack(fill=tk.BOTH, expand=1)
        self.left_pane = tk.PanedWindow(self.main_pane, orient=tk.VERTICAL, bg='black', sashwidth=1)
        self.main_pane.add(self.left_pane)
        self.input_label = None
        self.input_field = None
        self.netsize_var = tk.StringVar(self, value='0')
        self.netedge_var = tk.StringVar(self, value='0')
        self.user_list = None
        self.btn_ok = None
        self.btn_show = None
        self.graph = None
        self.prog_bar = None
        self.queue = None
        self.net = None
        self.add_user_input()
        self.add_progress_track()
        self.add_user_list()
        self.add_graph()
        self.pack()

    def add_user_input(self):
        input_frame = tk.Frame()
        self.input_label = tk.Label(input_frame, text='user id')
        self.input_field = tk.Entry(input_frame)
        self.btn_ok = tk.Button(input_frame, text='collect', command=self.btn_ok_clicked)
        self.input_label.pack(side=tk.LEFT)
        self.input_field.pack(fill=tk.X, expand=True, side=tk.LEFT)
        self.btn_ok.pack(side=tk.RIGHT)
        self.left_pane.add(input_frame)

    def add_progress_track(self):
        container = tk.Frame()
        label_netsize = tk.Label(container, text='net size:')
        label_relations = tk.Label(container, text='net edges:')
        msg_netsize = tk.Message(container, textvariable=self.netsize_var)
        msg_netedge = tk.Message(container, textvariable=self.netedge_var)
        self.btn_show = tk.Button(container, text='show', command=self.btn_show_clicked)
        label_netsize.grid(row=0, column=0, sticky=tk.W)
        label_relations.grid(row=0, column=2)
        msg_netsize.grid(row=0, column=1)
        msg_netedge.grid(row=0, column=3, padx=(0, 30))
        self.btn_show.grid(row=0, column=4, sticky=tk.E)
        self.left_pane.add(container)

    def add_user_list(self):
        self.user_list = tk.Listbox()
        self.user_list.bind('<Double-Button-1>', self.copy_user_id)
        self.left_pane.add(self.user_list)

    def update_user_list(self):
        assert self.net and self.user_list
        sz = self.user_list.size()
        if sz:
            self.user_list.delete(0, sz)
        for i, user in enumerate(self.net.users):
            self.user_list.insert(i, [user.uid, user.name])

    def add_graph(self):
        self.graph = tk.Canvas(self.master)
        self.main_pane.add(self.graph)

    def add_progress(self):
        if self.prog_bar is not None:
            return
        self.prog_bar = ttk.Progressbar(orient='vertical', mode='indeterminate')
        self.left_pane.add(self.prog_bar)

    def copy_user_id(self, event):
        self.master.clipboard_clear()
        assert self.user_list
        selected = self.user_list.get(tk.ANCHOR)[0]
        self.master.clipboard_append(selected)

    def process_queue(self):
        try:
            self.net = self.queue.get(0)
            self.netsize_var.set(f'{self.net.size}')
            self.netedge_var.set(f'{self.net.edges}')
            self.update_user_list()
            self.prog_bar.stop()
            self.left_pane.remove(self.prog_bar)
            self.prog_bar = None
            self.btn_ok['state'] = tk.NORMAL
        except queue.Empty:
            self.master.after(100, self.process_queue)

    def btn_ok_clicked(self):
        self.add_progress()
        self.prog_bar.start()
        self.queue = queue.Queue()
        self.queue.put(self.input_field.get())
        self.btn_ok['state'] = tk.DISABLED
        ThreadedTask(self.queue).start()
        self.process_queue()

    def btn_show_clicked(self):
        pass


root = tk.Tk()
root.title('social network')
root.geometry('800x400')
app = Gui(root)
app.mainloop()
