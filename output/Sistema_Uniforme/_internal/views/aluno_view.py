import customtkinter as ctk
from tkinter import ttk, messagebox

class TelaAlunos(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title("Gerenciamento de Alunos")
        self.geometry("800x650")

        self.lift()
        self.focus_force()
        self.grab_set()

        # --- BARRA DE PESQUISA ---
        self.frame_busca = ctk.CTkFrame(self)
        self.frame_busca.pack(pady=10, padx=20, fill="x")

        self.ent_busca = ctk.CTkEntry(self.frame_busca, placeholder_text="Pesquisar aluno por nome...", width=400)
        self.ent_busca.pack(side="left", padx=10, pady=10)

        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="Buscar", width=100, command=self.filtrar)
        self.btn_buscar.pack(side="left", padx=5)

        # --- FORMULÁRIO DE INCLUSÃO ---
        self.frame_cad = ctk.CTkFrame(self)
        self.frame_cad.pack(pady=10, padx=20, fill="x")

        self.ent_nome = ctk.CTkEntry(self.frame_cad, placeholder_text="Nome do Novo Aluno", width=250)
        self.ent_nome.grid(row=0, column=0, padx=10, pady=15)

        self.ent_matricula = ctk.CTkEntry(self.frame_cad, placeholder_text="Matricula", width=100)
        self.ent_matricula.grid(row=0, column=1, padx=10, pady=15)

        self.ent_ano = ctk.CTkEntry(self.frame_cad, placeholder_text="Ano", width=50)
        self.ent_ano.grid(row=0, column=2, padx=10, pady=15)

        self.btn_add = ctk.CTkButton(self.frame_cad, text="Incluir Aluno", fg_color="green",
                                     command=self.ao_clicar_incluir)
        self.btn_add.grid(row=0, column=3, padx=10, pady=15)

        # --- TABELA DE ALUNOS ---
        style = ttk.Style()
        style.configure("Treeview", rowheight=35, background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")

        self.tabela = ttk.Treeview(self, columns=("ID", "Nome", "Matricula", "Ano"), show="headings")
        self.tabela.heading("ID", text="ID", anchor="center")
        self.tabela.heading("Nome", text="Nome Completo", anchor="w")
        self.tabela.heading("Matricula", text="Matrícula", anchor="center")
        self.tabela.heading("Ano", text="Ano", anchor="center")

        self.tabela.column("ID", width=50, anchor="center")
        self.tabela.column("Nome", width=400, anchor="w")
        self.tabela.column("Matricula", width=100, anchor="center")
        self.tabela.column("Ano", width=100, anchor="center")

        self.tabela.pack(expand=True, fill="both", padx=20, pady=10)
        self.tabela.bind("<Double-1>", self.abrir_edicao_aluno)

        self.filtrar()  # Carrega os dados iniciais

    def filtrar(self):
        termo = self.ent_busca.get()
        self.controller.atualizar_tabela_alunos(self, termo)

    def ao_clicar_incluir(self):
        self.controller.cadastrar_aluno(self, self.ent_nome.get(), self.ent_matricula.get(), self.ent_ano.get())

    def abrir_edicao_aluno(self, event):
        it = self.tabela.selection()
        if not it: return
        dados = self.tabela.item(it)['values']
        JanelaEdicaoAluno(self, self.controller, dados)


# --- JANELA DE EDIÇÃO/EXCLUSÃO ---
class JanelaEdicaoAluno(ctk.CTkToplevel):
    def __init__(self, parent, controller, dados):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.id_aluno = dados[0]

        self.title("Editar Aluno")
        self.geometry("400x350")
        self.lift()
        self.grab_set()
        self.focus_force()

        ctk.CTkLabel(self, text="Editar Cadastro", font=("Roboto", 18, "bold")).pack(pady=20)

        self.ent_nome = ctk.CTkEntry(self, width=300)
        self.ent_nome.insert(0, dados[1])
        self.ent_nome.pack(pady=10)

        self.ent_matricula = ctk.CTkEntry(self, width=300)
        self.ent_matricula.insert(0, dados[2])
        self.ent_matricula.pack(pady=10)

        self.ent_ano = ctk.CTkEntry(self, width=300)
        self.ent_ano.insert(0, dados[3])
        self.ent_ano.pack(pady=10)

        ctk.CTkButton(self, text="Salvar Alterações", command=self.salvar).pack(pady=10)
        ctk.CTkButton(self, text="Excluir Aluno", fg_color="red", command=self.excluir).pack(pady=10)

    def salvar(self):
        self.controller.editar_aluno(self, self.id_aluno, self.ent_nome.get(), self.ent_matricula.get(), self.ent_ano.get())
        self.parent.filtrar()

    def excluir(self):
        if self.controller.excluir_aluno(self.id_aluno):
            self.parent.filtrar()
            self.destroy()
