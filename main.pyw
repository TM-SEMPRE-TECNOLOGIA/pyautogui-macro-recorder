"""
PyAutoGUI Macro Studio & Recorder
Interface moderna e intuitiva para gravar, reproduzir em lote, salvar/carregar e exportar scripts Python.
"""

import os
import sys
import time
import json
import threading
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pyautogui
from pynput import mouse, keyboard

# Configuração de segurança do PyAutoGUI
pyautogui.FAILSAFE = True  # Mover o mouse para o canto superior esquerdo da tela aborta a execução
pyautogui.PAUSE = 0.01

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MacroRecorderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyAutoGUI Macro Studio - Automação em Lote")
        self.geometry("980x720")
        self.minsize(860, 600)

        # Estado da gravação / execução
        self.is_recording = False
        self.is_playing = False
        self.stop_playback_flag = False

        self.recorded_events = []
        self.start_time = 0
        self.last_event_time = 0

        # Listeners do pynput
        self.mouse_listener = None
        self.keyboard_listener = None

        # Montar a interface
        self._build_ui()

        # Iniciar listener de atalho global de emergência (ESC / F8)
        self._start_global_hotkey_listener()

    def _build_ui(self):
        # Grid layout: 1 linha com barra lateral e painel principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- BARRA LATERAL (CONTROLES) ----------------
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_propagate(False)

        # Logo / Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="⚡ Macro Studio",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#38bdf8"
        )
        self.logo_label.pack(pady=(20, 5), padx=20, anchor="w")

        self.sub_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Automação & Lote PyAutoGUI",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        self.sub_label.pack(pady=(0, 20), padx=20, anchor="w")

        # Seção de Gravação
        rec_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#1e293b", corner_radius=10)
        rec_frame.pack(fill="x", padx=15, pady=(0, 15))

        rec_title = ctk.CTkLabel(
            rec_frame,
            text="GRAVAÇÃO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8"
        )
        rec_title.pack(anchor="w", padx=12, pady=(10, 5))

        self.btn_record = ctk.CTkButton(
            rec_frame,
            text="⏺ Iniciar Captura",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#ef4444",
            hover_color="#dc2626",
            height=40,
            command=self.toggle_recording
        )
        self.btn_record.pack(fill="x", padx=12, pady=(5, 10))

        # Opção de capturar movimento contínuo do mouse
        self.var_record_moves = ctk.BooleanVar(value=False)
        self.chk_moves = ctk.CTkCheckBox(
            rec_frame,
            text="Capturar arraste/movimento contínuo",
            variable=self.var_record_moves,
            font=ctk.CTkFont(size=12),
            text_color="#cbd5e1"
        )
        self.chk_moves.pack(anchor="w", padx=12, pady=(0, 10))

        # Seção de Execução em Lote
        play_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#1e293b", corner_radius=10)
        play_frame.pack(fill="x", padx=15, pady=(0, 15))

        play_title = ctk.CTkLabel(
            play_frame,
            text="EXECUÇÃO EM LOTE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8"
        )
        play_title.pack(anchor="w", padx=12, pady=(10, 5))

        # Controles de Repetições
        rep_box = ctk.CTkFrame(play_frame, fg_color="transparent")
        rep_box.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(rep_box, text="Repetições (Ciclos):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.spin_loops = ctk.CTkEntry(rep_box, width=70, font=ctk.CTkFont(size=12))
        self.spin_loops.insert(0, "1")
        self.spin_loops.pack(side="right")

        # Velocidade
        speed_box = ctk.CTkFrame(play_frame, fg_color="transparent")
        speed_box.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(speed_box, text="Velocidade (x):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.opt_speed = ctk.CTkOptionMenu(
            speed_box,
            values=["0.5x", "1.0x (Normal)", "1.5x", "2.0x", "3.0x", "5.0x", "Sem delay"],
            width=120,
            font=ctk.CTkFont(size=12)
        )
        self.opt_speed.set("1.0x (Normal)")
        self.opt_speed.pack(side="right")

        # Delay entre loops
        loop_delay_box = ctk.CTkFrame(play_frame, fg_color="transparent")
        loop_delay_box.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(loop_delay_box, text="Pausa entre ciclos (s):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.spin_loop_delay = ctk.CTkEntry(loop_delay_box, width=70, font=ctk.CTkFont(size=12))
        self.spin_loop_delay.insert(0, "1.0")
        self.spin_loop_delay.pack(side="right")

        # Botão Reproduzir
        self.btn_play = ctk.CTkButton(
            play_frame,
            text="▶ Executar Macro",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            height=40,
            command=self.start_playback
        )
        self.btn_play.pack(fill="x", padx=12, pady=(10, 5))

        # Botão Interromper
        self.btn_stop = ctk.CTkButton(
            play_frame,
            text="⏹ Interromper (ESC)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#64748b",
            hover_color="#475569",
            height=30,
            command=self.stop_playback,
            state="disabled"
        )
        self.btn_stop.pack(fill="x", padx=12, pady=(0, 10))

        # Seção Arquivos / Exportação
        file_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#1e293b", corner_radius=10)
        file_frame.pack(fill="x", padx=15, pady=(0, 15))

        file_title = ctk.CTkLabel(
            file_frame,
            text="PROJETO & SCRIPTS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8"
        )
        file_title.pack(anchor="w", padx=12, pady=(10, 5))

        btn_row1 = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_row1.pack(fill="x", padx=12, pady=3)
        ctk.CTkButton(btn_row1, text="Salvar (.json)", width=110, command=self.save_macro).pack(side="left")
        ctk.CTkButton(btn_row1, text="Carregar (.json)", width=110, command=self.load_macro).pack(side="right")

        self.btn_export = ctk.CTkButton(
            file_frame,
            text="📄 Exportar Script .py",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self.export_python_script
        )
        self.btn_export.pack(fill="x", padx=12, pady=(5, 10))

        # Dica de emergência no rodapé
        tip_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        tip_frame.pack(side="bottom", fill="x", padx=15, pady=15)
        ctk.CTkLabel(
            tip_frame,
            text="💡 Dicas de Emergência:\n• Pressione ESC para parar\n• Arraste mouse ao topo-esquerdo\n  da tela para abortar imediatamente.",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8",
            justify="left"
        ).pack(anchor="w")

        # ---------------- ÁREA PRINCIPAL ----------------
        self.main_frame = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Top Bar Status
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="#1e293b", corner_radius=10, height=60)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.top_bar.grid_columnconfigure(1, weight=1)

        self.status_indicator = ctk.CTkLabel(
            self.top_bar,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color="#10b981"
        )
        self.status_indicator.grid(row=0, column=0, padx=(15, 5), pady=12)

        self.status_text = ctk.CTkLabel(
            self.top_bar,
            text="Pronto para capturar",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc"
        )
        self.status_text.grid(row=0, column=1, sticky="w", pady=12)

        self.event_counter_badge = ctk.CTkLabel(
            self.top_bar,
            text="0 Ações Gravadas",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#334155",
            corner_radius=6,
            padx=12,
            pady=4,
            text_color="#cbd5e1"
        )
        self.event_counter_badge.grid(row=0, column=2, padx=15, pady=12)

        # Tabview para visualização (Tabela de Passos e Código Python ao vivo)
        self.tabview = ctk.CTkTabview(self.main_frame, fg_color="#1e293b")
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.tab_actions = self.tabview.add("📋 Ações Capturadas")
        self.tab_code = self.tabview.add("🐍 Código PyAutoGUI Gerado")

        # ----- TAB AÇÕES -----
        self.tab_actions.grid_columnconfigure(0, weight=1)
        self.tab_actions.grid_rowconfigure(1, weight=1)

        # Barra de ferramentas da tabela
        action_toolbar = ctk.CTkFrame(self.tab_actions, fg_color="transparent")
        action_toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 10))

        ctk.CTkLabel(
            action_toolbar,
            text="Sequência cronológica de ações:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94a3b8"
        ).pack(side="left")

        ctk.CTkButton(
            action_toolbar,
            text="🗑 Limpar Lista",
            width=100,
            height=28,
            fg_color="#475569",
            hover_color="#334155",
            command=self.clear_events
        ).pack(side="right", padx=5)

        # Caixa de texto rolável com as ações
        self.textbox_actions = ctk.CTkTextbox(
            self.tab_actions,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#e2e8f0",
            fg_color="#090d16",
            wrap="none"
        )
        self.textbox_actions.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # ----- TAB CÓDIGO PYTHON -----
        self.tab_code.grid_columnconfigure(0, weight=1)
        self.tab_code.grid_rowconfigure(0, weight=1)

        self.textbox_code = ctk.CTkTextbox(
            self.tab_code,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#38bdf8",
            fg_color="#090d16",
            wrap="none"
        )
        self.textbox_code.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self._refresh_displays()

    # ---------------- LÓGICA DE CAPTURA ----------------
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        if self.is_playing:
            return

        self.is_recording = True
        self.recorded_events = []
        self.start_time = time.time()
        self.last_event_time = self.start_time

        self.btn_record.configure(
            text="⏹ Finalizar Captura",
            fg_color="#f59e0b",
            hover_color="#d97706"
        )
        self.status_indicator.configure(text_color="#ef4444")
        self.status_text.configure(text="🔴 Gravando ações do mouse e teclado... (Clique em Finalizar quando terminar)")
        self.btn_play.configure(state="disabled")

        # Iniciar listeners de mouse e teclado em background
        self.mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_move=self._on_mouse_move if self.var_record_moves.get() else None,
            on_scroll=self._on_mouse_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False

        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

        self.btn_record.configure(
            text="⏺ Iniciar Captura",
            fg_color="#ef4444",
            hover_color="#dc2626"
        )
        self.status_indicator.configure(text_color="#10b981")
        self.status_text.configure(text=f"Captura finalizada com sucesso! {len(self.recorded_events)} ações gravadas.")
        self.btn_play.configure(state="normal" if len(self.recorded_events) > 0 else "disabled")

        self._refresh_displays()

    # Callbacks de captura
    def _record_event(self, event_data):
        now = time.time()
        delay = round(now - self.last_event_time, 3)
        self.last_event_time = now

        event_data["delay"] = delay
        self.recorded_events.append(event_data)

        # Atualizar badge de contagem de ações de forma segura na thread da UI
        self.after(0, self._update_badge_count)

    def _update_badge_count(self):
        self.event_counter_badge.configure(text=f"{len(self.recorded_events)} Ações Gravadas")

    def _on_mouse_click(self, x, y, button, pressed):
        if not self.is_recording:
            return
        btn_str = "left" if button == mouse.Button.left else ("right" if button == mouse.Button.right else "middle")
        self._record_event({
            "type": "mouse_click",
            "x": int(x),
            "y": int(y),
            "button": btn_str,
            "action": "down" if pressed else "up"
        })

    def _on_mouse_move(self, x, y):
        if not self.is_recording:
            return
        # Amostragem para evitar excesso de pontos caso queira mover
        now = time.time()
        if now - self.last_event_time >= 0.05:
            self._record_event({
                "type": "mouse_move",
                "x": int(x),
                "y": int(y)
            })

    def _on_mouse_scroll(self, x, y, dx, dy):
        if not self.is_recording:
            return
        # No Windows, 1 clique da rodinha do pynput (dy = 1 ou -1) equivale a 120 unidades de scroll no PyAutoGUI
        clicks = int(dy * 120) if abs(dy) <= 10 else int(dy)
        self._record_event({
            "type": "mouse_scroll",
            "x": int(x),
            "y": int(y),
            "clicks": clicks
        })

    def _on_key_press(self, key):
        if not self.is_recording:
            return
        key_str = self._format_key(key)
        self._record_event({
            "type": "key_press",
            "key": key_str
        })

    def _on_key_release(self, key):
        if not self.is_recording:
            return
        # Não registrar ESC se usado para parar
        if key == keyboard.Key.esc:
            self.after(0, self.stop_recording)
            return

        key_str = self._format_key(key)
        self._record_event({
            "type": "key_release",
            "key": key_str
        })

    def _format_key(self, key):
        try:
            return key.char if hasattr(key, "char") and key.char else str(key).replace("Key.", "")
        except Exception:
            return str(key).replace("Key.", "")

    # ---------------- ATALHO GLOBAL DE EMERGÊNCIA ----------------
    def _start_global_hotkey_listener(self):
        def on_press(key):
            if key == keyboard.Key.esc:
                if self.is_playing:
                    self.stop_playback_flag = True
                    self.after(0, self._on_playback_aborted)

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

    def _on_playback_aborted(self):
        self.status_indicator.configure(text_color="#f59e0b")
        self.status_text.configure(text="Execução abortada pelo usuário (ESC).")
        self._set_playback_ui_state(False)

    # ---------------- EXECUÇÃO EM LOTE ----------------
    def start_playback(self):
        if not self.recorded_events:
            messagebox.showwarning("Aviso", "Nenhuma ação gravada para executar.")
            return

        try:
            loops = int(self.spin_loops.get().strip())
            if loops <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "O número de repetições deve ser um número inteiro maior que 0.")
            return

        try:
            loop_delay = float(self.spin_loop_delay.get().strip().replace(",", "."))
            if loop_delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "O delay entre ciclos deve ser um número válido (ex: 1.0).")
            return

        # Obter multiplicador de velocidade
        speed_text = self.opt_speed.get()
        if "Sem delay" in speed_text:
            speed_mult = 0.0
        else:
            speed_mult = float(speed_text.split("x")[0])

        self.is_playing = True
        self.stop_playback_flag = False
        self._set_playback_ui_state(True)

        # Iniciar execução em thread dedicada para não travar a GUI
        playback_thread = threading.Thread(
            target=self._run_playback_thread,
            args=(loops, loop_delay, speed_mult),
            daemon=True
        )
        playback_thread.start()

    def _set_playback_ui_state(self, is_playing):
        if is_playing:
            self.btn_play.configure(state="disabled")
            self.btn_record.configure(state="disabled")
            self.btn_stop.configure(state="normal", fg_color="#ef4444", hover_color="#dc2626")
            self.status_indicator.configure(text_color="#10b981")
        else:
            self.is_playing = False
            self.btn_play.configure(state="normal")
            self.btn_record.configure(state="normal")
            self.btn_stop.configure(state="disabled", fg_color="#64748b", hover_color="#475569")

    def stop_playback(self):
        self.stop_playback_flag = True

    def _run_playback_thread(self, loops, loop_delay, speed_mult):
        # Contagem regressiva antes de iniciar (para o usuário posicionar a tela se necessário)
        for i in range(3, 0, -1):
            if self.stop_playback_flag:
                break
            self.status_text.configure(text=f"Iniciando em {i} segundos... Posicione suas janelas!")
            time.sleep(1)

        total_cycles = loops
        for cycle in range(1, total_cycles + 1):
            if self.stop_playback_flag:
                break

            self.status_text.configure(text=f"Executando ciclo {cycle} de {total_cycles}...")

            for event in self.recorded_events:
                if self.stop_playback_flag:
                    break

                # Aplicar delay proporcional à velocidade
                delay = event.get("delay", 0)
                if speed_mult > 0:
                    adjusted_delay = delay / speed_mult
                    time.sleep(adjusted_delay)

                try:
                    ev_type = event["type"]
                    if ev_type == "mouse_click":
                        x, y = event["x"], event["y"]
                        btn = event["button"]
                        if event["action"] == "down":
                            pyautogui.mouseDown(x=x, y=y, button=btn)
                        else:
                            pyautogui.mouseUp(x=x, y=y, button=btn)

                    elif ev_type == "mouse_move":
                        pyautogui.moveTo(event["x"], event["y"])

                    elif ev_type == "mouse_scroll":
                        pyautogui.scroll(event["clicks"], x=event["x"], y=event["y"])

                    elif ev_type == "key_press":
                        k = event["key"]
                        pyautogui.keyDown(k)

                    elif ev_type == "key_release":
                        k = event["key"]
                        pyautogui.keyUp(k)

                except Exception as e:
                    print(f"Erro na execução da ação: {e}")

            # Pausa entre ciclos
            if cycle < total_cycles and not self.stop_playback_flag:
                time.sleep(loop_delay)

        if not self.stop_playback_flag:
            self.status_text.configure(text=f"Lote concluído com sucesso ({total_cycles} ciclos)!")
        self.after(0, lambda: self._set_playback_ui_state(False))

    # ---------------- SALVAR, CARREGAR & EXPORTAR ----------------
    def save_macro(self):
        if not self.recorded_events:
            messagebox.showwarning("Aviso", "Nenhuma ação gravada para salvar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Arquivo Macro JSON", "*.json")],
            title="Salvar Sequência de Macro"
        )
        if file_path:
            data = {
                "created_at": datetime.now().isoformat(),
                "total_events": len(self.recorded_events),
                "events": self.recorded_events
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Sucesso", f"Macro salva com sucesso em:\n{file_path}")

    def load_macro(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivo Macro JSON", "*.json")],
            title="Carregar Sequência de Macro"
        )
        if file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.recorded_events = data.get("events", [])
            self.btn_play.configure(state="normal" if len(self.recorded_events) > 0 else "disabled")
            self._update_badge_count()
            self._refresh_displays()
            messagebox.showinfo("Sucesso", f"Macro carregada! {len(self.recorded_events)} ações prontas.")

    def clear_events(self):
        if messagebox.askyesno("Confirmar", "Deseja realmente limpar todas as ações gravadas?"):
            self.recorded_events = []
            self._update_badge_count()
            self._refresh_displays()
            self.btn_play.configure(state="disabled")
            self.status_text.configure(text="Pronto para nova captura")

    def _generate_python_code(self):
        code_lines = [
            "# ===========================================================",
            "# Script Gerado Automaticamente pelo PyAutoGUI Macro Studio",
            f"# Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "# ===========================================================",
            "import time",
            "import pyautogui",
            "",
            "pyautogui.FAILSAFE = True  # Puxe o mouse para o canto superior esquerdo para parar",
            "pyautogui.PAUSE = 0.01",
            "",
            "def executar_macro():",
            "    print('Iniciando macro em 3 segundos... Mantenha o mouse pronto.')",
            "    time.sleep(3)",
            ""
        ]

        if not self.recorded_events:
            code_lines.append("    # Nenhuma ação registrada ainda.")
            code_lines.append("    pass")
        else:
            for i, ev in enumerate(self.recorded_events):
                delay = ev.get("delay", 0)
                if delay > 0.02:
                    code_lines.append(f"    time.sleep({delay})")

                ev_type = ev["type"]
                if ev_type == "mouse_click":
                    btn = ev["button"]
                    x, y = ev["x"], ev["y"]
                    if ev["action"] == "down":
                        code_lines.append(f"    pyautogui.mouseDown(x={x}, y={y}, button='{btn}')")
                    else:
                        code_lines.append(f"    pyautogui.mouseUp(x={x}, y={y}, button='{btn}')")
                elif ev_type == "mouse_move":
                    code_lines.append(f"    pyautogui.moveTo({ev['x']}, {ev['y']})")
                elif ev_type == "mouse_scroll":
                    code_lines.append(f"    pyautogui.scroll({ev['clicks']}, x={ev['x']}, y={ev['y']})")
                elif ev_type == "key_press":
                    code_lines.append(f"    pyautogui.keyDown('{ev['key']}')")
                elif ev_type == "key_release":
                    code_lines.append(f"    pyautogui.keyUp('{ev['key']}')")

        code_lines.extend([
            "",
            "if __name__ == '__main__':",
            "    # Para executar em lote (ex: 5 vezes), ajuste o range abaixo:",
            "    REPETICOES = 1",
            "    for ciclo in range(1, REPETICOES + 1):",
            "        print(f'Executando ciclo {ciclo}/{REPETICOES}...')",
            "        executar_macro()",
            "        time.sleep(1) # pausa entre ciclos",
            "    print('Concluído com sucesso!')"
        ])
        return "\n".join(code_lines)

    def _refresh_displays(self):
        # Atualizar lista de ações
        self.textbox_actions.delete("1.0", "end")
        if not self.recorded_events:
            self.textbox_actions.insert("1.0", "Nenhuma ação capturada ainda.\nClique em '⏺ Iniciar Captura', realize as ações no seu computador e clique em 'Finalizar'.")
        else:
            header = f"{'#':<4} | {'TEMPO':<8} | {'TIPO':<14} | {'DETALHES'}\n"
            header += "-" * 75 + "\n"
            self.textbox_actions.insert("end", header)

            for i, ev in enumerate(self.recorded_events, 1):
                delay_str = f"+{ev.get('delay', 0):.2f}s"
                ev_type = ev["type"]

                if ev_type == "mouse_click":
                    btn = "Direito (Right)" if ev["button"] == "right" else ("Esquerdo (Left)" if ev["button"] == "left" else ev["button"])
                    act = "Pressionar" if ev["action"] == "down" else "Soltar"
                    details = f"{act} Botão {btn} em X={ev['x']}, Y={ev['y']}"
                elif ev_type == "mouse_move":
                    details = f"Mover cursor para X={ev['x']}, Y={ev['y']}"
                elif ev_type == "mouse_scroll":
                    details = f"Scroll {ev['clicks']} em X={ev['x']}, Y={ev['y']}"
                elif ev_type in ("key_press", "key_release"):
                    act = "Pressionar" if ev_type == "key_press" else "Soltar"
                    details = f"{act} Tecla '{ev['key']}'"
                else:
                    details = str(ev)

                line = f"{i:<4} | {delay_str:<8} | {ev_type:<14} | {details}\n"
                self.textbox_actions.insert("end", line)

        # Atualizar código Python gerado
        self.textbox_code.delete("1.0", "end")
        self.textbox_code.insert("1.0", self._generate_python_code())

    def export_python_script(self):
        if not self.recorded_events:
            messagebox.showwarning("Aviso", "Nenhuma ação gravada para exportar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Script Python", "*.py")],
            title="Exportar como Script PyAutoGUI Independente"
        )
        if file_path:
            code = self._generate_python_code()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            messagebox.showinfo("Sucesso", f"Script Python exportado com sucesso!\n\nVocê pode executá-lo diretamente via terminal:\npython {os.path.basename(file_path)}")


if __name__ == "__main__":
    app = MacroRecorderApp()
    app.mainloop()
