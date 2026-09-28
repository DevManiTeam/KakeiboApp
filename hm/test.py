import customtkinter as ctk
import CTkListbox as lbox

def on_select(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        selected_value = event.widget.get(index)
        print(f"選択された値: {selected_value}")

app = ctk.CTk()

# リストボックスの作成
listbox = lbox.CTkListbox(app)
items = ["アイテム1", "アイテム2", "アイテム3"]
for item in items:
    listbox.insert(ctk.END, item)
listbox.pack()

# イベントバインディング
listbox.bind("<<ListboxSelect>>", on_select)

app.mainloop()