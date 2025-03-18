import os
import asyncio
from functools import wraps
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import OperationalError, TimeoutError, DisconnectionError, ArgumentError, SQLAlchemyError
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import MetaData, text
from fastapi import HTTPException, WebSocket, WebSocketDisconnect, Request, WebSocketException
from dotenv import load_dotenv
from src.database_config.models.db_error_description import DatabaseExceptionDescription, SourceRelatedPopouts
from src.seedwork.logger import logging_component


logger = logging_component.get_gray_logger()

load_dotenv()

database_url = os.getenv("DATABASE_URL")
print(f"Database URL from env: {database_url}")

class AsyncDatabaseManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.database_error_description = DatabaseExceptionDescription()
        self.error_sources = SourceRelatedPopouts()
        self.engine = create_async_engine(
            self.database_url,
            pool_size=int(os.getenv('DB_POOL_SIZE',750)),
            max_overflow=0,
            pool_timeout=300,
            pool_recycle=1800,
            poolclass=AsyncAdaptedQueuePool,
            echo=False
        )
        self.session_local = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=True,
        )
        self.metadata = MetaData()

    # Need to remove the boilerplate code    
    async def get_db(self, request: Request):
            try:
                async with self.session_local() as session:
                    await asyncio.wait_for(session.execute(text("select(1)")), timeout= 3)
                    yield session
            except OperationalError as error:
                logger.error(f"Database Unable {error}", extra={'host':request.client.host, 'user':'system', 'source':self.error_sources.database_connectivity_sources})
                raise HTTPException(status_code=503,detail=[{"msg":self.database_error_description.query_execution_issue}], headers={"Retry-After": "18000","X-Request-ID":"0"}) # Need to implement promethieses
            except asyncio.TimeoutError as error:
                logger.error(f"Database Connection Issue {error}", extra={'host':request.client.host, 'user':'system', 'source':self.error_sources.database_connectivity_sources})
                raise HTTPException(status_code=503,detail=[{"msg":self.database_error_description.connection_issue}], headers={"Retry-After": "18000","X-Request-ID":"0"}) # Need to implement promethieses
            except TimeoutError as error:
                logger.error(f"Database error {error}", extra={'host':request.client.host, 'user':'system', 'source':self.error_sources.database_timeout_sources})
                raise HTTPException(status_code=503,detail=[{"msg":self.database_error_description.connection_issue}], headers={"Retry-After": "18000","X-Request-ID":"0"}) # Need to implement promethieses
            except DisconnectionError as error:
                logger.error(f"Database Disconnected {error}", extra={'host':request.client.host, 'user':'system', 'source':self.error_sources.database_connectivity_sources})
                raise HTTPException(status_code=503,detail=[{"msg":self.database_error_description.connection_read_timeout}], headers={"Retry-After": "18000","X-Request-ID":"0"}) # Need to implement promethieses
            except ArgumentError as error:
                logger.error(f"Sqlalchemy Argument {error}", extra={'host':request.client.host, 'user':'system', 'source':self.error_sources.database_connectivity_sources})
                raise HTTPException(status_code=500,detail=[{"msg":"Sqlalchemy Argument Error."}])
            except HTTPException as error:
                logger.error(error, extra={'host':request.client.host, 'user':'system', 'source':self.error_sources.error_sources})
                raise error
            except Exception as error:
                logger.error(f"Internal Server Error {error}", extra={'host':request.client.host, 'user':'system', 'source':self.error_sources.error_sources})
                raise HTTPException(status_code=500,detail=[{"msg":"Internal Server Error"}])
            finally:
                await session.close()

    def websocket_with_db(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(websocket: WebSocket, *args, **kwargs):
                logger.info("Connection successful", extra={"user": "system","source" : "Machine Live Dashboard", "host": websocket.client.host})
                await websocket.accept()
                try:
                    async with self.session_local() as session:
                        await asyncio.wait_for(session.execute(text("select(1)")), timeout= 3)
                        websocket.state.session = session
                        await func(websocket,  *args, **kwargs)
                except asyncio.TimeoutError as error:
                    logger.error(f"Database Connection Issue {error}", extra={'host':websocket.client.host, 'user':'system', 'source':self.error_sources.database_connectivity_sources})
                    await websocket.close(code=1012, reason="Database connectivity issue")
                except SQLAlchemyError as error:
                    logger.error(f"Database Connection Issue {error}", extra={'host':websocket.client.host, 'user':'system', 'source':self.error_sources.database_connectivity_sources})
                    await websocket.close(code=1012, reason="Database Error")
                except WebSocketDisconnect:
                    logger.error("Websocket disconnected successfully", extra={"user": "system","source" : "Websocket Disconnected", "host": websocket.client.host})
                except WebSocketException as error:
                    logger.error(f"Internal Server Error {error}", extra={"user": "system","source" : "Websocket exception", "host": websocket.client.host})
                    await websocket.close(code=1011, reason="Internal server error.")
                finally:
                    await session.close()
            return wrapper
        return decorator