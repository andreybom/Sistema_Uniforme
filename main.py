from database.models import SistemaModel
from controlles.app_controller import AppController
from views.main_view import MenuPrincipal

if __name__ == "__main__":
    # 1. Inicia o Model (Banco de Dados)
    model = SistemaModel()

    # 2. Inicia o Controller com o Model
    controller = AppController(model)

    # 3. Inicia a View Principal passando o Controller
    app = MenuPrincipal(controller)

    # 4. Inicia o loop do sistema
    app.mainloop()
