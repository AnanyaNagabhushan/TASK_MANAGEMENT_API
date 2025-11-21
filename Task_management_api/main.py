"""
Main Entry Point for Task Management API
========================================
"""

from flask import Flask
from config import Config
from app.extensions import init_extensions, api
from app.resources.todos import blp as TodosBlueprint
from app.resources.items import blp as ItemsBlueprint
from app.resources.auth import blp as AuthBlueprint

# Custom resolver to avoid duplicate schema names in Swagger/OpenAPI
def schema_name_resolver(schema):
    return schema.__class__.__name__

def create_app(test_config=None):
    """
    Factory function to create Flask app.

    Args:
        test_config (Config, optional): Override default Config for testing.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Override config if test_config is provided
    if test_config:
        app.config.from_object(test_config)

    # Initialize extensions (DB, JWT, API, etc.)
    init_extensions(app)

    # Apply custom schema name resolver for API documentation
    if api.spec:  # Make sure api.spec exists
        api.spec.components._schema_name_resolver = schema_name_resolver

    # Register all blueprints
    api.register_blueprint(TodosBlueprint)
    api.register_blueprint(ItemsBlueprint)
    api.register_blueprint(AuthBlueprint)

    # Home route
    @app.route("/")
    def home():
        return {"message": "Task Management API is running!"}

    return app


# Create app instance for running
app = create_app()

if __name__ == "__main__":
    # Debug mode can be True for development; set False in production
    app.run(debug=True)
