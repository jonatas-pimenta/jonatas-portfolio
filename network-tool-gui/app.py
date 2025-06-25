# Importações de bibliotecas padrão do Python
import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog, messagebox
from datetime import datetime
import threading
import queue

# Importações de módulos locais do projeto
import backend
import scanner

# --- Funções da Aba de Diagnóstico ---

def diagnostic_worker(host, result_queue):
    """
    Função executada em uma thread separada para realizar os testes de diagnóstico.
    Isso evita que a interface gráfica (GUI) congele durante operações demoradas.
    """
    ping_result = backend.run_ping(host)
    result_queue.put(("PING", ping_result))

    traceroute_result = backend.run_traceroute(host)
    result_queue.put(("TRACEROUTE", traceroute_result))

    nslookup_result = backend.run_nslookup(host)
    result_queue.put(("NSLOOKUP", nslookup_result))

    # Envia um sinal 'DONE' para a fila para indicar que o trabalho terminou.
    result_queue.put(("DONE", None))

def process_diagnostic_queue():
    """
    Verifica a fila de resultados de diagnóstico periodicamente.
    Esta função roda na thread principal da GUI e é segura para atualizar os widgets.
    """
    try:
        # Tenta pegar um item da fila sem bloquear.
        task_name, result_data = diagnostic_queue.get_nowait()
        if task_name == "DONE":
            # Se o trabalho terminou, reabilita o botão e para de verificar a fila.
            diag_button.config(state="normal")
            return

        diag_results_text.insert(tk.END, f"--- RESULTADO DO {task_name} ---\n")
        diag_results_text.insert(tk.END, result_data)
        diag_results_text.insert(tk.END, "\n\n")
        diag_results_text.see(tk.END)
    except queue.Empty: # Ocorre se a fila estiver vazia.
        pass
    # Agenda a si mesma para ser executada novamente após 100ms.
    # Este é o loop de polling que mantém a GUI atualizada.
    root.after(100, process_diagnostic_queue)

def start_diagnostics():
    """Função chamada pelo botão 'Verificar'. Inicia o processo de diagnóstico."""
    host = diag_host_entry.get()
    if not host:
        # Validação de entrada: exibe um aviso se o campo de host estiver vazio.
        messagebox.showwarning("Entrada Inválida", "Por favor, insira um host ou IP.")
        return

    # Desabilita o botão para prevenir múltiplos cliques enquanto uma verificação está em andamento.
    diag_button.config(state="disabled")
    # Limpa a área de resultados e exibe uma mensagem inicial.
    diag_results_text.delete('1.0', tk.END)
    diag_results_text.insert(tk.END, f"Executando verificações para: {host}\n\n")

    # Cria uma nova fila para esta execução.
    global diagnostic_queue
    diagnostic_queue = queue.Queue()
    # Cria e inicia a thread trabalhadora, passando o host e a fila como argumentos.
    threading.Thread(target=diagnostic_worker, args=(host, diagnostic_queue), daemon=True).start()
    # Inicia o processo de verificação da fila para atualizar a GUI.
    process_diagnostic_queue()

# --- Funções da Aba do Port Scanner ---

def scan_worker(host_ip, port_q, results_q):
    """Função do thread trabalhador para o scanner."""
    while not port_q.empty():
        try:
            port = port_q.get_nowait()
            scanner._scan_port(host_ip, port, results_q)
            port_q.task_done()
        except queue.Empty:
            break

def update_scan_ui():
    """
    Função de polling para a aba do scanner.
    Atualiza a barra de progresso e exibe portas abertas encontradas.
    """
    # Atualiza a barra de progresso
    processed_count = total_ports_to_scan - port_queue.unfinished_tasks
    scan_progressbar['value'] = processed_count

    # Processa resultados de portas abertas
    try:
        port, banner = scan_results_queue.get_nowait()
        scan_results_text.insert(tk.END, f"  Porta {port:<5} - Serviço: {banner}\n")
        scan_results_text.see(tk.END)
    except queue.Empty:
        pass

    # Continua o polling enquanto houver tarefas na fila.
    if port_queue.unfinished_tasks > 0:
        root.after(100, update_scan_ui)
    else:
        # Quando o scan termina, garante que a barra chegue a 100%.
        scan_progressbar['value'] = total_ports_to_scan # Garante que a barra chegue a 100%
        scan_results_text.insert(tk.END, "\nEscaneamento concluído.")
        scan_button.config(state="normal")

def start_scan():
    """Inicia o processo de scan de portas."""
    host = scan_host_entry.get()
    ports_str = scan_ports_entry.get()
    if not host or not ports_str:
        messagebox.showwarning("Entrada Inválida", "Por favor, insira o host e as portas.")
        return

    scan_button.config(state="disabled")
    scan_results_text.delete('1.0', tk.END)

    # Chama a função de preparação do módulo scanner para validar as entradas.
    scan_prep_result = scanner.run_scan(host, ports_str)
    if isinstance(scan_prep_result, str): # Verifica se retornou uma string de erro
        messagebox.showerror("Erro de Entrada", scan_prep_result)
        scan_button.config(state="normal")
        return

    # Desempacota o resultado da preparação.
    target_ip, ports_to_scan = scan_prep_result
    scan_results_text.insert(tk.END, f"Escaneando {host} ({target_ip}) em {len(ports_to_scan)} porta(s)...\n\n")

    # Prepara as filas para a comunicação entre threads.
    global port_queue, scan_results_queue, total_ports_to_scan
    port_queue = queue.Queue()
    total_ports_to_scan = len(ports_to_scan)
    for port in ports_to_scan:
        port_queue.put(port)

    scan_results_queue = queue.Queue()

    # Configura a barra de progresso
    scan_progressbar.config(maximum=total_ports_to_scan, value=0)

    # Cria e inicia os threads trabalhadores
    # O número de workers (100) está fixo, mas poderia ser um parâmetro da GUI.
    for _ in range(100): # 100 workers
        t = threading.Thread(target=scan_worker, args=(target_ip, port_queue, scan_results_queue), daemon=True)
        t.start()

    # Inicia o processo de atualização da UI
    update_scan_ui()

def save_results(text_widget):
    """Abre um diálogo para salvar o conteúdo de uma caixa de texto, adicionando data e hora."""
    content = text_widget.get("1.0", tk.END)
    if not content.strip():
        messagebox.showwarning("Aviso", "Não há resultados para salvar.")
        return
    
    # Pega a data e hora atuais
    now = datetime.now()
    
    # Cria um cabeçalho para o arquivo
    header = f"Resultados gerados em: {now.strftime('%d/%m/%Y %H:%M:%S')}\n"
    header += ("-" * 40) + "\n\n"
    content_to_save = header + content

    # Sugere um nome de arquivo padrão com a data e hora para fácil organização.
    default_filename = f"network_results_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

    # Abre a janela de diálogo "Salvar Como...".
    filepath = filedialog.asksaveasfilename(
        initialfile=default_filename,
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        title="Salvar Resultados Como..."
    )
    if not filepath:
        return # Usuário cancelou
    
    # Escreve o conteúdo no arquivo selecionado.
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_to_save)
        messagebox.showinfo("Sucesso", f"Resultados salvos em:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")

# --- Bloco Principal: Configuração da GUI ---
root = tk.Tk()
root.title("Network Tool by Jonatas")
root.geometry("700x550")

# --- Estilo da Aplicação ---
style = ttk.Style(root)
style.theme_use('clam') # 'clam' é um tema mais moderno que o padrão 'default'.
style.configure("TButton", padding=5, relief="flat", font=('Helvetica', 10))
style.configure("TNotebook.Tab", padding=[10, 5], font=('Helvetica', 11, 'bold'))

# --- Criação das Abas ---
notebook = ttk.Notebook(root)
notebook.pack(pady=10, padx=10, fill="both", expand=True)

diag_tab = ttk.Frame(notebook)
scan_tab = ttk.Frame(notebook)

notebook.add(diag_tab, text="Diagnóstico")
notebook.add(scan_tab, text="Port Scanner")

# --- Widgets da Aba de Diagnóstico ---
diag_frame = ttk.Frame(diag_tab, padding="10")
diag_frame.pack(fill='x')
diag_host_label = ttk.Label(diag_frame, text="Host ou IP:")
diag_host_label.pack(side='left')
diag_host_entry = ttk.Entry(diag_frame)
diag_host_entry.pack(side='left', fill='x', expand=True, padx=5)
diag_button = ttk.Button(diag_frame, text="Verificar", command=start_diagnostics, style="TButton")
diag_button.pack(side='left', padx=(0, 5))
# O comando do botão Salvar usa uma função lambda para passar o widget de texto correto.
diag_save_button = ttk.Button(diag_frame, text="Salvar", command=lambda: save_results(diag_results_text), style="TButton")
diag_save_button.pack(side='left')

diag_results_text = scrolledtext.ScrolledText(diag_tab, wrap=tk.WORD, width=80, height=25)
diag_results_text.pack(padx=10, pady=10, fill='both', expand=True)

# --- Widgets da Aba do Port Scanner ---
scan_frame = ttk.Frame(scan_tab, padding="10")
scan_frame.pack(fill='both', expand=True)

scan_host_label = ttk.Label(scan_frame, text="Host ou IP:")
scan_host_label.pack(side='left', padx=(0, 5))
scan_host_entry = ttk.Entry(scan_frame)
scan_host_entry.pack(side='left', fill='x', expand=True)
scan_ports_label = ttk.Label(scan_frame, text="Portas:")
scan_ports_label.pack(side='left', padx=(10, 5))
scan_ports_entry = ttk.Entry(scan_frame, width=20)
# Insere um valor padrão para guiar o usuário.
scan_ports_entry.insert(0, "22,80,443,8080")
scan_ports_entry.pack(side='left')
scan_button = ttk.Button(scan_frame, text="Escanear", command=start_scan, style="TButton")
scan_button.pack(side='left', padx=(5, 5))
scan_save_button = ttk.Button(scan_frame, text="Salvar", command=lambda: save_results(scan_results_text), style="TButton")
scan_save_button.pack(side='left')

# Barra de progresso
scan_progressbar = ttk.Progressbar(scan_frame, orient='horizontal', mode='determinate')
scan_progressbar.pack(fill='x', expand=False, pady=5)

# Caixa de texto para resultados
scan_results_text = scrolledtext.ScrolledText(scan_tab, wrap=tk.WORD, width=80, height=25)
scan_results_text.pack(fill='both', expand=True)

# Inicia o loop principal do Tkinter, que desenha a janela e espera por eventos do usuário.
root.mainloop()