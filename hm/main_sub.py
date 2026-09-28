import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import CTkListbox as Lbox
import PIL.Image as Image
import os

#関数リスト
from . import def_list
import func_editcsv

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x600")

        #widget
        ################################################################################################################################################
        self.label = ctk.CTkLabel(self, text="KAKEBO", font=("Arial", 30))
        self.label.pack(side="top", padx=10, pady=10,)
        #label.grid(row=0, column=0,padx=10, pady=10, columnspan=3, sticky=ctk.EW)

        #################
        self.test_frame = ctk.CTkFrame(self)
        self.test_frame.pack(side="top", fill="both", expand=True,)

        self.edit_button = ctk.CTkButton(self.test_frame, text="edit", )
        self.edit_button.pack(side="left",padx=10,pady=10)

        self.save_csv = ctk.CTkButton(self.test_frame, text="save_csv", command=lambda: def_list.create_graph)
        self.save_csv.pack(side="left",padx=10,pady=10)
        
        #################

        # main_frame = ctk.CTkFrame(self.app)
        # main_frame.pack(side="top",padx=10, pady=(5,10), fill="both", expand=True)
    
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.pack(side="left", padx=(10,5), pady=10, fill="both", expand=True)
        #left_frame.grid(row=1, column=0,padx=(10,5), pady=10, sticky="nswe")

        self.mid_frame = ctk.CTkFrame(self)
        self.mid_frame.pack(side="left", padx=(5,5), pady=10, fill="both", expand=True)
        #mid_frame.grid(row=1, column=1,padx=(5,5), pady=10, sticky="nswe")

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="left", padx=(5,10), pady=10, fill="both", expand=True)
        #right_frame.grid(row=1, column=2,padx=(5,10), pady=10, sticky="nswe")


        #gridを使い、ウィンドウサイズが変化したときにウィジェットのサイズを変化させる
        # main_frame.grid_columnconfigure(1, weight=1)
        # main_frame.grid_rowconfigure(0, weight=1)
        # main_frame.grid_rowconfigure(1, weight=1)
        # main_frame.grid_rowconfigure(2, weight=1)
    
        self.button = ctk.CTkButton(self.left_frame, hover_color="green", fg_color="green3", text="ファイルを開く", command=self.import_explorer)
        self.button.pack(padx=10, pady=10)
    
    
        #ドラッグ＆ドロップ
        TkinterDnD.require(self)
        self.button.drop_target_register(DND_FILES)
        self.button.dnd_bind("<<Drop>>", self.import_drop)

        #スクロールバー
        # self.scrollabelframe = ctk.CTkScrollableFrame(self.left_frame,)
        # self.scrollabelframe.pack(fill="both",expand=True,)
    
        # for i in range(10):
        #     self.button = ctk.CTkButton(self.scrollabelframe, text=f"button{i+1}", corner_radius=0)
        #     self.button.pack(fill="x", pady=3)
        self.listbox = Lbox.CTkListbox(self.left_frame)
        items = [1,2,3,4,5]
        for item in items:
            self.listbox.insert(ctk.END, item)
        self.listbox.pack(fill="both", expand=True, padx=(10,5),pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.list_click)

        #グラフ表示
        if os.path.isfile(r"./graph.png"):  #グラフ画像がある場合
            img = Image.open(r"./graph.png")
        else:                               #グラフ画像がない場合
            def_list.create_graph()
            img = Image.open(r"./graph.png")
            
        self.graph = ctk.CTkImage(light_image=img, dark_image=img, )
        self.graph_label = ctk.CTkLabel(self.right_frame, image=self.graph, text="")
        self.graph_label.pack(fill="both",expand=True)
    
        ################################################################################################################################################
    
    
        #画像を保存するフォルダを作成するすでにある場合は作成しない
        def_list.make_folder()
    

    #関数
    ################################################################################################################################################
    def import_explorer(self):
        file_path = () #tuple型
        file_path, time= def_list.save_file_explorer()
        print(file_path)
        print(time)
        self.label.configure(text="画像がエクスプローラーから保存されました")

    def import_drop(self, event):
        imgs_path = self.app.tk.splitlist(event.data)
        file_path, time = def_list.save_file_drop(imgs_path)
        print(file_path)
        print(time)
        self.label.configure(text="画像がドロップから保存されました")

    def list_click(self, event):
        print(event)
    ################################################################################################################################################

    
if __name__ == "__main__":
    app = App()
    app.mainloop()