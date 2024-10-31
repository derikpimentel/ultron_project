import time
import threading
from tkinter import *
from tkinter.ttk import Progressbar
import pythoncom
from wmi import WMI

widgets = [
    {
        "Caption": "Processador",
        "Class": "Win32_Processor",
        "Keys": [
            "Name"
        ],
        "Name": "Processor",
        "Visible": True
    },
    {
        "Caption": "Memória",
        "Class": "Win32_PhysicalMemory",
        "Keys": [
            "Capacity",
            "SMBIOSMemoryType",
            "Speed",
            "Manufacturer",
            "PartNumber",
            "SerialNumber"
        ],
        "Name": "PhysicalMemory",
        "Visible": True
    },
    {
        "Caption": "Unidade de Leitor Óptico",
        "Class": "Win32_CDROMDrive",
        "Keys": [
            "Name"
        ],
        "Name": "CDROMDrive",
        "Visible": True
    },
    {
        "Caption": "Unidade de Disco Rígido",
        "Class": "Win32_DiskDrive",
        "Filter": [
            "MediaType",
            "LIKE",
            "'Fixed%'"
        ],
        "Keys": [
            "Size",
            "Model"
        ],
        "Name": "DiskDrive",
        "Visible": True
    },
    {
        "Caption": "Controlador de Vídeo",
        "Class": "Win32_VideoController",
        "Keys": [
            "AdapterRAM",
            "Name",
            "VideoProcessor"
        ],
        "Name": "VideoController",
        "Visible": True
    },
    {
        "Caption": "Controlador de Rede",
        "Class": "Win32_NetworkAdapter",
        "Filter": [
            "PhysicalAdapter",
            "=",
            "'1'",
            "AND",
            "PNPDeviceID",
            "LIKE",
            "'PCI\\%'"
        ],
        "Keys": [
            "NetConnectionID",
            "MACAddress",
            "Name"
        ],
        "Name": "NetworkAdapter",
        "Visible": True
    },
    {
        "Caption": "BIOS",
        "Class": "Win32_BIOS",
        "Keys": [
            "Manufacturer",
            "Name",
            "SerialNumber"
        ],
        "Name": "BIOS",
        "Visible": False
    },
    {
        "Caption": "Sistema do Computador",
        "Class": "Win32_ComputerSystem",
        "Keys": [
            "Manufacturer",
            "Model",
            "SystemFamily"
        ],
        "Name": "ComputerSystem",
        "Visible": False
    },
    {
        "Caption": "Sistema Operacional",
        "Class": "Win32_OperatingSystem",
        "Keys": [
            "Caption"
        ],
        "Name": "OperatingSystem",
        "Visible": False
    },
    {
        "Caption": "Chave de Licença do Windows",
        "Class": "SoftwareLicensingService",
        "Keys": [
            "OA3xOriginalProductKey"
        ],
        "Name": "SoftwareLicensingService",
        "Visible": False
    },
    {
        "Caption": "Software de Segurança",
        "Class": "AntiVirusProduct",
        "Keys": [
            "displayName"
        ],
        "Name": "AntiVirusProduct",
        "Namespace": "root\\SecurityCenter2",
        "Visible": False
    },
    {
        "Caption": "Programas Instalados",
        "Class": "Win32_Product",
        "Keys": [
            "Name"
        ],
        "Name": "Product",
        "Visible": False
    },
    {
        "Caption": "Chave de Licença do Office",
        "Class": "SoftwareLicensingProduct",
        "Filter": [
            "LicenseStatus",
            "=",
            "'1'",
            "AND",
            "Name",
            "LIKE",
            "'Office%'"
        ],
        "Keys": [
            "Name",
            "PartialProductKey"
        ],
        "Name": "SoftwareLicensingProduct",
        "Visible": False
    }
]

# Estrutura da janela
class Application:
    def __init__(self, master=None):
        self.master = master # Faz a passagem da variável "root"
        self.master.title("Ultron") # Altera o título da janela
        self.master.geometry("300x75") # Define as dimensões da janela (L x A)
        self.master.overrideredirect(True) # Remove a barra superior

        self.wmi_data_collection = {} # Armazena os dados coletados do WMI

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
        """
        A função "pythoncom.CoInitialize()" corrige um problema ao qual garante que o COM seja 
        inicializado antes de fazer qualquer chamada WMI dentro de uma Thread.
        """
        pythoncom.CoInitialize() # Inicializa o COM para a Thread
        try:
            qtt_widgets = len(widgets) # Obtém a quantidade total de widgets
            # Estrutura de carregamento da barra de progresso
            for i, widget in enumerate(widgets, start=1):
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
        self.create_wmi_widgets() # Carrega os widgets do WMI na janela

        self.container_footer = Frame(self.main_screen)
        self.container_footer.pack()
        self.label_info = Label(self.container_footer)
        self.label_info["text"] = "Desenvolvido por Derik B. Pimentel"
        self.label_info.pack()
        # início do "main_screen"

        self.master.deiconify() # Mostra a janela novamente

    # Função que cria os widgets do WMI dinâmicamente na janela
    def create_wmi_widgets(self):
        for widget in widgets:
            # Obtém os dados do widget
            widget_text = widget["Caption"]
            widget_name = widget["Name"]
            widget_keys = widget["Keys"]
            widget_show = widget["Visible"]

            # Exibe os widgets habilitados
            if widget_show:
                wmi_widget = Frame(self.container_main)
                wmi_widget.pack()

                title = Label(wmi_widget)
                title["text"] = widget_text
                title["font"] = ("Segoe UI", "9", "bold")
                title.pack()

                # Obtém a lista de objetos do WMI
                wmi_objects = self.wmi_data_collection[widget_name]
                if wmi_objects:
                    for wmi_object in wmi_objects:

                        values = []
                        # Faz uma varredura nos atributos do objeto
                        for key in widget_keys:
                            value_str = str(getattr(wmi_object, key))
                            values.append(value_str)
                        values_str = " ".join(values) # Junta os valores

                        item = Text(wmi_widget, height=1, width=50)
                        item["wrap"] = 'none'
                        item["bd"] = 0 # Espessura de borda da caixa
                        item["bg"] = wmi_widget.cget('bg')
                        item["font"] = ("Segoe UI", "8")
                        item.insert(END, values_str) # Insere um texto na caixa de texto
                        item.config(state='disabled') # Desabilita a edição de texto
                        item.pack()
                else:
                    # Para o caso de não existirem dados
                    item = Text(wmi_widget, height=1, width=50)
                    item["wrap"] = 'none'
                    item["bd"] = 0
                    item["bg"] = wmi_widget.cget('bg')
                    item["font"] = ("Segoe UI", "8")
                    item.insert(END, "Indisponível")
                    item.config(state='disabled')
                    item.pack()

# Estrutura de execução
if __name__ == "__main__":
    root = Tk()
    Application(root)
    root.mainloop()