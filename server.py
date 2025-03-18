from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urls import router
from src.seedwork.logger import logging_component
from celery import Celery 

# app and logger initilize 
app = FastAPI(title = "kiosk-ausweg")
logger = logging_component.get_gray_logger()

# router included
app.include_router(router, prefix="/kiosk-ausweg/v1")
logger.info("Routes are initialized", extra = {'source':'Application Startup','host':'system host','user':'startup@ausweginfocontrols.com'})

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS are initialized", extra = {'source':'Application Startup','host':'system host','user':'startup@ausweginfocontrols.com'})



celery_app = Celery("tasks", broker="redis://localhost:6379/0")

def send_email_task(to_email: str, subject: str, body: str):
    celery_app.send_task("src.tasks.email_sending.send_email", args=[to_email, subject, body])
