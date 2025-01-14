from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = "mongodb+srv://kuzafri:kuzafri313@conms.i2dnl.mongodb.net/?retryWrites=true&w=majority&appName=conms"
client = MongoClient(MONGO_URI)
db = client["SmartAgro"]
collection = db["sensor_data"]

@app.get("/sensor-data")
async def get_sensor_data():
    try:
        # Get the last 24 hours of data
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=24)
        
        # Query MongoDB for data
        cursor = collection.find({
            "BSON_UTC": {"$gte": start_time, "$lte": end_time}
        }).sort("BSON_UTC", 1)
        
        # Process the data for charts
        data = []
        for doc in cursor:
            data.append({
                "timestamp": doc["BSON_UTC"].isoformat(),
                "soil_moisture": doc["soil_moisture"],
                "rain_analog": doc["rain_analog"],
                "soil_pump": doc["soil_pump"],
                "rain_pump": doc["rain_pump"]
            })
        
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)