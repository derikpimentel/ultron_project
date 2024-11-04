import os
import json
import time
import threading
from tkinter import *
from tkinter.ttk import Progressbar
import pythoncom
from wmi import WMI
import numpy as np
from PIL import Image, ImageTk

# Estrutura da janela
class Application:
    def __init__(self, master=None):
        self.master = master # Faz a passagem da variável "root"
        self.master.title("Ultron") # Altera o título da janela
        self.master.geometry("300x75") # Define as dimensões da janela (L x A)
        self.master.overrideredirect(True) # Remove a barra superior
        # Configurando um protocolo para fechamento da janela
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)

        self.widgets = self.load_to_json("widgets.json") # Carrega o arquivo "widgets.json"
        self.wmi_data_collection = {} # Armazena os dados coletados do WMI
        copy_icon = Image.open("copy.png") # Cria um ícone
        copy_icon = copy_icon.resize((8, 8), Image.LANCZOS) # Redimensiona para 8x8
        self.copy_icon = ImageTk.PhotoImage(copy_icon) # Converte para uso do Tkinter

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
        Adicionar o parâmetro "daemon=True" na Thread é uma boa ideia, pois faz com que a 
        Thread seja encerrada automaticamente quando a Thread principal (a aplicação Tkinter) 
        é fechada. Isso garante que o programa não continue rodando em segundo plano.
        """

    # Função para fechamento da janela
    def close_window(self):
        self.save_to_json("widgets.json", self.widgets) # Salva as alterações
        self.master.destroy() # Encerra o programa

    # Carrega os arquivos JSON com codificação UTF-8
    def load_to_json(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding='utf-8') as file:
                return json.load(file)

    # Salva os dados como arquivo JSON com codificação UTF-8
    def save_to_json(self, file_path, file_json):
        with open(file_path, "w", encoding='utf-8') as archive_json:
            json.dump(file_json, archive_json, ensure_ascii=False, indent=4)

    # Função que centraliza a janela na tela
    def center_window(self):
        self.master.update_idletasks() # Atualiza a interface gráfica
        """
        Atualiza a interface para o caso de haver tarefas pendentes, e para garantir que o 
        tamanho correto seja calculado.
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
        """
        A função "pythoncom.CoInitialize()" corrige um problema ao qual garante que o COM seja 
        inicializado antes de fazer qualquer chamada WMI dentro de uma Thread.
        """
        pythoncom.CoInitialize() # Inicializa o COM para a Thread
        try:
            qtt_widgets = len(self.widgets) # Obtém a quantidade total de widgets
            # Estrutura de carregamento da barra de progresso
            for i, widget in enumerate(self.widgets, start=1):
                wmi_objects = self.search_wmi_objects(widget) # Realiza a busca dos dados
                self.wmi_data_collection.update(wmi_objects) # Armazena os dados na memória
                percent = (i / qtt_widgets) * 100 # Cálcula a porcentagem de progresso
                self.update_progress(percent) # Atualiza a barra de progresso
        finally:
            pythoncom.CoUninitialize() # Libera os recursos COM
            time.sleep(1) # Paralisa a execução (Seg)
            self.loading_main_screen() # Carrega a estrutura da janela principal

    # Função que obtém os dados da biblioteca WMI
    def search_wmi_objects(self, element):
        # Obtém uma string formatada no modelo SELECT QUERY
        select_query = self.select_str(element["Class"], ['*'], element.get("Filter"))
        namespace = element.get("Namespace") # Se existir a chave "Namespace", busca o valor

        search_result = WMI(namespace=namespace).query(select_query)
        return { element["Name"]: search_result }
    
    # Função que obtém uma string formatada em SELECT QUERY
    def select_str(self, table, columns=['*'], search_filter=None):
        columns_str = ", ".join(columns)
        search_filter_str = ""
        if search_filter:
            placeholders = " ".join([f"{item}" for item in search_filter])
            search_filter_str = f"WHERE {placeholders}"
        return f"SELECT {columns_str} FROM {table} {search_filter_str}"

    # Função que atualiza a barra de progresso
    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.master.update_idletasks()

    # Função que inicializa a janela principal do sistema
    def loading_main_screen(self):
        self.master.withdraw() # Esconde a janela para fazer as modificações
        self.loading_screen.destroy() # Apaga o widget da tela de carregamento
        self.master.geometry("") # Retorna para o redmensionamento automático
        self.master.geometry(f"+{10}+{10}") # Posiciona a janela no canto superior esquerdo
        self.master.overrideredirect(False) # Devolve a barra superior
        self.master.resizable(False, False) # Desabilita o redimensionamento da janela

        # Estrutura do menu principal da janela
        self.menu_bar = Menu(self.master)
        self.menu_display = Menu(self.menu_bar, tearoff=0) # Criando o menu "Exibir"
        self.menu_bar.add_cascade(
            label="Exibir", 
            menu=self.menu_display
        ) # Insere o menu "Exibir" ao menu principal
        self.master.config(menu=self.menu_bar) # Acrescentando o menu principal na janela

        # Estruturando os widgets da janela principal
        self.main_screen = Frame(self.master)
        self.main_screen.pack(padx=10, pady=10)
        # início do "main_screen"
        self.container_header = Frame(self.main_screen)
        self.container_header.pack()
        self.label_title = Label(self.container_header)
        self.label_title["text"] = "Inventário de máquina"
        self.label_title["font"] = ("Segoe UI", "10", "bold")
        self.label_title.pack()

        # Estrutura do conteúdo dinâmico da janela
        self.container_main = Frame(self.main_screen)
        self.container_main.pack(padx=10, pady=10)
        self.wmi_widgets_collection = {} # Para armazenar os widgets do WMI
        self.create_wmi_widgets() # Carrega os widgets do WMI na janela

        self.container_footer = Frame(self.main_screen)
        self.container_footer.pack()
        self.label_info = Label(self.container_footer)
        self.label_info["text"] = "Desenvolvido por Derik B. Pimentel"
        self.label_info.pack()
        # final do "main_screen"

        self.master.deiconify() # Mostra a janela novamente

    # Função que cria os widgets do WMI dinâmicamente na janela
    def create_wmi_widgets(self):
        # Conversor de valores para exibição dos dados
        def text_converter(text_id, value_to_convert):

            if text_id in ['Capacity', 'AdapterRAM']:
                qtt_bytes = int(value_to_convert)
                to_giga = format(qtt_bytes/(1024**3), '.0f')
                return f"{str(to_giga)} GB"

            elif text_id in ['Size']:
                qtt_bytes = int(value_to_convert)
                to_giga = format(qtt_bytes/(1024**3), '.2f')
                return f"{str(to_giga)} GB"

            elif text_id in ['SMBIOSMemoryType']:
                type_dict = {
                    20: 'DDR', 
                    21: 'DDR2', 
                    22: 'DDR2 FB-DIMM', 
                    24: 'DDR3', 
                    26: 'DDR4'
                }
                # Identifica a numeração caso exista na lista
                select_type = type_dict.get(value_to_convert)
                return str(select_type)

            elif text_id in ['Speed']:
                return f"{str(value_to_convert)} Mhz"

            else:
                return str(value_to_convert)

        # Estrutura de criação dos widgets e do posicionamento na janela
        for position, widget in enumerate(self.widgets):
            # Obtém os dados do widget
            widget_text = widget["Caption"]
            widget_name = widget["Name"]

            wmi_widget = Frame(self.container_main)
            wmi_widget.grid(row=position) # Define um posicionamento ordenado

            title = Label(wmi_widget)
            title["text"] = widget_text
            title["font"] = ("Segoe UI", "9", "bold")
            title.grid(row=0, column=0, columnspan=2)

            # Obtém a lista de objetos do WMI
            wmi_objects = self.wmi_data_collection[widget_name]
            if wmi_objects:
                matrix = [] # Cria uma lista para matriz de dados

                # ETAPA 1: Busca todos os valores do objeto e guarda na matriz
                for wmi_object in wmi_objects:
                    values = [] # Cria uma lista para receber os valores
                    # Faz uma varredura nos atributos do objeto
                    for key in widget["Keys"]:
                        get_value = str(getattr(wmi_object, key))
                        # Faz a conversão do valor para exibição
                        value = text_converter(key, get_value)
                        values.append(value)
                    matrix.append(values) # Salva a lista de valores na matriz

                # ETAPA 2: Ordena os valores por chave e padroniza os valores
                # Transpõe a matriz de dados para ordenar os valores da mesma chave
                matrix_t = np.array(matrix).T
                for values in matrix_t:
                    max_length = len(values[0]) # Assume a primeira como a maior
                    for value in values:
                        str_length = len(value)
                        if str_length > max_length:
                            max_length = str_length # Se a atual for maior, troca o valor

                    # Depois de obter o maior comprimento, centraliza todas as strings
                    for i in range(len(values)):
                        values[i] = values[i].center(max_length)

                # ETAPA 3: Retorna a matriz para o formato original e exibe os valores
                matrix = np.array(matrix_t).T
                for row_counter, values in enumerate(matrix, start=1):
                    values_str = " | ".join(values) # Faz a junção dos valores

                    item = Text(wmi_widget)
                    item["wrap"] = 'none'
                    item["bd"] = 0 # Espessura de borda
                    item["bg"] = wmi_widget.cget('bg')
                    item["font"] = ("Courier", "8") # Fonte monoespaçada
                    item.insert(END, values_str) # Insere um texto na caixa de texto
                    self.adjust_textbox_size(item) # Ajusta o tamanho da caixa de texto
                    item.config(state='disabled') # Desabilita a edição de texto
                    item.grid(row=row_counter, column=0)

                    # Cria um botão para copiar o texto com o ícone
                    copy_button = Button(wmi_widget)
                    copy_button["width"] = 10
                    copy_button["height"] = 10
                    copy_button["bd"] = 0
                    copy_button["image"] = self.copy_icon # Insere o ícone
                    copy_button["command"] = lambda txt=item: self.text_copy(txt)
                    """
                    Função lambda:
                    Isso passa a 'Text' associada ao botão como argumento para a função 
                    'text_copy'.
                    """
                    copy_button.grid(row=row_counter, column=1, padx=10)
            else:
                # Para o caso de não existirem dados
                item = Text(wmi_widget)
                item["wrap"] = 'none'
                item["bd"] = 0
                item["bg"] = wmi_widget.cget('bg')
                item["font"] = ("Courier", "8")
                item.insert(END, "Indisponível")
                self.adjust_textbox_size(item)
                item.config(state='disabled')
                item.grid(row=1, column=0, columnspan=2)

            # Cria um BooleanVar para controle no menu
            check_widget = BooleanVar(value=widget["Visible"])
            self.wmi_widgets_collection[widget_name] = {
                "check": check_widget,
                "grid_info": wmi_widget.grid_info(),
                "widget": wmi_widget
            } # Armazena os dados do widget
            self.toggle_widget(widget_name) # Padroniza a visualização inicial
            # Adiciona o controle de opção ao menu "Exibir"
            self.menu_display.add_checkbutton(
                label=widget_text,
                variable=check_widget,
                command=lambda key=widget_name: self.toggle_widget(key)
            )
        
    # Alterna a visibilidade do widget com base no estado do checkbutton
    def toggle_widget(self, key):
        element = self.wmi_widgets_collection[key]
        widget = element["widget"]

        # Busca os dados no arquivo JSON
        widget_settings = self.find_widget("Name", key)

        if element["check"].get():
            # Reexibe o widget com as opções de empacotamento originais
            widget.grid(**element["grid_info"])
            widget_settings["Visible"] = "True"
        else:
            widget.grid_forget() # Esconde o widget
            widget_settings["Visible"] = "False"

    # Busca as configurações do widget no arquivo JSON carregado
    def find_widget(self, key, value):
        # A função 'next()' para a busca assim que encontrar o widget desejado
        return next(
            # Expressão geradora que verifica item a item
            (widget for widget in self.widgets if widget[key] == value), 
            None # Caso não exista
        )

    # Função para copiar o texto
    def text_copy(self, text_box):
        text = text_box.get("1.0", "end-1c") # Obtém o conteúdo diretamente do Text
        self.master.clipboard_clear() # Limpa a área de transferência
        self.master.clipboard_append(text) # Adiciona o texto à área de transferência

    # Ajusta o espaçamento da caixa de texto na janela
    def adjust_textbox_size(self, text_box=None):
        get_text = text_box.get("1.0", "end-1c")

        # Se o conteúdo estiver vazio, define dimensões mínimas
        if not get_text:
            text_box.config(width=10, height=1)
            return

        lines = get_text.split("\n") # Quebra o conteúdo em linhas

        # Calcula a largura da linha mais longa
        max_line_length = max(len(line) for line in lines)

        # Define a largura e a altura baseada no conteúdo
        text_box.config(width=max_line_length, height=len(lines))

# Estrutura de execução
if __name__ == "__main__":
    root = Tk()
    Application(root)
    root.mainloop()