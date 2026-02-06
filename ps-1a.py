import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import google.generativeai as genai
from typing import Dict, List, Any
import os

# Configure page
st.set_page_config(
    page_title="AI Trip Planner Agent",
    page_icon="✈️",
    layout="wide"
)


# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCox0TNVXJmV3gMfNPgMzItw1qzuFeaQr4")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "6f67e9df796e5a8336f9f50fc19d872b")

class TripPlannerAgent:
    """LLM-powered trip planning agent using MCP architecture"""
    
    def __init__(self, gemini_api_key: str, weather_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.weather_api_key = weather_api_key
        if gemini_api_key:
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def get_weather_data(self, city: str, country_code: str = "") -> Dict:
        """Fetch current weather and forecast using OpenWeather API"""
        try:
            # Get coordinates first
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{country_code}&limit=1&appid={self.weather_api_key}"
            geo_response = requests.get(geo_url)
            
            if geo_response.status_code != 200 or not geo_response.json():
                return {"error": "City not found"}
            
            geo_data = geo_response.json()[0]
            lat, lon = geo_data['lat'], geo_data['lon']
            
            # Get current weather
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
            weather_response = requests.get(weather_url)
            
            # Get forecast
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
            forecast_response = requests.get(forecast_url)
            
            if weather_response.status_code == 200 and forecast_response.status_code == 200:
                return {
                    "current": weather_response.json(),
                    "forecast": forecast_response.json(),
                    "coordinates": {"lat": lat, "lon": lon}
                }
            else:
                return {"error": "Failed to fetch weather data"}
        except Exception as e:
            return {"error": f"Weather API error: {str(e)}"}
    
    def get_places_data(self, city: str, place_type: str = "tourist_attraction") -> List[Dict]:
        """Simulate getting places data (would use Google Places API in production)"""
        # Extended database with more cities
        places_db = {
            "Tokyo": [
                {"name": "Senso-ji Temple", "type": "temple", "rating": 4.5},
                {"name": "Tokyo Skytree", "type": "landmark", "rating": 4.7},
                {"name": "Meiji Shrine", "type": "shrine", "rating": 4.6},
                {"name": "Shibuya Crossing", "type": "landmark", "rating": 4.4},
                {"name": "Tsukiji Outer Market", "type": "market", "rating": 4.5}
            ],
            "Udaipur": [
                {"name": "City Palace", "type": "palace", "rating": 4.7},
                {"name": "Lake Pichola", "type": "lake", "rating": 4.6},
                {"name": "Jag Mandir", "type": "palace", "rating": 4.5},
                {"name": "Saheliyon Ki Bari", "type": "garden", "rating": 4.4},
                {"name": "Bagore Ki Haveli", "type": "museum", "rating": 4.3}
            ],
            "Paris": [
                {"name": "Eiffel Tower", "type": "landmark", "rating": 4.7},
                {"name": "Louvre Museum", "type": "museum", "rating": 4.8},
                {"name": "Notre-Dame Cathedral", "type": "church", "rating": 4.6},
                {"name": "Arc de Triomphe", "type": "monument", "rating": 4.5},
                {"name": "Sacré-Cœur", "type": "church", "rating": 4.6}
            ],
            "London": [
                {"name": "Tower of London", "type": "castle", "rating": 4.6},
                {"name": "British Museum", "type": "museum", "rating": 4.7},
                {"name": "Buckingham Palace", "type": "palace", "rating": 4.5},
                {"name": "London Eye", "type": "landmark", "rating": 4.4},
                {"name": "Westminster Abbey", "type": "church", "rating": 4.7}
            ],
            "New York": [
                {"name": "Statue of Liberty", "type": "landmark", "rating": 4.7},
                {"name": "Central Park", "type": "park", "rating": 4.8},
                {"name": "Empire State Building", "type": "landmark", "rating": 4.6},
                {"name": "Times Square", "type": "landmark", "rating": 4.5},
                {"name": "Metropolitan Museum", "type": "museum", "rating": 4.8}
            ],
            "Dubai": [
                {"name": "Burj Khalifa", "type": "landmark", "rating": 4.8},
                {"name": "Dubai Mall", "type": "shopping", "rating": 4.7},
                {"name": "Palm Jumeirah", "type": "landmark", "rating": 4.6},
                {"name": "Dubai Marina", "type": "waterfront", "rating": 4.5},
                {"name": "Gold Souk", "type": "market", "rating": 4.4}
            ],
            "Singapore": [
                {"name": "Marina Bay Sands", "type": "landmark", "rating": 4.7},
                {"name": "Gardens by the Bay", "type": "garden", "rating": 4.8},
                {"name": "Sentosa Island", "type": "island", "rating": 4.6},
                {"name": "Merlion Park", "type": "park", "rating": 4.4},
                {"name": "Chinatown", "type": "neighborhood", "rating": 4.5}
            ],
            "Bangkok": [
                {"name": "Grand Palace", "type": "palace", "rating": 4.7},
                {"name": "Wat Pho", "type": "temple", "rating": 4.6},
                {"name": "Wat Arun", "type": "temple", "rating": 4.6},
                {"name": "Chatuchak Market", "type": "market", "rating": 4.5},
                {"name": "Khao San Road", "type": "street", "rating": 4.3}
            ],
            "Rome": [
                {"name": "Colosseum", "type": "landmark", "rating": 4.8},
                {"name": "Vatican Museums", "type": "museum", "rating": 4.7},
                {"name": "Trevi Fountain", "type": "fountain", "rating": 4.6},
                {"name": "Pantheon", "type": "monument", "rating": 4.7},
                {"name": "Spanish Steps", "type": "landmark", "rating": 4.5}
            ],
            "Barcelona": [
                {"name": "Sagrada Familia", "type": "church", "rating": 4.8},
                {"name": "Park Güell", "type": "park", "rating": 4.7},
                {"name": "La Rambla", "type": "street", "rating": 4.5},
                {"name": "Casa Batlló", "type": "architecture", "rating": 4.6},
                {"name": "Gothic Quarter", "type": "neighborhood", "rating": 4.6}
            ]
        }
        
        # If city is in database, return those places
        if city in places_db:
            return places_db[city]
        
        # For custom cities not in database, return generic attractions
        # In production, this would call Google Places API
        return [
            {"name": f"{city} Main Square", "type": "landmark", "rating": 4.5},
            {"name": f"{city} Museum", "type": "museum", "rating": 4.4},
            {"name": f"{city} Old Town", "type": "neighborhood", "rating": 4.6},
            {"name": f"{city} Cathedral", "type": "church", "rating": 4.5},
            {"name": f"{city} Market", "type": "market", "rating": 4.3}
        ]
    
    def get_flight_options(self, destination: str, travel_month: str) -> List[Dict]:
        """Simulate flight search (would use Skyscanner API in production)"""
        # Mock flight data
        flights = [
            {
                "airline": "Air India",
                "departure": "DEL",
                "arrival": destination[:3].upper(),
                "duration": "2h 30m" if destination == "Udaipur" else "6h 45m",
                "price": "₹8,500" if destination == "Udaipur" else "₹18,500",
                "stops": "Non-stop"
            },
            {
                "airline": "IndiGo",
                "departure": "BLR",
                "arrival": destination[:3].upper(),
                "duration": "2h 15m" if destination == "Udaipur" else "7h 20m",
                "price": "₹7,200" if destination == "Udaipur" else "₹22,000",
                "stops": "Non-stop" if destination == "Udaipur" else "1 stop"
            }
        ]
        return flights
    
    def get_hotel_options(self, city: str) -> List[Dict]:
        """Simulate hotel search (would use hotel booking API in production)"""
        # Mock hotel data
        hotels = [
            {
                "name": f"{city} Grand Hotel",
                "rating": 4.5,
                "price_per_night": "₹5,500" if city == "Udaipur" else "₹8,500",
                "amenities": ["WiFi", "Breakfast", "Pool", "Spa"]
            },
            {
                "name": f"Budget Inn {city}",
                "rating": 4.0,
                "price_per_night": "₹2,800" if city == "Udaipur" else "₹4,200",
                "amenities": ["WiFi", "Breakfast"]
            },
            {
                "name": f"Luxury Palace {city}",
                "rating": 5.0,
                "price_per_night": "₹12,000" if city == "Udaipur" else "₹18,000",
                "amenities": ["WiFi", "Breakfast", "Pool", "Spa", "Restaurant", "Gym"]
            }
        ]
        return hotels
    
    def generate_city_description(self, city: str, duration: int) -> str:
        """Generate cultural and historical description using Gemini"""
        if not self.model:
            # Expanded fallback descriptions for more cities
            descriptions = {
                "Tokyo": "Tokyo, Japan's bustling capital, seamlessly blends ancient tradition with cutting-edge modernity. Home to historic temples like Senso-ji and Meiji Shrine alongside futuristic skyscrapers, Tokyo offers a unique cultural experience. The city's rich heritage spans from samurai history to contemporary pop culture, making it a fascinating destination where centuries-old customs coexist with technological innovation. From traditional tea ceremonies to world-class cuisine and vibrant neighborhoods like Shibuya and Harajuku, Tokyo captivates visitors with its dynamic energy and cultural depth.",
                "Udaipur": "Udaipur, known as the 'City of Lakes' and the 'Venice of the East,' is a jewel of Rajasthan's royal heritage. Founded in 1559 by Maharana Udai Singh II, this enchanting city showcases magnificent palaces, pristine lakes, and stunning Rajput architecture. The City Palace complex stands as a testament to the valor and artistic sensibilities of the Mewar dynasty. With its romantic lakeside setting, ornate havelis, and vibrant bazaars, Udaipur preserves centuries of Indian culture and craftsmanship, offering visitors a glimpse into the opulent lifestyle of Rajasthan's maharajas.",
                "Paris": "Paris, the 'City of Light,' stands as a timeless symbol of art, culture, and romance. With its iconic landmarks like the Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral, Paris showcases centuries of architectural brilliance and artistic achievement. The city's charming boulevards, world-class museums, and exquisite cuisine have made it a cultural epicenter. From the bohemian streets of Montmartre to the elegant Champs-Élysées, Paris offers a perfect blend of historical grandeur and contemporary sophistication.",
                "London": "London, the vibrant capital of the United Kingdom, is a city where royal heritage meets modern multiculturalism. With over 2000 years of history, London boasts iconic landmarks like the Tower of London, Buckingham Palace, and Westminster Abbey. The city's world-renowned museums, theaters, and diverse neighborhoods reflect its status as a global cultural hub. From traditional afternoon tea to cutting-edge fashion and finance, London seamlessly combines historic traditions with contemporary innovation.",
                "New York": "New York City, the 'City that Never Sleeps,' is a dynamic metropolis that embodies the American dream. This global center of culture, finance, and entertainment features iconic landmarks like the Statue of Liberty, Empire State Building, and Central Park. The city's diverse neighborhoods, from Manhattan's skyscrapers to Brooklyn's artistic enclaves, showcase an unparalleled cultural mosaic. World-class museums, Broadway theaters, and culinary excellence make New York an essential destination for any traveler.",
                "Dubai": "Dubai, the jewel of the UAE, is a stunning fusion of traditional Arabian culture and futuristic innovation. Rising from desert sands, this city showcases architectural marvels like the Burj Khalifa and Palm Jumeirah. Dubai's luxury shopping malls, pristine beaches, and traditional souks offer contrasting experiences. The city's rapid transformation from a fishing village to a global hub exemplifies ambition and vision, making it a must-visit destination for those seeking luxury and cultural discovery.",
                "Singapore": "Singapore, the 'Lion City,' is a remarkable island nation that combines efficient urban planning with rich cultural diversity. This modern city-state features stunning architecture like Marina Bay Sands and Gardens by the Bay, while preserving its multicultural heritage in neighborhoods like Chinatown and Little India. Singapore's blend of Asian traditions, colonial history, and futuristic development creates a unique Southeast Asian experience, complemented by world-class cuisine and shopping.",
                "Rome": "Rome, the 'Eternal City,' stands as a living museum of Western civilization with over 2,500 years of history. From the ancient Colosseum and Roman Forum to the artistic treasures of the Vatican, Rome showcases the evolution of art, architecture, and culture. The city's baroque fountains, Renaissance palaces, and charming piazzas create an atmosphere where every corner tells a story. Roman cuisine, fashion, and the dolce vita lifestyle add to the city's timeless appeal."
            }
            return descriptions.get(city, f"{city} is a fascinating destination with rich cultural heritage and historical significance. This vibrant city offers unique experiences, local traditions, and memorable attractions that showcase its distinctive character. Visitors can explore historical sites, enjoy local cuisine, and immerse themselves in the authentic culture of this remarkable destination.")
        
        try:
            prompt = f"""Write a concise 1-paragraph description (100-120 words) about {city}'s cultural and historic significance. 
            Focus on what makes it unique, its historical importance, architectural heritage, and cultural attractions. 
            Make it engaging and informative for travelers planning a {duration}-day trip."""
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"{city} is a remarkable destination with rich cultural and historical heritage worth exploring. This city offers unique attractions, local experiences, and memorable moments for travelers."
    
    def generate_trip_plan(self, city: str, duration: int, weather_data: Dict, places: List[Dict]) -> str:
        """Generate detailed day-by-day trip itinerary using Gemini"""
        if not self.model:
            # Fallback itinerary
            plan = f"**Day-by-Day Itinerary for {city}**\n\n"
            for day in range(1, duration + 1):
                plan += f"**Day {day}:**\n"
                if day <= len(places):
                    start_idx = (day - 1) * 2
                    day_places = places[start_idx:start_idx + 2]
                    for place in day_places:
                        plan += f"- Visit {place['name']} ({place['type']})\n"
                plan += "\n"
            return plan
        
        try:
            weather_context = ""
            if "current" in weather_data and "error" not in weather_data:
                temp = weather_data["current"]["main"]["temp"]
                desc = weather_data["current"]["weather"][0]["description"]
                weather_context = f"Current weather: {temp}°C, {desc}. "
            
            places_list = ", ".join([p["name"] for p in places[:8]])
            
            prompt = f"""Create a detailed {duration}-day trip itinerary for {city}. 
            {weather_context}
            Include these attractions: {places_list}
            
            Format the response as:
            **Day 1:**
            - Morning: [activity]
            - Afternoon: [activity]
            - Evening: [activity]
            
            Make it practical, well-paced, and engaging. Include timing suggestions and brief descriptions."""
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return "Unable to generate detailed itinerary at this time."
    
    def plan_trip(self, city: str, duration: int, month: str) -> Dict[str, Any]:
        """Main trip planning function - orchestrates all components"""
        
        # Expanded country code mapping for weather API
        country_codes = {
            "Tokyo": "JP",
            "Udaipur": "IN",
            "Paris": "FR",
            "London": "GB",
            "New York": "US",
            "Dubai": "AE",
            "Singapore": "SG",
            "Bangkok": "TH",
            "Rome": "IT",
            "Barcelona": "ES",
            "Istanbul": "TR",
            "Amsterdam": "NL",
            "Prague": "CZ",
            "Vienna": "AT",
            "Sydney": "AU",
            "Bali": "ID",
            "Maldives": "MV",
            "Jaipur": "IN",
            "Mumbai": "IN",
            "Delhi": "IN"
        }
        
        # Try to get country code from mapping, or let OpenWeather auto-detect
        country_code = country_codes.get(city, "")
        
        # Gather all data
        weather_data = self.get_weather_data(city, country_code)
        places = self.get_places_data(city)
        flights = self.get_flight_options(city, month)
        hotels = self.get_hotel_options(city)
        
        # Generate LLM-powered content
        city_description = self.generate_city_description(city, duration)
        trip_plan = self.generate_trip_plan(city, duration, weather_data, places)
        
        return {
            "city_description": city_description,
            "weather": weather_data,
            "places": places,
            "flights": flights,
            "hotels": hotels,
            "trip_plan": trip_plan,
            "duration": duration,
            "month": month
        }


# Streamlit UI
def main():
    st.title("✈️ AI Trip Planner Agent")
    st.markdown("**Powered by Gemini LLM + Real-time Data APIs**")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        gemini_key = st.text_input(
            "Gemini API Key",
            value=GEMINI_API_KEY,
            type="password",
            help="Get your key from https://makersuite.google.com/app/apikey"
        )
        
        weather_key = st.text_input(
            "OpenWeather API Key",
            value=OPENWEATHER_API_KEY,
            type="password",
            help="Get your key from https://openweathermap.org/api"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info("This agent uses MCP architecture to combine LLM reasoning with real-time data APIs for intelligent trip planning.")
    
    # Main input form
    st.header("📝 Plan Your Trip")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # City selection with option for custom input
        city_options = [
            "Tokyo", "Udaipur", "Paris", "London", "New York", 
            "Dubai", "Singapore", "Bangkok", "Rome", "Barcelona",
            "Istanbul", "Amsterdam", "Prague", "Vienna", "Sydney",
            "Bali", "Maldives", "Jaipur", "Mumbai", "Delhi",
            "Custom (Enter your own)"
        ]
        
        city_selection = st.selectbox(
            "Destination City",
            city_options,
            help="Select a destination or choose 'Custom' to enter your own"
        )
        
        # If custom is selected, show text input
        if city_selection == "Custom (Enter your own)":
            city = st.text_input(
                "Enter City Name",
                placeholder="e.g., Kyoto, Venice, Santorini",
                help="Enter any city name worldwide"
            )
            if not city:
                st.warning("⚠️ Please enter a city name to continue")
        else:
            city = city_selection
    
    with col2:
        duration = st.selectbox(
            "Trip Duration",
            [2, 3, 4, 5, 6, 7],
            index=1,
            help="Number of days"
        )
    
    with col3:
        month = st.selectbox(
            "Travel Month",
            ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"],
            index=4,
            help="When do you plan to travel?"
        )
    
    # Sample prompts
    st.markdown("**Sample Prompts:**")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🗼 Plan a 3-day trip to Tokyo in May"):
            city_selection, city, duration, month = "Tokyo", "Tokyo", 3, "May"
    with col_b:
        if st.button("🏰 Plan a 2-day trip to Udaipur in May"):
            city_selection, city, duration, month = "Udaipur", "Udaipur", 2, "May"
    with col_c:
        if st.button("🗼 Plan a 4-day trip to Paris in June"):
            city_selection, city, duration, month = "Paris", "Paris", 4, "June"
    
    st.markdown("---")
    
    # Plan trip button
    if st.button("🚀 Generate Trip Plan", type="primary", use_container_width=True):
        # Validate city input
        if city_selection == "Custom (Enter your own)" and not city:
            st.error("⚠️ Please enter a city name in the 'Enter City Name' field above.")
            st.stop()
        
        if not city or city == "Custom (Enter your own)":
            st.error("⚠️ Please select or enter a valid city name.")
            st.stop()
        
        if not gemini_key or not weather_key:
            st.error("⚠️ Please provide API keys in the sidebar to continue.")
            st.info("**Note:** Demo mode available with fallback data if APIs are not configured.")
        
        # Initialize agent
        agent = TripPlannerAgent(gemini_key, weather_key)
        
        with st.spinner(f"🤖 AI Agent is planning your {duration}-day trip to {city}..."):
            # Get trip plan
            result = agent.plan_trip(city, duration, month)
            
            # Display results
            st.success(f"✅ Trip plan generated for {city}!")
            
            # 1. City Description
            st.header(f"🏙️ About {city}")
            st.write(result["city_description"])
            
            # 2. Weather Information
            st.header("🌤️ Weather Information")
            weather = result["weather"]
            
            if "error" not in weather and "current" in weather:
                col1, col2, col3, col4 = st.columns(4)
                
                current = weather["current"]
                with col1:
                    st.metric("Temperature", f"{current['main']['temp']}°C")
                with col2:
                    st.metric("Feels Like", f"{current['main']['feels_like']}°C")
                with col3:
                    st.metric("Humidity", f"{current['main']['humidity']}%")
                with col4:
                    st.metric("Condition", current['weather'][0]['main'])
                
                st.info(f"**Current Weather:** {current['weather'][0]['description'].title()}")
                
                # Forecast
                if "forecast" in weather:
                    st.subheader("5-Day Forecast")
                    forecast_data = weather["forecast"]["list"]
                    
                    forecast_cols = st.columns(5)
                    for i, col in enumerate(forecast_cols):
                        if i * 8 < len(forecast_data):
                            day_data = forecast_data[i * 8]
                            date = datetime.fromtimestamp(day_data['dt']).strftime('%b %d')
                            temp = day_data['main']['temp']
                            desc = day_data['weather'][0]['main']
                            
                            with col:
                                st.markdown(f"**{date}**")
                                st.markdown(f"{temp}°C")
                                st.markdown(f"{desc}")
            else:
                st.warning("Weather data unavailable. Please check API key.")
            
            # 3. Travel Dates
            st.header("📅 Travel Dates")
            start_date = datetime.now() + timedelta(days=30)  # Example: 30 days from now
            end_date = start_date + timedelta(days=duration - 1)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Departure:** {start_date.strftime('%B %d, %Y')}")
            with col2:
                st.info(f"**Return:** {end_date.strftime('%B %d, %Y')}")
            with col3:
                st.info(f"**Duration:** {duration} days")
            
            # 4. Flight Options
            st.header("✈️ Flight Options")
            for idx, flight in enumerate(result["flights"], 1):
                with st.expander(f"Option {idx}: {flight['airline']} - {flight['price']}", expanded=(idx==1)):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Route:** {flight['departure']} → {flight['arrival']}")
                    with col2:
                        st.write(f"**Duration:** {flight['duration']}")
                    with col3:
                        st.write(f"**Stops:** {flight['stops']}")
            
            # 5. Hotel Options
            st.header("🏨 Hotel Recommendations")
            for idx, hotel in enumerate(result["hotels"], 1):
                with st.expander(f"{hotel['name']} - {'⭐' * int(hotel['rating'])} ({hotel['rating']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Price:** {hotel['price_per_night']} per night")
                    with col2:
                        st.write(f"**Amenities:** {', '.join(hotel['amenities'])}")
            
            # 6. Trip Itinerary
            st.header("🗺️ Day-by-Day Itinerary")
            st.markdown(result["trip_plan"])
            
            # 7. Top Attractions
            st.header("🎯 Top Attractions")
            places_cols = st.columns(3)
            for idx, place in enumerate(result["places"][:6]):
                with places_cols[idx % 3]:
                    st.markdown(f"""
                    **{place['name']}**  
                    Type: {place['type'].title()}  
                    Rating: {'⭐' * int(place['rating'])} ({place['rating']})
                    """)
            
            # Download button
            st.markdown("---")
            trip_summary = f"""
TRIP PLAN: {duration}-day trip to {city} in {month}

{result['city_description']}

TRAVEL DATES:
Departure: {start_date.strftime('%B %d, %Y')}
Return: {end_date.strftime('%B %d, %Y')}

ITINERARY:
{result['trip_plan']}

FLIGHTS:
{chr(10).join([f"- {f['airline']}: {f['price']} ({f['duration']})" for f in result['flights']])}

HOTELS:
{chr(10).join([f"- {h['name']}: {h['price_per_night']}/night" for h in result['hotels']])}
"""
            st.download_button(
                label="📥 Download Trip Plan",
                data=trip_summary,
                file_name=f"trip_plan_{city}_{duration}days.txt",
                mime="text/plain"
            )


if __name__ == "__main__":
    main()