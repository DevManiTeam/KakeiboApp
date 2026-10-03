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

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="top",padx=10, pady=(5,10), fill="both", expand=True)
        #横の比率を指定
        #weight:比率　uniform:weightの比率にそろえる
        self.main_frame.grid_columnconfigure(0, weight=1, uniform="columns")
        self.main_frame.grid_columnconfigure(1, weight=2, uniform="columns")
        self.main_frame.grid_columnconfigure(2, weight=3, uniform="columns")
        #縦の比率を指定
        self.main_frame.grid_rowconfigure(0, weight=1)
    
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5)

        self.mid_frame = ctk.CTkFrame(self.main_frame)
        self.mid_frame.grid(row=0, column=1, sticky="nsew", padx=5)

        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=5)
    
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
        items = def_list.csv_to_list()
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

        #元画像の元のサイズを保持
        self.graph_original_size = img.size
        
        self.graph = ctk.CTkImage(light_image=img, dark_image=img, size=(1,1))
        self.graph_label = ctk.CTkLabel(self.right_frame, image=self.graph, text="",width=1, height=1)
        #relx,rely　相対的な位置を0~1で指定　anchorはウィジェットを配置する基準位置
        self.graph_label.place(relx=0.5, rely=0.5, anchor="center")
        #add="+"はbindで複数の関数を同じイベントにバインドするためのオプション
        self.right_frame.bind("<Configure>", self.resize_graph, add="+")
    
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

    def resize_graph(self, event):
        #表示倍率
        scaling = self.right_frame._get_widget_scaling()
        #event.width, event.heightは変更後のサイズ
        available_width = event.width / scaling -20 #-20は余白
        available_height = event.height / scaling - 20

        #画像を配置できない大きさなら、処理を終える
        if available_width <= 0 or available_height < - 0:
            return
        original_width, original_height = self.graph_original_size

        #縦か横小さいほうの倍率に合わせる
        ratio = min(available_width / original_width, available_height / original_height,)

        #新しいサイズを計算　タプルにまとめる
        new_size = (max(1, int(original_width * ratio)), max(1, int(original_height * ratio)))

        #cget("size")で現在設定されている画像の表示サイズを取得　新しいサイズと違う時だけリサイズする
        #そうすることでサイズが同じときはリサイズをしないようにする
        if self.graph.cget("size") != new_size:
            self.graph.configure(size=new_size)
    ################################################################################################################################################

    
if __name__ == "__main__":
    app = App()
    app.mainloop()