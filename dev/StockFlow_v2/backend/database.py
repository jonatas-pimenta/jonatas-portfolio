#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STOCKFLOW - FLUXO DE ESTOQUE COM CRIPTOGRAFIA E BACKUP EM NUVEM
"""

import datetime
import sqlite3
from typing import Dict, List, Optional

import bcrypt
import pandas as pd


class EstoqueDB:
    """Classe para gerenciar operações do banco de dados relacional SQLite."""

    def __init__(self, db_path: str = "estoque.db"):
        """Inicializa a conexão com o SQLite e cria tabelas se necessário."""
        try:
            self.conexao = sqlite3.connect(db_path)
            self.conexao.row_factory = sqlite3.Row
            self.conexao.execute("PRAGMA foreign_keys = ON")
            self._criar_tabelas()
            self._migrar_campos_contato()
            self._garantir_usuarios_padrao()
            self._normalizar_usuarios_movimentacoes_historicas()
            print(f"✅ Conexão com SQLite estabelecida ({db_path})")
        except Exception as e:
            print(f"❌ Erro na conexão com SQLite: {e}")
            raise

    def _criar_tabelas(self) -> None:
        """Cria o esquema relacional do sistema."""
        with self.conexao:
            self.conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    categoria TEXT NOT NULL,
                    preco REAL NOT NULL,
                    quantidade INTEGER NOT NULL,
                    estoque_minimo INTEGER NOT NULL,
                    fornecedor TEXT NOT NULL,
                    data_cadastro TEXT NOT NULL
                )
                """
            )
            self.conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS movimentacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
                    quantidade INTEGER NOT NULL,
                    data_movimentacao TEXT NOT NULL,
                    observacao TEXT,
                    usuario TEXT NOT NULL,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
                )
                """
            )
            self.conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    perfil TEXT CHECK(perfil IN ('ADM', 'gerente', 'operador')) DEFAULT 'operador',
                    ativo BOOLEAN DEFAULT 1
                )
                """
            )
            self.conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS fornecedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    telefone_celular TEXT,
                    telefone_fixo TEXT,
                    email TEXT,
                    endereco TEXT,
                    observacao TEXT,
                    data_cadastro TEXT NOT NULL
                )
                """
            )
            self.conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    telefone_celular TEXT,
                    telefone_fixo TEXT,
                    email TEXT,
                    endereco TEXT,
                    observacao TEXT,
                    data_cadastro TEXT NOT NULL
                )
                """
            )

    def _coluna_existe(self, tabela: str, coluna: str) -> bool:
        rows = self.conexao.execute(f"PRAGMA table_info({tabela})").fetchall()
        return any(r["name"] == coluna for r in rows)

    def _migrar_campos_contato(self) -> None:
        """Garante colunas de contato atuais e preserva dados legados."""
        try:
            for tabela in ("fornecedores", "clientes"):
                with self.conexao:
                    if not self._coluna_existe(tabela, "telefone_celular"):
                        self.conexao.execute(
                            f"ALTER TABLE {tabela} ADD COLUMN telefone_celular TEXT"
                        )
                    if not self._coluna_existe(tabela, "telefone_fixo"):
                        self.conexao.execute(
                            f"ALTER TABLE {tabela} ADD COLUMN telefone_fixo TEXT"
                        )

                    # Compatibilidade com bases antigas que usavam apenas 'telefone'.
                    if self._coluna_existe(tabela, "telefone"):
                        self.conexao.execute(
                            f"""
                            UPDATE {tabela}
                            SET telefone_celular = COALESCE(NULLIF(TRIM(telefone_celular), ''), telefone)
                            WHERE telefone IS NOT NULL AND TRIM(telefone) <> ''
                            """
                        )
        except Exception as e:
            print(f"❌ Erro ao migrar campos de contato: {e}")

    @staticmethod
    def gerar_hash_senha(senha: str) -> str:
        """Gera hash bcrypt para armazenamento seguro de senha."""
        return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _garantir_usuarios_padrao(self) -> None:
        """Cria usuários padrão para facilitar login em demonstrações."""
        usuarios_padrao = [
            {"username": "Operador1", "perfil": "operador"},
            {"username": "Operador2", "perfil": "operador"},
            {"username": "Gerente", "perfil": "gerente"},
            {"username": "ADM", "perfil": "ADM"},
        ]

        for item in usuarios_padrao:
            existe = self.conexao.execute(
                "SELECT 1 FROM usuarios WHERE username = ?",
                (item["username"],),
            ).fetchone()

            if existe:
                continue

            senha_hash = self.gerar_hash_senha("123qwe")
            self.criar_usuario(item["username"], senha_hash, item["perfil"], sistema=True)

    def _usuario_ativo_existe(self, username: str) -> bool:
        row = self.conexao.execute(
            "SELECT 1 FROM usuarios WHERE username = ? AND ativo = 1",
            (username,),
        ).fetchone()
        return bool(row)

    def _normalizar_usuarios_movimentacoes_historicas(self) -> None:
        """Corrige usuários legados nas movimentações para usuários cadastrados ativos."""
        try:
            alias = {
                "admin": "ADM",
                "operador 1": "Operador1",
                "operador 2": "Operador2",
                "gerente": "Gerente",
                "adm": "ADM",
            }

            with self.conexao:
                # Primeiro, corrige aliases conhecidos.
                for origem, destino in alias.items():
                    if self._usuario_ativo_existe(destino):
                        self.conexao.execute(
                            """
                            UPDATE movimentacoes
                            SET usuario = ?
                            WHERE LOWER(TRIM(usuario)) = ?
                            """,
                            (destino, origem),
                        )

                # Depois, qualquer usuário sem cadastro ativo vira um usuário fallback válido.
                fallback = self.conexao.execute(
                    """
                    SELECT username
                    FROM usuarios
                    WHERE ativo = 1
                    ORDER BY CASE perfil WHEN 'ADM' THEN 1 WHEN 'gerente' THEN 2 ELSE 3 END, username
                    LIMIT 1
                    """
                ).fetchone()

                if fallback:
                    fallback_username = fallback["username"]
                    self.conexao.execute(
                        """
                        UPDATE movimentacoes
                        SET usuario = ?
                        WHERE usuario NOT IN (
                            SELECT username FROM usuarios WHERE ativo = 1
                        )
                        """,
                        (fallback_username,),
                    )
        except Exception as e:
            print(f"❌ Erro ao normalizar usuários das movimentações: {e}")

    @staticmethod
    def _normalizar_perfil(perfil: Optional[str]) -> str:
        return (perfil or "").strip().lower()

    def autenticar_usuario(self, username: str, senha: str) -> Optional[str]:
        """Autentica usuário e retorna seu perfil em caso de sucesso."""
        try:
            row = self.conexao.execute(
                """
                SELECT senha_hash, perfil
                FROM usuarios
                WHERE username = ? AND ativo = 1
                """,
                (username,),
            ).fetchone()

            if not row:
                return None

            senha_hash = row["senha_hash"].encode("utf-8")
            if bcrypt.checkpw(senha.encode("utf-8"), senha_hash):
                return row["perfil"]
            return None
        except Exception as e:
            print(f"❌ Erro ao autenticar usuário: {e}")
            return None

    def criar_usuario(
        self,
        username: str,
        senha_hash: str,
        perfil: str,
        executor_perfil: Optional[str] = None,
        sistema: bool = False,
    ) -> bool:
        """Cria usuário com hash de senha já processado."""
        try:
            if perfil not in {"ADM", "gerente", "operador"}:
                print("❌ Perfil inválido!")
                return False

            if not sistema:
                perfil_exec = self._normalizar_perfil(executor_perfil)
                if perfil_exec not in {"adm", "gerente"}:
                    print("❌ Permissão negada: apenas ADM/gerente podem criar usuários.")
                    return False
                if perfil_exec == "gerente" and perfil != "operador":
                    print("❌ Permissão negada: gerente só pode criar usuário operador.")
                    return False

            with self.conexao:
                self.conexao.execute(
                    """
                    INSERT INTO usuarios (username, senha_hash, perfil, ativo)
                    VALUES (?, ?, ?, 1)
                    """,
                    (username.strip(), senha_hash, perfil),
                )

            # Triggers para evitar que a quantidade de produtos fique negativa
            self.conexao.execute(
                """
                CREATE TRIGGER IF NOT EXISTS produtos_no_negative_insert
                BEFORE INSERT ON produtos
                FOR EACH ROW
                WHEN NEW.quantidade < 0
                BEGIN
                    SELECT RAISE(ABORT, 'quantidade nao pode ser negativa');
                END;
                """
            )
            self.conexao.execute(
                """
                CREATE TRIGGER IF NOT EXISTS produtos_no_negative_update
                BEFORE UPDATE ON produtos
                FOR EACH ROW
                WHEN NEW.quantidade < 0
                BEGIN
                    SELECT RAISE(ABORT, 'quantidade nao pode ser negativa');
                END;
                """
            )
            print(f"✅ Usuário '{username}' criado com sucesso!")
            return True
        except sqlite3.IntegrityError:
            print(f"❌ Usuário '{username}' já existe!")
            return False
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            return False

    def atualizar_usuario(
        self,
        username_original: str,
        novo_username: Optional[str] = None,
        novo_perfil: Optional[str] = None,
        nova_senha_hash: Optional[str] = None,
        executor_perfil: Optional[str] = None,
        sistema: bool = False,
    ) -> bool:
        """Atualiza dados de um usuário existente."""
        try:
            usuario_atual = self.conexao.execute(
                "SELECT perfil FROM usuarios WHERE username = ? AND ativo = 1",
                (username_original,),
            ).fetchone()

            if not usuario_atual:
                print(f"❌ Usuário '{username_original}' não encontrado!")
                return False

            if not sistema:
                perfil_exec = self._normalizar_perfil(executor_perfil)
                if perfil_exec not in {"adm", "gerente"}:
                    print("❌ Permissão negada: apenas ADM/gerente podem atualizar usuários.")
                    return False
                if perfil_exec == "gerente":
                    if self._normalizar_perfil(usuario_atual["perfil"]) != "operador":
                        print("❌ Permissão negada: gerente só pode editar usuário operador.")
                        return False
                    if novo_perfil and novo_perfil != "operador":
                        print("❌ Permissão negada: gerente só pode definir perfil operador.")
                        return False

            updates = []
            valores: List[str] = []

            if novo_username:
                updates.append("username = ?")
                valores.append(novo_username.strip())

            if novo_perfil:
                if novo_perfil not in {"ADM", "gerente", "operador"}:
                    print("❌ Perfil inválido para atualização!")
                    return False

                if (
                    usuario_atual["perfil"] == "ADM"
                    and novo_perfil != "ADM"
                    and self._contar_adms_ativos() <= 1
                ):
                    print("❌ Operação bloqueada: não é permitido rebaixar o último usuário ADM.")
                    return False

                updates.append("perfil = ?")
                valores.append(novo_perfil)

            if nova_senha_hash:
                updates.append("senha_hash = ?")
                valores.append(nova_senha_hash)

            if not updates:
                return False

            valores.append(username_original)

            with self.conexao:
                cursor = self.conexao.execute(
                    f"UPDATE usuarios SET {', '.join(updates)} WHERE username = ? AND ativo = 1",
                    tuple(valores),
                )

            if cursor.rowcount > 0:
                print(f"✅ Usuário '{username_original}' atualizado!")
                return True

            print(f"❌ Usuário '{username_original}' não encontrado!")
            return False
        except sqlite3.IntegrityError:
            print("❌ Já existe um usuário com esse nome!")
            return False
        except Exception as e:
            print(f"❌ Erro ao atualizar usuário: {e}")
            return False

    def listar_usuarios(self) -> List[Dict]:
        """Lista usuários ativos ordenados por perfil e username."""
        try:
            cursor = self.conexao.execute(
                """
                SELECT id, username, perfil, ativo
                FROM usuarios
                WHERE ativo = 1
                ORDER BY CASE perfil
                    WHEN 'ADM' THEN 1
                    WHEN 'gerente' THEN 2
                    ELSE 3
                END, username
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erro ao listar usuários: {e}")
            return []

    def _contar_adms_ativos(self) -> int:
        """Retorna a quantidade de usuários ADM ativos."""
        row = self.conexao.execute(
            "SELECT COUNT(1) AS total FROM usuarios WHERE ativo = 1 AND perfil = 'ADM'"
        ).fetchone()
        return int(row["total"] if row else 0)

    def _listar_registros_contato(self, tabela: str) -> List[Dict]:
        """Lista contatos cadastrados em tabelas simples de cadastro."""
        try:
            cursor = self.conexao.execute(
                f"""
                SELECT id, nome, telefone_celular, telefone_fixo, email, endereco, observacao, data_cadastro
                FROM {tabela}
                ORDER BY nome
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erro ao listar registros de {tabela}: {e}")
            return []

    def _criar_registro_contato(
        self,
        tabela: str,
        nome: str,
        telefone_celular: str = "",
        telefone_fixo: str = "",
        email: str = "",
        endereco: str = "",
        observacao: str = "",
    ) -> bool:
        """Insere um cadastro simples de contato."""
        try:
            nome = (nome or "").strip()
            if not nome:
                print("❌ Nome obrigatório!")
                return False

            with self.conexao:
                self.conexao.execute(
                    f"""
                    INSERT INTO {tabela}
                    (nome, telefone_celular, telefone_fixo, email, endereco, observacao, data_cadastro)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nome,
                        (telefone_celular or "").strip(),
                        (telefone_fixo or "").strip(),
                        (email or "").strip(),
                        (endereco or "").strip(),
                        (observacao or "").strip(),
                        datetime.datetime.now().isoformat(),
                    ),
                )

            print(f"✅ Registro '{nome}' criado em {tabela}!")
            return True
        except sqlite3.IntegrityError:
            print(f"❌ Registro '{nome}' já existe em {tabela}!")
            return False
        except Exception as e:
            print(f"❌ Erro ao criar registro em {tabela}: {e}")
            return False

    def _atualizar_registro_contato(
        self,
        tabela: str,
        nome_original: str,
        novo_nome: Optional[str] = None,
        telefone_celular: Optional[str] = None,
        telefone_fixo: Optional[str] = None,
        email: Optional[str] = None,
        endereco: Optional[str] = None,
        observacao: Optional[str] = None,
    ) -> bool:
        """Atualiza um cadastro simples de contato."""
        try:
            atual = self.conexao.execute(
                f"SELECT id FROM {tabela} WHERE nome = ?",
                (nome_original,),
            ).fetchone()
            if not atual:
                print(f"❌ Registro '{nome_original}' não encontrado em {tabela}!")
                return False

            updates = []
            valores: List[str] = []

            if novo_nome and novo_nome.strip() and novo_nome.strip() != nome_original:
                updates.append("nome = ?")
                valores.append(novo_nome.strip())
            if telefone_celular is not None:
                updates.append("telefone_celular = ?")
                valores.append(telefone_celular.strip())
            if telefone_fixo is not None:
                updates.append("telefone_fixo = ?")
                valores.append(telefone_fixo.strip())
            if email is not None:
                updates.append("email = ?")
                valores.append(email.strip())
            if endereco is not None:
                updates.append("endereco = ?")
                valores.append(endereco.strip())
            if observacao is not None:
                updates.append("observacao = ?")
                valores.append(observacao.strip())

            if not updates:
                return False

            valores.append(nome_original)

            with self.conexao:
                cursor = self.conexao.execute(
                    f"UPDATE {tabela} SET {', '.join(updates)} WHERE nome = ?",
                    tuple(valores),
                )

            if cursor.rowcount > 0:
                print(f"✅ Registro '{nome_original}' atualizado em {tabela}!")
                return True

            return False
        except sqlite3.IntegrityError:
            print(f"❌ Já existe um registro com esse nome em {tabela}!")
            return False
        except Exception as e:
            print(f"❌ Erro ao atualizar registro em {tabela}: {e}")
            return False

    def _deletar_registro_contato(self, tabela: str, nome: str) -> bool:
        """Remove um cadastro simples de contato."""
        try:
            with self.conexao:
                cursor = self.conexao.execute(f"DELETE FROM {tabela} WHERE nome = ?", (nome,))

            if cursor.rowcount > 0:
                print(f"✅ Registro '{nome}' deletado de {tabela}!")
                return True

            print(f"❌ Registro '{nome}' não encontrado em {tabela}!")
            return False
        except Exception as e:
            print(f"❌ Erro ao deletar registro em {tabela}: {e}")
            return False

    def listar_fornecedores(self) -> List[Dict]:
        return self._listar_registros_contato("fornecedores")

    def criar_fornecedor(
        self,
        nome: str,
        telefone_celular: str = "",
        telefone_fixo: str = "",
        email: str = "",
        endereco: str = "",
        observacao: str = "",
        documento: str = "",
        telefone: str = "",
    ) -> bool:
        # Compatibilidade: se vier assinatura legada, reaproveita no novo campo celular.
        celular = telefone_celular or telefone
        _ = documento
        return self._criar_registro_contato("fornecedores", nome, celular, telefone_fixo, email, endereco, observacao)

    def atualizar_fornecedor(
        self,
        nome_original: str,
        novo_nome: Optional[str] = None,
        telefone_celular: Optional[str] = None,
        telefone_fixo: Optional[str] = None,
        email: Optional[str] = None,
        endereco: Optional[str] = None,
        observacao: Optional[str] = None,
        documento: Optional[str] = None,
        telefone: Optional[str] = None,
    ) -> bool:
        celular = telefone_celular if telefone_celular is not None else telefone
        _ = documento
        return self._atualizar_registro_contato(
            "fornecedores",
            nome_original,
            novo_nome=novo_nome,
            telefone_celular=celular,
            telefone_fixo=telefone_fixo,
            email=email,
            endereco=endereco,
            observacao=observacao,
        )

    def deletar_fornecedor(self, nome: str) -> bool:
        return self._deletar_registro_contato("fornecedores", nome)

    def listar_clientes(self) -> List[Dict]:
        return self._listar_registros_contato("clientes")

    def criar_cliente(
        self,
        nome: str,
        telefone_celular: str = "",
        telefone_fixo: str = "",
        email: str = "",
        endereco: str = "",
        observacao: str = "",
        documento: str = "",
        telefone: str = "",
    ) -> bool:
        celular = telefone_celular or telefone
        _ = documento
        return self._criar_registro_contato("clientes", nome, celular, telefone_fixo, email, endereco, observacao)

    def atualizar_cliente(
        self,
        nome_original: str,
        novo_nome: Optional[str] = None,
        telefone_celular: Optional[str] = None,
        telefone_fixo: Optional[str] = None,
        email: Optional[str] = None,
        endereco: Optional[str] = None,
        observacao: Optional[str] = None,
        documento: Optional[str] = None,
        telefone: Optional[str] = None,
    ) -> bool:
        celular = telefone_celular if telefone_celular is not None else telefone
        _ = documento
        return self._atualizar_registro_contato(
            "clientes",
            nome_original,
            novo_nome=novo_nome,
            telefone_celular=celular,
            telefone_fixo=telefone_fixo,
            email=email,
            endereco=endereco,
            observacao=observacao,
        )

    def deletar_cliente(self, nome: str) -> bool:
        return self._deletar_registro_contato("clientes", nome)

    def deletar_usuario(
        self,
        username: str,
        executor_perfil: Optional[str] = None,
        sistema: bool = False,
    ) -> bool:
        """Exclui usuário pelo username."""
        try:
            if not sistema and self._normalizar_perfil(executor_perfil) != "adm":
                print("❌ Permissão negada: apenas ADM pode deletar usuários.")
                return False

            row = self.conexao.execute(
                "SELECT perfil FROM usuarios WHERE username = ? AND ativo = 1",
                (username,),
            ).fetchone()

            if not row:
                print(f"❌ Usuário '{username}' não encontrado!")
                return False

            if row["perfil"] == "ADM" and self._contar_adms_ativos() <= 1:
                print("❌ Operação bloqueada: não é permitido remover o último usuário ADM.")
                return False

            with self.conexao:
                cursor = self.conexao.execute(
                    "DELETE FROM usuarios WHERE username = ?",
                    (username,),
                )

            if cursor.rowcount > 0:
                print(f"✅ Usuário '{username}' deletado!")
                return True

            print(f"❌ Usuário '{username}' não encontrado!")
            return False
        except Exception as e:
            print(f"❌ Erro ao deletar usuário: {e}")
            return False

    @staticmethod
    def _row_para_dict(row: sqlite3.Row) -> Dict:
        """Converte sqlite3.Row para dict com parse de campos de data."""
        item = dict(row)
        for campo_data in ("data_cadastro", "data_movimentacao"):
            if campo_data in item and isinstance(item[campo_data], str):
                try:
                    item[campo_data] = datetime.datetime.fromisoformat(item[campo_data])
                except ValueError:
                    pass
        return item

    @staticmethod
    def calcular_status_estoque(quantidade: int, estoque_minimo: int) -> str:
        """Classifica o nível do estoque em três faixas semáforo."""
        if quantidade <= estoque_minimo:
            return "CRITICO"
        if quantidade <= estoque_minimo * 2:
            return "BAIXO"
        return "OK"

    def criar_produto(
        self,
        nome: str,
        categoria: str,
        preco: float,
        quantidade: int,
        estoque_minimo: int,
        fornecedor: str,
    ) -> bool:
        """Cria um novo produto."""
        try:
            if self.buscar_produto(nome):
                print(f"❌ Produto '{nome}' já existe!")
                return False

            if int(quantidade) < 0:
                print(f"❌ Quantidade inicial inválida (negativa) para '{nome}'")
                return False

            with self.conexao:
                self.conexao.execute(
                    """
                    INSERT INTO produtos
                    (nome, categoria, preco, quantidade, estoque_minimo, fornecedor, data_cadastro)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nome,
                        categoria,
                        float(preco),
                        int(quantidade),
                        int(estoque_minimo),
                        fornecedor,
                        datetime.datetime.now().isoformat(),
                    ),
                )
            print(f"✅ Produto '{nome}' adicionado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar produto: {e}")
            return False

    def listar_produtos(self) -> List[Dict]:
        """Lista todos os produtos."""
        try:
            cursor = self.conexao.execute("SELECT * FROM produtos ORDER BY nome")
            return [self._row_para_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erro ao listar produtos: {e}")
            return []

    def buscar_produto(self, nome: str) -> Optional[Dict]:
        """Busca um produto pelo nome."""
        try:
            row = self.conexao.execute(
                "SELECT * FROM produtos WHERE nome = ?", (nome,)
            ).fetchone()
            return self._row_para_dict(row) if row else None
        except Exception as e:
            print(f"❌ Erro ao buscar produto: {e}")
            return None

    def buscar_produtos_filtrados(self, filtro_por: str, termo_pesquisa: str) -> List[Dict]:
        """Busca produtos com base em um filtro e termo de pesquisa (case-insensitive)."""
        try:
            if not termo_pesquisa:
                return self.listar_produtos()

            coluna = "nome" if filtro_por not in {"nome", "categoria"} else filtro_por
            cursor = self.conexao.execute(
                f"SELECT * FROM produtos WHERE {coluna} LIKE ? COLLATE NOCASE ORDER BY nome",
                (f"%{termo_pesquisa}%",),
            )
            return [self._row_para_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erro ao buscar produtos filtrados: {e}")
            return []

    def atualizar_produto(self, nome: str, dados: Dict) -> bool:
        """Atualiza dados de um produto."""
        try:
            campos_permitidos = {"categoria", "preco", "quantidade", "estoque_minimo", "fornecedor"}
            dados_filtrados = {k: v for k, v in dados.items() if k in campos_permitidos}
            if not dados_filtrados:
                return False

            # Validação adicional: não aceitar quantidade negativa
            if "quantidade" in dados_filtrados and int(dados_filtrados["quantidade"]) < 0:
                print("❌ Quantidade inválida: não é permitido definir quantidade negativa.")
                return False

            set_clause = ", ".join(f"{campo} = ?" for campo in dados_filtrados.keys())
            valores = list(dados_filtrados.values()) + [nome]

            with self.conexao:
                cursor = self.conexao.execute(
                    f"UPDATE produtos SET {set_clause} WHERE nome = ?", valores
                )

            if cursor.rowcount > 0:
                print(f"✅ Produto '{nome}' atualizado!")
                return True

            print(f"❌ Produto '{nome}' não encontrado!")
            return False
        except Exception as e:
            print(f"❌ Erro ao atualizar produto: {e}")
            return False

    def deletar_produto(self, nome: str) -> bool:
        """Deleta um produto."""
        try:
            with self.conexao:
                cursor = self.conexao.execute("DELETE FROM produtos WHERE nome = ?", (nome,))

            if cursor.rowcount > 0:
                print(f"✅ Produto '{nome}' deletado!")
                return True

            print(f"❌ Produto '{nome}' não encontrado!")
            return False
        except Exception as e:
            print(f"❌ Erro ao deletar produto: {e}")
            return False

    def registrar_movimentacao(
        self,
        nome_produto: str,
        tipo_movimento: str,
        quantidade: int,
        observacao: str = "",
        usuario: str = "Sistema",
    ) -> bool:
        """Registra uma movimentação de estoque com vínculo FK em produtos."""
        try:
            produto = self.buscar_produto(nome_produto)
            if not produto:
                print(f"❌ Produto '{nome_produto}' não encontrado!")
                return False

            tipo = tipo_movimento.lower().strip()
            if tipo not in {"entrada", "saida"}:
                print("❌ Tipo de movimentação inválido!")
                return False

            quantidade = int(quantidade)
            if quantidade <= 0:
                print("❌ A quantidade deve ser maior que zero!")
                return False

            usuario = (usuario or "").strip()
            if not usuario or not self._usuario_ativo_existe(usuario):
                print("❌ Usuário da movimentação inválido ou não cadastrado.")
                return False

            if tipo == "saida" and produto["quantidade"] < quantidade:
                print(
                    f"❌ Estoque insuficiente! Disponível: {produto['quantidade']}, Solicitado: {quantidade}"
                )
                return False

            nova_quantidade = (
                produto["quantidade"] + quantidade if tipo == "entrada" else produto["quantidade"] - quantidade
            )

            # Garantia extra de consistência: nunca permitir nova_quantidade negativa
            if nova_quantidade < 0:
                print(
                    f"❌ Operação inválida: nova quantidade negativa ({nova_quantidade}) para produto '{nome_produto}'"
                )
                return False

            with self.conexao:
                self.conexao.execute(
                    """
                    INSERT INTO movimentacoes
                    (produto_id, tipo, quantidade, data_movimentacao, observacao, usuario)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        produto["id"],
                        tipo,
                        quantidade,
                        datetime.datetime.now().isoformat(),
                        observacao,
                        usuario,
                    ),
                )
                self.conexao.execute(
                    "UPDATE produtos SET quantidade = ? WHERE id = ?",
                    (nova_quantidade, produto["id"]),
                )

            print(f"✅ Movimentação registrada: {tipo} de {quantidade} unidades")
            if nova_quantidade <= produto["estoque_minimo"]:
                print(f"⚠️ ALERTA: Estoque baixo para '{nome_produto}'!")
            return True
        except Exception as e:
            print(f"❌ Erro ao registrar movimentação: {e}")
            return False

    def listar_movimentacoes(self, limite: int = 50) -> List[Dict]:
        """Lista as movimentações mais recentes."""
        try:
            cursor = self.conexao.execute(
                """
                SELECT m.*, COALESCE(p.nome, 'Produto removido') AS produto_nome
                FROM movimentacoes m
                LEFT JOIN produtos p ON p.id = m.produto_id
                ORDER BY m.data_movimentacao DESC
                LIMIT ?
                """,
                (limite,),
            )
            return [self._row_para_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erro ao listar movimentações: {e}")
            return []

    def produtos_em_falta(self) -> List[Dict]:
        """Lista produtos com estoque baixo ou em falta."""
        try:
            cursor = self.conexao.execute(
                """
                SELECT *
                FROM produtos
                WHERE quantidade <= estoque_minimo
                ORDER BY nome
                """
            )
            return [self._row_para_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erro ao buscar produtos em falta: {e}")
            return []

    def relatorio_estoque(self) -> Dict:
        """Gera relatório geral do estoque."""
        try:
            totais = self.conexao.execute(
                """
                SELECT
                    COUNT(*) AS total_produtos,
                    COALESCE(SUM(preco * quantidade), 0) AS valor_total,
                    COALESCE(SUM(quantidade), 0) AS quantidade_total
                FROM produtos
                """
            ).fetchone()

            produtos_criticos = self.conexao.execute(
                "SELECT COUNT(*) AS total FROM produtos WHERE quantidade <= estoque_minimo"
            ).fetchone()["total"]

            total_movimentacoes = self.conexao.execute(
                "SELECT COUNT(*) AS total FROM movimentacoes"
            ).fetchone()["total"]

            return {
                "total_produtos": totais["total_produtos"],
                "valor_total": totais["valor_total"],
                "quantidade_total": totais["quantidade_total"],
                "produtos_criticos": produtos_criticos,
                "total_movimentacoes": total_movimentacoes,
            }
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
            return {}

    def exportar_para_excel(self, caminho_arquivo: str) -> bool:
        """Exporta inventário e produtos críticos para um arquivo Excel."""
        try:
            produtos = self.listar_produtos()
            produtos_criticos = self.produtos_em_falta()

            for produto in produtos:
                status_base = self.calcular_status_estoque(produto["quantidade"], produto["estoque_minimo"])
                produto["status"] = {
                    "OK": "🟢️ OK",
                    "BAIXO": "🟡 BAIXO",
                    "CRITICO": "🔴 CRITICO",
                }[status_base]

            for produto in produtos:
                if isinstance(produto.get("data_cadastro"), datetime.datetime):
                    produto["data_cadastro"] = produto["data_cadastro"].strftime("%d/%m/%Y %H:%M:%S")

            for produto in produtos_criticos:
                status_base = self.calcular_status_estoque(produto["quantidade"], produto["estoque_minimo"])
                produto["status"] = {
                    "OK": "🟢️ OK",
                    "BAIXO": "🟡 BAIXO",
                    "CRITICO": "🔴 CRITICO",
                }[status_base]
                if isinstance(produto.get("data_cadastro"), datetime.datetime):
                    produto["data_cadastro"] = produto["data_cadastro"].strftime("%d/%m/%Y %H:%M:%S")

            df_produtos = pd.DataFrame(produtos)
            df_criticos = pd.DataFrame(produtos_criticos)

            with pd.ExcelWriter(caminho_arquivo, engine="openpyxl") as writer:
                df_produtos.to_excel(writer, sheet_name="Inventário Completo", index=False)
                if not df_criticos.empty:
                    df_criticos.to_excel(writer, sheet_name="Produtos Críticos", index=False)

            print(f"✅ Relatório exportado para {caminho_arquivo}")
            return True
        except Exception as e:
            print(f"❌ Erro ao exportar para Excel: {e}")
            return False

    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados."""
        if hasattr(self, "conexao"):
            self.conexao.close()
            print("🔌 Conexão com SQLite fechada")


if __name__ == "__main__":
    try:
        db = EstoqueDB()
        print("\n🧪 Testando funcionalidades...")

        print("\n📦 Listando produtos:")
        for produto in db.listar_produtos():
            print(f"  • {produto['nome']} - Estoque: {produto['quantidade']}")

        print("\n📊 Relatório:")
        for chave, valor in db.relatorio_estoque().items():
            print(f"  • {chave}: {valor}")

        db.fechar_conexao()
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
