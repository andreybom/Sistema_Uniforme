import customtkinter as ctk
from views.aluno_view import TelaAlunos
from views.uniforme_view import TelaUniformes
from views.entrega_view import TelaEntrega
from views.relatorio_view import TelaRelatorio

class MenuPrincipal(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Configurações da Janela Principal
        self.title("Sistema de Gestão de Uniformes Escolar")
        self.geometry("800x500")

        # Configurar layout de colunas (0 = Menu, 1 = Conteúdo)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- MENU LATERAL ---
        self.frame_menu = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")

        self.lbl_logo = ctk.CTkLabel(self.frame_menu, text="ESCOLA\n ZILDA ARNS", font=("Roboto", 20, "bold"))
        self.lbl_logo.pack(pady=30, padx=20)

        # Botão: Gerenciar Alunos
        self.btn_alunos = ctk.CTkButton(self.frame_menu, text="Gerenciar Alunos",
                                        command=self.abrir_alunos, height=40)
        self.btn_alunos.pack(pady=10, padx=20)

        # Botão: Cadastrar Uniformes
        self.btn_uniformes = ctk.CTkButton(self.frame_menu, text="Estoque Uniformes",
                                           command=self.abrir_uniformes, height=40)
        self.btn_uniformes.pack(pady=10, padx=20)

        # Botão: Registrar Entregas
        self.btn_entregas = ctk.CTkButton(self.frame_menu, text="Registrar Entrega",
                                          command=self.abrir_entregas, height=40,
                                          fg_color="#1f6aa5")
        self.btn_entregas.pack(pady=10, padx=20)

        self.btn_relatorio = ctk.CTkButton(self.frame_menu, text="Relatório Geral",
                                           command=self.abrir_relatorio, height=40)
        self.btn_relatorio.pack(pady=10, padx=20)

        # --- ÁREA CENTRAL (DASHBOARD) ---
        self.frame_dash = ctk.CTkFrame(self, corner_radius=15)
        self.frame_dash.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.lbl_welcome = ctk.CTkLabel(self.frame_dash, text="Painel de Controle de Uniformes",
                                        font=("Roboto", 24, "bold"))
        self.lbl_welcome.pack(pady=40)

        self.lbl_instrucao = ctk.CTkLabel(self.frame_dash,
                                          text="Selecione uma opção no menu lateral para começar.",
                                          font=("Roboto", 14))
        self.lbl_instrucao.pack()

    # --- MÉTODOS PARA ABRIR AS TELAS ---
    def abrir_alunos(self):
        TelaAlunos(self, self.controller)

    def abrir_uniformes(self):
        TelaUniformes(self, self.controller)

    def abrir_entregas(self):
        TelaEntrega(self, self.controller)

    def abrir_relatorio(self):
        TelaRelatorio(self, self.controller)
