from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta
import time
import uvicorn

class CoinHistory(BaseModel):
    coin_name: str

app = FastAPI()
cg = CoinGeckoAPI(api_key='')

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_coin_id(coin_name):
    try:
        # Use the CoinGecko API to search for the cryptocurrency by name
        search_results = cg.get_coins_list()
        
        # Find the cryptocurrency by name in the search results
        coin_id = None
        for coin in search_results:
            if coin["name"].lower() == coin_name.lower():
                coin_id = coin["id"]
                break
        
        return coin_id
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.get("/coins/markets")
async def get_coin_markets(page: int = 1, per_page: int = 250):
    if per_page > 250:
        return {"error": "per_page exceeds maximum allowed (250)"}

    # Calculate the offset based on page number and per_page
    offset = (page - 1) * per_page

    # Fetch cryptocurrency data for the specified page and per_page
    markets = cg.get_coins_markets(vs_currency='usd', page=page, per_page=per_page)

    return markets
@app.get("/coin_history/{coin_name}")
def get_coin_history(coin_name: str, timeframe: int = 5):
    valid_timeframes = [1, 2, 5]
    if timeframe not in valid_timeframes:
        timeframe = 5

    coin_id = get_coin_id(coin_name)

    if coin_id is not None:
        current_timestamp = int(time.time())
        seconds_per_minute = 60
        timeframe_seconds = timeframe * seconds_per_minute

        to_timestamp = current_timestamp
        from_timestamp = to_timestamp - (timeframe_seconds * 200)

        coin_history = cg.get_coin_market_chart_range_by_id(id=coin_id,
                                                            vs_currency='usd',
                                                            from_timestamp=str(from_timestamp),
                                                            to_timestamp=str(to_timestamp),
                                                            localization=False)

        coin_prices = coin_history['prices']

        results = []

        for i, price in enumerate(coin_prices[::-1]):
            timestamp = price[0] / 1000
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            time_increment = i * timeframe * seconds_per_minute
            timestamp_str = (datetime.fromtimestamp(to_timestamp) - timedelta(seconds=time_increment)).strftime('%H:%M:%S')
            price_usd = price[1]
            result = {
                "datetime": f"{date} {timestamp_str}",
                "price_usd": price_usd
            }
            results.append(result)

        return {"coin_id": coin_id, "timeframe": timeframe, "results": results}
    else:
        return {"message": "Cryptocurrency not found."}

if __name__ == "__main__":
    uvicorn.run("Graph API:app", port=6000, reload=True)
