from apscheduler.schedulers.background import BackgroundScheduler
from app.price_service import update_all_prices

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(
        update_all_prices,
        'interval',
        days=3,
        id='update_prices_job'
    )
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()