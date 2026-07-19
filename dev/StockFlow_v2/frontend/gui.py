#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STOCKFLOW - FLUXO DE ESTOQUE COM CRIPTOGRAFIA E BACKUP EM NUVEM
"""

import json
import re
import argparse
import threading
import shutil
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import backend.database as db


class StockFlowGUI:
    CONTATO_NAO_CADASTRADO = "Nao cadastrado"
    CAMPOS_CONTATO = ["nome", "telefone_celular", "telefone_fixo", "email", "endereco", "observacao"]
    CAMPOS_CONTATO_OPCIONAIS = {"telefone_celular", "telefone_fixo", "email", "endereco", "observacao"}
    # Mapas entre rótulos exibidos na UI e valores internos armazenados no DB
    PROFILE_LABEL_TO_VALUE = {
        "Administrador": "ADM",
        "Gerente": "gerente",
        "Operador": "operador",
    }
    PROFILE_VALUE_TO_LABEL = {v: k for k, v in PROFILE_LABEL_TO_VALUE.items()}

    def __init__(self, root):
        """Inicializa a interface gráfica"""
        try:
            self.db = db.EstoqueDB()
        except Exception as e:
            messagebox.showerror(
                "Erro de Conexão",
                f"Não foi possível conectar ao banco (SQLite):\n{e}\n\n"
                "Verifique permissões de escrita na pasta do projeto.",
            )
            self.root = None
            return

        self.root = root
        self.root.title("STOCKFLOW - FLUXO DE ESTOQUE COM CRIPTOGRAFIA E BACKUP EM NUVEM")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        self.usuario_logado = ""
        self.perfil_usuario = ""

        self.project_root = Path(__file__).resolve().parents[1]
        self.backup_config_path = self.project_root / "config_backup.json"
        self.backup_history_path = self.project_root / "outputs" / "backups" / "backup_history.json"
        self.sync_pendentes_em_execucao = False
        self.contato_tabs = {}

        if not self.tela_login():
            self.db.fechar_conexao()
            self.root.destroy()
            self.root = None
            return

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._criar_abas()
        self.aplicar_permissoes()

        self.atualizar_lista_produtos()
        self.atualizar_combo_produtos()
        self.atualizar_lista_movimentacoes()
        self.atualizar_lista_fornecedores()
        self.atualizar_lista_clientes()
        self.atualizar_relatorios()

        if self.perfil_usuario.strip().lower() == "adm":
            self._atualizar_historico_backups_ui()
            self._iniciar_agendador_sincronizacao_pendentes()

    # =========================
    # Login / sessão
    # =========================
    def tela_login(self) -> bool:
        login_ok = {"valor": False}

        janela_login = tk.Toplevel(self.root)
        janela_login.title("Login - STOCKFLOW")
        janela_login.geometry("380x220")
        janela_login.resizable(False, False)
        janela_login.transient(self.root)

        # Garante que a janela esteja visivel antes de aplicar grab modal.
        try:
            janela_login.update_idletasks()
            janela_login.wait_visibility()
            janela_login.grab_set()
        except tk.TclError:
            # Em alguns ambientes a janela ainda nao esta pronta neste ponto.
            pass

        frame = ttk.Frame(janela_login, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Acesso ao Sistema", font=("TkDefaultFont", 12, "bold")).pack(pady=(0, 10))

        ttk.Label(frame, text="Usuário:").pack(anchor="w")
        entry_usuario = ttk.Entry(frame, width=30)
        entry_usuario.pack(fill="x", pady=(0, 8))

        ttk.Label(frame, text="Senha:").pack(anchor="w")
        entry_senha = ttk.Entry(frame, width=30, show="*")
        entry_senha.pack(fill="x", pady=(0, 12))

        def confirmar_login(event=None):
            usuario = entry_usuario.get().strip()
            senha = entry_senha.get()

            if not usuario or not senha:
                messagebox.showwarning("Login", "Informe usuário e senha.", parent=janela_login)
                return

            perfil = self.db.autenticar_usuario(usuario, senha)
            if not perfil:
                messagebox.showerror("Login", "Usuário ou senha inválidos.", parent=janela_login)
                entry_senha.delete(0, tk.END)
                return

            self.usuario_logado = usuario
            self.perfil_usuario = str(perfil)
            login_ok["valor"] = True
            janela_login.destroy()

        def cancelar_login():
            janela_login.destroy()

        botoes = ttk.Frame(frame)
        botoes.pack(fill="x")
        ttk.Button(botoes, text="Entrar", command=confirmar_login).pack(side="left")
        ttk.Button(botoes, text="Sair", command=cancelar_login).pack(side="right")

        entry_usuario.focus_set()
        janela_login.bind("<Return>", confirmar_login)
        janela_login.protocol("WM_DELETE_WINDOW", cancelar_login)

        self.root.wait_window(janela_login)
        return login_ok["valor"]

    def trocar_usuario(self):
        if not messagebox.askyesno("Trocar Usuário", "Deseja trocar o usuário atual?"):
            return

        usuario_atual = self.usuario_logado
        perfil_atual = self.perfil_usuario

        if not self.tela_login():
            self.usuario_logado = usuario_atual
            self.perfil_usuario = perfil_atual
            self.atualizar_status("Troca de usuário cancelada")
            return

        self.reconstruir_interface()
        self.atualizar_status(f"Sessão alterada para: {self.usuario_logado} ({self.perfil_usuario})")

    def reconstruir_interface(self):
        if hasattr(self, "top_bar"):
            self.top_bar.destroy()
        if hasattr(self, "notebook"):
            self.notebook.destroy()
        if hasattr(self, "status_bar"):
            self.status_bar.destroy()

        self._criar_abas()
        self.aplicar_permissoes()
        self.atualizar_lista_produtos()
        self.atualizar_combo_produtos()
        self.atualizar_lista_movimentacoes()
        self.atualizar_lista_fornecedores()
        self.atualizar_lista_clientes()
        self.atualizar_relatorios()

    def sair_programa(self):
        self.on_closing()

    # =========================
    # Construção da UI
    # =========================
    def _criar_abas(self):
        self.top_bar = ttk.Frame(self.root, padding=(10, 8))
        self.top_bar.pack(fill="x")

        self.frame_info_usuario = ttk.Frame(self.top_bar)
        self.frame_info_usuario.pack(side="left", fill="x", expand=True)

        self.label_usuario = ttk.Label(self.frame_info_usuario, text="")
        self.label_usuario.pack(anchor="w")

        self.label_frequencia_backup = ttk.Label(self.frame_info_usuario, text="")
        self.label_frequencia_backup.pack(anchor="w")

        self.btn_trocar_usuario = ttk.Button(self.top_bar, text="Trocar Usuário", command=self.trocar_usuario)
        self.btn_trocar_usuario.pack(side="right", padx=(6, 0))

        self.btn_sair_programa = ttk.Button(self.top_bar, text="Sair", command=self.sair_programa)
        self.btn_sair_programa.pack(side="right")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_produtos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_produtos, text="📦 Produtos")
        self.criar_aba_produtos()

        self.frame_movimentacoes = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_movimentacoes, text="🔄 Movimentações")
        self.criar_aba_movimentacoes()

        self.frame_fornecedores = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_fornecedores, text="🏷️ Fornecedores")
        self.criar_aba_contatos("fornecedores")

        self.frame_clientes = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_clientes, text="🧾 Clientes")
        self.criar_aba_contatos("clientes")

        self.frame_relatorios = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_relatorios, text="📊 Relatórios")
        self.criar_aba_relatorios()

        self.frame_usuarios = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_usuarios, text="👤 Gerenciar Usuários")
        self.criar_aba_usuarios()

        if self.perfil_usuario.strip().lower() == "adm":
            self.frame_config_backup = ttk.Frame(self.notebook)
            self.notebook.add(self.frame_config_backup, text="⚙️ Configurações de Backup")
            self._criar_aba_config_backup()

        self.status_bar = tk.Label(
            self.root,
            text="Sistema iniciado",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#e0e0e0",
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self._atualizar_indicador_frequencia_backup()

    def aplicar_permissoes(self):
        perfil = self.perfil_usuario.strip().lower()

        if perfil in {"gerente", "operador"}:
            try:
                self.notebook.forget(self.frame_relatorios)
            except tk.TclError:
                pass

        if perfil == "operador":
            for fr in [self.frame_movimentacoes, self.frame_usuarios]:
                try:
                    self.notebook.forget(fr)
                except tk.TclError:
                    pass

        if perfil == "gerente":
            self.btn_deletar_usuario.config(state="disabled")

        if perfil != "adm" and hasattr(self, "frame_config_backup"):
            try:
                self.notebook.forget(self.frame_config_backup)
            except tk.TclError:
                pass

        perfil_exibido = self.PROFILE_VALUE_TO_LABEL.get(self.perfil_usuario, self.perfil_usuario)
        self.label_usuario.config(text=f"Logado como: {self.usuario_logado} ({perfil_exibido})")
        self._atualizar_indicador_frequencia_backup()
        self.atualizar_status(f"Usuário: {self.usuario_logado} | Perfil: {perfil_exibido}")

    def _configuracao_contato(self, tipo_contato: str):
        if tipo_contato == "fornecedores":
            return {
                "titulo": "Cadastro de Fornecedores",
                "nome_entidade": "Fornecedor",
                "plural": "fornecedores",
                "listar": self.db.listar_fornecedores,
                "criar": self.db.criar_fornecedor,
                "atualizar": self.db.atualizar_fornecedor,
                "deletar": self.db.deletar_fornecedor,
            }
        return {
            "titulo": "Cadastro de Clientes",
            "nome_entidade": "Cliente",
            "plural": "clientes",
            "listar": self.db.listar_clientes,
            "criar": self.db.criar_cliente,
            "atualizar": self.db.atualizar_cliente,
            "deletar": self.db.deletar_cliente,
        }

    def criar_aba_contatos(self, tipo_contato: str):
        cfg = self._configuracao_contato(tipo_contato)
        frame_pai = self.frame_fornecedores if tipo_contato == "fornecedores" else self.frame_clientes

        form_frame = ttk.LabelFrame(frame_pai, text=cfg["titulo"])
        form_frame.pack(fill="x", padx=5, pady=5)

        campos = [
            ("nome", "Nome", 28),
            ("telefone_celular", "Telefone Celular", 18),
            ("telefone_fixo", "Telefone Fixo", 18),
            ("email", "E-mail", 26),
            ("endereco", "Endereço", 34),
            ("observacao", "Observação", 34),
        ]

        entradas = {}
        for indice, (chave, rotulo, largura) in enumerate(campos):
            linha = indice // 3
            coluna = (indice % 3) * 2
            ttk.Label(form_frame, text=f"{rotulo}:").grid(row=linha, column=coluna, sticky="w", padx=5, pady=2)
            entrada = ttk.Entry(form_frame, width=largura)
            entrada.grid(row=linha, column=coluna + 1, padx=5, pady=2, sticky="ew")
            entradas[chave] = entrada

        for coluna in range(6):
            form_frame.columnconfigure(coluna, weight=1 if coluna % 2 else 0)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=6, pady=10, sticky="w")

        ttk.Button(btn_frame, text=f"Adicionar {cfg['nome_entidade']}", command=lambda t=tipo_contato: self.adicionar_contato(t)).pack(
            side="left",
            padx=4,
        )
        ttk.Button(btn_frame, text="Atualizar", command=lambda t=tipo_contato: self.atualizar_contato(t)).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Deletar", command=lambda t=tipo_contato: self.deletar_contato(t)).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Limpar Campos", command=lambda t=tipo_contato: self.limpar_campos_contato(t)).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Atualizar Lista", command=lambda t=tipo_contato: self.atualizar_lista_contatos(t)).pack(
            side="left",
            padx=4,
        )

        list_frame = ttk.LabelFrame(frame_pai, text=f"Lista de {cfg['plural'].capitalize()}")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        colunas = ("Nome", "Telefone Celular", "Telefone Fixo", "E-mail", "Endereço", "Observação")
        tree = ttk.Treeview(list_frame, columns=colunas, show="headings", height=14)
        for col in colunas:
            tree.heading(col, text=col)
            if col == "Nome":
                tree.column(col, width=180)
            elif col == "Observação":
                tree.column(col, width=220)
            elif col == "Endereço":
                tree.column(col, width=200)
            else:
                tree.column(col, width=130)

        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        tree.bind("<<TreeviewSelect>>", lambda event, t=tipo_contato: self.on_contato_select(t, event))

        self.contato_tabs[tipo_contato] = {
            "entries": entradas,
            "tree": tree,
            "listar": cfg["listar"],
            "criar": cfg["criar"],
            "atualizar": cfg["atualizar"],
            "deletar": cfg["deletar"],
            "nome_entidade": cfg["nome_entidade"],
        }

        self.atualizar_lista_contatos(tipo_contato)

    def _obter_ui_contato(self, tipo_contato: str):
        return self.contato_tabs.get(tipo_contato, {})

    def limpar_campos_contato(self, tipo_contato: str):
        ui = self._obter_ui_contato(tipo_contato)
        for entrada in ui.get("entries", {}).values():
            entrada.delete(0, tk.END)

    @staticmethod
    def _telefone_apenas_numeros(valor: str) -> bool:
        valor = (valor or "").strip()
        return (not valor) or valor.isdigit()

    def on_contato_select(self, tipo_contato: str, event=None):
        ui = self._obter_ui_contato(tipo_contato)
        tree = ui.get("tree")
        if not tree:
            return

        selecionado = tree.selection()
        if not selecionado:
            return

        valores = tree.item(selecionado[0])["values"]
        entradas = ui.get("entries", {})
        self.limpar_campos_contato(tipo_contato)

        for indice, chave in enumerate(self.CAMPOS_CONTATO):
            if chave in entradas and indice < len(valores):
                valor = valores[indice]
                if chave in self.CAMPOS_CONTATO_OPCIONAIS and valor == self.CONTATO_NAO_CADASTRADO:
                    valor = ""
                entradas[chave].insert(0, valor)

    def adicionar_contato(self, tipo_contato: str):
        ui = self._obter_ui_contato(tipo_contato)
        entradas = ui.get("entries", {})
        nome = entradas.get("nome").get().strip() if entradas.get("nome") else ""
        telefone_celular = entradas.get("telefone_celular").get().strip() if entradas.get("telefone_celular") else ""
        telefone_fixo = entradas.get("telefone_fixo").get().strip() if entradas.get("telefone_fixo") else ""
        email = entradas.get("email").get().strip() if entradas.get("email") else ""
        endereco = entradas.get("endereco").get().strip() if entradas.get("endereco") else ""
        observacao = entradas.get("observacao").get().strip() if entradas.get("observacao") else ""

        if not nome:
            messagebox.showerror("Erro", f"Informe o nome do {ui.get('nome_entidade', 'registro').lower()}!")
            return

        if not self._telefone_apenas_numeros(telefone_celular):
            messagebox.showerror("Erro", "Telefone Celular deve conter apenas numeros.")
            return

        if not self._telefone_apenas_numeros(telefone_fixo):
            messagebox.showerror("Erro", "Telefone Fixo deve conter apenas numeros.")
            return

        if ui.get("criar") and ui["criar"](
            nome,
            telefone_celular=telefone_celular,
            telefone_fixo=telefone_fixo,
            email=email,
            endereco=endereco,
            observacao=observacao,
        ):
            messagebox.showinfo("Sucesso", f"{ui.get('nome_entidade', 'Registro')} cadastrado com sucesso!")
            self.limpar_campos_contato(tipo_contato)
            self.atualizar_lista_contatos(tipo_contato)
            self.atualizar_status(f"{ui.get('nome_entidade', 'Registro')} '{nome}' cadastrado")
        else:
            messagebox.showerror("Erro", f"Não foi possível cadastrar o {ui.get('nome_entidade', 'registro').lower()}.")

    def atualizar_contato(self, tipo_contato: str):
        ui = self._obter_ui_contato(tipo_contato)
        tree = ui.get("tree")
        if not tree:
            return

        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", f"Selecione um {ui.get('nome_entidade', 'registro').lower()} para atualizar!")
            return

        valores_atuais = tree.item(selecionado[0])["values"]
        nome_original = valores_atuais[0]
        entradas = ui.get("entries", {})

        novo_nome = entradas.get("nome").get().strip() if entradas.get("nome") else ""
        telefone_celular = entradas.get("telefone_celular").get().strip() if entradas.get("telefone_celular") else ""
        telefone_fixo = entradas.get("telefone_fixo").get().strip() if entradas.get("telefone_fixo") else ""
        email = entradas.get("email").get().strip() if entradas.get("email") else ""
        endereco = entradas.get("endereco").get().strip() if entradas.get("endereco") else ""
        observacao = entradas.get("observacao").get().strip() if entradas.get("observacao") else ""

        if not novo_nome:
            messagebox.showerror("Erro", f"O nome do {ui.get('nome_entidade', 'registro').lower()} é obrigatório.")
            return

        if not self._telefone_apenas_numeros(telefone_celular):
            messagebox.showerror("Erro", "Telefone Celular deve conter apenas numeros.")
            return

        if not self._telefone_apenas_numeros(telefone_fixo):
            messagebox.showerror("Erro", "Telefone Fixo deve conter apenas numeros.")
            return

        if ui.get("atualizar") and ui["atualizar"](
            nome_original,
            novo_nome=novo_nome,
            telefone_celular=telefone_celular,
            telefone_fixo=telefone_fixo,
            email=email,
            endereco=endereco,
            observacao=observacao,
        ):
            messagebox.showinfo("Sucesso", f"{ui.get('nome_entidade', 'Registro')} atualizado com sucesso!")
            self.atualizar_lista_contatos(tipo_contato)
            self.atualizar_status(f"{ui.get('nome_entidade', 'Registro')} '{nome_original}' atualizado")
        else:
            messagebox.showerror("Erro", f"Não foi possível atualizar o {ui.get('nome_entidade', 'registro').lower()}.")

    def deletar_contato(self, tipo_contato: str):
        ui = self._obter_ui_contato(tipo_contato)
        tree = ui.get("tree")
        if not tree:
            return

        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", f"Selecione um {ui.get('nome_entidade', 'registro').lower()} para deletar!")
            return

        nome = tree.item(selecionado[0])["values"][0]
        if not messagebox.askyesno("Confirmar", f"Deseja deletar o {ui.get('nome_entidade', 'registro').lower()} '{nome}'?"):
            return

        if ui.get("deletar") and ui["deletar"](nome):
            messagebox.showinfo("Sucesso", f"{ui.get('nome_entidade', 'Registro')} deletado com sucesso!")
            self.limpar_campos_contato(tipo_contato)
            self.atualizar_lista_contatos(tipo_contato)
            self.atualizar_status(f"{ui.get('nome_entidade', 'Registro')} '{nome}' deletado")
        else:
            messagebox.showerror("Erro", f"Não foi possível deletar o {ui.get('nome_entidade', 'registro').lower()}.")

    def atualizar_lista_contatos(self, tipo_contato: str):
        ui = self._obter_ui_contato(tipo_contato)
        tree = ui.get("tree")
        if not tree:
            return

        for item in tree.get_children():
            tree.delete(item)

        for registro in ui.get("listar", lambda: [])():
            valores_linha = [registro.get("nome", "")]
            for campo in self.CAMPOS_CONTATO[1:]:
                valor = (registro.get(campo, "") or "").strip()
                valores_linha.append(valor if valor else self.CONTATO_NAO_CADASTRADO)
            tree.insert(
                "",
                "end",
                values=tuple(valores_linha),
            )

    def atualizar_lista_fornecedores(self):
        self.atualizar_lista_contatos("fornecedores")

    def atualizar_lista_clientes(self):
        self.atualizar_lista_contatos("clientes")

    # =========================
    # Aba: Produtos
    # =========================
    def criar_aba_produtos(self):
        form_frame = ttk.LabelFrame(self.frame_produtos, text="Cadastro de Produtos")
        form_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_nome = ttk.Entry(form_frame, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Categoria:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_categoria = ttk.Entry(form_frame, width=20)
        self.entry_categoria.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(form_frame, text="Preço:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_preco = ttk.Entry(form_frame, width=15)
        self.entry_preco.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Quantidade:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_quantidade = ttk.Entry(form_frame, width=10)
        self.entry_quantidade.grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(form_frame, text="Estoque Mínimo:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_estoque_min = ttk.Entry(form_frame, width=10)
        self.entry_estoque_min.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Fornecedor:").grid(row=2, column=2, sticky="w", padx=5, pady=2)
        self.entry_fornecedor = ttk.Entry(form_frame, width=25)
        self.entry_fornecedor.grid(row=2, column=3, padx=5, pady=2)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)

        self.btn_add_produto = ttk.Button(btn_frame, text="Adicionar Produto", command=self.adicionar_produto)
        self.btn_add_produto.pack(side="left", padx=5)
        self.btn_edit_produto = ttk.Button(btn_frame, text="Atualizar Produto", command=self.atualizar_produto)
        self.btn_edit_produto.pack(side="left", padx=5)
        self.btn_delete_produto = ttk.Button(btn_frame, text="Deletar Produto", command=self.deletar_produto)
        self.btn_delete_produto.pack(side="left", padx=5)
        self.btn_limpar_campos = ttk.Button(btn_frame, text="Limpar Campos", command=self.limpar_campos)
        self.btn_limpar_campos.pack(side="left", padx=5)

        search_frame = ttk.LabelFrame(self.frame_produtos, text="Pesquisar Produtos")
        search_frame.pack(fill="x", padx=5, pady=5)

        self.search_var = tk.StringVar(value="nome")
        ttk.Radiobutton(search_frame, text="Nome", variable=self.search_var, value="nome").pack(side="left", padx=(10, 5))
        ttk.Radiobutton(search_frame, text="Categoria", variable=self.search_var, value="categoria").pack(side="left", padx=5)

        self.entry_pesquisa = ttk.Entry(search_frame, width=40)
        self.entry_pesquisa.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_pesquisa.bind("<Return>", self.pesquisar_produtos)

        ttk.Button(search_frame, text="Pesquisar", command=self.pesquisar_produtos).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Limpar", command=self.limpar_pesquisa).pack(side="left", padx=5)

        list_frame = ttk.LabelFrame(self.frame_produtos, text="Lista de Produtos")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        colunas = ("Nome", "Categoria", "Preço", "Quantidade", "Est.Min", "Fornecedor", "Status")
        self.tree_produtos = ttk.Treeview(list_frame, columns=colunas, show="tree headings", height=15)

        self.tree_produtos.heading("#0", text="Sinal")
        self.tree_produtos.column("#0", width=52, anchor="center", stretch=False)

        self.status_icons = self._criar_icones_status()

        for col in colunas:
            self.tree_produtos.heading(col, text=col)
            if col == "Nome":
                self.tree_produtos.column(col, width=200)
            elif col == "Preço":
                self.tree_produtos.column(col, width=80)
            elif col in ["Quantidade", "Est.Min"]:
                self.tree_produtos.column(col, width=70)
            else:
                self.tree_produtos.column(col, width=120)

        scrollbar_produtos = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_produtos.yview)
        self.tree_produtos.configure(yscrollcommand=scrollbar_produtos.set)
        self.tree_produtos.pack(side="left", fill="both", expand=True)
        scrollbar_produtos.pack(side="right", fill="y")

        self.tree_produtos.bind("<<TreeviewSelect>>", self.on_produto_select)

    def adicionar_produto(self):
        try:
            nome = self.entry_nome.get().strip()
            categoria = self.entry_categoria.get().strip()
            preco = float(self.entry_preco.get())
            quantidade = int(self.entry_quantidade.get())
            estoque_min = int(self.entry_estoque_min.get())
            fornecedor = self.entry_fornecedor.get().strip()

            if not all([nome, categoria, fornecedor]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
                return

            sucesso = self.db.criar_produto(nome, categoria, preco, quantidade, estoque_min, fornecedor)
            if sucesso:
                messagebox.showinfo("Sucesso", f"Produto '{nome}' adicionado com sucesso!")
                self.limpar_campos()
                self.atualizar_lista_produtos()
                self.atualizar_combo_produtos()
                self.atualizar_status(f"Produto '{nome}' adicionado")
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos inseridos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar produto: {e}")

    def atualizar_produto(self):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para atualizar!")
            return

        try:
            nome_original = self.tree_produtos.item(selecionado[0])["values"][0]
            dados = {}

            if self.entry_categoria.get().strip():
                dados["categoria"] = self.entry_categoria.get().strip()
            if self.entry_preco.get().strip():
                dados["preco"] = float(self.entry_preco.get())
            if self.entry_quantidade.get().strip():
                dados["quantidade"] = int(self.entry_quantidade.get())
            if self.entry_estoque_min.get().strip():
                dados["estoque_minimo"] = int(self.entry_estoque_min.get())
            if self.entry_fornecedor.get().strip():
                dados["fornecedor"] = self.entry_fornecedor.get().strip()

            if not dados:
                messagebox.showwarning("Aviso", "Nenhum campo foi alterado!")
                return

            sucesso = self.db.atualizar_produto(nome_original, dados)
            if sucesso:
                messagebox.showinfo("Sucesso", f"Produto '{nome_original}' atualizado!")
                self.limpar_campos()
                self.atualizar_lista_produtos()
                self.atualizar_status(f"Produto '{nome_original}' atualizado")
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos inseridos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar produto: {e}")

    def deletar_produto(self):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para deletar!")
            return

        nome = self.tree_produtos.item(selecionado[0])["values"][0]
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar o produto '{nome}'?"):
            return

        sucesso = self.db.deletar_produto(nome)
        if sucesso:
            messagebox.showinfo("Sucesso", f"Produto '{nome}' deletado!")
            self.limpar_campos()
            self.atualizar_lista_produtos()
            self.atualizar_combo_produtos()
            self.atualizar_status(f"Produto '{nome}' deletado")

    def limpar_campos(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_categoria.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)
        self.entry_quantidade.delete(0, tk.END)
        self.entry_estoque_min.delete(0, tk.END)
        self.entry_fornecedor.delete(0, tk.END)

    def on_produto_select(self, event=None):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            return

        valores = self.tree_produtos.item(selecionado[0])["values"]
        self.limpar_campos()
        self.entry_nome.insert(0, valores[0])
        self.entry_categoria.insert(0, valores[1])
        self.entry_preco.insert(0, str(valores[2]).replace("R$ ", ""))
        self.entry_quantidade.insert(0, valores[3])
        self.entry_estoque_min.insert(0, valores[4])
        self.entry_fornecedor.insert(0, valores[5])

    def pesquisar_produtos(self, event=None):
        filtro = self.search_var.get()
        termo = self.entry_pesquisa.get().strip()

        if not termo:
            self.atualizar_lista_produtos()
            return

        produtos_filtrados = self.db.buscar_produtos_filtrados(filtro, termo)
        self.atualizar_lista_produtos(produtos_filtrados)
        self.atualizar_status(f"{len(produtos_filtrados)} produtos encontrados para '{termo}'")

    def limpar_pesquisa(self):
        self.entry_pesquisa.delete(0, tk.END)
        self.atualizar_lista_produtos()
        self.atualizar_status("Pesquisa limpa. Exibindo todos os produtos.")

    # =========================
    # Aba: Movimentações
    # =========================
    def criar_aba_movimentacoes(self):
        mov_frame = ttk.LabelFrame(self.frame_movimentacoes, text="Registrar Movimentação")
        mov_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(mov_frame, text="Produto:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.combo_produto = ttk.Combobox(mov_frame, width=30, state="readonly")
        self.combo_produto.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(mov_frame, text="Tipo:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.combo_tipo = ttk.Combobox(mov_frame, values=["entrada", "saida"], width=10, state="readonly")
        self.combo_tipo.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(mov_frame, text="Quantidade:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_qtd_mov = ttk.Entry(mov_frame, width=10)
        self.entry_qtd_mov.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(mov_frame, text="Observação:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_observacao = ttk.Entry(mov_frame, width=40)
        self.entry_observacao.grid(row=1, column=3, padx=5, pady=2)

        btn_mov_frame = ttk.Frame(mov_frame)
        btn_mov_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(btn_mov_frame, text="Atualizar", command=self._atualizar_movimentacoes_ui).pack(side="left", padx=5)

        self.btn_registrar_movimentacao = ttk.Button(
            btn_mov_frame, text="Registrar Movimentação", command=self.registrar_movimentacao
        )
        self.btn_registrar_movimentacao.pack(side="left", padx=5)

        hist_frame = ttk.LabelFrame(self.frame_movimentacoes, text="Histórico de Movimentações")
        hist_frame.pack(fill="both", expand=True, padx=5, pady=5)

        colunas_mov = ("Data", "Produto", "Tipo", "Quantidade", "Usuário", "Observação")
        self.tree_movimentacoes = ttk.Treeview(hist_frame, columns=colunas_mov, show="headings", height=15)

        for col in colunas_mov:
            self.tree_movimentacoes.heading(col, text=col)
            if col == "Data":
                self.tree_movimentacoes.column(col, width=150)
            elif col == "Produto":
                self.tree_movimentacoes.column(col, width=200)
            elif col in {"Tipo", "Quantidade"}:
                self.tree_movimentacoes.column(col, width=80)
            else:
                self.tree_movimentacoes.column(col, width=120)

        scrollbar_mov = ttk.Scrollbar(hist_frame, orient="vertical", command=self.tree_movimentacoes.yview)
        self.tree_movimentacoes.configure(yscrollcommand=scrollbar_mov.set)
        self.tree_movimentacoes.pack(side="left", fill="both", expand=True)
        scrollbar_mov.pack(side="right", fill="y")

    def registrar_movimentacao(self):
        try:
            produto = self.combo_produto.get()
            tipo = self.combo_tipo.get()
            quantidade = int(self.entry_qtd_mov.get())
            observacao = self.entry_observacao.get().strip()

            if not produto or not tipo:
                messagebox.showerror("Erro", "Selecione produto e tipo de movimentação!")
                return

            produto_info = self.db.buscar_produto(produto)
            if not produto_info:
                messagebox.showerror("Erro", f"Produto '{produto}' não encontrado no estoque!")
                return

            saldo_atual = int(produto_info["quantidade"])
            if tipo == "saida" and quantidade > saldo_atual:
                messagebox.showwarning(
                    "Saldo insuficiente",
                    (
                        f"Saldo insuficiente para '{produto}'.\n\n"
                        f"Saldo atual: {saldo_atual}\n"
                        f"Quantidade solicitada: {quantidade}"
                    ),
                )
                self.atualizar_status(
                    f"Saldo insuficiente em '{produto}': disponível {saldo_atual}, solicitado {quantidade}"
                )
                return

            sucesso = self.db.registrar_movimentacao(produto, tipo, quantidade, observacao, self.usuario_logado)
            if sucesso:
                novo_saldo = saldo_atual + quantidade if tipo == "entrada" else saldo_atual - quantidade
                messagebox.showinfo(
                    "Sucesso",
                    (
                        f"Movimentação registrada: {tipo} de {quantidade} unidades\n\n"
                        f"Saldo anterior: {saldo_atual}\n"
                        f"Saldo atual: {novo_saldo}"
                    ),
                )
                self.entry_qtd_mov.delete(0, tk.END)
                self.entry_observacao.delete(0, tk.END)
                self.atualizar_lista_produtos()
                self.atualizar_lista_movimentacoes()
                self.atualizar_status(
                    f"Movimentação registrada: {tipo} {quantidade} {produto} | Saldo atual: {novo_saldo}"
                )
            else:
                messagebox.showerror(
                    "Falha",
                    "Não foi possível registrar a movimentação. Verifique saldo ou dados e tente novamente.",
                )
                self.atualizar_status(f"Falha ao registrar movimentação: {tipo} {quantidade} {produto}")
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar movimentação: {e}")

    def _atualizar_movimentacoes_ui(self):
        self.atualizar_combo_produtos()
        self.atualizar_lista_movimentacoes()
        self.atualizar_status("Lista de movimentações atualizada")

    # =========================
    # Aba: Relatórios
    # =========================
    def criar_aba_relatorios(self):
        stats_frame = ttk.LabelFrame(self.frame_relatorios, text="Estatísticas Gerais")
        stats_frame.pack(fill="x", padx=5, pady=5)

        self.label_stats = tk.Text(stats_frame, height=8, width=80, state="disabled")
        self.label_stats.pack(padx=10, pady=10)

        falta_frame = ttk.LabelFrame(self.frame_relatorios, text="Produtos em Falta ou Estoque Baixo")
        falta_frame.pack(fill="both", expand=True, padx=5, pady=5)

        colunas_falta = ("Produto", "Categoria", "Estoque Atual", "Estoque Mínimo", "Necessário")
        self.tree_falta = ttk.Treeview(falta_frame, columns=colunas_falta, show="headings", height=10)

        for col in colunas_falta:
            self.tree_falta.heading(col, text=col)
            self.tree_falta.column(col, width=140)

        scrollbar_falta = ttk.Scrollbar(falta_frame, orient="vertical", command=self.tree_falta.yview)
        self.tree_falta.configure(yscrollcommand=scrollbar_falta.set)
        self.tree_falta.pack(side="left", fill="both", expand=True)
        scrollbar_falta.pack(side="right", fill="y")

        btn_relatorio_frame = ttk.Frame(self.frame_relatorios)
        btn_relatorio_frame.pack(pady=10)

        self.btn_atualizar_relatorio = ttk.Button(
            btn_relatorio_frame, text="Atualizar Relatórios", command=self.atualizar_relatorios_com_confirmacao
        )
        self.btn_atualizar_relatorio.pack(side="left", padx=5)

        self.btn_salvar_local = ttk.Button(
            btn_relatorio_frame, text="Salvar Local", command=self.exportar_para_excel_local
        )
        self.btn_salvar_local.pack(side="left", padx=5)

        self.btn_salvar_nuvem = ttk.Button(
            btn_relatorio_frame, text="Salvar e Enviar para Nuvem", command=self.exportar_para_excel_nuvem
        )
        self.btn_salvar_nuvem.pack(side="left", padx=5)

    def atualizar_relatorios(self):
        if not hasattr(self, "label_stats"):
            return

        relatorio = self.db.relatorio_estoque()

        self.label_stats.config(state="normal")
        self.label_stats.delete(1.0, tk.END)

        valor_total = float(relatorio.get("valor_total", 0) or 0)
        quantidade_total = int(relatorio.get("quantidade_total", 0) or 0)
        media = valor_total / max(quantidade_total, 1)

        stats_text = f"""📊 ESTATÍSTICAS GERAIS DO ESTOQUE
💼 Total de produtos cadastrados: {relatorio.get('total_produtos', 0)}
📦 Total de itens em estoque: {quantidade_total}
💰 Valor total do estoque: R$ {valor_total:,.2f}
🔄 Total de movimentações: {relatorio.get('total_movimentacoes', 0)}
⚠️ Produtos em situação crítica: {relatorio.get('produtos_criticos', 0)}
📈 Valor médio por item: R$ {media:.2f}

Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        self.label_stats.insert(1.0, stats_text)
        self.label_stats.config(state="disabled")

        for item in self.tree_falta.get_children():
            self.tree_falta.delete(item)

        produtos_criticos = self.db.produtos_em_falta()
        for produto in produtos_criticos:
            necessario = max(int(produto["estoque_minimo"]) - int(produto["quantidade"]), 0)
            self.tree_falta.insert(
                "",
                "end",
                values=(
                    produto["nome"],
                    produto["categoria"],
                    produto["quantidade"],
                    produto["estoque_minimo"],
                    necessario,
                ),
            )

    def exportar_para_excel(self):
        try:
            destino_nuvem = messagebox.askyesnocancel(
                "Destino do Relatorio",
                "Deseja enviar a planilha para a nuvem (Google Drive)?\n\n"
                "Sim: salvar localmente em outputs/backups e enviar para nuvem\n"
                "Nao: salvar apenas localmente em outputs/backups\n"
                "Cancelar: interromper exportacao",
            )
            if destino_nuvem is None:
                return

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_filename = f"relatorio_estoque_{timestamp}.xlsx"
            pasta_backups = self.project_root / "outputs" / "backups"
            pasta_backups.mkdir(parents=True, exist_ok=True)
            caminho_arquivo = pasta_backups / default_filename

            sucesso = self.db.exportar_para_excel(str(caminho_arquivo))
            if not sucesso:
                messagebox.showerror("Erro", "Falha ao exportar o relatório para Excel.")
                return

            if destino_nuvem:
                file_id = self._enviar_arquivo_para_drive(caminho_arquivo)
                messagebox.showinfo(
                    "Sucesso",
                    "Relatório exportado com sucesso.\n\n"
                    f"Arquivo local:\n{caminho_arquivo}\n\n"
                    f"Upload no Drive concluido (file_id: {file_id})",
                )
                self.atualizar_status("Relatório exportado para Excel (local + nuvem)")
                return

            messagebox.showinfo(
                "Sucesso",
                f"Relatório exportado com sucesso para:\n{caminho_arquivo}",
            )
            self.atualizar_status("Relatório exportado para Excel (local)")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao exportar: {e}")

    def exportar_para_excel_local(self):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_filename = f"relatorio_estoque_{timestamp}.xlsx"

            caminho_str = filedialog.asksaveasfilename(
                title="Salvar Relatório como",
                initialdir=str(self.project_root / "outputs" / "backups"),
                initialfile=default_filename,
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx"), ("Todos", "*")],
            )

            if not caminho_str:
                return

            caminho_arquivo = Path(caminho_str)

            # Garante que a pasta exista se o usuário escolher um caminho dentro do projeto
            try:
                caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

            sucesso = self.db.exportar_para_excel(str(caminho_arquivo))
            if not sucesso:
                messagebox.showerror("Erro", "Falha ao exportar o relatório para Excel.")
                return

            messagebox.showinfo(
                "Sucesso",
                f"Relatório exportado com sucesso para:\n{caminho_arquivo}",
            )
            self.atualizar_status("Relatório exportado para Excel (local)")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao exportar: {e}")

    def exportar_para_excel_nuvem(self):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_filename = f"relatorio_estoque_{timestamp}.xlsx"
            pasta_backups = self.project_root / "outputs" / "backups"
            pasta_backups.mkdir(parents=True, exist_ok=True)
            caminho_arquivo = pasta_backups / default_filename

            sucesso = self.db.exportar_para_excel(str(caminho_arquivo))
            if not sucesso:
                messagebox.showerror("Erro", "Falha ao exportar o relatório para Excel.")
                return

            file_id = self._enviar_arquivo_para_drive(caminho_arquivo)
            messagebox.showinfo(
                "Sucesso",
                "Relatório exportado com sucesso.\n\n"
                f"Arquivo local:\n{caminho_arquivo}\n\n"
                f"Upload no Drive concluido (file_id: {file_id})",
            )
            self.atualizar_status("Relatório exportado para Excel (local + nuvem)")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao exportar: {e}")

    def atualizar_relatorios_com_confirmacao(self):
        try:
            self.atualizar_relatorios()
            messagebox.showinfo("Relatórios", "Relatórios atualizados com sucesso.")
            self.atualizar_status("Relatórios atualizados")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar relatórios: {e}")
            self.atualizar_status("Falha ao atualizar relatórios")

    def _enviar_arquivo_para_drive(self, caminho_arquivo: Path) -> str:
        from scripts.backup_offsite import upload_file_to_drive

        cfg = self._carregar_config_backup()
        oauth_client_secret_path = self.project_root / "credentials_oauth.json"
        default_credentials_path = self.project_root / "credentials.json"
        oauth_token_path = self.project_root / "token_google_drive.json"
        cfg_drive_auth_mode = (cfg.get("drive_auth_mode") or "auto").strip().lower()
        if cfg_drive_auth_mode not in {"auto", "oauth_user", "service_account"}:
            cfg_drive_auth_mode = "auto"

        drive_auth_mode = "oauth_user"
        drive_service_account_json = None

        if cfg_drive_auth_mode == "service_account":
            drive_auth_mode = "service_account"
            if default_credentials_path.exists():
                drive_service_account_json = default_credentials_path
        elif cfg_drive_auth_mode == "oauth_user":
            drive_auth_mode = "oauth_user"
        else:
            if default_credentials_path.exists():
                try:
                    cred_data = json.loads(default_credentials_path.read_text(encoding="utf-8"))
                    if isinstance(cred_data, dict) and cred_data.get("type") == "service_account":
                        drive_auth_mode = "service_account"
                        drive_service_account_json = default_credentials_path
                    elif not oauth_client_secret_path.exists():
                        oauth_client_secret_path = default_credentials_path
                except Exception:
                    if not oauth_client_secret_path.exists():
                        oauth_client_secret_path = default_credentials_path

        return upload_file_to_drive(
            file_path=caminho_arquivo,
            drive_folder_id=((cfg.get("drive_folder_id") or "").strip() or None),
            drive_auth_mode=drive_auth_mode,
            drive_service_account_json=drive_service_account_json,
            drive_oauth_client_secret_json=(
                oauth_client_secret_path
                if drive_auth_mode == "oauth_user" and oauth_client_secret_path.exists()
                else None
            ),
            drive_oauth_token_json=oauth_token_path,
        )

    # =========================
    # Aba: Usuários
    # =========================
    def criar_aba_usuarios(self):
        frame = ttk.Frame(self.frame_usuarios)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        colunas = ("Usuário", "Perfil")
        self.tree_usuarios = ttk.Treeview(frame, columns=colunas, show="headings", height=16)
        self.tree_usuarios.heading("Usuário", text="Usuário")
        self.tree_usuarios.heading("Perfil", text="Perfil")
        self.tree_usuarios.column("Usuário", width=220)
        self.tree_usuarios.column("Perfil", width=120)

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=scroll.set)
        self.tree_usuarios.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        btns = ttk.Frame(self.frame_usuarios)
        btns.pack(fill="x", padx=8, pady=6)

        self.btn_novo_usuario = ttk.Button(btns, text="Novo", command=self.novo_usuario)
        self.btn_novo_usuario.pack(side="left", padx=4)
        self.btn_editar_usuario = ttk.Button(btns, text="Editar", command=self.editar_usuario)
        self.btn_editar_usuario.pack(side="left", padx=4)
        self.btn_deletar_usuario = ttk.Button(btns, text="Deletar", command=self.deletar_usuario)
        self.btn_deletar_usuario.pack(side="left", padx=4)

        self.atualizar_lista_usuarios()

    def atualizar_lista_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)

        for usuario in self.db.listar_usuarios():
            perfil_label = self.PROFILE_VALUE_TO_LABEL.get(usuario["perfil"], usuario["perfil"])
            self.tree_usuarios.insert("", "end", values=(usuario["username"], perfil_label))

    def novo_usuario(self):
        self.abrir_form_usuario(modo="novo")

    def editar_usuario(self):
        selecionado = self.tree_usuarios.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário para editar!")
            return

        username = self.tree_usuarios.item(selecionado[0])["values"][0]
        perfil_label = self.tree_usuarios.item(selecionado[0])["values"][1]
        perfil_internal = self.PROFILE_LABEL_TO_VALUE.get(perfil_label, perfil_label)

        if self.perfil_usuario.strip().lower() == "gerente" and str(perfil_internal).strip().lower() != "operador":
            messagebox.showerror("Permissão", "Gerente só pode editar usuários do tipo Operador.")
            return

        self.abrir_form_usuario(modo="editar", username=username, perfil=perfil_internal)

    def deletar_usuario(self):
        if self.perfil_usuario.strip().lower() != "adm":
            messagebox.showerror("Permissão", "Apenas ADM pode deletar usuários.")
            return

        selecionado = self.tree_usuarios.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário para deletar!")
            return

        username = self.tree_usuarios.item(selecionado[0])["values"][0]
        if username == self.usuario_logado:
            messagebox.showwarning("Aviso", "Você não pode excluir seu próprio usuário logado.")
            return

        if not messagebox.askyesno("Confirmar", f"Deseja deletar o usuário '{username}'?"):
            return

        if self.db.deletar_usuario(username, executor_perfil=self.perfil_usuario):
            messagebox.showinfo("Sucesso", "Usuário deletado com sucesso!")
            self.atualizar_lista_usuarios()
        else:
            messagebox.showerror(
                "Falha ao deletar",
                "Operação não permitida ou usuário não encontrado.\n"
                "Regra de segurança: não é permitido remover o último ADM.",
            )

    def abrir_form_usuario(self, modo: str, username: str = "", perfil: str = "operador"):
        janela = tk.Toplevel(self.root)
        janela.title("Novo Usuário" if modo == "novo" else "Editar Usuário")
        janela.geometry("350x240")
        janela.resizable(False, False)
        janela.transient(self.root)
        janela.grab_set()

        frame = ttk.Frame(janela, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Usuário:").pack(anchor="w")
        entry_usuario = ttk.Entry(frame, width=30)
        entry_usuario.pack(fill="x", pady=(0, 8))
        entry_usuario.insert(0, username)

        ttk.Label(frame, text="Senha:").pack(anchor="w")
        entry_senha = ttk.Entry(frame, width=30, show="*")
        entry_senha.pack(fill="x", pady=(0, 8))
        if modo == "editar":
            ttk.Label(frame, text="(deixe em branco para manter a senha)").pack(anchor="w", pady=(0, 8))

        ttk.Label(frame, text="Perfil:").pack(anchor="w")
        # Mostrar rótulos amigáveis na UI
        perfis_disponiveis = list(self.PROFILE_LABEL_TO_VALUE.keys())
        # Se o usuário logado for Gerente, só pode criar/editar Operador
        if self.perfil_usuario.strip().lower() == "gerente":
            perfis_disponiveis = ["Operador"]

        combo_perfil = ttk.Combobox(frame, values=perfis_disponiveis, state="readonly")
        combo_perfil.pack(fill="x", pady=(0, 10))
        # perfil recebido pode ser o valor interno; converter para label para exibir
        perfil_label_default = self.PROFILE_VALUE_TO_LABEL.get(perfil, perfil)
        combo_perfil.set(perfil_label_default if perfil_label_default in perfis_disponiveis else perfis_disponiveis[-1])

        def salvar():
            novo_username = entry_usuario.get().strip()
            nova_senha = entry_senha.get()
            novo_perfil = combo_perfil.get().strip()
            # converter rótulo para valor interno antes de operações no DB
            novo_perfil_val = self.PROFILE_LABEL_TO_VALUE.get(novo_perfil, novo_perfil)

            if not novo_username or not novo_perfil:
                messagebox.showerror("Erro", "Usuário e perfil são obrigatórios.", parent=janela)
                return

            if self.perfil_usuario.strip().lower() == "gerente" and novo_perfil_val != "operador":
                messagebox.showerror(
                    "Permissão",
                    "Gerente só pode criar/editar usuários do tipo operador.",
                    parent=janela,
                )
                return

            if modo == "novo":
                if not nova_senha:
                    messagebox.showerror("Erro", "Senha é obrigatória para novo usuário.", parent=janela)
                    return
                senha_hash = self.db.gerar_hash_senha(nova_senha)
                if self.db.criar_usuario(
                    novo_username,
                    senha_hash,
                    novo_perfil_val,
                    executor_perfil=self.perfil_usuario,
                ):
                    messagebox.showinfo("Sucesso", "Usuário criado com sucesso!", parent=janela)
                    janela.destroy()
            else:
                nova_senha_hash = self.db.gerar_hash_senha(nova_senha) if nova_senha else None
                if self.db.atualizar_usuario(
                    username_original=username,
                    novo_username=novo_username,
                    novo_perfil=novo_perfil_val,
                    nova_senha_hash=nova_senha_hash,
                    executor_perfil=self.perfil_usuario,
                ):
                    messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!", parent=janela)
                    janela.destroy()
                else:
                    messagebox.showerror(
                        "Falha ao atualizar",
                        "Operação não permitida ou inválida.\n"
                        "Regra de segurança: não é permitido rebaixar o último ADM.",
                        parent=janela,
                    )

            self.atualizar_lista_usuarios()

        botoes = ttk.Frame(frame)
        botoes.pack(fill="x")
        ttk.Button(botoes, text="Salvar", command=salvar).pack(side="left")
        ttk.Button(botoes, text="Cancelar", command=janela.destroy).pack(side="right")

    # =========================
    # Aba: Config Backup (ADM)
    # =========================
    def _carregar_config_backup(self):
        if self.backup_config_path.exists():
            try:
                with open(self.backup_config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "horario_backup": "03:00",
            "frequencia": "diaria",
            "drive_folder_id": "",
            "updated_at": None,
        }

    @staticmethod
    def _texto_frequencia_backup(valor_frequencia: str) -> str:
        mapa = {
            "diaria": "Diaria",
            "semanal": "Semanal",
            "mensal": "Mensal",
        }
        return mapa.get((valor_frequencia or "").strip().lower(), "Diaria")

    def _atualizar_indicador_frequencia_backup(self):
        if not hasattr(self, "label_frequencia_backup"):
            return

        cfg = self._carregar_config_backup()
        frequencia = self._texto_frequencia_backup(cfg.get("frequencia", "diaria"))
        horario = (cfg.get("horario_backup") or "03:00").strip()
        self.label_frequencia_backup.config(text=f"Backup automatico: {frequencia} as {horario}")

    def _criar_aba_config_backup(self):
        frame = ttk.Frame(self.frame_config_backup, padding=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        cfg = self._carregar_config_backup()

        ttk.Label(frame, text="Horário do Backup (HH:MM):").grid(row=0, column=0, sticky="w", pady=6)
        self.var_horario_backup = tk.StringVar(value=cfg.get("horario_backup", "03:00"))
        ttk.Entry(frame, textvariable=self.var_horario_backup, width=12).grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Frequência:").grid(row=1, column=0, sticky="w", pady=6)
        self.var_freq_backup = tk.StringVar(value=cfg.get("frequencia", "diaria"))
        ttk.Combobox(
            frame,
            textvariable=self.var_freq_backup,
            values=["diaria", "semanal", "mensal"],
            state="readonly",
            width=12,
        ).grid(row=1, column=1, sticky="w", pady=6)

        botoes = ttk.Frame(frame)
        botoes.grid(row=2, column=0, columnspan=2, sticky="w", pady=12)

        ttk.Button(botoes, text="Salvar Configuração", command=self._salvar_config_backup).pack(side="left")

        self.btn_backup_agora = ttk.Button(
            botoes,
            text="Executar Backup Agora",
            command=self._executar_backup_agora,
        )
        self.btn_backup_agora.pack(side="left", padx=(8, 0))

        self.btn_sync_pendentes = ttk.Button(
            botoes,
            text="Sincronizar Pendentes com Drive",
            command=self._sincronizar_pendentes_manual,
        )
        self.btn_sync_pendentes.pack(side="left", padx=(8, 0))

        ttk.Separator(frame, orient="horizontal").grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 12))

        ttk.Label(frame, text="Validar / Restaurar Backup (.enc.json):").grid(row=4, column=0, sticky="w", pady=6)
        self.var_restore_backup_file = tk.StringVar(value=self._sugerir_ultimo_backup_local())
        ttk.Entry(frame, textvariable=self.var_restore_backup_file, width=70).grid(
            row=4,
            column=1,
            sticky="ew",
            pady=6,
        )

        ttk.Label(frame, text="Chave Privada RSA (PEM):").grid(row=5, column=0, sticky="w", pady=6)
        self.var_restore_private_key = tk.StringVar(value=str(self.project_root / "keys" / "backup_private.pem"))
        ttk.Entry(frame, textvariable=self.var_restore_private_key, width=70).grid(
            row=5,
            column=1,
            sticky="ew",
            pady=6,
        )

        botoes_restore = ttk.Frame(frame)
        botoes_restore.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 4))

        ttk.Button(
            botoes_restore,
            text="Selecionar .enc.json",
            command=self._selecionar_arquivo_backup_restore,
        ).pack(side="left")

        ttk.Button(
            botoes_restore,
            text="Selecionar Chave Privada",
            command=self._selecionar_chave_privada_restore,
        ).pack(side="left", padx=(8, 0))

        self.btn_validar_backup = ttk.Button(
            botoes_restore,
            text="Validar Backup Selecionado",
            command=self._validar_backup_selecionado,
        )
        self.btn_validar_backup.pack(side="left", padx=(8, 0))

        self.btn_restaurar_backup = ttk.Button(
            botoes_restore,
            text="Restaurar Backup Selecionado",
            command=self._restaurar_backup_selecionado,
        )
        self.btn_restaurar_backup.pack(side="left", padx=(8, 0))

        ttk.Separator(frame, orient="horizontal").grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 10))

        ttk.Label(frame, text="Histórico de Backups (local / nuvem):").grid(row=8, column=0, sticky="w", pady=(0, 6))

        frame_hist = ttk.Frame(frame)
        frame_hist.grid(row=9, column=0, columnspan=2, sticky="nsew")
        frame.rowconfigure(9, weight=1)
        frame_hist.columnconfigure(0, weight=1)

        colunas_hist = ("data_hora", "arquivo", "local", "nuvem", "tentativas", "erro")
        self.tree_backup_historico = ttk.Treeview(frame_hist, columns=colunas_hist, show="headings", height=8)
        self.tree_backup_historico.grid(row=0, column=0, sticky="nsew")

        self.tree_backup_historico.heading("data_hora", text="Data/Hora")
        self.tree_backup_historico.heading("arquivo", text="Arquivo")
        self.tree_backup_historico.heading("local", text="Local")
        self.tree_backup_historico.heading("nuvem", text="Nuvem")
        self.tree_backup_historico.heading("tentativas", text="Tentativas")
        self.tree_backup_historico.heading("erro", text="Ultimo Erro")

        self.tree_backup_historico.column("data_hora", width=150, anchor="center")
        self.tree_backup_historico.column("arquivo", width=280, anchor="w")
        self.tree_backup_historico.column("local", width=80, anchor="center")
        self.tree_backup_historico.column("nuvem", width=110, anchor="center")
        self.tree_backup_historico.column("tentativas", width=80, anchor="center")
        self.tree_backup_historico.column("erro", width=350, anchor="w")

        scroll_hist = ttk.Scrollbar(frame_hist, orient="vertical", command=self.tree_backup_historico.yview)
        scroll_hist.grid(row=0, column=1, sticky="ns")
        self.tree_backup_historico.configure(yscrollcommand=scroll_hist.set)

        ttk.Button(
            frame,
            text="Atualizar Historico",
            command=self._atualizar_historico_backups_ui,
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=(8, 0))

    def _salvar_config_backup(self):
        horario = (self.var_horario_backup.get() or "").strip()
        frequencia = (self.var_freq_backup.get() or "").strip().lower()
        # Pasta do Drive fixa: preserva valor ja salvo no arquivo de configuracao.
        cfg_atual = self._carregar_config_backup()
        drive_folder_id = (cfg_atual.get("drive_folder_id") or "").strip()
        drive_auth_mode = (cfg_atual.get("drive_auth_mode") or "auto").strip().lower()
        if drive_auth_mode not in {"auto", "oauth_user", "service_account"}:
            drive_auth_mode = "auto"

        if not re.fullmatch(r"^([01]\d|2[0-3]):([0-5]\d)$", horario):
            messagebox.showerror("Erro", "Horário inválido. Use HH:MM (ex: 03:00).")
            return

        if frequencia not in {"diaria", "semanal", "mensal"}:
            messagebox.showerror("Erro", "Frequência inválida. Use diaria, semanal ou mensal.")
            return

        payload = {
            "horario_backup": horario,
            "frequencia": frequencia,
            "drive_folder_id": drive_folder_id,
            "drive_auth_mode": drive_auth_mode,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }

        try:
            with open(self.backup_config_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Sucesso", f"Configuração salva em:\n{self.backup_config_path}")
            self._atualizar_indicador_frequencia_backup()
            self.atualizar_status("Configuração de backup salva")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar config_backup.json:\n{e}")

    def _executar_backup_agora(self):
        if hasattr(self, "btn_backup_agora"):
            self.btn_backup_agora.config(state="disabled")

        self.atualizar_status("Executando backup agora...")

        def tarefa_backup():
            try:
                from scripts.backup_offsite import run_backup

                public_key_path = self.project_root / "keys" / "backup_public.pem"
                cfg = self._carregar_config_backup()
                oauth_client_secret_path = self.project_root / "credentials_oauth.json"
                default_credentials_path = self.project_root / "credentials.json"
                oauth_token_path = self.project_root / "token_google_drive.json"
                cfg_drive_auth_mode = (cfg.get("drive_auth_mode") or "auto").strip().lower()
                if cfg_drive_auth_mode not in {"auto", "oauth_user", "service_account"}:
                    cfg_drive_auth_mode = "auto"

                drive_auth_mode = "oauth_user"
                drive_service_account_json = None

                # Modo fixo para usar conta de servico (robo) e evitar fluxo OAuth no navegador.
                if cfg_drive_auth_mode == "service_account":
                    drive_auth_mode = "service_account"
                    if default_credentials_path.exists():
                        drive_service_account_json = str(default_credentials_path)
                elif cfg_drive_auth_mode == "oauth_user":
                    drive_auth_mode = "oauth_user"
                else:
                    # Auto: prioriza service account quando credentials.json for desse tipo.
                    if default_credentials_path.exists():
                        try:
                            with default_credentials_path.open("r", encoding="utf-8") as cred_file:
                                cred_data = json.load(cred_file)
                            if isinstance(cred_data, dict) and cred_data.get("type") == "service_account":
                                drive_auth_mode = "service_account"
                                drive_service_account_json = str(default_credentials_path)
                            elif not oauth_client_secret_path.exists():
                                oauth_client_secret_path = default_credentials_path
                        except Exception:
                            if not oauth_client_secret_path.exists():
                                # Em caso de JSON invalido, o erro sera registrado no log no fluxo OAuth.
                                oauth_client_secret_path = default_credentials_path

                if not public_key_path.exists():
                    self.root.after(
                        0,
                        lambda chave=public_key_path: self._finalizar_backup_agora_erro(
                            FileNotFoundError(
                                "Chave publica de backup nao encontrada. "
                                f"Configure a chave em: {chave}"
                            )
                        ),
                    )
                    return

                args = argparse.Namespace(
                    db_path=str(self.project_root / "estoque.db"),
                    output_dir=str(self.project_root / "outputs" / "backups"),
                    public_key=str(public_key_path),
                    log_file=str(self.project_root / "outputs" / "logs" / "backup_offsite.log"),
                    keep_plain_archive=False,
                    drive_service_account_json=drive_service_account_json,
                    drive_folder_id=((cfg.get("drive_folder_id") or "").strip() or None),
                    drive_auth_mode=drive_auth_mode,
                    drive_oauth_client_secret_json=(
                        str(oauth_client_secret_path)
                        if drive_auth_mode == "oauth_user" and oauth_client_secret_path.exists()
                        else None
                    ),
                    drive_oauth_token_json=str(oauth_token_path),
                    strict_drive_upload=False,
                )

                rc = run_backup(args)
                self.root.after(0, lambda: self._finalizar_backup_agora(rc, Path(args.output_dir), Path(args.log_file)))
            except ModuleNotFoundError as e:
                if getattr(e, "name", "") == "cryptography":
                    self.root.after(
                        0,
                        lambda: self._finalizar_backup_agora_erro(
                            ModuleNotFoundError(
                                "Dependencia 'cryptography' nao encontrada. "
                                "Instale as dependencias do projeto para habilitar backup criptografado."
                            )
                        ),
                    )
                    return
                self.root.after(0, lambda erro=e: self._finalizar_backup_agora_erro(erro))
            except Exception as e:
                # Bind da excecao no lambda para evitar perda de referencia fora do bloco except.
                self.root.after(0, lambda erro=e: self._finalizar_backup_agora_erro(erro))

        threading.Thread(target=tarefa_backup, daemon=True).start()

    def _finalizar_backup_agora(self, return_code: int, output_dir: Path, log_file: Path):
        if hasattr(self, "btn_backup_agora"):
            self.btn_backup_agora.config(state="normal")

        arquivo_gerado = self._obter_ultimo_backup_criptografado(output_dir)

        if return_code == 0:
            ultimo_backup = ""
            if arquivo_gerado:
                ultimo_backup = f"\n\nArquivo gerado:\n{arquivo_gerado}"
                self._registrar_evento_backup(
                    arquivo_gerado,
                    status_local="OK",
                    status_nuvem="OK",
                    tentativas_upload=1,
                    ultimo_erro="",
                )
                self._atualizar_historico_backups_ui()

            messagebox.showinfo(
                "Sucesso",
                f"Backup executado com sucesso.{ultimo_backup}\n\nLog:\n{log_file}",
            )
            self.atualizar_status("Backup executado manualmente com sucesso")
            return

        if return_code == 2:
            ultimo_backup = ""
            if arquivo_gerado:
                ultimo_backup = f"\n\nArquivo gerado:\n{arquivo_gerado}"

            detalhe_upload = self._resumir_falha_upload_drive(log_file)
            orientacao = (
                "Verifique se o arquivo credentials_oauth.json existe no projeto e se a conta usada tem permissao de upload no Drive."
            )

            if "No module named 'google_auth_oauthlib'" in detalhe_upload:
                orientacao = (
                    "Dependencia ausente: google-auth-oauthlib. "
                    "Instale as dependencias do projeto (requirements.txt) na mesma .venv usada para abrir a GUI."
                )
            elif "Credencial OAuth de usuario nao encontrada" in detalhe_upload:
                orientacao = (
                    "Arquivo de credencial OAuth nao encontrado. "
                    "Adicione credentials_oauth.json (ou credentials.json com tipo OAuth) na raiz do projeto."
                )
            elif "storageQuotaExceeded" in detalhe_upload or "Service Accounts do not have storage quota" in detalhe_upload:
                orientacao = (
                    "A conta de servico nao grava em Meu Drive por falta de cota. "
                    "Crie/uso uma pasta em Shared Drive, compartilhe com o e-mail da service account como Content manager, "
                    "atualize o drive_folder_id dessa pasta e tente sincronizar novamente."
                )
            elif "File not found:" in detalhe_upload:
                orientacao = (
                    "ID de pasta invalido ou sem permissao de acesso para a credencial configurada no Google Drive."
                )
            elif "invalid_grant" in detalhe_upload or "expired or revoked" in detalhe_upload:
                orientacao = (
                    "Token OAuth expirado/revogado para a conta atual. "
                    "Remova token_google_drive.json e execute a sincronizacao novamente para autenticar com o novo e-mail."
                )
            elif "access_denied" in detalhe_upload or "OAuth bloqueado pelo Google" in detalhe_upload:
                orientacao = (
                    "A conta atual nao esta autorizada no app OAuth. "
                    "No Google Cloud Console, adicione esse e-mail em OAuth Consent Screen > Test users "
                    "(ou publique/verifique o app) e tente novamente."
                )

            if arquivo_gerado:
                self._registrar_evento_backup(
                    arquivo_gerado,
                    status_local="OK",
                    status_nuvem="PENDENTE",
                    tentativas_upload=1,
                    ultimo_erro=detalhe_upload,
                )
                self._atualizar_historico_backups_ui()
                self._sincronizar_pendentes_em_background(mostrar_feedback=False)

            messagebox.showwarning(
                "Backup executado com ressalva",
                "Backup local criptografado concluido, mas o upload no Google Drive falhou."
                "\nO arquivo ficou pendente e sera reenviado automaticamente quando houver internet."
                f"{ultimo_backup}\n\n"
                f"Motivo detectado:\n{detalhe_upload}\n\n"
                f"{orientacao}"
                f"\n\nConsulte o log para detalhes:\n{log_file}",
            )
            self.atualizar_status("Backup local OK; upload pendente para sincronizacao")
            return

        messagebox.showerror(
            "Erro",
            f"Falha ao executar backup agora.\nConsulte o log em:\n{log_file}",
        )
        self.atualizar_status("Falha na execução manual do backup")

    def _finalizar_backup_agora_erro(self, erro: Exception):
        if hasattr(self, "btn_backup_agora"):
            self.btn_backup_agora.config(state="normal")

        messagebox.showerror(
            "Erro",
            f"Não foi possível iniciar o backup agora:\n{erro}",
        )
        self.atualizar_status("Erro ao iniciar backup manual")

    def _sugerir_ultimo_backup_local(self) -> str:
        try:
            pasta_backups = self.project_root / "outputs" / "backups"
            arquivos = sorted(
                pasta_backups.glob("*.enc.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if arquivos:
                return str(arquivos[0])
        except Exception:
            pass
        return ""

    def _selecionar_arquivo_backup_restore(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar backup criptografado (.enc.json)",
            filetypes=[("Backup criptografado", "*.enc.json"), ("JSON", "*.json"), ("Todos", "*.*")],
            initialdir=str(self.project_root / "outputs" / "backups"),
        )
        if caminho:
            self.var_restore_backup_file.set(caminho)

    def _selecionar_chave_privada_restore(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar chave privada RSA (PEM)",
            filetypes=[("Chave PEM", "*.pem"), ("Todos", "*.*")],
            initialdir=str(self.project_root / "keys"),
        )
        if caminho:
            self.var_restore_private_key.set(caminho)

    def _set_estado_botoes_restore(self, habilitado: bool):
        estado = "normal" if habilitado else "disabled"
        if hasattr(self, "btn_validar_backup"):
            self.btn_validar_backup.config(state=estado)
        if hasattr(self, "btn_restaurar_backup"):
            self.btn_restaurar_backup.config(state=estado)
        if hasattr(self, "btn_backup_agora"):
            self.btn_backup_agora.config(state=estado)
        if hasattr(self, "btn_sync_pendentes"):
            self.btn_sync_pendentes.config(state=estado)

    def _validar_backup_selecionado(self):
        caminho_backup = Path((self.var_restore_backup_file.get() or "").strip())
        chave_privada = Path((self.var_restore_private_key.get() or "").strip())

        if not caminho_backup.exists():
            messagebox.showerror("Erro", "Selecione um arquivo .enc.json válido.")
            return
        if not chave_privada.exists():
            messagebox.showerror("Erro", "Selecione uma chave privada .pem válida.")
            return

        self._set_estado_botoes_restore(False)
        self.atualizar_status("Validando backup selecionado...")

        def tarefa_validar():
            try:
                from scripts.backup_offsite import run_validate_restore

                args = argparse.Namespace(
                    encrypted_file=str(caminho_backup),
                    private_key=str(chave_privada),
                    private_key_passphrase=None,
                    test_restore_dir=str(self.project_root / "outputs" / "restore_test"),
                    log_file=str(self.project_root / "outputs" / "logs" / "backup_offsite.log"),
                )

                rc = run_validate_restore(args)
                self.root.after(0, lambda: self._finalizar_validacao_backup(rc, Path(args.log_file)))
            except Exception as e:
                self.root.after(0, lambda erro=e: self._finalizar_validacao_backup_erro(erro))

        threading.Thread(target=tarefa_validar, daemon=True).start()

    def _restaurar_backup_selecionado(self):
        caminho_backup = Path((self.var_restore_backup_file.get() or "").strip())
        chave_privada = Path((self.var_restore_private_key.get() or "").strip())

        if not caminho_backup.exists():
            messagebox.showerror("Erro", "Selecione um arquivo .enc.json válido.")
            return
        if not chave_privada.exists():
            messagebox.showerror("Erro", "Selecione uma chave privada .pem válida.")
            return

        output_default = self.project_root / "outputs" / "restore_test" / f"restaurado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        output_db = filedialog.asksaveasfilename(
            title="Salvar banco restaurado (.db)",
            initialdir=str((self.project_root / "outputs" / "restore_test")),
            initialfile=output_default.name,
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db"), ("Todos", "*.*")],
        )

        if not output_db:
            return

        self._set_estado_botoes_restore(False)
        self.atualizar_status("Restaurando backup selecionado...")

        def tarefa_restaurar():
            try:
                from scripts.backup_offsite import run_restore

                args = argparse.Namespace(
                    encrypted_file=str(caminho_backup),
                    private_key=str(chave_privada),
                    output_db=str(output_db),
                    private_key_passphrase=None,
                    log_file=str(self.project_root / "outputs" / "logs" / "backup_offsite.log"),
                )

                rc = run_restore(args)
                self.root.after(0, lambda: self._finalizar_restore_backup(rc, Path(args.output_db), Path(args.log_file)))
            except Exception as e:
                self.root.after(0, lambda erro=e: self._finalizar_restore_backup_erro(erro))

        threading.Thread(target=tarefa_restaurar, daemon=True).start()

    def _finalizar_validacao_backup(self, return_code: int, log_file: Path):
        self._set_estado_botoes_restore(True)

        if return_code == 0:
            messagebox.showinfo(
                "Validação concluída",
                "Backup validado com sucesso (integrity_check=ok).\n\n"
                f"Log:\n{log_file}",
            )
            self.atualizar_status("Validação de backup concluída com sucesso")
            return

        messagebox.showerror(
            "Erro na validação",
            f"Falha ao validar backup selecionado.\n\nConsulte o log:\n{log_file}",
        )
        self.atualizar_status("Falha na validação do backup selecionado")

    def _finalizar_validacao_backup_erro(self, erro: Exception):
        self._set_estado_botoes_restore(True)
        messagebox.showerror("Erro", f"Não foi possível validar o backup:\n{erro}")
        self.atualizar_status("Erro ao validar backup selecionado")

    def _finalizar_restore_backup(self, return_code: int, output_db: Path, log_file: Path):
        self._set_estado_botoes_restore(True)

        if return_code == 0:
            messagebox.showinfo(
                "Restore concluído",
                "Backup restaurado com sucesso.\n\n"
                f"Banco restaurado:\n{output_db}\n\n"
                f"Log:\n{log_file}",
            )
            self.atualizar_status("Backup restaurado com sucesso")
            return

        messagebox.showerror(
            "Erro no restore",
            f"Falha ao restaurar backup selecionado.\n\nConsulte o log:\n{log_file}",
        )
        self.atualizar_status("Falha ao restaurar backup selecionado")

    def _finalizar_restore_backup_erro(self, erro: Exception):
        self._set_estado_botoes_restore(True)
        messagebox.showerror("Erro", f"Não foi possível restaurar o backup:\n{erro}")
        self.atualizar_status("Erro ao restaurar backup selecionado")

    @staticmethod
    def _resumir_falha_upload_drive(log_file: Path) -> str:
        try:
            if not log_file.exists():
                return "Falha de upload no Drive (detalhe nao encontrado no log)."

            linhas = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            for linha in reversed(linhas):
                if "Falha no upload para Google Drive:" in linha:
                    return linha.split("Falha no upload para Google Drive:", 1)[1].strip() or linha.strip()
                if "ModuleNotFoundError:" in linha or "FileNotFoundError:" in linha:
                    return linha.strip()

            return "Falha de upload no Drive (consulte o traceback completo no log)."
        except Exception:
            return "Falha de upload no Drive (nao foi possivel ler o log)."

    @staticmethod
    def _extrair_data_hora_nome_arquivo(nome_arquivo: str) -> str:
        match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})", nome_arquivo)
        if match:
            return f"{match.group(1)} {match.group(2).replace('-', ':')}"

        match_legacy = re.search(r"(\d{8})_(\d{6})", nome_arquivo)
        if match_legacy:
            d = match_legacy.group(1)
            t = match_legacy.group(2)
            return f"{d[0:4]}-{d[4:6]}-{d[6:8]} {t[0:2]}:{t[2:4]}:{t[4:6]}"

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _carregar_historico_backups(self):
        try:
            if self.backup_history_path.exists():
                conteudo = json.loads(self.backup_history_path.read_text(encoding="utf-8"))
                if isinstance(conteudo, list):
                    return conteudo
                if isinstance(conteudo, dict) and isinstance(conteudo.get("items"), list):
                    return conteudo["items"]
        except Exception:
            pass
        return []

    def _salvar_historico_backups(self, itens):
        self.backup_history_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"items": itens}
        self.backup_history_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _registrar_evento_backup(
        self,
        arquivo_path: Path,
        status_local: str,
        status_nuvem: str,
        tentativas_upload: int = 0,
        ultimo_erro: str = "",
        drive_file_id: str = "",
    ):
        itens = self._carregar_historico_backups()
        nome = arquivo_path.name
        data_hora = self._extrair_data_hora_nome_arquivo(nome)

        existente = None
        for item in itens:
            if item.get("arquivo") == nome:
                existente = item
                break

        if existente is None:
            existente = {
                "arquivo": nome,
                "caminho": str(arquivo_path),
                "data_hora": data_hora,
                "status_local": status_local,
                "status_nuvem": status_nuvem,
                "tentativas_upload": tentativas_upload,
                "ultimo_erro": ultimo_erro,
                "drive_file_id": drive_file_id,
            }
            itens.append(existente)
        else:
            existente["caminho"] = str(arquivo_path)
            existente["data_hora"] = data_hora
            existente["status_local"] = status_local
            existente["status_nuvem"] = status_nuvem
            existente["tentativas_upload"] = max(
                int(existente.get("tentativas_upload", 0)),
                int(tentativas_upload),
            )
            existente["ultimo_erro"] = ultimo_erro
            if drive_file_id:
                existente["drive_file_id"] = drive_file_id

        itens.sort(key=lambda x: x.get("data_hora", ""), reverse=True)
        self._salvar_historico_backups(itens)

    def _obter_ultimo_backup_criptografado(self, output_dir: Path) -> Path | None:
        try:
            arquivos = sorted(output_dir.glob("*.enc.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if arquivos:
                return arquivos[0]
        except Exception:
            pass
        return None

    def _atualizar_historico_backups_ui(self):
        if not hasattr(self, "tree_backup_historico"):
            return

        for item in self.tree_backup_historico.get_children():
            self.tree_backup_historico.delete(item)

        itens = self._carregar_historico_backups()
        for item in itens:
            self.tree_backup_historico.insert(
                "",
                "end",
                values=(
                    item.get("data_hora", ""),
                    item.get("arquivo", ""),
                    item.get("status_local", ""),
                    item.get("status_nuvem", ""),
                    item.get("tentativas_upload", 0),
                    item.get("ultimo_erro", ""),
                ),
            )

    def _iniciar_agendador_sincronizacao_pendentes(self):
        self._agendar_proxima_sincronizacao_pendentes()

    def _agendar_proxima_sincronizacao_pendentes(self):
        if not self.root:
            return
        self.root.after(60_000, self._sincronizar_pendentes_automatico)

    def _sincronizar_pendentes_automatico(self):
        self._sincronizar_pendentes_em_background(mostrar_feedback=False)
        self._agendar_proxima_sincronizacao_pendentes()

    def _sincronizar_pendentes_manual(self):
        self._sincronizar_pendentes_em_background(mostrar_feedback=True)

    def _sincronizar_pendentes_em_background(self, mostrar_feedback: bool):
        if self.sync_pendentes_em_execucao:
            if mostrar_feedback:
                messagebox.showinfo("Sincronização", "Já existe uma sincronização em andamento.")
            return

        self.sync_pendentes_em_execucao = True

        def tarefa_sync():
            enviados = 0
            falhas = 0
            ultimo_erro = ""
            try:
                from scripts.backup_offsite import upload_encrypted_backup

                cfg = self._carregar_config_backup()
                itens = self._carregar_historico_backups()

                oauth_client_secret_path = self.project_root / "credentials_oauth.json"
                default_credentials_path = self.project_root / "credentials.json"
                oauth_token_path = self.project_root / "token_google_drive.json"
                cfg_drive_auth_mode = (cfg.get("drive_auth_mode") or "auto").strip().lower()
                if cfg_drive_auth_mode not in {"auto", "oauth_user", "service_account"}:
                    cfg_drive_auth_mode = "auto"

                drive_auth_mode = "oauth_user"
                drive_service_account_json = None

                if cfg_drive_auth_mode == "service_account":
                    drive_auth_mode = "service_account"
                    if default_credentials_path.exists():
                        drive_service_account_json = default_credentials_path
                elif cfg_drive_auth_mode == "oauth_user":
                    drive_auth_mode = "oauth_user"
                else:
                    if default_credentials_path.exists():
                        try:
                            cred_data = json.loads(default_credentials_path.read_text(encoding="utf-8"))
                            if isinstance(cred_data, dict) and cred_data.get("type") == "service_account":
                                drive_auth_mode = "service_account"
                                drive_service_account_json = default_credentials_path
                            elif not oauth_client_secret_path.exists():
                                oauth_client_secret_path = default_credentials_path
                        except Exception:
                            if not oauth_client_secret_path.exists():
                                oauth_client_secret_path = default_credentials_path

                for item in itens:
                    if item.get("status_nuvem") != "PENDENTE":
                        continue

                    arquivo = Path(item.get("caminho") or (self.project_root / "outputs" / "backups" / item.get("arquivo", "")))
                    if not arquivo.exists():
                        item["status_nuvem"] = "ERRO"
                        item["ultimo_erro"] = "Arquivo local nao encontrado para envio"
                        falhas += 1
                        continue

                    item["tentativas_upload"] = int(item.get("tentativas_upload", 0)) + 1

                    try:
                        file_id = upload_encrypted_backup(
                            encrypted_file_path=arquivo,
                            drive_folder_id=((cfg.get("drive_folder_id") or "").strip() or None),
                            drive_auth_mode=drive_auth_mode,
                            drive_service_account_json=drive_service_account_json,
                            drive_oauth_client_secret_json=(
                                oauth_client_secret_path
                                if drive_auth_mode == "oauth_user" and oauth_client_secret_path.exists()
                                else None
                            ),
                            drive_oauth_token_json=oauth_token_path,
                        )
                        item["status_nuvem"] = "OK"
                        item["drive_file_id"] = file_id
                        item["ultimo_erro"] = ""
                        enviados += 1
                    except Exception as exc:
                        item["status_nuvem"] = "PENDENTE"
                        item["ultimo_erro"] = str(exc)
                        ultimo_erro = str(exc)
                        falhas += 1

                self._salvar_historico_backups(itens)
            except Exception as exc:
                ultimo_erro = str(exc)
                falhas += 1
            finally:
                self.sync_pendentes_em_execucao = False

                def finalizar_ui():
                    self._atualizar_historico_backups_ui()
                    if mostrar_feedback:
                        if enviados > 0 and falhas == 0:
                            messagebox.showinfo("Sincronização", f"Sincronização concluída. Enviados: {enviados}.")
                        elif enviados > 0 and falhas > 0:
                            messagebox.showwarning(
                                "Sincronização",
                                f"Sincronização parcial. Enviados: {enviados}. Falhas: {falhas}.\n\nÚltimo erro:\n{ultimo_erro}",
                            )
                        elif falhas > 0:
                            messagebox.showwarning(
                                "Sincronização",
                                f"Nenhum backup pendente foi enviado. Falhas: {falhas}.\n\nÚltimo erro:\n{ultimo_erro}",
                            )
                        else:
                            messagebox.showinfo("Sincronização", "Não há backups pendentes para enviar.")

                self.root.after(0, finalizar_ui)

        threading.Thread(target=tarefa_sync, daemon=True).start()

    # =========================
    # Atualizações das listas
    # =========================
    def atualizar_lista_produtos(self, produtos_para_exibir=None):
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)

        produtos = produtos_para_exibir if produtos_para_exibir is not None else self.db.listar_produtos()

        for produto in produtos:
            status_base = self.db.calcular_status_estoque(produto["quantidade"], produto["estoque_minimo"])
            status_exibicao = {"OK": "OK", "BAIXO": "BAIXO", "CRITICO": "CRITICO"}.get(status_base, "OK")
            status_icon = self.status_icons.get(status_base, self.status_icons["OK"])

            self.tree_produtos.insert(
                "",
                "end",
                values=(
                    produto["nome"],
                    produto["categoria"],
                    f"R$ {produto['preco']:.2f}",
                    produto["quantidade"],
                    produto["estoque_minimo"],
                    produto["fornecedor"],
                    status_exibicao,
                ),
                image=status_icon,
            )

    def atualizar_combo_produtos(self):
        produtos = self.db.listar_produtos()
        self.combo_produto["values"] = [p["nome"] for p in produtos]

    def atualizar_lista_movimentacoes(self):
        for item in self.tree_movimentacoes.get_children():
            self.tree_movimentacoes.delete(item)

        movimentacoes = self.db.listar_movimentacoes(100)
        for mov in movimentacoes:
            data = mov["data_movimentacao"]
            if hasattr(data, "strftime"):
                data_formatada = data.strftime("%d/%m/%Y %H:%M")
            else:
                data_formatada = str(data)

            tipo_emoji = "📈 Entrada" if mov["tipo"] == "entrada" else "📉 Saída"
            self.tree_movimentacoes.insert(
                "",
                "end",
                values=(
                    data_formatada,
                    mov["produto_nome"],
                    tipo_emoji,
                    mov["quantidade"],
                    mov["usuario"],
                    mov.get("observacao", ""),
                ),
            )

    # =========================
    # Ícones de status
    # =========================
    @staticmethod
    def _hex_para_rgb(cor_hex):
        cor = cor_hex.lstrip("#")
        return (int(cor[0:2], 16), int(cor[2:4], 16), int(cor[4:6], 16))

    @staticmethod
    def _rgb_para_hex(rgb):
        return "#{:02X}{:02X}{:02X}".format(*rgb)

    @staticmethod
    def _misturar_cores(cor_a, cor_b, fator):
        return (
            int(cor_a[0] * (1 - fator) + cor_b[0] * fator),
            int(cor_a[1] * (1 - fator) + cor_b[1] * fator),
            int(cor_a[2] * (1 - fator) + cor_b[2] * fator),
        )

    def _criar_icone_circulo(self, cor_hex, tamanho=14):
        img = tk.PhotoImage(width=tamanho, height=tamanho)
        raio = (tamanho - 1) / 2
        centro = raio
        fundo = self.root.cget("bg")

        cor_base = self._hex_para_rgb(cor_hex)
        cor_borda = self._misturar_cores(cor_base, (0, 0, 0), 0.35)
        cor_luz = self._misturar_cores(cor_base, (255, 255, 255), 0.22)

        for x in range(tamanho):
            for y in range(tamanho):
                dx = x - centro
                dy = y - centro
                dist = (dx * dx + dy * dy) ** 0.5

                if dist > raio:
                    img.put(fundo, (x, y))
                    continue

                if dist > raio - 1.2:
                    fator = max(0.0, min(1.0, (dist - (raio - 1.2)) / 1.2))
                    cor = self._misturar_cores(cor_borda, cor_base, 1 - fator)
                    img.put(self._rgb_para_hex(cor), (x, y))
                    continue

                if dy < -1 and dx < 1:
                    img.put(self._rgb_para_hex(cor_luz), (x, y))
                else:
                    img.put(cor_hex, (x, y))

        return img

    def _criar_icones_status(self):
        return {
            "OK": self._criar_icone_circulo("#2E7D32"),
            "BAIXO": self._criar_icone_circulo("#F9A825"),
            "CRITICO": self._criar_icone_circulo("#C62828"),
        }

    # =========================
    # Utilitários
    # =========================
    def atualizar_status(self, mensagem):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"{timestamp} - {mensagem}")

    def on_closing(self):
        try:
            if self.root and messagebox.askokcancel("Sair", "Deseja fechar o sistema?"):
                self.db.fechar_conexao()
                self.root.destroy()
        except KeyboardInterrupt:
            if self.root:
                self.db.fechar_conexao()
                self.root.destroy()

    def executar(self):
        if not self.root:
            return
        self.atualizar_status("Sistema iniciado e pronto para uso")
        self.root.mainloop()


def main():
    root = tk.Tk()
    app = StockFlowGUI(root)
    if getattr(app, "root", None):
        app.executar()


if __name__ == "__main__":
    main()
