import json
import logging
import random
import azure.functions as func
import pyodbc
import statistics
# Define your database connection details
connection_string = (
    "Driver=ODBC Driver 18 for SQL Server;"
    "Server=tcp:ml19asaaserver.database.windows.net,1433;"
    "Database=ml19asaaDBN;"
    "Uid=azure;"
    "Pwd=Ali12345;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

def insert_sensor_data(cursor, sensor_id, temperature, wind_speed, humidity, co2_level):
    cursor.execute("""
        INSERT INTO SensorNetwork 
        (SensorId,Temperature, WindSpeed, Humidity, CO2LEVEL) 
        VALUES (?, ?, ?, ?, ?)
    """,sensor_id, temperature, wind_speed, humidity, co2_level)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="generate_data")
def generate_data(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    num_sensors = 20
    sensor_data_list = []

    try:
        # Establish a connection to the database
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            for _ in range(num_sensors):
                sensor_id = random.randint(1, 20)
                temperature = random.randint(8, 15)
                wind_speed = random.randint(15, 25)
                humidity = random.randint(40, 70)
                co2_level = random.randint(500, 1500)

                sensor_data = {
                    "sensor_id": sensor_id,
                    "temperature": temperature,
                    "wind_speed": wind_speed,
                    "humidity": humidity,
                    "co2_level": co2_level,
                }

                sensor_data_list.append(sensor_data)

                # Insert data into the SQL database using PyODBC
                insert_sensor_data(cursor, sensor_id, temperature, wind_speed, humidity, co2_level)

            # Commit the changes to the database
            conn.commit()

    except Exception as e:
        # Handle exceptions
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)

    return func.HttpResponse(
        json.dumps(sensor_data_list),
        mimetype="application/json",
        status_code=200
    )



@app.route(route="analysisData", auth_level=func.AuthLevel.ANONYMOUS)
def analysisData(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Establish a connection to the database
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            # Retrieve data from the SQL database
            cursor.execute("SELECT SensorID, Temperature, WindSpeed, Humidity, CO2LEVEL FROM SensorNetwork ORDER BY SensorID")
            rows = cursor.fetchall()

            # Calculate statistics
            sensor_statistics = {}
            for row in rows:
                sensor_id, temperature, wind_speed, humidity, co2_level = row
                temperature_values = [temperature]  
                ws_values = [wind_speed]
                humidity_values = [humidity]
                co2_values = [co2_level]

                
                stats = {
                    "min_temperature": min(temperature_values),
                    "max_temperature": max(temperature_values),
                    "average_temperature": statistics.mean(temperature_values),
                    "min_wind_speed": min(ws_values),
                    "max_wind_speed": max(ws_values),
                    "average_wind_speed": statistics.mean(ws_values),
                    "min_humidity": min(humidity_values),
                    "max_humidity": max(humidity_values),
                    "average_humidity": statistics.mean(humidity_values),
                    "min_co2_level": min(co2_values),
                    "max_co2_level": max(co2_values),
                    "average_co2_level": statistics.mean(co2_values),

                }

              
                sensor_statistics[sensor_id] = stats

            # Output the calculated statistics
            return func.HttpResponse(f"Sensor Statistics: {sensor_statistics}", status_code=200)

    except Exception as e:
        # Handle exceptions
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)


    