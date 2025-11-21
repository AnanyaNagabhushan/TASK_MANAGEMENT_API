from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_smorest import Api

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = Api()  # ✅ no schema_name_resolver here

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    api.init_app(app)

    # 🔒 Token blacklist check
    from app.models.token_blocklist import TokenBlocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None  # True = revoked
