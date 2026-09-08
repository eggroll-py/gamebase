from fastapi import APIRouter
from app.price_service import update_all_prices

router = APIRouter(prefix='/prices')

@router.get('/health')
def health_check():
    return {'status': 'ok'}

@router.post('/update')
def trigger_price_update():
    results = update_all_prices()
    return {'Updated': len(results), 'Results': results}
