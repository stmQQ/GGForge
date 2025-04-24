from apscheduler.schedulers.background import BackgroundScheduler
from app.services.user_service import remove_expired_tokens

def register_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=remove_expired_tokens, trigger="interval", hours=1)
    scheduler.start()