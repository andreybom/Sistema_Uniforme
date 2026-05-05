from tkinter import messagebox
from datetime import datetime

class AppController:
    def __init__(self, model):
        self.model = model
        # Referências para as views (serão definidas ao abrir as janelas)
        self.main_view = None

    # --- LÓGICA PARA ALUNOS ---
    def cadastrar_aluno(self, view_ref, nome, matricula, ano):
        """Valida os dados e solicita ao model para salvar."""
        if not nome or not ano:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return

        try:
            self.model.salvar_aluno(nome, matricula, ano)
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")

            # Após salvar, limpa os campos na View e atualiza a lista
            view_ref.ent_nome.delete(0, 'end')
            view_ref.ent_matricula.delete(0, 'end')
            view_ref.ent_ano.delete(0, 'end')
            self.atualizar_tabela_alunos(view_ref)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")

    def atualizar_tabela_alunos(self, view_ref, busca=""):
        # Limpa a tabela
        for item in view_ref.tabela.get_children():
            view_ref.tabela.delete(item)

        # Busca dados no Model com o filtro
        alunos = self.model.listar_alunos(busca)

        # Insere na View
        for aluno in alunos:
            view_ref.tabela.insert("", "end", values=aluno)

    def editar_aluno(self, view_ref, id_aluno, nome, matricula, ano):
        if not nome or not matricula:
            messagebox.showwarning("Aviso", "Campos não podem ficar vazios!")
            return

        try:
            self.model.atualizar_aluno(id_aluno, nome, matricula, ano)
            messagebox.showinfo("Sucesso", "Cadastro do aluno atualizado!")
            view_ref.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível atualizar: {e}")

    def excluir_aluno(self, id_aluno):
        # 1. Verifica se o aluno possui vínculos
        if self.model.aluno_tem_entregas(id_aluno):
            messagebox.showerror("Erro de Integridade",
                                 "Não é possível excluir este aluno pois ele possui histórico de entregas.\n"
                                 "Para excluí-lo, você deve primeiro apagar as entregas dele no relatório.")
            return False

        if messagebox.askyesno("Confirmar",
                               "Deseja realmente excluir este aluno?\nIsso pode afetar o histórico de entregas."):
            try:
                self.model.excluir_aluno(id_aluno)
                messagebox.showinfo("Sucesso", "Aluno removido!")
                return True
            except Exception as e:
                print(e)
                messagebox.showerror("Erro", "Não é possível excluir um aluno que possui histórico de uniformes.")
                return False
        return False

    def cadastrar_uniforme(self, view_ref, item, tamanho, qtd):
        if not item or not tamanho or not qtd:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        try:
            self.model.salvar_uniforme(item, tamanho, int(qtd))
            messagebox.showinfo("Sucesso", "Item adicionado ao estoque!")
            view_ref.ent_item.delete(0, 'end')
            view_ref.ent_tam.delete(0, 'end')
            view_ref.ent_qtd.delete(0, 'end')
            self.atualizar_tabela_uniformes(view_ref)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número!")

    def atualizar_tabela_uniformes(self, view_ref, busca=""):
        # Limpa tabela na tela
        for item in view_ref.tabela.get_children():
            view_ref.tabela.delete(item)

        # Chama o model com o termo de busca
        uniformes = self.model.listar_uniformes(busca)
        for u in uniformes:
            view_ref.tabela.insert("", "end", values=u)

    def get_lista_alunos_entrega(self):
        alunos = self.model.listar_alunos()
        return {f"{a[1]} (Mat: {a[2]})": a[0] for a in alunos}

    def get_lista_uniformes_entrega(self):
        uniformes = self.model.listar_uniformes()
        # Exibe item, tamanho e estoque disponível no menu
        return {f"{u[1]} - {u[2]} (Qtd: {u[3]})": u[0] for u in uniformes}

    def realizar_entrega(self, view_ref, aluno_id, uniforme_id, qtd, data_str):
        # 1. Validação básica de preenchimento
        if not all([aluno_id, uniforme_id, qtd, data_str]):
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios!")
            return

        # 2. Validação rigorosa da Data
        try:
            datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Data Inválida", f"A data '{data_str}' é inválida.\nUse o formato DD/MM/AAAA")
            return

        # 3. Validação da Quantidade (Inteiro e Positivo)
        try:
            qtd_int = int(qtd)
            if qtd_int <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número inteiro maior que zero!")
            return

        # 4. Execução da Transação no Model
        sucesso = self.model.registrar_entrega(aluno_id, uniforme_id, qtd_int, data_str)

        if sucesso:
            messagebox.showinfo("Sucesso", "Entrega realizada com sucesso!")

            # --- MELHORIA DE UX ---
            # Limpa os campos para evitar duplicidade acidental
            view_ref.entry_qtd.delete(0, 'end')
            view_ref.combo_item.set("")  # Limpa a seleção do uniforme

            # Atualiza a lista interna e o visual do ComboBox com o estoque novo
            view_ref.uniformes_dict = self.get_lista_uniformes_entrega()
            view_ref.combo_item.configure(values=list(view_ref.uniformes_dict.keys()))

            # Coloca o foco de volta na quantidade para a próxima entrega
            view_ref.entry_qtd.focus()
        else:
            # Se o model retornar False, geralmente é porque o estoque acabou entre o clique e o processamento
            messagebox.showerror("Erro", "Estoque insuficiente para realizar esta entrega.")

    def atualizar_tabela_relatorio(self, view_ref, busca=""):
        # Limpa a tabela atual
        for item in view_ref.tabela.get_children():
            view_ref.tabela.delete(item)

        # Busca dados (com ou sem filtro)
        entregas = self.model.listar_relatorio_entregas(busca)

        for e in entregas:
            view_ref.tabela.insert("", "end", values=e)

    def processar_entrada_estoque(self, view_ref, uniforme_id, qtd):
        if not uniforme_id or not qtd:
            messagebox.showwarning("Aviso", "Selecione o uniforme e a quantidade!")
            return

        try:
            qtd_int = int(qtd)
            if qtd_int <= 0: raise ValueError

            if self.model.adicionar_estoque(uniforme_id, qtd_int):
                messagebox.showinfo("Sucesso", "Estoque atualizado com sucesso!")
                view_ref.destroy()  # Fecha a janelinha após somar
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar o banco de dados.")
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número inteiro positivo!")

    def excluir_registro_entrega(self, view_ref, dados_entrega):
        # dados_entrega contém: (ID_Entrega, Nome_Aluno, Item_Nome, Tam, Qtd, Data)
        id_entrega = dados_entrega[0]
        item_nome = dados_entrega[2]
        tamanho = dados_entrega[3]
        quantidade = dados_entrega[4]

        if messagebox.askyesno("Confirmar Estorno",
                               f"Deseja excluir esta entrega?\n\nItem: {item_nome}\nQtd: {quantidade}\n"
                               "O estoque será devolvido automaticamente."):

            # Precisamos do ID do uniforme. Vamos buscar pelo Nome e Tamanho no banco
            # ou simplificar buscando o ID_Uniforme que você pode adicionar na Query do relatório.
            conn = self.model._conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM uniformes WHERE item = ? AND tamanho = ?", (item_nome, tamanho))
            res = cursor.fetchone()
            conn.close()

            if res:
                id_uniforme = res[0]
                if self.model.excluir_entrega_estornar_estoque(id_entrega, id_uniforme, quantidade):
                    messagebox.showinfo("Sucesso", "Entrega excluída e estoque devolvido!")
                    self.atualizar_tabela_relatorio(view_ref, view_ref.ent_busca.get())
                else:
                    messagebox.showerror("Erro", "Falha ao processar o estorno.")
