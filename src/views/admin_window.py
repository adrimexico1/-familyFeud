import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QLineEdit, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QSpinBox, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from views.styles import GLOBAL_STYLE

class AdminWindow(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()
        self.model = model
        self.controller = controller
        self.setWindowTitle("100 Mexicanos Dijeron - Panel de Administración")
        self.resize(1000, 750)
        self.setStyleSheet(GLOBAL_STYLE)
        
        # Timer de cuenta regresiva de Dinero Rápido (30s)
        self.fm_timer = QTimer(self)
        self.fm_timer.setInterval(1000)
        self.fm_timer.timeout.connect(self.process_timer_tick)
        self.current_time_left = 30

        self.init_ui()
        self.connect_signals()
        self.update_ui_from_model()
        
        # Cargar combos de dinero rápido si ya hay datos en el modelo
        if self.model.dinero_rapido_preguntas:
            self.populate_fast_money_combos()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("adminWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        self.setup_config_panel()
        
        self.tabs = QTabWidget(self)
        self.setup_rondas_tab()
        self.setup_dinero_rapido_tab()
        self.main_layout.addWidget(self.tabs, 1)
        
        self.setup_status_bar()

    def setup_config_panel(self):
        group = QGroupBox("CONFIGURACIÓN DEL JUEGO", self)
        layout = QHBoxLayout(group)
        layout.setSpacing(15)
        
        self.btn_load = QPushButton("Cargar JSON", self)
        self.btn_load.clicked.connect(self.load_json_file)
        layout.addWidget(self.btn_load)
        
        self.lbl_json_path = QLabel("Ningún archivo cargado.", self)
        self.lbl_json_path.setStyleSheet("color: #a0a5c0;")
        layout.addWidget(self.lbl_json_path, 2)
        
        layout.addWidget(QLabel("Equipo A:", self))
        self.txt_team_a = QLineEdit(self.model.team_a_name, self)
        self.txt_team_a.textChanged.connect(self.update_team_names)
        layout.addWidget(self.txt_team_a)
        
        layout.addWidget(QLabel("Equipo B:", self))
        self.txt_team_b = QLineEdit(self.model.team_b_name, self)
        self.txt_team_b.textChanged.connect(self.update_team_names)
        layout.addWidget(self.txt_team_b)
        
        self.main_layout.addWidget(group)

    def setup_rondas_tab(self):
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        controls_layout = QHBoxLayout()
        self.btn_prev_round = QPushButton("◀ Ronda Ant.", self)
        self.btn_prev_round.clicked.connect(self.controller.prev_round)
        controls_layout.addWidget(self.btn_prev_round)
        
        self.lbl_current_round = QLabel("Ronda: - / -", self)
        self.lbl_current_round.setStyleSheet("font-size: 16px; font-weight: bold;")
        controls_layout.addWidget(self.lbl_current_round)
        
        self.btn_next_round = QPushButton("Ronda Sig. ▶", self)
        self.btn_next_round.clicked.connect(self.controller.next_round)
        controls_layout.addWidget(self.btn_next_round)
        layout.addLayout(controls_layout)
        
        self.lbl_round_question = QLabel("Pregunta: Carga un archivo para comenzar", self)
        self.lbl_round_question.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffd700;")
        self.lbl_round_question.setWordWrap(True)
        layout.addWidget(self.lbl_round_question)
        
        self.table_answers = QTableWidget(0, 4, self)
        self.table_answers.setHorizontalHeaderLabels(["N°", "Respuesta", "Puntos", "Acción"])
        self.table_answers.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_answers)
        
        ronda_panel = QHBoxLayout()
        strikes_group = QGroupBox("STRIKES", self)
        strikes_layout = QHBoxLayout(strikes_group)
        self.btn_strike = QPushButton("STRIKE (X)", self)
        self.btn_strike.setObjectName("btnStrike")
        self.btn_strike.clicked.connect(self.controller.trigger_strike)
        
        self.btn_clear_strikes = QPushButton("Limpiar", self)
        self.btn_clear_strikes.clicked.connect(self.controller.clear_strikes)
        
        self.lbl_admin_strikes = QLabel("Strikes: 0", self)
        strikes_layout.addWidget(self.btn_strike)
        strikes_layout.addWidget(self.btn_clear_strikes)
        strikes_layout.addWidget(self.lbl_admin_strikes)
        ronda_panel.addWidget(strikes_group, 1)
        
        points_group = QGroupBox("PUNTOS", self)
        points_layout = QHBoxLayout(points_group)
        self.lbl_admin_accumulated = QLabel("Acumulado: 0", self)
        self.btn_assign_a = QPushButton("Asignar A", self)
        self.btn_assign_a.clicked.connect(lambda: self.controller.assign_points_to_team("A"))
        self.btn_assign_b = QPushButton("Asignar B", self)
        self.btn_assign_b.clicked.connect(lambda: self.controller.assign_points_to_team("B"))
        
        points_layout.addWidget(self.lbl_admin_accumulated)
        points_layout.addWidget(self.btn_assign_a)
        points_layout.addWidget(self.btn_assign_b)
        ronda_panel.addWidget(points_group, 1)
        
        layout.addLayout(ronda_panel)
        self.tabs.addTab(widget, "Rondas del Juego")

    def setup_dinero_rapido_tab(self):
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        header = QHBoxLayout()
        header.addWidget(QLabel("DINERO RÁPIDO - PANEL Y CONTROL DE TIEMPO", self))
        
        self.lbl_timer_admin = QLabel("⏱ 30s", self)
        self.lbl_timer_admin.setStyleSheet("font-size: 22px; font-weight: bold; color: #ff0044; background: #0b0d18; padding: 2px 10px; border-radius: 5px;")
        
        self.btn_timer_start = QPushButton("▶ Iniciar Tiempo", self)
        self.btn_timer_start.setStyleSheet("background-color: #00aa44; color: white;")
        self.btn_timer_start.clicked.connect(self.start_fast_money_timer)
        
        self.btn_timer_reset = QPushButton("🔄 Reiniciar (30s)", self)
        self.btn_timer_reset.clicked.connect(self.reset_fast_money_timer)
        
        self.btn_fm_buzzer = QPushButton("Buzzer 🔊", self)
        self.btn_fm_buzzer.setStyleSheet("background-color: #ffaa00; color: black;")
        self.btn_fm_buzzer.clicked.connect(self.controller.play_buzzer_sound)
        
        header.addWidget(self.lbl_timer_admin)
        header.addWidget(self.btn_timer_start)
        header.addWidget(self.btn_timer_reset)
        header.addWidget(self.btn_fm_buzzer)
        layout.addLayout(header)
        
        players_layout = QHBoxLayout()
        
        # Jugador 1
        group_p1 = QGroupBox("JUGADOR 1", self)
        layout_p1 = QVBoxLayout(group_p1)
        self.fm_p1_inputs = []
        
        for i in range(5):
            row = QVBoxLayout()
            lbl_q = QLabel(f"P{i+1}: [Cargando pregunta...]", self)
            lbl_q.setStyleSheet("color: #00f0ff; font-weight: bold;")
            
            sub_row = QHBoxLayout()
            combo_resp = QComboBox(self)
            combo_resp.setEditable(True)
            combo_resp.setPlaceholderText("Seleccionar o escribir respuesta")
            combo_resp.currentIndexChanged.connect(lambda idx, p=1, row_idx=i: self.on_combo_changed(p, row_idx))
            
            pts = QSpinBox(self)
            pts.setRange(0, 100)
            pts.valueChanged.connect(lambda val, p=1, row_idx=i: self.update_fast_money_val(p, row_idx))

            chk_resp = QCheckBox("Rev Resp", self)
            chk_resp.stateChanged.connect(lambda state, p=1, row_idx=i: self.update_fast_money_val(p, row_idx))
            
            chk_pts = QCheckBox("Rev Pts", self)
            chk_pts.stateChanged.connect(lambda state, p=1, row_idx=i: self.update_fast_money_val(p, row_idx))

            sub_row.addWidget(combo_resp, 3)
            sub_row.addWidget(pts, 1)
            sub_row.addWidget(chk_resp)
            sub_row.addWidget(chk_pts)
            
            row.addWidget(lbl_q)
            row.addLayout(sub_row)
            layout_p1.addLayout(row)
            self.fm_p1_inputs.append((lbl_q, combo_resp, pts, chk_resp, chk_pts))
            
        players_layout.addWidget(group_p1, 1)
        
        # Jugador 2
        group_p2 = QGroupBox("JUGADOR 2", self)
        layout_p2 = QVBoxLayout(group_p2)
        self.fm_p2_inputs = []
        
        for i in range(5):
            row = QVBoxLayout()
            lbl_q = QLabel(f"P{i+1}: [Cargando pregunta...]", self)
            lbl_q.setStyleSheet("color: #00f0ff; font-weight: bold;")
            
            sub_row = QHBoxLayout()
            combo_resp = QComboBox(self)
            combo_resp.setEditable(True)
            combo_resp.setPlaceholderText("Seleccionar o escribir respuesta")
            combo_resp.currentIndexChanged.connect(lambda idx, p=2, row_idx=i: self.on_combo_changed(p, row_idx))
            
            pts = QSpinBox(self)
            pts.setRange(0, 100)
            pts.valueChanged.connect(lambda val, p=2, row_idx=i: self.update_fast_money_val(p, row_idx))

            chk_resp = QCheckBox("Rev Resp", self)
            chk_resp.stateChanged.connect(lambda state, p=2, row_idx=i: self.update_fast_money_val(p, row_idx))
            
            chk_pts = QCheckBox("Rev Pts", self)
            chk_pts.stateChanged.connect(lambda state, p=2, row_idx=i: self.update_fast_money_val(p, row_idx))

            sub_row.addWidget(combo_resp, 3)
            sub_row.addWidget(pts, 1)
            sub_row.addWidget(chk_resp)
            sub_row.addWidget(chk_pts)
            
            row.addWidget(lbl_q)
            row.addLayout(sub_row)
            layout_p2.addLayout(row)
            self.fm_p2_inputs.append((lbl_q, combo_resp, pts, chk_resp, chk_pts))
            
        players_layout.addWidget(group_p2, 1)
        layout.addLayout(players_layout)
        
        fm_total_layout = QHBoxLayout()
        self.lbl_fm_admin_total = QLabel("Total Dinero Rápido: 0 / 200 Puntos", self)
        self.lbl_fm_admin_total.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffd700;")
        fm_total_layout.addWidget(self.lbl_fm_admin_total)
        layout.addLayout(fm_total_layout)
        
        self.tabs.addTab(widget, "Dinero Rápido (Final)")

    def setup_status_bar(self):
        bar = QHBoxLayout()
        self.btn_open_board = QPushButton("Abrir Tablero Público", self)
        self.btn_open_board.clicked.connect(self.controller.open_board_window)
        bar.addWidget(self.btn_open_board)
        
        bar.addWidget(QLabel("Fase:", self))
        self.btn_phase_lobby = QPushButton("Lobby", self)
        self.btn_phase_lobby.clicked.connect(lambda: self.controller.change_game_phase("LOBBY"))
        bar.addWidget(self.btn_phase_lobby)
        
        self.btn_phase_ronda = QPushButton("Rondas", self)
        self.btn_phase_ronda.clicked.connect(lambda: self.controller.change_game_phase("RONDA"))
        bar.addWidget(self.btn_phase_ronda)
        
        self.btn_phase_fm = QPushButton("Dinero Rápido", self)
        self.btn_phase_fm.clicked.connect(lambda: self.controller.change_game_phase("DINERO_RAPIDO"))
        bar.addWidget(self.btn_phase_fm)
        
        self.main_layout.addLayout(bar)

    def load_json_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Cargar Preguntas", "", "Archivos JSON (*.json)")
        if filepath:
            self.controller.load_questions(filepath)
            self.lbl_json_path.setText(os.path.basename(filepath))
            self.populate_fast_money_combos()

    def populate_fast_money_combos(self):
        """Llena y actualiza dinámicamente los menús desplegables cruzando opciones entre J1 y J2."""
        if not self.model.dinero_rapido_preguntas or not self.fm_p1_inputs:
            return

        for i in range(5):
            if i < len(self.model.fast_money_p1) and i < len(self.model.fast_money_p2):
                q_data_p1 = self.model.fast_money_p1[i]
                q_data_p2 = self.model.fast_money_p2[i]
                
                lbl_q1, combo1, _, _, _ = self.fm_p1_inputs[i]
                lbl_q2, combo2, _, _, _ = self.fm_p2_inputs[i]
                
                lbl_q1.setText(f"P{i+1}: {q_data_p1['pregunta']}")
                lbl_q2.setText(f"P{i+1}: {q_data_p2['pregunta']}")
                
                val_p1 = combo1.currentData()
                val_p2 = combo2.currentData()
                text_p1 = val_p1[0] if val_p1 and isinstance(val_p1, tuple) else ""
                text_p2 = val_p2[0] if val_p2 and isinstance(val_p2, tuple) else ""

                # Actualizar combo Jugador 1
                current_text_1 = combo1.currentText()
                combo1.blockSignals(True)
                combo1.clear()
                combo1.addItem("-- Seleccionar o Escribir --", ( "", 0 ))
                for opt in q_data_p1["opciones"]:
                    opt_text = opt.get('texto', '')
                    if opt_text != text_p2 or (val_p1 and val_p1[0] == opt_text):
                        combo1.addItem(f"{opt_text} ({opt.get('puntos', 0)} pts)", (opt_text, opt.get('puntos', 0)))
                if val_p1 and val_p1[0] != "":
                    idx = combo1.findData(val_p1)
                    if idx >= 0: combo1.setCurrentIndex(idx)
                    else: combo1.setEditText(current_text_1)
                combo1.blockSignals(False)

                # Actualizar combo Jugador 2
                current_text_2 = combo2.currentText()
                combo2.blockSignals(True)
                combo2.clear()
                combo2.addItem("-- Seleccionar o Escribir --", ( "", 0 ))
                for opt in q_data_p2["opciones"]:
                    opt_text = opt.get('texto', '')
                    if opt_text != text_p1 or (val_p2 and val_p2[0] == opt_text):
                        combo2.addItem(f"{opt_text} ({opt.get('puntos', 0)} pts)", (opt_text, opt.get('puntos', 0)))
                if val_p2 and val_p2[0] != "":
                    idx = combo2.findData(val_p2)
                    if idx >= 0: combo2.setCurrentIndex(idx)
                    else: combo2.setEditText(current_text_2)
                combo2.blockSignals(False)

    def on_combo_changed(self, player_num, idx):
        """Autocompleta puntos y refresca los combos cruzados."""
        if player_num == 1:
            _, combo, pts, _, _ = self.fm_p1_inputs[idx]
            data = combo.currentData()
            if data and isinstance(data, tuple) and data[0] != "":
                pts.setValue(int(data[1]))
            self.update_fast_money_val(1, idx)
        else:
            _, combo, pts, _, _ = self.fm_p2_inputs[idx]
            data = combo.currentData()
            if data and isinstance(data, tuple) and data[0] != "":
                pts.setValue(int(data[1]))
            self.update_fast_money_val(2, idx)
        
        self.populate_fast_money_combos()

    def update_team_names(self):
        self.controller.update_team_names(self.txt_team_a.text(), self.txt_team_b.text())

    def update_fast_money_val(self, player_num, idx):
        if player_num == 1:
            _, combo, pts, chk_resp, chk_pts = self.fm_p1_inputs[idx]
            answer_text = combo.currentText().split(" (")[0] if combo.currentIndex() > 0 else combo.currentText()
            self.controller.update_fast_money_player1(
                idx, answer_text, pts.value(), chk_resp.isChecked(), chk_pts.isChecked()
            )
        else:
            _, combo, pts, chk_resp, chk_pts = self.fm_p2_inputs[idx]
            answer_text = combo.currentText().split(" (")[0] if combo.currentIndex() > 0 else combo.currentText()
            self.controller.update_fast_money_player2(
                idx, answer_text, pts.value(), chk_resp.isChecked(), chk_pts.isChecked()
            )

    def start_fast_money_timer(self):
        if self.fm_timer.isActive():
            self.fm_timer.stop()
            self.btn_timer_start.setText("▶ Reanudar")
        else:
            self.fm_timer.start()
            self.btn_timer_start.setText("⏸ Pausar")

    def reset_fast_money_timer(self):
        self.fm_timer.stop()
        self.current_time_left = 30
        self.lbl_timer_admin.setText(f"⏱ {self.current_time_left}s")
        self.btn_timer_start.setText("▶ Iniciar Tiempo")
        self.controller.set_fast_money_timer(self.current_time_left)

    def process_timer_tick(self):
        if self.current_time_left > 0:
            self.current_time_left -= 1
            self.lbl_timer_admin.setText(f"⏱ {self.current_time_left}s")
            self.controller.set_fast_money_timer(self.current_time_left)
            if self.current_time_left == 0:
                self.fm_timer.stop()
                self.btn_timer_start.setText("▶ Iniciar Tiempo")

    def connect_signals(self):
        self.model.state_changed.connect(self.update_ui_from_model)
        self.model.round_changed.connect(self.update_answers_table)
        self.model.round_points_changed.connect(self.update_accumulated)
        self.model.strikes_changed.connect(self.update_strikes_label)
        self.model.fast_money_updated.connect(self.update_fast_money_total)

    def update_ui_from_model(self):
        total_rondas = len(self.model.rondas)
        if total_rondas > 0:
            self.lbl_current_round.setText(f"Ronda: {self.model.current_round_idx + 1} / {total_rondas}")
            self.lbl_round_question.setText(f"Pregunta: {self.model.rondas[self.model.current_round_idx]['pregunta']}")
        
        if self.model.dinero_rapido_preguntas and self.fm_p1_inputs:
            if self.fm_p1_inputs[0][0].text().endswith("[Cargando pregunta...]"):
                self.populate_fast_money_combos()

        if self.model.game_phase == "RONDA":
            self.tabs.setCurrentIndex(0)
        elif self.model.game_phase == "DINERO_RAPIDO":
            self.tabs.setCurrentIndex(1)

    def update_answers_table(self):
        if 0 <= self.model.current_round_idx < len(self.model.rondas):
            respuestas = self.model.rondas[self.model.current_round_idx]["respuestas"]
            self.table_answers.setRowCount(len(respuestas))
            for i, r in enumerate(respuestas):
                self.table_answers.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.table_answers.setItem(i, 1, QTableWidgetItem(r["texto"]))
                self.table_answers.setItem(i, 2, QTableWidgetItem(str(r["puntos"])))
                btn = QPushButton("Ocultar" if r["revelada"] else "Revelar")
                btn.clicked.connect(lambda checked=False, idx=i: self.controller.toggle_reveal_answer(idx))
                self.table_answers.setCellWidget(i, 3, btn)

    def update_accumulated(self, points):
        self.lbl_admin_accumulated.setText(f"Acumulado: {points}")

    def update_strikes_label(self, count):
        self.lbl_admin_strikes.setText(f"Strikes: {count}")

    def update_fast_money_total(self):
        total = self.model.get_fast_money_total()
        self.lbl_fm_admin_total.setText(f"Total Dinero Rápido: {total} / 200 Puntos")