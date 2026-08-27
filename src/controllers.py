from audio import AudioManager
from views.board_window import BoardWindow

class GameController:
    def __init__(self, model):
        self.model = model
        self.audio_manager = AudioManager.get_instance()
        self.board_window = None

    def set_board_window(self, board_window):
        self.board_window = board_window

    def open_board_window(self):
        """Abre o enfoca la ventana de visualización del público."""
        if self.board_window is None:
            self.board_window = BoardWindow(self.model)
        self.board_window.show()
        self.board_window.raise_()
        self.board_window.activateWindow()

    def load_questions(self, filepath):
        """Carga las preguntas en el modelo."""
        try:
            self.model.load_game_data(filepath)
        except Exception as e:
            print(f"Error al cargar el archivo de preguntas: {e}")

    def update_team_names(self, name_a, name_b):
        """Actualiza los nombres de los equipos en el modelo."""
        self.model.team_a_name = name_a if name_a else "Equipo A"
        self.model.team_b_name = name_b if name_b else "Equipo B"
        # Forzar actualización en el tablero del público
        if self.board_window:
            self.board_window.lbl_team_a_name.setText(self.model.team_a_name.upper())
            self.board_window.lbl_team_b_name.setText(self.model.team_b_name.upper())

    def next_round(self):
        """Avanza a la siguiente ronda."""
        self.model.next_round()

    def prev_round(self):
        """Retrocede a la ronda anterior."""
        self.model.prev_round()

    def toggle_reveal_answer(self, idx):
        """Revela u oculta una respuesta en el modelo y reproduce sonido de acierto."""
        if 0 <= self.model.current_round_idx < len(self.model.rondas):
            respuestas = self.model.rondas[self.model.current_round_idx]["respuestas"]
            if 0 <= idx < len(respuestas):
                is_revealed = respuestas[idx]["revelada"]
                if not is_revealed:
                    # Reproducir sonido de acierto antes de revelar para mejor sincronización
                    self.audio_manager.play_correct()
                    self.model.reveal_answer(idx)
                else:
                    self.model.hide_answer(idx)

    def trigger_strike(self):
        """Aumenta un strike en el modelo y reproduce sonido de error."""
        self.audio_manager.play_strike()
        self.model.add_strike()

    def clear_strikes(self):
        """Limpia todos los strikes de la ronda actual."""
        self.model.clear_strikes()

    def assign_points_to_team(self, team):
        """Asigna puntos acumulados de la ronda actual al equipo 'A' o 'B'."""
        self.model.assign_points(team)

    def change_game_phase(self, phase):
        """Cambia la fase del juego (LOBBY, RONDA, DINERO_RAPIDO)."""
        self.model.set_game_phase(phase)

    # Métodos para Dinero Rápido (Final)
    def update_fast_money_player1(self, idx, answer, points, respuesta_revelada, puntos_revelados):
        """Actualiza el estado de las respuestas del Jugador 1."""
        old_val = self.model.fast_money_p1[idx] if idx < len(self.model.fast_money_p1) else None
        was_resp_revealed = old_val["respuesta_revelada"] if old_val else False
        was_pts_revealed = old_val["puntos_revelados"] if old_val else False
        
        if respuesta_revelada and not was_resp_revealed:
            self.audio_manager.play_correct()
        elif puntos_revelados and not was_pts_revealed:
            if int(points) > 0:
                self.audio_manager.play_correct()
            else:
                self.audio_manager.play_strike()
                
        self.model.update_fast_money_p1(idx, answer, points, respuesta_revelada, puntos_revelados)

    def update_fast_money_player2(self, idx, answer, points, respuesta_revelada, puntos_revelados):
        """Actualiza el estado de las respuestas del Jugador 2."""
        old_val = self.model.fast_money_p2[idx] if idx < len(self.model.fast_money_p2) else None
        was_resp_revealed = old_val["respuesta_revelada"] if old_val else False
        was_pts_revealed = old_val["puntos_revelados"] if old_val else False
        
        if respuesta_revelada and not was_resp_revealed:
            self.audio_manager.play_correct()
        elif puntos_revelados and not was_pts_revealed:
            if int(points) > 0:
                self.audio_manager.play_correct()
            else:
                self.audio_manager.play_strike()
                
        self.model.update_fast_money_p2(idx, answer, points, respuesta_revelada, puntos_revelados)

    def play_buzzer_sound(self):
        """Reproduce el zumbador (Buzzer) de dinero rápido."""
        self.audio_manager.play_buzzer()
