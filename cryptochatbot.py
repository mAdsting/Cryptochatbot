# cryptochatbot.py
import requests
import time
from typing import Dict, Any

# CoinGecko API configuration
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
SUPPORTED_COINS = ["bitcoin", "ethereum", "cardano", "solana"]

def fetch_coin_data(coin_id: str) -> Dict[str, Any]:
    """
    Fetch real-time data for a specific cryptocurrency from CoinGecko.
    """
    try:
        # Get basic coin data
        response = requests.get(f"{COINGECKO_API_BASE}/coins/{coin_id}")
        response.raise_for_status()
        data = response.json()
        
        # Calculate sustainability score based on available data
        sustainability_score = 5/10  # Default middle score
        
        # Get market data
        market_data = data.get("market_data", {})
        price_change_24h = market_data.get("price_change_percentage_24h", 0)
        
        # Determine price trend
        if price_change_24h > 5:
            price_trend = "rising"
        elif price_change_24h < -5:
            price_trend = "falling"
        else:
            price_trend = "stable"
            
        # Determine market cap category
        market_cap = market_data.get("market_cap", {}).get("usd", 0)
        if market_cap > 10000000000:  # > 10B
            market_cap_category = "high"
        elif market_cap > 1000000000:  # > 1B
            market_cap_category = "medium"
        else:
            market_cap_category = "low"
            
        return {
            "price_trend": price_trend,
            "market_cap": market_cap_category,
            "energy_use": "medium",  # CoinGecko doesn't provide this directly
            "sustainability_score": sustainability_score,
            "description": data.get("description", {}).get("en", "No description available."),
            "risk_level": "medium",  # This would need more sophisticated analysis
            "popularity": "high" if market_cap > 10000000000 else "medium",
            "use_case": data.get("categories", ["General purpose"])[0],
            "current_price": market_data.get("current_price", {}).get("usd", 0),
            "price_change_24h": price_change_24h,
            "market_cap_usd": market_cap
        }
    except Exception as e:
        print(f"Error fetching data for {coin_id}: {str(e)}")
        return None

def update_crypto_db():
    """
    Update the crypto database with real-time data from CoinGecko.
    """
    global crypto_db
    for coin_id in SUPPORTED_COINS:
        data = fetch_coin_data(coin_id)
        if data:
            crypto_db[coin_id.capitalize()] = data
        time.sleep(1)  # Respect rate limits

# Initialize crypto_db with empty data
crypto_db = {}

# Update the database with real-time data
update_crypto_db()

# 1. Design the Chatbot's Personality
BOT_NAME = "CryptoBuddy"
BOT_TONE = "Hey there! I'm your friendly crypto advisor Do you want me to help you find your riches 🌱"
DISCLAIMER = "⚠️ DISCLAIMER: Crypto is risky—always do your own research! Past performance doesn't guarantee future results."

# Define keyword patterns for different types of queries
KEYWORD_PATTERNS = {
    "growth": [
        "long-term growth", "trending up", "profitable", "invest", "buy", "purchase",
        "which crypto", "what should i invest", "recommend", "suggestion", "advice",
        "what to buy", "best crypto", "top crypto", "good investment", "should i invest",
        "looking to invest", "want to invest", "thinking of investing", "investment advice",
        "investment recommendation", "investment suggestion"
    ],
    "sustainability": [
        "sustainable", "eco-friendly", "green", "environment", "energy efficient",
        "low energy", "environmental", "climate", "carbon", "sustainability",
        "eco", "green crypto", "environmental impact", "environmentally friendly",
        "sustainable crypto", "eco friendly crypto", "green investment"
    ],
    "trend": [
        "trending", "trend", "going up", "price movement", "price action",
        "market movement", "market trend", "price trend", "movement",
        "what's moving", "what's going up", "what's rising", "price changes",
        "market changes", "market direction", "price direction"
    ],
    "market_cap": [
        "market cap", "market capitalization", "biggest crypto", "largest crypto",
        "market size", "market value", "total value", "market worth",
        "which is biggest", "largest market", "biggest market", "market dominance",
        "market share", "largest by market", "biggest by market"
    ],
    "energy": [
        "energy use", "energy consumption", "power usage", "electricity",
        "energy efficient", "power consumption", "energy impact",
        "environmental impact", "carbon footprint", "power usage",
        "energy usage", "power consumption", "energy efficiency"
    ],
    "price": [
        "price", "prices", "cost", "value", "worth", "trading at",
        "current price", "price movement", "price action", "price trend",
        "price changes", "price direction", "price analysis"
    ],
    "greeting": [
        "hello", "hi", "hey", "greetings", "good morning", "good afternoon",
        "good evening", "howdy", "sup", "what's up", "greetings", "hi there",
        "hello there", "hey there"
    ]
}

def check_keywords(query, pattern_list):
    """
    Check if any of the keywords in the pattern list are present in the query.
    """
    query = query.lower().strip()
    # Check for exact matches first
    if any(keyword == query for keyword in pattern_list):
        return True
    # Then check for partial matches
    return any(keyword in query for keyword in pattern_list)

def get_recommendation(query):
    """
    Analyzes the user query and provides a crypto recommendation.
    """
    query = query.lower().strip()

    # Handle general questions about specific cryptocurrencies
    for coin in crypto_db.keys():
        if coin.lower() in query:
            data = crypto_db[coin]
            return f"Let me tell you about {coin}:\n\n" + \
                   f"💰 Current Price: ${data['current_price']:,.2f}\n" + \
                   f"📈 24h Change: {data['price_change_24h']:+.2f}%\n" + \
                   f"🌍 Sustainability: {data['sustainability_score']*10}/10\n" + \
                   f"⚡ Energy Use: {data['energy_use']}\n" + \
                   f"📊 Risk Level: {data['risk_level']}\n" + \
                   f"💡 Use Case: {data['use_case']}\n\n" + \
                   f"Description: {data['description']}\n\n" + \
                   f"{DISCLAIMER}"

    # Rule 1: Profitability and Growth
    if check_keywords(query, KEYWORD_PATTERNS["growth"]):
        potential_coins = []
        for coin, data in crypto_db.items():
            if data["price_trend"] == "rising" and data["market_cap"] == "high":
                potential_coins.append(coin)
        if potential_coins:
            if check_keywords(query, KEYWORD_PATTERNS["sustainability"]):
                best_coin = ""
                highest_sustainability = -1
                for coin in potential_coins:
                    if crypto_db[coin]["sustainability_score"] > highest_sustainability:
                        highest_sustainability = crypto_db[coin]["sustainability_score"]
                        best_coin = coin
                if best_coin:
                    data = crypto_db[best_coin]
                    return f"Based on your interest in both growth and sustainability, I'd recommend looking into {best_coin}! 🚀\n\n" + \
                           f"Here's why:\n" + \
                           f"• Current Price: ${data['current_price']:,.2f}\n" + \
                           f"• 24h Change: {data['price_change_24h']:+.2f}%\n" + \
                           f"• Description: {data['description']}\n" + \
                           f"• Use Case: {data['use_case']}\n" + \
                           f"• Sustainability Score: {data['sustainability_score']*10}/10\n\n" + \
                           f"{DISCLAIMER}"
                else:
                    return f"I see you're interested in growth! Some promising options include {', '.join(potential_coins)}. Would you like to know more about any of these specifically? {DISCLAIMER}"
            else:
                return f"I've analyzed the market and found some promising options: {', '.join(potential_coins)}. Would you like to know more about any of these? {DISCLAIMER}"
        else:
            return "I'm currently not seeing any coins that perfectly match the criteria for both rising trend and high market cap. Would you like to explore other aspects like sustainability or energy efficiency? {DISCLAIMER}"

    # Rule 2: Sustainability
    elif check_keywords(query, KEYWORD_PATTERNS["sustainability"]):
        recommend = ""
        highest_score = -1
        for coin, data in crypto_db.items():
            if data["energy_use"] == "low" and data["sustainability_score"] > 7/10:
                if data["sustainability_score"] > highest_score:
                    highest_score = data["sustainability_score"]
                    recommend = coin
        if recommend:
            data = crypto_db[recommend]
            return f"Looking for eco-friendly options? {recommend} stands out! 🌱\n\n" + \
                   f"Here's what makes it special:\n" + \
                   f"• Current Price: ${data['current_price']:,.2f}\n" + \
                   f"• 24h Change: {data['price_change_24h']:+.2f}%\n" + \
                   f"• Description: {data['description']}\n" + \
                   f"• Sustainability Score: {data['sustainability_score']*10}/10\n" + \
                   f"• Use Case: {data['use_case']}\n\n" + \
                   f"{DISCLAIMER}"
        else:
            return "I'm currently not seeing any cryptocurrencies that meet the highest sustainability standards. Would you like to know about other aspects like market trends or energy efficiency? {DISCLAIMER}"

    # General queries about trending up / market cap / energy use
    elif check_keywords(query, KEYWORD_PATTERNS["trend"]):
        trending_coins = [coin for coin, data in crypto_db.items() if data["price_trend"] == "rising"]
        if trending_coins:
            response = f"Looking at the current trends, these cryptocurrencies are showing upward movement: {', '.join(trending_coins)}.\n\n"
            for coin in trending_coins:
                data = crypto_db[coin]
                response += f"\n{coin}:\n• Current Price: ${data['current_price']:,.2f}\n• 24h Change: {data['price_change_24h']:+.2f}%\n• Description: {data['description']}\n• Risk Level: {data['risk_level']}\n"
            return response + f"\nWould you like to know more about any of these specifically? {DISCLAIMER}"
        else:
            return "I'm not seeing any strong upward trends in my current data. Would you like to explore other aspects like sustainability or market cap? {DISCLAIMER}"
            
    elif check_keywords(query, KEYWORD_PATTERNS["market_cap"]):
        high_market_cap_coins = [coin for coin, data in crypto_db.items() if data["market_cap"] == "high"]
        if high_market_cap_coins:
            response = f"Looking at market capitalization, these are the major players: {', '.join(high_market_cap_coins)}.\n\n"
            for coin in high_market_cap_coins:
                data = crypto_db[coin]
                response += f"\n{coin}:\n• Market Cap: ${data['market_cap_usd']:,.2f}\n• Current Price: ${data['current_price']:,.2f}\n• Description: {data['description']}\n• Popularity: {data['popularity']}\n"
            return response + f"\nWould you like to know more about any of these specifically? {DISCLAIMER}"
        else:
            return "I'm not seeing any cryptocurrencies with high market cap in my current data. Would you like to explore other aspects? {DISCLAIMER}"

    elif check_keywords(query, KEYWORD_PATTERNS["energy"]):
        low_energy_coins = [coin for coin, data in crypto_db.items() if data["energy_use"] == "low"]
        if low_energy_coins:
            response = f"Looking for energy-efficient options? Here are some cryptocurrencies with lower energy consumption: {', '.join(low_energy_coins)}.\n\n"
            for coin in low_energy_coins:
                data = crypto_db[coin]
                response += f"\n{coin}:\n• Current Price: ${data['current_price']:,.2f}\n• 24h Change: {data['price_change_24h']:+.2f}%\n• Sustainability Score: {data['sustainability_score']*10}/10\n• Description: {data['description']}\n"
            return response + f"\nWould you like to know more about any of these specifically? {DISCLAIMER}"
        else:
            return "I'm not seeing any cryptocurrencies with low energy use in my current data. Would you like to explore other aspects? {DISCLAIMER}"
            
    elif check_keywords(query, KEYWORD_PATTERNS["price"]):
        prices = []
        for coin, data in crypto_db.items():
            prices.append(f"{coin}: ${data['current_price']:,.2f} ({data['price_change_24h']:+.2f}%)")
        return f"Let me break down the current prices for you:\n{', '.join(prices)}.\n\nWould you like to know more about any specific cryptocurrency? {DISCLAIMER}"

    elif check_keywords(query, KEYWORD_PATTERNS["greeting"]):
        return f"{BOT_TONE}\n\nI'm here to help you explore the crypto world! I can help you with:\n" + \
               f"• Long-term growth recommendations\n" + \
               f"• Sustainable crypto options\n" + \
               f"• Price trends\n" + \
               f"• Market cap information\n" + \
               f"• Energy usage details\n\n" + \
               f"What would you like to know about?"

    elif "help" in query:
        return f"I'm here to help you navigate the crypto world! Here's what I can do:\n\n" + \
               f"1. Investment advice (try asking about 'long-term growth' or 'what should I invest in?')\n" + \
               f"2. Sustainability information (ask about 'eco-friendly' options or 'green crypto')\n" + \
               f"3. Market trends (ask about 'trending' coins or 'what's going up?')\n" + \
               f"4. Market cap details (ask about 'biggest crypto' or 'market size')\n" + \
               f"5. Energy usage information (ask about 'energy consumption' or 'environmental impact')\n\n" + \
               f"Remember: {DISCLAIMER}"

    else:
        return "I'm not quite sure what you're asking about. I can help you with:\n" + \
               f"• Long-term growth recommendations\n" + \
               f"• Sustainable crypto options\n" + \
               f"• Price trends\n" + \
               f"• Market cap information\n" + \
               f"• Energy usage details\n\n" + \
               f"Or type 'help' for more information!"

# Main chat loop
def chat():
    print(f"{BOT_NAME}: {BOT_TONE}")
    print(f"{BOT_NAME}: Type 'exit' to quit or 'help' for available commands.")
    
    last_update = time.time()
    UPDATE_INTERVAL = 300  # Update every 5 minutes

    while True:
        # Update data periodically
        current_time = time.time()
        if current_time - last_update > UPDATE_INTERVAL:
            print(f"\n{BOT_NAME}: Updating cryptocurrency data...")
            update_crypto_db()
            last_update = current_time
            print(f"{BOT_NAME}: Data updated successfully!")

        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print(f"\n{BOT_NAME}: Goodbye! Remember to do your own research. 👋")
            break
        
        response = get_recommendation(user_input)
        print(f"\n{BOT_NAME}: {response}")

if __name__ == "__main__":
    chat() 