# Estilos visuales para Cien Mexicanos Dijeron en PySide6
# Estilo moderno tipo Game Show / Cyberpunk con tonos oscuros y neón.

THEME_DARK_BG = "#0a0c16"
THEME_CARD_BG = "#13182b"
THEME_CYAN = "#00f0ff"
THEME_GOLD = "#ffd700"
THEME_RED = "#ff0044"
THEME_GREEN = "#00ff66"
THEME_TEXT_LIGHT = "#ffffff"
THEME_TEXT_GRAY = "#a0a5c0"

GLOBAL_STYLE = f"""
QMainWindow {{
    background-color: {THEME_DARK_BG};
}}

QWidget#boardContainer {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0a0c1a, stop:1 #141a36);
    border: 3px solid #1a2244;
    border-radius: 15px;
}}

/* Marca de agua antes de la pregunta */
QLabel#watermarkLabelHeader {{
    font-size: 14px;
    font-weight: 900;
    color: {THEME_GOLD};
    text-transform: uppercase;
    letter-spacing: 1.5px;
    background-color: rgba(255, 215, 0, 0.1);
    border: 1px solid {THEME_GOLD};
    border-radius: 10px;
    padding: 10px 15px;
}}

/* Etiquetas generales */
QLabel {{
    color: {THEME_TEXT_LIGHT};
    font-family: 'Montserrat', 'Helvetica Neue', 'Arial', sans-serif;
}}

QLabel#titleLabel {{
    font-size: 36px;
    font-weight: bold;
    color: {THEME_GOLD};
    letter-spacing: 2px;
}}

QLabel#questionLabel {{
    font-size: 26px;
    font-weight: 500;
    color: {THEME_TEXT_LIGHT};
    padding: 10px;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}}

/* Estilo para las Tarjetas del Tablero (Público) */
QFrame.answerCardHidden {{
    background-color: qradialgradient(cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, stop:0 #1a2242, stop:1 #0f152d);
    border: 3px solid {THEME_GOLD};
    border-radius: 12px;
}}

QFrame.answerCardHidden:hover {{
    border-color: {THEME_CYAN};
}}

QFrame.answerCardRevealed {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0a2540, stop:1 #101c36);
    border: 3px solid {THEME_CYAN};
    border-radius: 12px;
}}

QLabel#cardIndexLabel {{
    font-size: 32px;
    font-weight: 900;
    color: {THEME_GOLD};
    background-color: #101630;
    border: 2px solid {THEME_GOLD};
    border-radius: 20px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}}

QLabel#cardTextLabel {{
    font-size: 20px;
    font-weight: bold;
    color: {THEME_TEXT_LIGHT};
    text-transform: uppercase;
}}

QLabel#cardPointsLabel {{
    font-size: 24px;
    font-weight: 900;
    color: {THEME_CYAN};
    background-color: #0b1a30;
    border: 2px solid {THEME_CYAN};
    border-radius: 8px;
    padding: 2px 10px;
    min-width: 50px;
    text-align: center;
}}

/* Marcadores */
QFrame#scoreFrame {{
    background-color: #0d1226;
    border: 2px solid #1c2448;
    border-radius: 12px;
}}

QLabel#teamScoreValue {{
    font-size: 48px;
    font-weight: 900;
    color: {THEME_GOLD};
}}

QLabel#teamNameLabel {{
    font-size: 18px;
    font-weight: bold;
    color: {THEME_TEXT_GRAY};
    text-transform: uppercase;
}}

QLabel#roundPointsValue {{
    font-size: 64px;
    font-weight: 900;
    color: {THEME_CYAN};
    background-color: #050b18;
    border: 3px solid {THEME_CYAN};
    border-radius: 10px;
    padding: 5px 20px;
}}

/* Estilo para los Strikes */
QLabel.strikeX {{
    font-size: 100px;
    font-weight: 900;
    color: {THEME_RED};
}}

/* Estilo para la Ventana de Administración */
QWidget#adminWidget {{
    background-color: #121626;
}}

QPushButton {{
    font-family: 'Segoe UI', sans-serif;
    font-weight: bold;
    font-size: 14px;
    color: white;
    background-color: #202744;
    border: 1px solid #323d6a;
    border-radius: 6px;
    padding: 8px 16px;
    min-height: 25px;
}}

QPushButton:hover {{
    background-color: #2c3660;
    border-color: #42518e;
}}

QPushButton:pressed {{
    background-color: #1a1f38;
}}

QPushButton#btnStrike {{
    background-color: {THEME_RED};
    font-size: 16px;
    border: none;
}}

QPushButton#btnStrike:hover {{
    background-color: #ff2a60;
}}

QPushButton#btnCorrect {{
    background-color: {THEME_GREEN};
    color: #051405;
    font-size: 16px;
    border: none;
}}

QPushButton#btnCorrect:hover {{
    background-color: #26ff80;
}}

QPushButton#btnAssignA {{
    background-color: #0066cc;
    border: none;
}}

QPushButton#btnAssignB {{
    background-color: #cc6600;
    border: none;
}}

QPushButton#btnOpenBoard {{
    background-color: {THEME_CYAN};
    color: #001020;
    border: none;
}}

QPushButton#btnOpenBoard:hover {{
    background-color: #33f5ff;
}}

QGroupBox {{
    font-weight: bold;
    border: 2px solid #202744;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 15px;
    color: {THEME_CYAN};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}}

QLineEdit {{
    background-color: #0b0d18;
    border: 1px solid #28325a;
    border-radius: 4px;
    color: white;
    padding: 6px;
    font-size: 14px;
}}

QLineEdit:focus {{
    border-color: {THEME_CYAN};
}}

QTableWidget {{
    background-color: #0f1220;
    gridline-color: #202744;
    color: white;
    border: 1px solid #202744;
    border-radius: 8px;
}}

QHeaderView::section {{
    background-color: #181d33;
    color: {THEME_CYAN};
    font-weight: bold;
    border: 1px solid #202744;
    padding: 4px;
}}
"""