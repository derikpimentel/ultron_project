import time
import threading
from tkinter import *
from tkinter.ttk import Progressbar

# Estrutura da janela
class Application:
    def __init__(self, master=None):
        self.master = master # Faz a passagem da variável "root"
        self.master.geometry("300x75") # Define as dimensões da janela (L x A)
        self.master.overrideredirect(True) # Remove a barra superior

        # Estruturando os widgets da janela
        self.container_load_screen = Frame(self.master)
        self.container_load_screen.pack(pady=10) # O método "pack()" organiza em bloco
        # início do "container_load_screen"
        self.label_notice = Label(self.container_load_screen)
        self.label_notice["text"] = "Carregando, por favor aguarde..."
        self.label_notice.pack()
        self.progress_bar = Progressbar(self.container_load_screen)
        self.progress_bar["orient"] = "horizontal"
        self.progress_bar["mode"] = "determinate"
        self.progress_bar["length"] = 250
        self.progress_bar.pack()
        # final do "container_load_screen"

        # Cria uma Thread para executar a operação de carregamento
        threading.Thread(target=self.running_operation, daemon=True).start()
        """
        Observação:
        Adicionar o parâmetro "daemon=True" na Thread é uma boa ideia, pois faz com que a Thread 
        seja encerrada automaticamente quando a Thread principal (a aplicação Tkinter) é fechada. 
        Isso garante que o programa não continue rodando em segundo plano.
        """

    # Função para carregamento
    def running_operation(self):
        # Estrutura de carregamento da barra de progresso
        for i in range(101):
            time.sleep(0.05)
            self.update_progress(i) # Atualiza a barra de progresso
        time.sleep(1) # Paralisa a execução (Seg)
        self.close() # Fecha a tela de carregamento após a operação

    # Função que atualiza a barra de progresso
    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.master.update_idletasks()  # Atualiza a interface gráfica

    # Função que encerra a janela
    def close(self):
        self.master.destroy() # Fecha a janela e encerra a aplicação

# Estrutura de execução
if __name__ == "__main__":
    root = Tk()
    Application(root)
    root.mainloop()