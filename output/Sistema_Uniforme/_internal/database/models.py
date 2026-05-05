import os
import sys
import sqlite3

class SistemaModel:
    def __init__(self):
        # Detecta se está rodando como script ou como executável (.exe)
        if getattr(sys, 'frozen', False):
            # Caminho da pasta onde o .exe está
            diretorio_base = os.path.dirname(sys.executable)
        else:
            # Caminho da pasta onde o script .py está
            diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Volta um nível se o models.py estiver dentro da pasta database
            diretorio_base = os.path.dirname(diretorio_base)

        self.db_path = os.path.join(diretorio_base, "sistema_escola.db")
        self.init_db()

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Cria as tabelas caso não existam no início do sistema."""
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS alunos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL,
                            matricula TEXT NOT NULL,
                            ano TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS uniformes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item TEXT NOT NULL,
                            tamanho TEXT NOT NULL,
                            quantidade INTEGER NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS entregas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            aluno_id INTEGER,
                            uniforme_id INTEGER,
                            qtd_entregue INTEGER NOT NULL,
                            data TEXT NOT NULL,
                            FOREIGN KEY(aluno_id) REFERENCES alunos(id),
                            FOREIGN KEY(uniforme_id) REFERENCES uniformes(id))''')
        conn.commit()
        conn.close()

    # --- MÉTODOS PARA ALUNOS ---
    def salvar_aluno(self, nome, matricula, ano):
        conn = self._conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO alunos (nome, matricula, ano) VALUES (?, ?, ?)", (nome, matricula, ano))
        conn.commit()
        conn.close()

    def listar_alunos(self,busca=""):
        conn = self._conectar()
        cursor = conn.cursor()
        if busca.strip():
            # Busca por nome ou Ano usando o operador LIKE
            cursor.execute("SELECT * FROM alunos WHERE nome LIKE ? OR matricula LIKE ?",
                           (f"%{busca}%", f"%{busca}%"))
        else:
            cursor.execute("SELECT * FROM alunos")

        dados = cursor.fetchall()
        conn.close()
        return dados

    def atualizar_aluno(self, id_aluno, nome, matricula, ano):
        conn = self._conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE alunos SET nome = ?, matricula = ?, ano = ? WHERE id = ?", (nome, matricula, ano, id_aluno))
        conn.commit()
        conn.close()

    def aluno_tem_entregas(self, id_aluno):
        conn = self._conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM entregas WHERE aluno_id = ? LIMIT 1", (id_aluno,))
        tem_registro = cursor.fetchone() is not None
        conn.close()
        return tem_registro

    def excluir_aluno(self, id_aluno):
        conn = self._conectar()
        cursor = conn.cursor()
        # Nota: Cuidado ao excluir alunos que já possuem entregas registradas (pode causar erro de FK)
        cursor.execute("DELETE FROM alunos WHERE id = ?", (id_aluno,))
        conn.commit()
        conn.close()

    # --- MÉTODOS PARA UNIFORMES E ESTOQUE ---
    def listar_uniformes(self, busca=""):
        conn = self._conectar()
        cursor = conn.cursor()
        if busca.strip():
            # Busca por nome do item ou pelo tamanho
            # O % permite que encontre o texto em qualquer parte da descrição
            query = "SELECT * FROM uniformes WHERE item LIKE ? OR tamanho LIKE ?"
            params = (f"%{busca}%", f"%{busca}%")
            cursor.execute(query, params)
        else:
            # Se não houver busca, traz tudo em ordem alfabética por item
            cursor.execute("SELECT * FROM uniformes ORDER BY item ASC")

        dados = cursor.fetchall()
        conn.close()
        return dados

    def registrar_entrega(self, aluno_id, uniforme_id, qtd, data):
        conn = self._conectar()
        try:
            cursor = conn.cursor()

            # 1. Busca o estoque atual direto do banco para ter certeza
            cursor.execute("SELECT quantidade FROM uniformes WHERE id = ?", (uniforme_id,))
            resultado = cursor.fetchone()

            if not resultado or resultado[0] < qtd:
                return False  # Bloqueia a entrega se não houver estoque suficiente

            # 2. Se tem estoque, registra a entrega
            cursor.execute("INSERT INTO entregas (aluno_id, uniforme_id, qtd_entregue, data) VALUES (?, ?, ?, ?)",
                           (aluno_id, uniforme_id, qtd, data))

            # 3. Baixa no estoque
            cursor.execute("UPDATE uniformes SET quantidade = quantidade - ? WHERE id = ?", (qtd, uniforme_id))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro: {e}")
            return False
        finally:
            conn.close()

    # Adicionar ao SistemaModel:
    def salvar_uniforme(self, item, tamanho, quantidade):
        conn = self._conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO uniformes (item, tamanho, quantidade) VALUES (?, ?, ?)",
                       (item, tamanho, quantidade))
        conn.commit()
        conn.close()

    def listar_relatorio_entregas(self, busca=""):
        conn = self._conectar()
        cursor = conn.cursor()

        # Base da query
        # O JOIN une as tabelas para mostrar nomes em vez de IDs
        query = '''
            SELECT e.id, a.nome, u.item, u.tamanho, e.qtd_entregue, e.data
            FROM entregas e
            JOIN alunos a ON e.aluno_id = a.id
            JOIN uniformes u ON e.uniforme_id = u.id
        '''
        # Lógica de Ordenação (Converte DD/MM/AAAA para AAAA-MM-DD para o SQLite entender)
        # Substr pega: (string, posição_inicial, tamanho)
        ordenacao = '''
                ORDER BY 
                substr(e.data, 7, 4) || '-' || substr(e.data, 4, 2) || '-' || substr(e.data, 1, 2) DESC
            '''
        # Use DESC para as entregas mais recentes aparecerem primeiro
        # Use ASC se quiser que as mais antigas apareçam primeiro

        # Se houver busca, adiciona o filtro WHERE
        if busca.strip():
            query += " WHERE a.nome LIKE ? OR u.item LIKE ?"
            params = (f"%{busca}%", f"%{busca}%")
            query += ordenacao
            cursor.execute(query, params)
        else:
            query += ordenacao
            cursor.execute(query)

        dados = cursor.fetchall()
        conn.close()
        return dados

    def adicionar_estoque(self, uniforme_id, qtd):
        conn = self._conectar()
        try:
            cursor = conn.cursor()
            # Soma a nova quantidade à que já existe
            cursor.execute("UPDATE uniformes SET quantidade = quantidade + ? WHERE id = ?",
                           (qtd, uniforme_id))
            conn.commit()
            return True
        except Exception as e:
            print(e)
            conn.rollback()
            return False
        finally:
            conn.close()

    def excluir_entrega_estornar_estoque(self, id_entrega, id_uniforme, quantidade):
        conn = self._conectar()
        try:
            cursor = conn.cursor()
            # 1. Devolve a quantidade ao estoque do uniforme
            cursor.execute("UPDATE uniformes SET quantidade = quantidade + ? WHERE id = ?",
                           (quantidade, id_uniforme))

            # 2. Remove o registro da entrega
            cursor.execute("DELETE FROM entregas WHERE id = ?", (id_entrega,))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao estornar: {e}")
            return False
        finally:
            conn.close()
