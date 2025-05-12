from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from app.services.tournament_service import start_tournament
from app.services.user_service import remove_expired_tokens

scheduler = BackgroundScheduler()


def register_scheduler(app):
    scheduler.add_job(func=remove_expired_tokens, trigger="interval", hours=1)
    scheduler.start()


# Schedule a tournament start
def schedule_tournament_start(tournament_id, start_time: datetime):
    scheduler.add_job(
        func=start_tournament,
        trigger=DateTrigger(run_date=start_time),
        args=[tournament_id],
        id=f"tournament_start_{tournament_id}",
        replace_existing=True
    )
