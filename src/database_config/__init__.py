from src.database_config.database import AsyncDatabaseManager

database_manager = AsyncDatabaseManager.get_instance()
engine = database_manager.engine
session_local = database_manager.session_local
metadata = database_manager.metadata
get_db = database_manager.get_db
websocket_with_db = database_manager.websocket_with_db()