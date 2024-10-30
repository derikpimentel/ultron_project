import time
import threading
from tkinter import *
from tkinter.ttk import Progressbar

# Estrutura da janela
class Application:
    def __init__(self, master=None):
        self.master = master # Faz a passagem da variável "root"
        self.master.title("Ultron") # Altera o título da janela
        self.master.geometry("300x75") # Define as dimensões da janela (L x A)
        self.master.overrideredirect(True) # Remove a barra superior

        # Estruturando os widgets da janela de carregamento
        self.loading_screen = Frame(self.master)
        self.loading_screen.pack(pady=10) # O método "pack()" organiza em bloco
        # início do "loading_screen"
        self.label_notice = Label(self.loading_screen)
        self.label_notice["text"] = "Carregando, por favor aguarde..."
        self.label_notice.pack()
        self.progress_bar = Progressbar(self.loading_screen)
        self.progress_bar["orient"] = "horizontal"
        self.progress_bar["mode"] = "determinate"
        self.progress_bar["length"] = 250
        self.progress_bar.pack()
        # final do "loading_screen"

        self.center_window() # Centraliza a janela após criar todo conteúdo da tela

        # Cria uma Thread para executar a operação de carregamento
        threading.Thread(target=self.running_operation, daemon=True).start()
        """
        Observação:
        Adicionar o parâmetro "daemon=True" na Thread é uma boa ideia, pois faz com que a Thread 
        seja encerrada automaticamente quando a Thread principal (a aplicação Tkinter) é fechada. 
        Isso garante que o programa não continue rodando em segundo plano.
        """

    # Função que centraliza a janela na tela
    def center_window(self):
        self.master.update_idletasks() # Atualiza a interface gráfica
        """
        Atualiza a interface para o caso de haver tarefas pendentes, e para garantir que o tamanho 
        correto seja calculado.
        """

        # Obtém a largura e altura da tela
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Obtém a largura e altura da janela atual
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        # Calcula a posição x e y para centralizar a janela
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    # Função para carregamento
    def running_operation(self):
        # Estrutura de carregamento da barra de progresso
        for i in range(101):
            time.sleep(0.05)
            self.update_progress(i) # Atualiza a barra de progresso
        time.sleep(1) # Paralisa a execução (Seg)
        self.loading_main_screen() # Carrega a estrutura da janela principal

    # Função que atualiza a barra de progresso
    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.master.update_idletasks()

    # Função que inicializa a janela principal do sistema
    def loading_main_screen(self):
        self.master.withdraw() # Esconde a janela para fazer as modificações
        self.loading_screen.destroy() # Apaga o widget da tela de carregamento
        #self.master.geometry("") # Retorna para o redmensionamento automático
        self.master.overrideredirect(False) # Devolve a barra superior
        self.master.resizable(False, False) # Desabilita o redimensionamento da janela

        # Estruturando os widgets da janela principal
        self.main_screen = Frame(self.master)
        self.main_screen.pack()
        # início do "main_screen"
        self.container_header = Frame(self.main_screen)
        self.container_header.pack()
        self.label_title = Label(self.container_header)
        self.label_title["text"] = "Inventário de máquina"
        self.label_title.pack()

        self.container_main = Frame(self.main_screen)
        self.container_main.pack()
        self.label_description = Label(self.container_main)
        self.label_description["text"] = "Dados do equipamento"
        self.label_description.pack()

        self.container_footer = Frame(self.main_screen)
        self.container_footer.pack()
        self.label_info = Label(self.container_footer)
        self.label_info["text"] = "Desenvolvido por Derik B. Pimentel"
        self.label_info.pack()
        # início do "main_screen"

        self.center_window()
        self.master.deiconify() # Mostra a janela novamente

# Estrutura de execução
if __name__ == "__main__":
    root = Tk()
    Application(root)
    root.mainloop()