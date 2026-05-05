import customtkinter as ctk
from tkinter import ttk, messagebox

class TelaUniformes(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title("Gerenciamento de Estoque de Uniformes")
        self.geometry("850x650")

        # Foco e Janela modal
        self.lift()
        self.focus_force()
        self.grab_set()

        # --- BARRA DE PESQUISA ---
        self.frame_busca = ctk.CTkFrame(self)
        self.frame_busca.pack(pady=10, padx=20, fill="x")

        self.ent_busca = ctk.CTkEntry(self.frame_busca, placeholder_text="Pesquisar uniforme por nome...", width=400)
        self.ent_busca.pack(side="left", padx=10, pady=10)

        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="Buscar", width=100, command=self.filtrar)
        self.btn_buscar.pack(side="left", padx=5)

        # --- FORMULÁRIO DE CADASTRO (Novo Item) ---
        self.frame_cad = ctk.CTkFrame(self)
        self.frame_cad.pack(pady=20, padx=20, fill="x")

        (ctk.CTkLabel(self.frame_cad, text="Novo Uniforme:", font=("Roboto", 12, "bold")).grid(row=0, column=0, padx=10, sticky="w"))

        self.ent_item = ctk.CTkEntry(self.frame_cad, placeholder_text="Descrição (Ex: Calça)", width=250)
        self.ent_item.grid(row=1, column=0, padx=10, pady=5)

        self.ent_tam = ctk.CTkEntry(self.frame_cad, placeholder_text="Tamanho", width=80)
        self.ent_tam.grid(row=1, column=1, padx=10, pady=10)

        self.ent_qtd = ctk.CTkEntry(self.frame_cad, placeholder_text="Qtd", width=80)
        self.ent_qtd.grid(row=1, column=2, padx=10, pady=10)

        self.btn_add = ctk.CTkButton(self.frame_cad, text="Cadastrar", fg_color="green",
                                     command=self.ao_clicar_salvar)
        self.btn_add.grid(row=1, column=3, padx=10, pady=10)

        # --- TABELA DE ESTOQUE ---
        style = ttk.Style()
        style.configure("Treeview", rowheight=35, background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")

        self.tabela = ttk.Treeview(self, columns=("ID", "Item", "Tamanho", "Quantidade"), show="headings")
        self.tabela.heading("ID", text="ID", anchor="center")
        self.tabela.heading("Item", text="Item/Descrição", anchor="w")
        self.tabela.heading("Tamanho", text="Tam", anchor="center")
        self.tabela.heading("Quantidade", text="Em Estoque", anchor="center")

        self.tabela.column("ID", width=50, anchor="center")
        self.tabela.column("Item", width=350, anchor="w")
        self.tabela.column("Tamanho", width=100, anchor="center")
        self.tabela.column("Quantidade", width=120, anchor="center")

        self.tabela.pack(expand=True, fill="both", padx=20, pady=10)

        # Vínculo do Clique Duplo
        self.tabela.bind("<Double-1>", self.abrir_edicao_uniforme)

        self.filtrar()  # Carrega os dados iniciais

    def filtrar(self):
        termo = self.ent_busca.get()
        self.controller.atualizar_tabela_uniformes(self, termo)

    def ao_clicar_salvar(self):
        self.controller.cadastrar_uniforme(self, self.ent_item.get(), self.ent_tam.get(), self.ent_qtd.get())

    def abrir_edicao_uniforme(self, event):
        item = self.tabela.selection()
        if not item: return
        dados = self.tabela.item(item)['values']
        JanelaEdicaoUniforme(self, self.controller, dados)


# --- JANELA DE EDIÇÃO, EXCLUSÃO E ENTRADA ---
class JanelaEdicaoUniforme(ctk.CTkToplevel):
    def __init__(self, parent, controller, dados):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.id_item = dados[0]  # Pega o ID

        self.title("Editar Uniforme / Entrada")
        self.geometry("450x550")
        self.grab_set()

        ctk.CTkLabel(self, text="Editar Cadastro", font=("Roboto", 18, "bold")).pack(pady=15)

        self.ent_item = ctk.CTkEntry(self, width=300)
        self.ent_item.insert(0, dados[1])
        self.ent_item.pack(pady=5)

        self.ent_tam = ctk.CTkEntry(self, width=300)
        self.ent_tam.insert(0, dados[2])
        self.ent_tam.pack(pady=5)

        self.ent_qtd = ctk.CTkEntry(self, width=300)
        self.ent_qtd.insert(0, dados[3])
        self.ent_qtd.pack(pady=5)

        ctk.CTkButton(self, text="Salvar Alterações", command=self.salvar).pack(pady=10)

        # Seção de Entrada (Soma)
        ctk.CTkLabel(self, text="--- Dar Entrada em Novo Lote ---", font=("Roboto", 14)).pack(pady=(20, 5))
        self.ent_soma = ctk.CTkEntry(self, placeholder_text="Quantidade para somar", width=300)
        self.ent_soma.pack(pady=5)

        ctk.CTkButton(self, text="Confirmar Entrada", fg_color="orange", hover_color="#b37400",
                      command=self.entrada).pack(pady=5)

        ctk.CTkButton(self, text="Excluir Item do Sistema", fg_color="red", command=self.excluir).pack(pady=30)

    def salvar(self):
        self.controller.editar_uniforme(self, self.id_item, self.ent_item.get(), self.ent_tam.get(), self.ent_qtd.get())
        self.parent.filtrar()

    def entrada(self):
        self.controller.processar_entrada_estoque(self, self.id_item, self.ent_soma.get())
        self.parent.filtrar()

    def excluir(self):
        if self.controller.excluir_uniforme(self.id_item):
            self.parent.filtrar()
            self.destroy()
