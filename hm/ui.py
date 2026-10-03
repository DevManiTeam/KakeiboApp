import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import PIL.Image as Image

#関数リスト
import def_list

#関数
################################################################################################################################################
def import_explorer():
    file_path = () #tuple型
    file_path, time= def_list.save_file_explorer()
    print(file_path)
    print(time)
    label.configure(text="画像がエクスプローラーから保存されました")

def import_drop(event):
    imgs_path = app.tk.splitlist(event.data)
    file_path, time = def_list.save_file_drop(imgs_path)
    print(file_path)
    print(time)
    label.configure(text="画像がドロップから保存されました")
################################################################################################################################################



#UI
################################################################################################################################################
app = ctk.CTk()
app.geometry("1000x600")

label = ctk.CTkLabel(app, text="KAKEBO", font=("Arial", 30))
label.pack(side="top", padx=10, pady=10)

left_frame = ctk.CTkFrame(app)
left_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

right_frame = ctk.CTkFrame(app)
right_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)

   
label = ctk.CTkLabel(left_frame, text="ファイルは選択されていません", font=("Arial", 20))
label.pack(padx=10, pady=10)

button = ctk.CTkButton(left_frame, hover_color="green", fg_color="green3", text="ファイルを開く", command=import_explorer)
button.pack(padx=10, pady=10)



TkinterDnD.require(app)
button.drop_target_register(DND_FILES)
button.dnd_bind("<<Drop>>", import_drop)

scrollabelframe = ctk.CTkScrollableFrame(left_frame,)
scrollabelframe.pack(fill="both",expand=True,)

for i in range(10):
    button = ctk.CTkButton(scrollabelframe, text=f"button{i+1}", corner_radius=0)
    button.pack(fill="x", pady=3)

#画像表示　テスト
img = Image.open("./IMG_0329.png")
graph = ctk.CTkImage(light_image=img, dark_image=img, )
graph_label = ctk.CTkLabel(right_frame, image=graph, text="")
graph_label.pack(fill="both",expand=True)

################################################################################################################################################


#画像を保存するフォルダを作成するすでにある場合は作成しない
def_list.make_folder()


app.mainloop()