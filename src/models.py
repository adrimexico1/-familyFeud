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
    fast_money_timer_updated = Signal(int)  # <--- ASEGÚRATE DE TENER ESTA LÍNEA AQUÍ

    def __init__(self):
        super().__init__()
        self.team_a_name = "Equipo A"
        self.team_b_name = "Equipo B"
        self.team_a_score = 0
        self.team_b_score = 0
        
        self.rondas = []
        self.current_round_idx = -1
        self.round_accumulated_points = 0
        self.strikes = 0
        self.controlling_team = None
        
        # Dinero Rápido
        self.dinero_rapido_preguntas = []
        self.fast_money_p1 = []
        self.fast_money_p2 = []
        self.fast_money_time_left = 30
        
        self.game_phase = "LOBBY"

    def load_game_data(self, filepath):
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
            respuestas.sort(key=lambda x: x["puntos"], reverse=True)
            self.rondas.append({
                "pregunta": r.get("pregunta", ""),
                "respuestas": respuestas
            })
            
        # Cargar preguntas de dinero rápido desde el JSON
        self.dinero_rapido_preguntas = data.get("dinero_rapido", [])
        
        # Inicializar estructuras para 5 preguntas tomando los datos del JSON
        self.fast_money_p1 = []
        self.fast_money_p2 = []
        
        for q in self.dinero_rapido_preguntas[:5]:
            opciones = q.get("respuestas", [])
            # Ordenar opciones de mayor a menor puntaje para la lista desplegable
            opciones.sort(key=lambda x: int(x.get("puntos", 0)), reverse=True)
            
            item_data = {
                "pregunta": q.get("pregunta", ""),
                "opciones": opciones,
                "respuesta": "",
                "puntos": 0,
                "respuesta_revelada": False,
                "puntos_revelados": False
            }
            self.fast_money_p1.append(item_data.copy())
            self.fast_money_p2.append(item_data.copy())
            
        if self.rondas:
            self.current_round_idx = 0
            self.game_phase = "RONDA"
        else:
            self.current_round_idx = -1
            self.game_phase = "LOBBY"
            
        self.state_changed.emit()
        self.round_changed.emit()

    def update_fast_money_p1(self, idx, answer, points, respuesta_revelada=False, puntos_revelados=False):
        if 0 <= idx < len(self.fast_money_p1):
            self.fast_money_p1[idx]["respuesta"] = answer
            self.fast_money_p1[idx]["puntos"] = int(points) if points else 0
            self.fast_money_p1[idx]["respuesta_revelada"] = respuesta_revelada
            self.fast_money_p1[idx]["puntos_revelados"] = puntos_revelados
            self.fast_money_updated.emit()

    def update_fast_money_p2(self, idx, answer, points, respuesta_revelada=False, puntos_revelados=False):
        if 0 <= idx < len(self.fast_money_p2):
            self.fast_money_p2[idx]["respuesta"] = answer
            self.fast_money_p2[idx]["puntos"] = int(points) if points else 0
            self.fast_money_p2[idx]["respuesta_revelada"] = respuesta_revelada
            self.fast_money_p2[idx]["puntos_revelados"] = puntos_revelados
            self.fast_money_updated.emit()

    def set_fast_money_timer(self, seconds):
        self.fast_money_time_left = seconds
        self.fast_money_timer_updated.emit(seconds)

    def get_fast_money_total(self):
        total = 0
        for item in self.fast_money_p1:
            if item["puntos_revelados"]:
                total += item["puntos"]
        for item in self.fast_money_p2:
            if item["puntos_revelados"]:
                total += item["puntos"]
        return total

    def next_round(self):
        if self.current_round_idx < len(self.rondas) - 1:
            self.current_round_idx += 1
            self.round_accumulated_points = 0
            self.strikes = 0
            self.controlling_team = None
            for resp in self.rondas[self.current_round_idx]["respuestas"]:
                resp["revelada"] = False
            self.round_changed.emit()
            self.round_points_changed.emit(0)
            self.strikes_changed.emit(0)
            self.state_changes.emit() if hasattr(self, 'state_changes') else self.state_changed.emit()
            return True
        return False

    def prev_round(self):
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
        if self.strikes < 3:
            self.strikes += 1
            self.strikes_changed.emit(self.strikes)
            return True
        return False

    def clear_strikes(self):
        self.strikes = 0
        self.strikes_changed.emit(self.strikes)

    def assign_points(self, team):
        if team == "A":
            self.team_a_score += self.round_accumulated_points
        elif team == "B":
            self.team_b_score += self.round_accumulated_points
        self.round_accumulated_points = 0
        self.round_points_changed.emit(0)
        self.scores_changed.emit(self.team_a_score, self.team_b_score)

    def set_game_phase(self, phase):
        self.game_phase = phase
        self.state_changed.emit()