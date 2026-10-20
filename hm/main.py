import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import Menu
from tkinter import ttk
from pathlib import Path
import CTkListbox as Lbox
import PIL.Image as Image
import os

#関数リスト
from . import def_list
import func_editcsv2
import image2csv

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1100x700")

        #widget
        ################################################################################################################################################
        self.label = ctk.CTkLabel(self, text="KAKEBO", font=("Arial", 30))
        self.label.pack(side="top", padx=10, pady=10,)

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
    

        #left_frame
        #コンテキストメニュー
        #メニューの操作対象
        self.context_index = None

        #メニューを作成
        self.context_menu = Menu(self, tearoff=False)
        self.context_menu.add_command(label="金額編集",command=self.edit_amount)
        self.context_menu.add_command(label="日付編集",command=self.edit_date)
        self.context_menu.add_command(label="削除",command=self.delete_csv)

        #ドラッグ＆ドロップ
        TkinterDnD.require(self)
        self.button.drop_target_register(DND_FILES)
        self.button.dnd_bind("<<Drop>>", self.import_drop)

        #リストボックス
        tree_frame = ctk.CTkFrame(self.left_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=10)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("amount",), #金額用の列を１つ追加
            show="tree headings", #親子関係の列と見出しの行を表示
            selectmode="browse", #一度に１項目を選択
        )

        self.tree.heading("#0", text="日付・画像") #日付・画像の列
        self.tree.heading("amount", text="金額") #金額の列

        self.tree.column("#0", width=160, minwidth=80)
        self.tree.column("amount", width=85, minwidth=70, anchor="e")

        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=self.tree.yview, #スクロールバーを操作したらツリーを動かすという指定
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand = True)

        self.receipt_nodes = {}
        self.context_node=None



        #mid_frame
        #表示中の画像を保持
        self.mid_graph = None

        self.mid_graph_label = ctk.CTkLabel(
            self.mid_frame,
            text="リストから日付を選択してください",
        )
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>",self.show_context_menu)
        self.mid_graph_label.pack(fill="both", expand=True, padx=10, pady=10, )

        
        self.edit_button = ctk.CTkButton(self.mid_frame, text="test", )
        self.edit_button.pack(side="left",padx=10,pady=10)


        


        #right_frame
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

        #csvを読んでグラフを更新
        self.refresh_ui()
    
        #画像を保存するフォルダを作成するすでにある場合は作成しない
        def_list.make_folder()
    

    #関数
    ################################################################################################################################################
    def import_explorer(self):
        file_paths = () #tuple型
        file_paths, saved_date= def_list.save_file_explorer()

        #ファイル選択をキャンセルした場合
        if not file_paths:
            return

        #画像を１枚ずつOCR処理し、csvに追記
        for image_path in file_paths:
            image2csv.makecsv(image_path)

        #全画面の追記が終わったら画面を更新
        self.refresh_ui()

    def import_drop(self, event):
        imgs_paths = self.tk.splitlist(event.data)
        file_paths, saved_date = def_list.save_file_drop(imgs_paths)

        #ファイル選択をキャンセルした場合
        if not file_paths:
            return

        for image_path in file_paths:
            image2csv.makecsv(image_path)
        self.refresh_ui()

    #リストボックスをクリックした際のコンテキストメニュー表示
    def show_context_menu(self, event, ):
        node = self.tree.identify_row(event.y)

        if node not in self.receipt_nodes:
            self.context_node = None
            return

        self.tree.selection_set(node)
        self.tree.focus(node)
        self.context_node = node 

        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()


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

    def edit_amount(self,):
        pass

    def edit_date(self,):
        pass

    def delete_csv(self,):
        receipt = self.receipt_nodes.get(self.context_node)

        if receipt is None:
            return

        func_editcsv2.del_line(
            receipt["row_index"],
            csv_path=def_list.CSV_PATH,
        )
        #ui更新
        self.refresh_ui()

    def refresh_ui(self,):
        #リストの再作成と右クリックの設定
        self.update_tree()

        #グラフも作りなおす
        def_list.create_graph()

        with Image.open("./graph.png") as image:
            img = image.copy()

        self.graph_original_size = img.size
        self.graph.configure(light_image=img, dark_image=img)

        self.mid_graph_label.configure(
            image=None,
            text="リストから日付を選択してください",
        )
        self.mid_graph = None

    #日付と明細を親子にする
    def update_tree(self,):
        roots = self.tree.get_children() #更新前の親項目を取得する
        open_states = {
            self.tree.item(node, "text"):self.tree.item(node, "open")
            for node in roots
        } #親の日付と開いているかどうかを辞書に保存する

        self.context_node = None
        self.receipt_nodes.clear()

        if roots:
            self.tree.delete(*roots)

        data = def_list.read_receipts()

        for date, group in data.groupby("date"):
            parent = self.tree.insert(
                "",
                "end",
                text=date,
                values=(f"{group["amount"].sum():,.0f}円",),
                open=open_states.get( date, True),
            )

            for row_index, row in group.iterrows():
                image_path = Path(row["image_path"])

                if not image_path.is_absolute():
                    image_path = def_list.CSV_PATH.parent / image_path

                child = self.tree.insert(
                    parent,
                    "end",
                    text=image_path.name,
                    values=(f"{row["amount"]:,.0f}円",),
                )

                self.receipt_nodes[child] = {
                    "row_index": row_index,
                    "image_path": str(image_path),
                }

    #指定された画像を読み込み、mid_frameに表示する
    def display_image(self, image_path):
        try:
            with Image.open(image_path) as image:
                img = image.copy()
        except OSError as error:
            self.mid_graph_label.configure(
                image=None,
                text=f"画像を読み込めません\n{error}"
            )
            self.mid_graph = None
            return

        #縦横比を保ち220x300に収める
        width, height = img.size
        ratio = min(220 / width, 300 / height)

        display_size = (
            max(1, int(width * ratio)),
            max(1, int(height * ratio))
        )

        self.mid_graph = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=display_size,
        )

        self.mid_graph_label.configure(
            image=self.mid_graph,
            text="",
        )
        

    #選択した日付の画像候補を準備する
    def on_tree_select(self, event):
        selected = self.tree.selection()

        if not selected:
            return

        receipt = self.receipt_nodes.get(selected[0])

        if receipt is None:
            # 親の日付を選択した場合
            self.mid_graph_label.configure(
                image=None,
                text="子項目のレシートを選択してください",
            )
            self.mid_graph = None
            return

        self.display_image(receipt["image_path"])


    ################################################################################################################################################

    
if __name__ == "__main__":
    app = App()
    app.mainloop()