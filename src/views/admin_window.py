import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QLineEdit, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt
from views.styles import GLOBAL_STYLE

class AdminWindow(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()
        self.model = model
        self.controller = controller
        self.setWindowTitle("100 Mexicanos Dijeron - Panel de Administración")
        self.resize(900, 700)
        self.setStyleSheet(GLOBAL_STYLE)
        
        self.init_ui()
        self.connect_signals()
        self.update_ui_from_model()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("adminWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        # 1. Configuración de Archivo y Nombres
        self.setup_config_panel()
        
        # Tabs para separar Rondas Regulares y Dinero Rápido
        self.tabs = QTabWidget(self)
        self.setup_rondas_tab()
        self.setup_dinero_rapido_tab()
        self.main_layout.addWidget(self.tabs, 1)
        
        # 2. Barra de Estado / Ventana del público
        self.setup_status_bar()

    def setup_config_panel(self):
        group = QGroupBox("CONFIGURACIÓN DEL JUEGO", self)
        layout = QHBoxLayout(group)
        layout.setSpacing(15)
        
        # Carga de archivo
        self.btn_load = QPushButton("Cargar JSON", self)
        self.btn_load.clicked.connect(self.load_json_file)
        layout.addWidget(self.btn_load)
        
        self.lbl_json_path = QLabel("Ningún archivo cargado.", self)
        self.lbl_json_path.setStyleSheet("color: #a0a5c0;")
        layout.addWidget(self.lbl_json_path, 2)
        
        # Nombres de Equipos
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
        
        # Controles superiores de ronda
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
        
        # Pregunta Actual
        self.lbl_round_question = QLabel("Pregunta: Carga un archivo para comenzar", self)
        self.lbl_round_question.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffd700;")
        self.lbl_round_question.setWordWrap(True)
        layout.addWidget(self.lbl_round_question)
        
        # Tabla de respuestas
        self.table_answers = QTableWidget(0, 4, self)
        self.table_answers.setHorizontalHeaderLabels(["N°", "Respuesta", "Puntos", "Acción"])
        self.table_answers.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_answers.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_answers.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_answers.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.table_answers)
        
        # Panel de control de puntos y strikes de la ronda
        ronda_panel = QHBoxLayout()
        
        # Sección Strikes (Izquierda)
        strikes_group = QGroupBox("STRIKES", self)
        strikes_layout = QHBoxLayout(strikes_group)
        self.btn_strike = QPushButton("STRIKE (X)", self)
        self.btn_strike.setObjectName("btnStrike")
        self.btn_strike.clicked.connect(self.controller.trigger_strike)
        
        self.btn_clear_strikes = QPushButton("Limpiar Strikes", self)
        self.btn_clear_strikes.clicked.connect(self.controller.clear_strikes)
        
        self.lbl_admin_strikes = QLabel("Strikes: 0", self)
        self.lbl_admin_strikes.setStyleSheet("font-size: 16px; font-weight: bold; color: #ff0044;")
        
        strikes_layout.addWidget(self.btn_strike)
        strikes_layout.addWidget(self.btn_clear_strikes)
        strikes_layout.addWidget(self.lbl_admin_strikes)
        ronda_panel.addWidget(strikes_group, 1)
        
        # Sección Puntos de Ronda (Derecha)
        points_group = QGroupBox("ASIGNACIÓN DE PUNTOS", self)
        points_layout = QHBoxLayout(points_group)
        
        self.lbl_admin_accumulated = QLabel("Acumulado: 0", self)
        self.lbl_admin_accumulated.setStyleSheet("font-size: 18px; font-weight: bold; color: #00f0ff;")
        
        self.btn_assign_a = QPushButton("Asignar a A", self)
        self.btn_assign_a.setObjectName("btnAssignA")
        self.btn_assign_a.clicked.connect(lambda: self.controller.assign_points_to_team("A"))
        
        self.btn_assign_b = QPushButton("Asignar a B", self)
        self.btn_assign_b.setObjectName("btnAssignB")
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
        
        # Cabecera de dinero rápido
        header = QHBoxLayout()
        header.addWidget(QLabel("DINERO RÁPIDO - PANEL DE RESPUESTAS", self))
        
        self.btn_fm_buzzer = QPushButton("Sonido Buzzer 🔊", self)
        self.btn_fm_buzzer.setStyleSheet("background-color: #ffaa00; color: black;")
        self.btn_fm_buzzer.clicked.connect(self.controller.play_buzzer_sound)
        header.addWidget(self.btn_fm_buzzer)
        
        layout.addLayout(header)
        
        # Dos columnas para Jugador 1 y Jugador 2
        players_layout = QHBoxLayout()
        
        # Jugador 1
        group_p1 = QGroupBox("JUGADOR 1", self)
        layout_p1 = QVBoxLayout(group_p1)
        self.fm_p1_inputs = []
        
        for i in range(5):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"P{i+1}:", self))
            
            txt = QLineEdit(self)
            txt.setPlaceholderText("Respuesta")
            txt.textChanged.connect(lambda text, idx=i: self.update_fast_money_val(1, idx))
            
            pts = QSpinBox(self)
            pts.setRange(0, 100)
            pts.valueChanged.connect(lambda val, idx=i: self.update_fast_money_val(1, idx))

            chk_resp = QCheckBox("Rev Resp", self)
            chk_resp.stateChanged.connect(lambda state, idx=i: self.update_fast_money_val(1, idx))
            chk_pts = QCheckBox("Rev Pts", self)
            chk_pts.stateChanged.connect(lambda state, idx=i: self.update_fast_money_val(1, idx))

            row.addWidget(txt, 2)
            row.addWidget(pts, 1)
            row.addWidget(chk_resp)
            row.addWidget(chk_pts)
            layout_p1.addLayout(row)
            self.fm_p1_inputs.append((txt, pts, chk_resp, chk_pts))
            pts.setRange(0, 100)
            pts.valueChanged.connect(lambda val, idx=i: self.update_fast_money_val(1, idx))
            

            
        players_layout.addWidget(group_p1, 1)
        
        # Jugador 2
        group_p2 = QGroupBox("JUGADOR 2", self)
        layout_p2 = QVBoxLayout(group_p2)
        self.fm_p2_inputs = []
        
        for i in range(5):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"P{i+1}:", self))
            
            txt = QLineEdit(self)
            txt.setPlaceholderText("Respuesta")
            txt.textChanged.connect(lambda text, idx=i: self.update_fast_money_val(2, idx))
            
            pts = QSpinBox(self)
            pts.setRange(0, 100)
            pts.valueChanged.connect(lambda val, idx=i: self.update_fast_money_val(2, idx))

            chk_resp = QCheckBox("Rev Resp", self)
            chk_resp.stateChanged.connect(lambda state, idx=i: self.update_fast_money_val(2, idx))
            chk_pts = QCheckBox("Rev Pts", self)
            chk_pts.stateChanged.connect(lambda state, idx=i: self.update_fast_money_val(2, idx))

            row.addWidget(txt, 2)
            row.addWidget(pts, 1)
            row.addWidget(chk_resp)
            row.addWidget(chk_pts)
            layout_p2.addLayout(row)
            self.fm_p2_inputs.append((txt, pts, chk_resp, chk_pts))
            
        players_layout.addWidget(group_p2, 1)
        layout.addLayout(players_layout)
        
        # Totalizador final
        fm_total_layout = QHBoxLayout()
        self.lbl_fm_admin_total = QLabel("Total Dinero Rápido: 0 / 200 Puntos", self)
        self.lbl_fm_admin_total.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffd700;")
        fm_total_layout.addWidget(self.lbl_fm_admin_total)
        layout.addLayout(fm_total_layout)
        
        self.tabs.addTab(widget, "Dinero Rápido (Final)")

    def setup_status_bar(self):
        bar = QHBoxLayout()
        
        # Botón para abrir la ventana del público si se cerró
        self.btn_open_board = QPushButton("Abrir Tablero Público", self)
        self.btn_open_board.setObjectName("btnOpenBoard")
        self.btn_open_board.clicked.connect(self.controller.open_board_window)
        bar.addWidget(self.btn_open_board)
        
        # Botones de Fase del Juego
        bar.addWidget(QLabel("Fase de Juego:", self))
        
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
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Cargar Preguntas", "", "Archivos JSON (*.json)"
        )
        if filepath:
            self.controller.load_questions(filepath)
            self.lbl_json_path.setText(os.path.basename(filepath))

    def update_team_names(self):
        name_a = self.txt_team_a.text()
        name_b = self.txt_team_b.text()
        self.controller.update_team_names(name_a, name_b)

    def update_fast_money_val(self, player_num, idx):
        if player_num == 1:
            txt, pts, chk_resp, chk_pts = self.fm_p1_inputs[idx]
            self.controller.update_fast_money_player1(
                idx, txt.text(), pts.value(), chk_resp.isChecked(), chk_pts.isChecked()
            )
        else:
            txt, pts, chk_resp, chk_pts = self.fm_p2_inputs[idx]
            self.controller.update_fast_money_player2(
                idx, txt.text(), pts.value(), chk_resp.isChecked(), chk_pts.isChecked()
            )

    def connect_signals(self):
        self.model.state_changed.connect(self.update_ui_from_model)
        self.model.round_changed.connect(self.update_answers_table)
        self.model.round_points_changed.connect(self.update_accumulated)
        self.model.strikes_changed.connect(self.update_strikes_label)
        self.model.fast_money_updated.connect(self.update_fast_money_total)

    def update_ui_from_model(self):
        # Actualizar índice de la ronda actual
        total_rondas = len(self.model.rondas)
        if total_rondas > 0:
            self.lbl_current_round.setText(f"Ronda: {self.model.current_round_idx + 1} / {total_rondas}")
            self.lbl_round_question.setText(f"Pregunta: {self.model.rondas[self.model.current_round_idx]['pregunta']}")
        else:
            self.lbl_current_round.setText("Ronda: - / -")
            self.lbl_round_question.setText("Pregunta: Carga un archivo para comenzar")
            
        # Pestaña activa según fase de juego
        if self.model.game_phase == "RONDA":
            self.tabs.setCurrentIndex(0)
        elif self.model.game_phase == "DINERO_RAPIDO":
            self.tabs.setCurrentIndex(1)

    def update_answers_table(self):
        """Llena la tabla de respuestas para la ronda actual."""
        if 0 <= self.model.current_round_idx < len(self.model.rondas):
            respuestas = self.model.rondas[self.model.current_round_idx]["respuestas"]
            self.table_answers.setRowCount(len(respuestas))
            
            for i, r in enumerate(respuestas):
                # N°
                item_idx = QTableWidgetItem(str(i + 1))
                item_idx.setTextAlignment(Qt.AlignCenter)
                self.table_answers.setItem(i, 0, item_idx)
                
                # Respuesta
                item_text = QTableWidgetItem(r["texto"])
                self.table_answers.setItem(i, 1, item_text)
                
                # Puntos
                item_pts = QTableWidgetItem(str(r["puntos"]))
                item_pts.setTextAlignment(Qt.AlignCenter)
                self.table_answers.setItem(i, 2, item_pts)
                
                # Botón de acción
                btn_text = "Ocultar" if r["revelada"] else "Revelar"
                btn = QPushButton(btn_text, self)
                # Color distintivo si ya está revelada
                if r["revelada"]:
                    btn.setStyleSheet("background-color: #202744; color: #555555;")
                else:
                    btn.setStyleSheet("")
                
                btn.clicked.connect(lambda checked=False, idx=i: self.toggle_reveal_answer(idx))
                self.table_answers.setCellWidget(i, 3, btn)
        else:
            self.table_answers.setRowCount(0)

    def toggle_reveal_answer(self, idx):
        self.controller.toggle_reveal_answer(idx)
        self.update_answers_table()

    def update_accumulated(self, points):
        self.lbl_admin_accumulated.setText(f"Acumulado: {points}")

    def update_strikes_label(self, count):
        self.lbl_admin_strikes.setText(f"Strikes: {count}")

    def update_fast_money_total(self):
        total = self.model.get_fast_money_total()
        self.lbl_fm_admin_total.setText(f"Total Dinero Rápido: {total} / 200 Puntos")
