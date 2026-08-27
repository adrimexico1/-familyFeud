import sys
from PySide6.QtWidgets import QApplication
from models import GameModel
from controllers import GameController
from views.admin_window import AdminWindow
from views.board_window import BoardWindow

def main():
    # Inicializar la aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("100 Mexicanos Dijeron")
    
    # Crear modelo y controlador
    model = GameModel()
    controller = GameController(model)
    
    # Crear las ventanas
    admin_window = AdminWindow(model, controller)
    board_window = BoardWindow(model)
    
    # Vincular la ventana del público al controlador
    controller.set_board_window(board_window)
    
    # Mostrar ventanas
    # Mostramos ambas por defecto para facilitar el desarrollo y la proyección
    admin_window.show()
    board_window.show()
    
    # Ejecutar el bucle principal de Qt
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
