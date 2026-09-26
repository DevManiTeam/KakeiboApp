import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

def drop_file(event):
    files = app.tk.splitlist(event.data) #event.dataはファイルパスが入っている。splitlistで複数のファイルパスをリストにする
    entry.delete(0, "end")
    entry.insert(0, files)

app = ctk.CTk()
app.geometry("600x300")

TkinterDnD.require(app) #DnDを有効化する

entry = ctk.CTkEntry(app,width=450,height=40,placeholder_text="ここにファイルを")
entry.pack(pady=50)

entry.drop_target_register(DND_FILES) #このEntryをファイルのドロップ先として登録する　DND_FILEはファイルを受けつける
entry.dnd_bind("<<Drop>>",drop_file) #Entryにファイルがドロップされたら関数を呼び出す

app.mainloop()