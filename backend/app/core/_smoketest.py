from .settings import settings
print("APP:", settings.app_name, "| ENV:", settings.app_env)
print("DB:", settings.db_dsn_async)
print("JWT ALG:", settings.jwt_alg)
