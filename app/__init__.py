from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, jwt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from app.routes.user_routes import user_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)

    # Global error handlers -> keep every response JSON
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.get("/health")
    def health():
        return jsonify({"success": True, "message": "Service is up"}), 200

    @app.cli.command("init-db")
    def init_db():
        """Create database tables. Usage: flask --app run.py init-db"""
        with app.app_context():
            db.create_all()
        print("Database tables created.")

    return app
