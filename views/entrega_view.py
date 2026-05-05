import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

class TelaEntrega(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title("Registrar Entrega de Uniforme")
        self.geometry("500x550")
        self.grab_set()
        self.lift()
        self.focus_force()

        # --- BUSCAR DADOS PARA OS MENUS ---
        # O controller buscará os dicionários {Nome: ID} do model
        self.alunos_dict = self.controller.get_lista_alunos_entrega()
        self.uniformes_dict = self.controller.get_lista_uniformes_entrega()

        # --- INTERFACE ---
        ctk.CTkLabel(self, text="Nova Saída de Material", font=("Roboto", 20, "bold")).pack(pady=20)

        # Seleção de Aluno
        ctk.CTkLabel(self, text="Selecione o Aluno:").pack(pady=5)
        self.combo_aluno = ctk.CTkComboBox(self, values=list(self.alunos_dict.keys()), width=350)
        self.combo_aluno.pack(pady=5)

        # --- A MÁGICA DO FILTRO ---
        # Detecta quando o usuário solta uma tecla dentro do combo
        self.combo_aluno.bind('<KeyRelease>', self.filtrar_alunos_combo)

        # Seleção de Uniforme
        ctk.CTkLabel(self, text="Selecione o Item (Estoque Atual):").pack(pady=5)
        self.combo_item = ctk.CTkComboBox(self, values=list(self.uniformes_dict.keys()), width=350)
        self.combo_item.pack(pady=5)

        self.frame_lancamento = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_lancamento.pack(pady=10)

        # Container da Quantidade (Esquerda)
        self.frame_qtd = ctk.CTkFrame(self.frame_lancamento, fg_color="transparent")
        self.frame_qtd.pack(side="left", padx=10)

        ctk.CTkLabel(self.frame_qtd, text="Quantidade:").pack()
        self.entry_qtd = ctk.CTkEntry(self.frame_qtd, placeholder_text="Ex: 1",width=80)
        self.entry_qtd.pack()

        # Container da Data (Direita)
        self.frame_data = ctk.CTkFrame(self.frame_lancamento, fg_color="transparent")
        self.frame_data.pack(side="left", padx=10)

        ctk.CTkLabel(self.frame_data, text="Data:").pack()
        self.entry_data = ctk.CTkEntry(self.frame_data, width=90)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_data.pack()

        # Botão Confirmar
        self.btn_confirmar = ctk.CTkButton(self, text="Confirmar Entrega",
                                           fg_color="#1f6aa5", height=45,
                                           command=self.ao_clicar_confirmar)
        self.btn_confirmar.pack(pady=30)

    def ao_clicar_confirmar(self):
        # Traduz o texto selecionado no combo para o ID real do banco
        aluno_id = self.alunos_dict.get(self.combo_aluno.get())
        uniforme_id = self.uniformes_dict.get(self.combo_item.get())
        qtd = self.entry_qtd.get()
        data = self.entry_data.get()

        self.controller.realizar_entrega(self, aluno_id, uniforme_id, qtd, data)

    def filtrar_alunos_combo(self, event):
        # 1. Pega o que o usuário já digitou
        termo_digitado = self.combo_aluno.get().lower()

        # 2. Filtra as chaves do dicionário de alunos
        # Mostra apenas os alunos que contém o texto digitado
        novos_valores = [nome for nome in self.alunos_dict.keys() if termo_digitado in nome.lower()]

        # 3. Atualiza os valores do ComboBox
        if novos_valores:
            self.combo_aluno.configure(values=novos_valores)
        else:
            self.combo_aluno.configure(values=["Nenhum aluno encontrado"])