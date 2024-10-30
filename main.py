from tkinter import *

# Estrutura da janela
class Application:
    def __init__(self, master=None):
        self.master = master # Faz a passagem da variável "root"
        self.master.geometry("300x300") # Define as dimensões da janela (L x A)

# Estrutura de execução
if __name__ == "__main__":
    root = Tk()
    Application(root)
    root.mainloop()