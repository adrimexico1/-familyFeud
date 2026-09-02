import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QGridLayout, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from views.styles import GLOBAL_STYLE

class AnswerCard(QFrame):
    def __init__(self, num, parent=None):
        super().__init__(parent)
        self.num = num
        self.text = ""
        self.points = 0
        self.revealed = False
        self.init_ui()
        self.update_appearance()

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 8, 15, 8)
        self.lbl_index = QLabel(str(self.num), self)
        self.lbl_index.setObjectName("cardIndexLabel")
        self.lbl_index.setAlignment(Qt.AlignCenter)
        
        self.lbl_text = QLabel("", self)
        self.lbl_text.setObjectName("cardTextLabel")
        self.lbl_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_text.setWordWrap(True)
        
        self.lbl_points = QLabel("", self)
        self.lbl_points.setObjectName("cardPointsLabel")
        self.lbl_points.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.lbl_index, 0, Qt.AlignCenter)
        self.layout.addWidget(self.lbl_text, 1)
        self.layout.addWidget(self.lbl_points, 0, Qt.AlignRight | Qt.AlignVCenter)

    def set_data(self, text, points, revealed):
        self.text = text
        self.points = points
        self.revealed = revealed
        self.update_appearance()

    def update_appearance(self):
        if not self.text:
            self.setVisible(False)
            return
        self.setVisible(True)
        if self.revealed:
            self.lbl_index.setVisible(False)
            self.lbl_text.setText(self.text.upper())
            self.lbl_text.setVisible(True)
            self.lbl_points.setText(str(self.points))
            self.lbl_points.setVisible(True)
            self.setProperty("class", "answerCardRevealed")
        else:
            self.lbl_index.setVisible(True)
            self.lbl_text.setVisible(False)
            self.lbl_points.setVisible(False)
            self.setProperty("class", "answerCardHidden")
        self.style().unpolish(self)
        self.style().polish(self)


class BoardWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("100 Mexicanos Dijeron - Tablero del Público")
        self.resize(1024, 768)
        self.setStyleSheet(GLOBAL_STYLE)
        
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.stacked_widget = QStackedWidget(self)
        self.main_layout.addWidget(self.stacked_widget)
        
        self.board_page = QWidget(self)
        self.setup_board_page()
        self.stacked_widget.addWidget(self.board_page)
        
        self.fast_money_page = QWidget(self)
        self.setup_fast_money_page()
        self.stacked_widget.addWidget(self.fast_money_page)
        
        self.lobby_page = QWidget(self)
        self.setup_lobby_page()
        self.stacked_widget.addWidget(self.lobby_page)
        
        self.stacked_widget.setCurrentWidget(self.lobby_page)
        
        self.setup_strike_overlay()
        self.setup_watermark_overlay()

    def setup_watermark_overlay(self):
        self.watermark_overlay = QLabel("Powered by adrimexico1", self)
        self.watermark_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.watermark_overlay.setAlignment(Qt.AlignCenter)
        self.watermark_overlay.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: rgba(120, 130, 160, 35); 
            background: transparent;
        """)
        self.watermark_overlay.setGeometry(self.rect())
        self.watermark_overlay.raise_()
        self.watermark_overlay.show()

    def setup_lobby_page(self):
        layout = QVBoxLayout(self.lobby_page)
        layout.setAlignment(Qt.AlignCenter)
        lbl_welcome = QLabel("100 MEXICANOS DIJERON", self)
        lbl_welcome.setObjectName("titleLabel")
        lbl_welcome.setStyleSheet("font-size: 60px; font-weight: 900;")
        lbl_welcome.setAlignment(Qt.AlignCenter)
        
        lbl_sub = QLabel("Esperando al Administrador para iniciar el juego...", self)
        lbl_sub.setStyleSheet("font-size: 24px; color: #a0a5c0;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_welcome)
        layout.addWidget(lbl_sub)

    def setup_board_page(self):
        layout = QVBoxLayout(self.board_page)
        layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        self.lbl_watermark = QLabel("powered by adrimexico1", self)
        self.lbl_watermark.setObjectName("watermarkLabelHeader")
        self.lbl_watermark.setAlignment(Qt.AlignCenter)
        
        self.lbl_question = QLabel("PREGUNTA AQUÍ", self)
        self.lbl_question.setObjectName("questionLabel")
        self.lbl_question.setAlignment(Qt.AlignCenter)
        
        self.lbl_round_points = QLabel("0", self)
        self.lbl_round_points.setObjectName("roundPointsValue")
        self.lbl_round_points.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.lbl_watermark, 0)
        header_layout.addWidget(self.lbl_question, 4)
        header_layout.addWidget(self.lbl_round_points, 1)
        layout.addLayout(header_layout)
        
        self.board_container = QWidget(self)
        self.board_container.setObjectName("boardContainer")
        board_container_layout = QVBoxLayout(self.board_container)
        board_container_layout.setContentsMargins(15, 15, 15, 15)
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        self.cards = []
        for i in range(8):
            card = AnswerCard(i + 1, self)
            self.cards.append(card)
            self.grid_layout.addWidget(card, i % 4, i // 4)
            
        board_container_layout.addLayout(self.grid_layout)
        layout.addWidget(self.board_container, 1)
        
        scores_layout = QHBoxLayout()
        scores_layout.setSpacing(40)
        
        self.frame_team_a = QFrame(self)
        self.frame_team_a.setObjectName("scoreFrame")
        layout_a = QVBoxLayout(self.frame_team_a)
        self.lbl_team_a_name = QLabel("EQUIPO A", self)
        self.lbl_team_a_name.setObjectName("teamNameLabel")
        self.lbl_team_a_name.setAlignment(Qt.AlignCenter)
        self.lbl_team_a_score = QLabel("0", self)
        self.lbl_team_a_score.setObjectName("teamScoreValue")
        self.lbl_team_a_score.setAlignment(Qt.AlignCenter)
        layout_a.addWidget(self.lbl_team_a_name)
        layout_a.addWidget(self.lbl_team_a_score)
        
        self.frame_team_b = QFrame(self)
        self.frame_team_b.setObjectName("scoreFrame")
        layout_b = QVBoxLayout(self.frame_team_b)
        self.lbl_team_b_name = QLabel("EQUIPO B", self)
        self.lbl_team_b_name.setObjectName("teamNameLabel")
        self.lbl_team_b_name.setAlignment(Qt.AlignCenter)
        self.lbl_team_b_score = QLabel("0", self)
        self.lbl_team_b_score.setObjectName("teamScoreValue")
        self.lbl_team_b_score.setAlignment(Qt.AlignCenter)
        layout_b.addWidget(self.lbl_team_b_name)
        layout_b.addWidget(self.lbl_team_b_score)
        
        scores_layout.addWidget(self.frame_team_a, 1)
        scores_layout.addWidget(self.frame_team_b, 1)
        layout.addLayout(scores_layout)

    def setup_fast_money_page(self):
        layout = QVBoxLayout(self.fast_money_page)
        
        # Cabecera de Dinero Rápido con la Marca de Agua Estilo Etiqueta y el Reloj
        header_fm = QHBoxLayout()
        header_fm.setSpacing(15)
        
        # Marca de agua superior idéntica a la de las rondas normales
        self.lbl_fm_watermark = QLabel("powered by adrimexico1", self)
        self.lbl_fm_watermark.setObjectName("watermarkLabelHeader")
        self.lbl_fm_watermark.setAlignment(Qt.AlignCenter)
        
        lbl_fm_title = QLabel("DINERO RÁPIDO", self)
        lbl_fm_title.setObjectName("titleLabel")
        lbl_fm_title.setAlignment(Qt.AlignCenter)
        
        # Etiqueta grande del Reloj (30s)
        self.lbl_fm_timer = QLabel("30 s", self)
        self.lbl_fm_timer.setStyleSheet("font-size: 36px; font-weight: 900; color: #ff0044; background-color: #0d1226; border: 2px solid #ff0044; border-radius: 10px; padding: 2px 15px;")
        self.lbl_fm_timer.setAlignment(Qt.AlignCenter)
        
        header_fm.addWidget(self.lbl_fm_watermark, 0)
        header_fm.addWidget(lbl_fm_title, 3)
        header_fm.addWidget(self.lbl_fm_timer, 1, Qt.AlignRight)
        
        layout.addLayout(header_fm)
        
        # Contenedor de respuestas dinero rápido
        fm_container = QWidget(self)
        fm_container.setObjectName("boardContainer")
        fm_grid = QGridLayout(fm_container)
        fm_grid.setSpacing(15)
        fm_grid.setContentsMargins(20, 20, 20, 20)
        
        lbl_player1 = QLabel("JUGADOR 1", self)
        lbl_player1.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffd700;")
        lbl_player1.setAlignment(Qt.AlignCenter)
        
        lbl_player2 = QLabel("JUGADOR 2", self)
        lbl_player2.setStyleSheet("font-size: 24px; font-weight: bold; color: #00f0ff;")
        lbl_player2.setAlignment(Qt.AlignCenter)
        
        fm_grid.addWidget(lbl_player1, 0, 0, 1, 2)
        fm_grid.addWidget(lbl_player2, 0, 2, 1, 2)
        
        self.fm_p1_cards = []
        self.fm_p2_cards = []
        
        for i in range(5):
            card_p1_text = QLabel("-", self)
            card_p1_text.setObjectName("cardTextLabel")
            card_p1_text.setStyleSheet("background-color: #10152b; border: 1px solid #1a2244; padding: 10px; border-radius: 5px; font-size: 18px;")
            
            card_p1_pts = QLabel("-", self)
            card_p1_pts.setObjectName("cardPointsLabel")
            card_p1_pts.setStyleSheet("font-size: 20px; padding: 5px 15px;")
            
            fm_grid.addWidget(card_p1_text, i + 1, 0)
            fm_grid.addWidget(card_p1_pts, i + 1, 1)
            self.fm_p1_cards.append((card_p1_text, card_p1_pts))
            
            card_p2_text = QLabel("-", self)
            card_p2_text.setObjectName("cardTextLabel")
            card_p2_text.setStyleSheet("background-color: #10152b; border: 1px solid #1a2244; padding: 10px; border-radius: 5px; font-size: 18px;")
            
            card_p2_pts = QLabel("-", self)
            card_p2_pts.setObjectName("cardPointsLabel")
            card_p2_pts.setStyleSheet("font-size: 20px; padding: 5px 15px;")
            
            fm_grid.addWidget(card_p2_text, i + 1, 2)
            fm_grid.addWidget(card_p2_pts, i + 1, 3)
            self.fm_p2_cards.append((card_p2_text, card_p2_pts))
            
        layout.addWidget(fm_container, 1)
        
        fm_footer = QHBoxLayout()
        lbl_total_txt = QLabel("PUNTUACIÓN TOTAL:", self)
        lbl_total_txt.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffffff;")
        
        self.lbl_fm_total = QLabel("0", self)
        self.lbl_fm_total.setObjectName("roundPointsValue")
        self.lbl_fm_total.setStyleSheet("font-size: 48px; min-width: 100px;")
        self.lbl_fm_total.setAlignment(Qt.AlignCenter)
        
        fm_footer.addStretch()
        fm_footer.addWidget(lbl_total_txt)
        fm_footer.addWidget(self.lbl_fm_total)
        fm_footer.addStretch()
        layout.addLayout(fm_footer)

    def setup_strike_overlay(self):
        self.strike_overlay = QFrame(self)
        self.strike_overlay.setGeometry(self.rect())
        self.strike_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.75);")
        self.strike_overlay.setVisible(False)
        layout = QVBoxLayout(self.strike_overlay)
        layout.setAlignment(Qt.AlignCenter)
        self.lbl_strike_x = QLabel("", self.strike_overlay)
        self.lbl_strike_x.setObjectName("strikeXLabel")
        self.lbl_strike_x.setStyleSheet("font-size: 180px; font-weight: 900; color: #ff0044;")
        self.lbl_strike_x.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_strike_x)
        self.strike_timer = QTimer(self)
        self.strike_timer.setSingleShot(True)
        self.strike_timer.timeout.connect(self.hide_strike_overlay)

    def show_strikes(self, count):
        if count <= 0:
            return
        self.lbl_strike_x.setText((" X " * count).strip())
        self.strike_overlay.setGeometry(self.rect())
        self.strike_overlay.setVisible(True)
        self.strike_overlay.raise_()
        if hasattr(self, 'watermark_overlay'):
            self.watermark_overlay.raise_()
        self.strike_timer.start(1500)

    def hide_strike_overlay(self):
        self.strike_overlay.setVisible(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'strike_overlay'):
            self.strike_overlay.setGeometry(self.rect())
        if hasattr(self, 'watermark_overlay'):
            self.watermark_overlay.setGeometry(self.rect())
            self.watermark_overlay.raise_()

    def connect_signals(self):
        self.model.state_changed.connect(self.update_state)
        self.model.scores_changed.connect(self.update_scores)
        self.model.round_points_changed.connect(self.update_round_points)
        self.model.round_changed.connect(self.update_round)
        self.model.answer_revealed.connect(self.update_card)
        self.model.strikes_changed.connect(self.show_strikes)
        self.model.fast_money_updated.connect(self.update_fast_money_board)
        self.model.fast_money_timer_updated.connect(self.update_timer_display)

    def update_timer_display(self, seconds):
        """Actualiza el reloj en la pantalla del público."""
        self.lbl_fm_timer.setText(f"{seconds} s")
        if seconds <= 5:
            self.lbl_fm_timer.setStyleSheet("font-size: 40px; font-weight: 900; color: #ffff00; background-color: #330000; border: 2px solid #ff0000; border-radius: 10px; padding: 2px 20px;")
        else:
            self.lbl_fm_timer.setStyleSheet("font-size: 40px; font-weight: 900; color: #ff0044; background-color: #0d1226; border: 2px solid #ff0044; border-radius: 10px; padding: 2px 20px;")

    def update_state(self):
        if self.model.game_phase == "LOBBY":
            self.stacked_widget.setCurrentWidget(self.lobby_page)
        elif self.model.game_phase == "RONDA":
            self.stacked_widget.setCurrentWidget(self.board_page)
        elif self.model.game_phase == "DINERO_RAPIDO":
            self.stacked_widget.setCurrentWidget(self.fast_money_page)
            self.update_fast_money_board()
        if hasattr(self, 'watermark_overlay'):
            self.watermark_overlay.raise_()

    def update_scores(self, score_a, score_b):
        self.lbl_team_a_score.setText(str(score_a))
        self.lbl_team_b_score.setText(str(score_b))

    def update_round_points(self, points):
        self.lbl_round_points.setText(str(points))

    def update_round(self):
        if 0 <= self.model.current_round_idx < len(self.model.rondas):
            round_data = self.model.rondas[self.model.current_round_idx]
            self.lbl_question.setText(round_data["pregunta"].upper())
            respuestas = round_data["respuestas"]
            for i in range(8):
                card = self.cards[i]
                if i < len(respuestas):
                    resp = respuestas[i]
                    card.set_data(resp["texto"], resp["puntos"], resp["revelada"])
                else:
                    card.set_data("", 0, False)
        else:
            self.lbl_question.setText("NO HAY RONDAS CARGADAS")
            for card in self.cards:
                card.set_data("", 0, False)

    def update_card(self, idx):
        if 0 <= self.model.current_round_idx < len(self.model.rondas):
            respuestas = self.model.rondas[self.model.current_round_idx]["respuestas"]
            if 0 <= idx < len(respuestas) and idx < len(self.cards):
                resp = respuestas[idx]
                self.cards[idx].set_data(resp["texto"], resp["puntos"], resp["revelada"])

    def update_fast_money_board(self):
        for i, item in enumerate(self.model.fast_money_p1):
            lbl_txt, lbl_pts = self.fm_p1_cards[i]
            if item.get("respuesta_revelada", False):
                lbl_txt.setText(item["respuesta"].upper() if item["respuesta"] else "-")
            else:
                lbl_txt.setText("")
            if item.get("puntos_revelados", False):
                lbl_pts.setText(str(item["puntos"]))
            else:
                lbl_pts.setText("")
                
        for i, item in enumerate(self.model.fast_money_p2):
            lbl_txt, lbl_pts = self.fm_p2_cards[i]
            if item.get("respuesta_revelada", False):
                lbl_txt.setText(item["respuesta"].upper() if item["respuesta"] else "-")
            else:
                lbl_txt.setText("")
            if item.get("puntos_revelados", False):
                lbl_pts.setText(str(item["puntos"]))
            else:
                lbl_pts.setText("")
                
        total = self.model.get_fast_money_total()
        self.lbl_fm_total.setText(str(total))