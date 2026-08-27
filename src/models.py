import json
from PySide6.QtCore import QObject, Signal

class GameModel(QObject):
    # Señales para notificar cambios a los observadores (controlador/vistas)
    state_changed = Signal()
    scores_changed = Signal(int, int)  # (puntos_A, puntos_B)
    round_points_changed = Signal(int)  # puntos acumulados en la ronda
    strikes_changed = Signal(int)  # cantidad de strikes (0 a 3)
    round_changed = Signal()  # cambio de ronda
    answer_revealed = Signal(int)  # índice de la respuesta revelada
    fast_money_updated = Signal()  # actualización en la fase final

    def __init__(self):
        super().__init__()
        # Datos de los equipos
        self.team_a_name = "Equipo A"
        self.team_b_name = "Equipo B"
        self.team_a_score = 0
        self.team_b_score = 0
        
        # Datos de las rondas normales
        self.rondas = []
        self.current_round_idx = -1
        self.round_accumulated_points = 0
        self.strikes = 0
        self.controlling_team = None  # None, "A" o "B"
        
        # Datos de Dinero Rápido
        self.dinero_rapido_preguntas = []
        # Lista de diccionarios: {"pregunta": "", "respuesta": "", "puntos": 0, "revelada": False}
        self.fast_money_p1 = []
        self.fast_money_p2 = []
        
        # Fase del juego: "LOBBY", "RONDA", "DINERO_RAPIDO"
        self.game_phase = "LOBBY"

    def load_game_data(self, filepath):
        """Carga las preguntas y respuestas desde un archivo JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.rondas = []
        for r in data.get("rondas", []):
            respuestas = []
            for resp in r.get("respuestas", []):
                respuestas.append({
                    "texto": resp.get("texto", ""),
                    "puntos": int(resp.get("puntos", 0)),
                    "revelada": False
                })
            # Ordenar respuestas por puntaje descendente
            respuestas.sort(key=lambda x: x["puntos"], reverse=True)
            self.rondas.append({
                "pregunta": r.get("pregunta", ""),
                "respuestas": respuestas
            })
            
        self.dinero_rapido_preguntas = data.get("dinero_rapido", [])
        
        # Inicializar estructuras de dinero rápido para 5 preguntas
        self.fast_money_p1 = [{"pregunta": q.get("pregunta", ""), "respuesta": "", "puntos": 0, "respuesta_revelada": False, "puntos_revelados": False} for q in self.dinero_rapido_preguntas[:5]]
        self.fast_money_p2 = [{"pregunta": q.get("pregunta", ""), "respuesta": "", "puntos": 0, "respuesta_revelada": False, "puntos_revelados": False} for q in self.dinero_rapido_preguntas[:5]]
        
        if self.rondas:
            self.current_round_idx = 0
            self.game_phase = "RONDA"
        else:
            self.current_round_idx = -1
            self.game_phase = "LOBBY"
            
        self.team_a_score = 0
        self.team_b_score = 0
        self.round_accumulated_points = 0
        self.strikes = 0
        self.controlling_team = None
        
        self.state_changed.emit()
        self.round_changed.emit()

    def next_round(self):
        """Avanza a la siguiente ronda si está disponible."""
        if self.current_round_idx < len(self.rondas) - 1:
            self.current_round_idx += 1
            self.round_accumulated_points = 0
            self.strikes = 0
            self.controlling_team = None
            # Asegurar que todas las respuestas inicien ocultas
            for resp in self.rondas[self.current_round_idx]["respuestas"]:
                resp["revelada"] = False
            self.round_changed.emit()
            self.round_points_changed.emit(0)
            self.strikes_changed.emit(0)
            self.state_changed.emit()
            return True
        return False

    def prev_round(self):
        """Retrocede a la ronda anterior."""
        if self.current_round_idx > 0:
            self.current_round_idx -= 1
            self.round_accumulated_points = 0
            self.strikes = 0
            self.controlling_team = None
            self.round_changed.emit()
            self.round_points_changed.emit(0)
            self.strikes_changed.emit(0)
            self.state_changed.emit()
            return True
        return False

    def reveal_answer(self, idx):
        """Revela una respuesta en la ronda actual y acumula los puntos."""
        if 0 <= self.current_round_idx < len(self.rondas):
            respuestas = self.rondas[self.current_round_idx]["respuestas"]
            if 0 <= idx < len(respuestas) and not respuestas[idx]["revelada"]:
                respuestas[idx]["revelada"] = True
                self.round_accumulated_points += respuestas[idx]["puntos"]
                self.answer_revealed.emit(idx)
                self.round_points_changed.emit(self.round_accumulated_points)
                return True
        return False

    def hide_answer(self, idx):
        """Oculta una respuesta previamente revelada y resta sus puntos."""
        if 0 <= self.current_round_idx < len(self.rondas):
            respuestas = self.rondas[self.current_round_idx]["respuestas"]
            if 0 <= idx < len(respuestas) and respuestas[idx]["revelada"]:
                respuestas[idx]["revelada"] = False
                self.round_accumulated_points -= respuestas[idx]["puntos"]
                self.answer_revealed.emit(idx)
                self.round_points_changed.emit(self.round_accumulated_points)
                return True
        return False

    def add_strike(self):
        """Agrega un strike al equipo actual (máximo 3)."""
        if self.strikes < 3:
            self.strikes += 1
            self.strikes_changed.emit(self.strikes)
            return True
        return False

    def clear_strikes(self):
        """Limpia los strikes de la ronda actual."""
        self.strikes = 0
        self.strikes_changed.emit(self.strikes)

    def assign_points(self, team):
        """Asigna los puntos acumulados de la ronda a un equipo ('A' o 'B') y los limpia."""
        if team == "A":
            self.team_a_score += self.round_accumulated_points
        elif team == "B":
            self.team_b_score += self.round_accumulated_points
            
        self.round_accumulated_points = 0
        self.round_points_changed.emit(0)
        self.scores_changed.emit(self.team_a_score, self.team_b_score)

    def set_controlling_team(self, team):
        """Establece qué equipo tiene el control ('A', 'B' o None)."""
        self.controlling_team = team
        self.state_changed.emit()

    def set_game_phase(self, phase):
        """Cambia la fase del juego ('LOBBY', 'RONDA', 'DINERO_RAPIDO')."""
        self.game_phase = phase
        self.state_changed.emit()

    # Métodos para Dinero Rápido
    def update_fast_money_p1(self, idx, answer, points, respuesta_revelada=False, puntos_revelados=False):
        """Actualiza una respuesta del Jugador 1 en la ronda final."""
        if 0 <= idx < len(self.fast_money_p1):
            self.fast_money_p1[idx]["respuesta"] = answer
            self.fast_money_p1[idx]["puntos"] = int(points) if points else 0
            self.fast_money_p1[idx]["respuesta_revelada"] = respuesta_revelada
            self.fast_money_p1[idx]["puntos_revelados"] = puntos_revelados
            self.fast_money_updated.emit()

    def update_fast_money_p2(self, idx, answer, points, respuesta_revelada=False, puntos_revelados=False):
        """Actualiza una respuesta del Jugador 2 en la ronda final."""
        if 0 <= idx < len(self.fast_money_p2):
            self.fast_money_p2[idx]["respuesta"] = answer
            self.fast_money_p2[idx]["puntos"] = int(points) if points else 0
            self.fast_money_p2[idx]["respuesta_revelada"] = respuesta_revelada
            self.fast_money_p2[idx]["puntos_revelados"] = puntos_revelados
            self.fast_money_updated.emit()

    def get_fast_money_total(self):
        """Calcula la suma total de puntos de ambos jugadores en dinero rápido."""
        total = 0
        for item in self.fast_money_p1:
            if item["puntos_revelados"]:
                total += item["puntos"]
        for item in self.fast_money_p2:
            if item["puntos_revelados"]:
                total += item["puntos"]
        return total
