from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pycoingecko import CoinGeckoAPI
import uvicorn

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

def get_crypto_data(crypto_name):
    try:
        # Use the CoinGecko API to search for the cryptocurrency by name
        search_results = cg.get_coins_list()

        # Find the cryptocurrency by name in the search results
        coin_id = None
        for coin in search_results:
            if coin["name"].lower() == crypto_name.lower():
                coin_id = coin["id"]
                break

        if coin_id is not None:
            # Get detailed data for the cryptocurrency using its ID
            data = cg.get_coin_by_id(id=coin_id)
            return data
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.get("/crypto/{crypto_name}")
def get_crypto_info(crypto_name: str):
    crypto_data = get_crypto_data(crypto_name)

    if crypto_data is not None:
        selected_fields = {
            "id": crypto_data["id"],
            "symbol": crypto_data["symbol"],
            "name": crypto_data["name"],
            "image": crypto_data["image"]["large"],
            "current_price": crypto_data["market_data"]["current_price"]["usd"],
            "market_cap": crypto_data["market_data"]["market_cap"]["usd"],
            "market_cap_rank": crypto_data["market_data"]["market_cap_rank"],
            "fully_diluted_valuation": crypto_data["market_data"].get("fully_diluted_valuation", {}).get("usd"),
            "total_volume": crypto_data["market_data"]["total_volume"]["usd"],
            "high_24h": crypto_data["market_data"]["high_24h"]["usd"],
            "low_24h": crypto_data["market_data"]["low_24h"]["usd"],
            "price_change_24h": crypto_data["market_data"]["price_change_24h"],
            "price_change_percentage_24h": crypto_data["market_data"]["price_change_percentage_24h"],
            "market_cap_change_24h": crypto_data["market_data"]["market_cap_change_24h"],
            "market_cap_change_percentage_24h": crypto_data["market_data"]["market_cap_change_percentage_24h"],
            "circulating_supply": crypto_data["market_data"]["circulating_supply"],
            "total_supply": crypto_data["market_data"]["total_supply"],
            "max_supply": crypto_data["market_data"]["max_supply"],
            "ath": crypto_data["market_data"]["ath"]["usd"],
            "ath_change_percentage": crypto_data["market_data"]["ath_change_percentage"],
            "ath_date": crypto_data["market_data"]["ath_date"]["usd"],
            "atl": crypto_data["market_data"]["atl"]["usd"],
            "atl_change_percentage": crypto_data["market_data"]["atl_change_percentage"],
            "atl_date": crypto_data["market_data"]["atl_date"]["usd"],
            "roi": crypto_data.get("roi"),
            "last_updated": crypto_data["last_updated"],
        }

        return selected_fields
    else:
        return {"message": "Cryptocurrency not found or failed to retrieve data."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Crypto Info API:app", port=5000, reload=True)