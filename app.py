from flask import Flask
from pathlib import Path

def create_app():
    app = Flask(__name__)

    # garante pastas
    Path("dados").mkdir(exist_ok=True)
    Path("dados/pacientes").mkdir(exist_ok=True)
    Path("dados/estoque").mkdir(exist_ok=True)

    # importa blueprints
    from blueprints.pacientes.routes import pacientes_bp
    from blueprints.estoque.routes import estoque_bp
    from blueprints.token.routes import token_bp
    from blueprints.resumo.routes import resumo_bp

    # registra blueprints
    app.register_blueprint(pacientes_bp, url_prefix="/pacientes")
    app.register_blueprint(estoque_bp, url_prefix="/estoque")
    app.register_blueprint(token_bp, url_prefix="/token")
    app.register_blueprint(resumo_bp, url_prefix="/resumo")

    # rota inicial -> seleção paciente
    @app.route("/")
    def index():
        return "<script>location.href='/pacientes/selecionar'</script>"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
