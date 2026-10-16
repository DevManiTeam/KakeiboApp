import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import Menu
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

        self.listbox = Lbox.CTkListbox(self.left_frame)
        self.listbox.pack(fill="both", expand=True, padx=(10,5),pady=10)
        self.update_listbox()
        



        #mid_frame
        #表示中の画像を保持
        self.mid_graph = None

        #同じ日付の画像を切り替える選択欄
        self.image_selector = ctk.CTkOptionMenu(
            self.mid_frame,
            values=["画像なし"], #選択肢として表示する文字列のリスト
            command=self.display_image, #イメージ　self.display_image("C:\\...\\receipt2.jpg")
            state="disabled", #最初は操作できない状態
        )
        self.image_selector.pack(fill="x", padx=10, pady=10)

        self.mid_graph_label = ctk.CTkLabel(
            self.mid_frame,
            text="リストから日付を選択してください",
        )
        self.mid_graph_label.pack(fill="both", expand=True, padx=10, pady=10, )

        #選択変更時に画像を表示
        self.listbox.bind(
            "<<ListboxSelect>>",
            self.display_selected_image,
            add="+",
        )

        
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
    def show_context_menu(self, event, index):
        #クリックした行を選択する
        self.listbox.select(index)
        self.context_index = index

        #右クリックした画面座標にメニューを表示
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
        index = self.listbox.curselection()
        value = self.listbox.get()

        print(index)
        print(value)
        func_editcsv2.del_line(index)
        #ui更新
        self.refresh_ui()

    def refresh_ui(self,):
        #リストの再作成と右クリックの設定
        self.update_listbox()

        #グラフも作りなおす
        def_list.create_graph()

        with Image.open("./graph.png") as image:
            img = image.copy()

        self.graph_original_size = img.size

        self.graph.configure(light_image=img, dark_image=img)

        self.update_listbox()
        self.mid_graph_label.configure(
            image=None,
            text="リストから日付を選択してください",
        )
        self.mid_graph = None
        self.image_selector.configure(values=["画像なし"], state="disabled")
        self.image_selector.set("画像なし")

    #リストのデータの数が変わるとindexが変わるのでリストを一度削除してから再作成する
    def update_listbox(self,):
        self.context_index = None
        self.listbox.delete("all")

        #画面の選択位置と日付を対応させるためのデータ
        self.csv_items = def_list.csv_to_list()

        for index, item in enumerate(self.csv_items): #nnumerateは位置とデータをセットで取り出す
            row_button = self.listbox.insert(ctk.END, item)

            #i=indexその行の位置を関数を作った時点で保存する
            row_button.bind("<Button-3>",
                            lambda event, i=index: self.show_context_menu(event, i),
                            add="+")

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
    def display_selected_image(self, event):
        index = self.listbox.curselection()

        if index is None:
            return

        #表示データは　番号、日付、合計金額
        date = self.csv_items[index][1]

        try:
            paths = def_list.get_image_paths(date) #取得した日付で画像パスを検索する
        except OSError as error:
            self.image_selector.configure(state="disabled")
            self.mid_graph_label.cinfigure(
                image=None,
                text="csvを読み込めません\n{error}",
            )
            return

        if not paths:
            self.image_selector.configure(
                values=["画像なし"],
                state="disabled",
            )
            self.image_selector.set("画像なし")
            self.mid_graph_label.configure(
                image=None,
                text="この日付の画像はありません",
            )
            self.mid_graph = None
            return

        #ドロップダウンに画像パスを設定
        self.image_selector.configure(values=paths, state="normal")
        self.image_selector.set(paths[0])

        #最初の画像を表示
        self.display_image(paths[0])


    ################################################################################################################################################

    
if __name__ == "__main__":
    app = App()
    app.mainloop()