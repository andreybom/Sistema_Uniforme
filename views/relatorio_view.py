import customtkinter as ctk
from tkinter import ttk

class TelaRelatorio(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Relatório de Entregas")
        self.geometry("900x600")

        self.grab_set()
        self.lift()
        self.focus_force()

        ctk.CTkLabel(self, text="Histórico de Uniformes Entregues", font=("Roboto", 20, "bold")).pack(pady=20)

        # --- BARRA DE PESQUISA ---
        self.frame_busca = ctk.CTkFrame(self)
        self.frame_busca.pack(pady=10, padx=20, fill="x")

        self.ent_busca = ctk.CTkEntry(self.frame_busca, placeholder_text="Pesquisar por aluno ou uniforme...",
                                      width=400)
        self.ent_busca.pack(side="left", padx=10, pady=10)

        # O botão chama a função de filtrar
        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="Pesquisar", width=100, command=self.filtrar)
        self.btn_buscar.pack(side="left", padx=5)

        # Botão para limpar a busca
        self.btn_limpar = ctk.CTkButton(self.frame_busca, text="Limpar", width=80, fg_color="gray",
                                        command=self.limpar_busca)
        self.btn_limpar.pack(side="left", padx=5)

        # 1. Crie o objeto de estilo
        style = ttk.Style()

        # 2. Configure a altura da linha (rowheight)
        # O valor 30 ou 35 costuma ficar muito elegante com CustomTkinter
        style.configure("Treview",
                        rowheight=35,
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        borderwidth=0)

        # Opcional: muda a cor quando a linha é selecionada
        style.configure("Treview", background=[('selected', '#1f538d')])

        # Configuração da Tabela
        self.tabela = ttk.Treeview(self, columns=("ID", "Aluno", "Item", "Tam", "Qtd", "Data"), show="headings")
        self.tabela.heading("ID", text="ID", anchor="center")
        self.tabela.heading("Aluno", text="Nome do Aluno")
        self.tabela.heading("Item", text="Uniforme")
        self.tabela.heading("Tam", text="Tam", anchor="center")
        self.tabela.heading("Qtd", text="Qtd", anchor="center")
        self.tabela.heading("Data", text="Data da Entrega", anchor="center")

        # Ajuste de larguras
        self.tabela.column("ID", width=40, anchor="center")
        self.tabela.column("Aluno", width=250)
        self.tabela.column("Item", width=200)
        self.tabela.column("Tam", width=50, anchor="center")
        self.tabela.column("Qtd", width=50, anchor="center")
        self.tabela.column("Data", width=120, anchor="center")

        self.tabela.pack(expand=True, fill="both", padx=20, pady=20)

        self.tabela.bind("<Double-1>", self.ao_clique_duplo_excluir)

        # Carregar dados
        self.filtrar()
        #self.controller.atualizar_tabela_relatorio(self)

    def filtrar(self):
        termo = self.ent_busca.get()
        self.controller.atualizar_tabela_relatorio(self, termo)

    def limpar_busca(self):
        self.ent_busca.delete(0, "end")
        self.filtrar()

    def ao_clique_duplo_excluir(self, event):
        item_selecionado = self.tabela.selection()
        if not item_selecionado:
            return

        dados = self.tabela.item(item_selecionado)['values']
        # Chama o controller para excluir
        self.controller.excluir_registro_entrega(self, dados)