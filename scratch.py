from dotenv import load_dotenv
load_dotenv()

import weather

result = weather.get_weather("Seattle")
print(f"Result: {result}")