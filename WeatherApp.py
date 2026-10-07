import requests
from datetime import datetime
from tkinter import *

#use the geocoding api to fetch the coordinates for the entered city
def getCoords(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()

        if "results" in data:
            result = data["results"][0]
            return result["latitude"], result["longitude"]
        return None
    except requests.exceptions.RequestException as err:
        print(f"Request error: {err}")
        return None

#get 7 day forecast from open-meteo
def getDailyWeather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        #gets max and min temperature, sunrise/sunset times, max change of precipitation and max uv index
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max,uv_index_max",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        return data.get("daily", {})
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request error: {err}")
    except ValueError:
        print("Invalid JSON Response")
    return None

#get the weather forecast for 24 hours on the current day
def getHourlyWeather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        #fetch the temperature, precipitation and uv index for each hour
        "hourly": "temperature_2m,precipitation_probability,uv_index",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        return data.get("hourly", {})
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request error: {err}")
    except ValueError:
        print("Invalid JSON Response")
    return None

#get the weather right now
def getCurrentWeather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        #get current temperature, humidity, precipitation and uv index
        "current": "temperature_2m,relative_humidity_2m,precipitation_probability,apparent_temperature",
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        return data.get("current", {})
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request error: {err}")
    except ValueError:
        print("Invalid JSON Response")
    return None

# function to display the current weather
def displayCurrentWeather():
    clearFrame(frame2) #clears any previous data in the frame
    city = cityEntry.get() # fetch the inputted city
    coordinates = getCoords(city) #finds coordinates for the city
    currentFrame = Frame(frame2, relief='solid', borderwidth=1,background="ivory") #configures a new frame which stores the data
    currentFrame.pack(fill='x',pady=3)

    if coordinates:
        lat,lon = coordinates
        current = getCurrentWeather(lat,lon)


        if current:
            currentDateTime = datetime.now()
            date = currentDateTime.strftime("%A %d/%m/%Y") #current date
            time = currentDateTime.strftime("%H:%M") # current time

            #label storing date/time
            Label(
                currentFrame,
                text=f"{date} {time}",
                font=("Arial", 10, "bold"),
                background="ivory"
            ).pack(fill='x')

            #label storing weather data
            Label(
                currentFrame,
                text=f"Current Temperature: {current['temperature_2m']}°C\n"
                     f"Apparent Temperature: {current['apparent_temperature']}°C\n"
                     f"Current Humidity: {current['relative_humidity_2m']}%\n"
                     f"Precipitation %: {current['precipitation_probability']}%",
                justify="center",
                background="lightblue",
                fg="white", font=("Arial",10,"bold"),
                borderwidth=1,
                padx=10, pady=10,
                relief="solid"
            ).pack(pady=10,padx=10)
        else:
            #label if there is no data available
            Label(
                currentFrame,
                text="No weather data",
                font=('Arial',10,'bold'),
                justify="center",
                background="ivory",
                fg="red",
            ).pack(pady=10, fill='x')
    else:
        #label if an invalid city was entered
        Label(
            currentFrame,
            text="Invalid city",
            font=('Arial', 10, 'bold'),
            justify="center",
            background="ivory",
            fg="red",
        ).pack(pady=10, padx=10)

#display weather forecast for whole day
def displayHourlyWeather():
    clearFrame(frame2) #clear old data from frame
    city = cityEntry.get() #get city from input
    coordinates = getCoords(city) #get coordinates for city
    currentFrame = Frame(frame2, relief='solid', borderwidth=1, background="ivory")
    currentFrame.pack(fill='x', pady=3)

    #if city is valid
    if coordinates:
        lat,lon = coordinates
        hourly = getHourlyWeather(lat,lon)
        daily = getDailyWeather(lat,lon)

        #if data available
        if hourly:
            #get the current date and display it in day form
            dates = daily["time"][0]
            day = datetime.strptime(dates, "%Y-%m-%d").strftime("%A")

            #label storing the day
            Label(
                currentFrame,
                text=day,
                justify='center',
                font=('Arial',10,'bold'),
                background="ivory"
            ).pack(fill='x')

            #for 24 hours
            for i in range(24):
                #frame for each hour of data
                hourlyFrame = Frame(frame2, relief="solid", borderwidth=1,background="ivory")
                hourlyFrame.pack(fill="x", pady=3)

                #get the ith hour and display in 00:00 format
                date = hourly["time"][i]
                hour = datetime.strptime(date, "%Y-%m-%dT%H:%M").strftime("%H:%M")

                #frame storing the hour
                Label(
                    hourlyFrame,
                    text=hour,
                    background="ivory",
                    font=("Arial",10,"bold"),
                    justify="center"
                ).pack(fill='x')

                #Frame that stores the data for the current hour
                Label(
                    hourlyFrame,
                    text=f"Temperature: {hourly['temperature_2m'][i]}°C\n" # temperature
                         f"Precipitation %: {hourly['precipitation_probability'][i]}%\n"#precipitation probability
                         f"UV Index: {hourly['uv_index'][i]}",#uv index
                    justify="center",
                    background="lightblue",
                    fg = "white", font = ("Arial",10,"bold"),
                    borderwidth = 1,
                    padx = 10, pady = 10,
                    relief = "solid"
                    ).pack(padx=10,pady=10)
        else:
            #no data available
            Label(
                currentFrame,
                text="No weather data",
                font=('Arial', 10, 'bold'),
                justify="center",

            ).pack(pady=10, padx=10)
    else:
        #invalid city
        Label(
            currentFrame,
            text="Invalid city",
            font=('Arial', 10, 'bold'),
            justify="center",
            background="ivory",
            fg="red",
        ).pack(pady=10, padx=10)

#display 7 day weather forecast
def displayDailyWeather():
    clearFrame(frame2) #clear frame 2
    city = cityEntry.get() #get city
    coordinates = getCoords(city) # get coordinates for city
    currentFrame = Frame(frame2, relief='solid', borderwidth=1,background="ivory")
    currentFrame.pack(fill='x', pady=3)

    #valid city
    if coordinates:
        lat,lon = coordinates
        daily = getDailyWeather(lat,lon)
        #data available
        if daily:
            #7 days
            for i in range(7):
                dayFrame = Frame(frame2, relief="solid", borderwidth=1,background="ivory")
                dayFrame.pack(fill="x", pady=3)

                date = daily["time"][i]
                sunriseDate = daily["sunrise"][i]
                sunsetDate = daily["sunset"][i]
                day = datetime.strptime(date, "%Y-%m-%d").strftime("%A") #display date as its day

                #display sunrise/sunset time in 00:00 format
                sunrise = datetime.strptime(sunriseDate, "%Y-%m-%dT%H:%M").strftime("%H:%M")
                sunset = datetime.strptime(sunsetDate, "%Y-%m-%dT%H:%M").strftime("%H:%M")
                Label(
                    dayFrame,
                    text=day,
                    font=("Arial",10,"bold"),
                    justify="center",
                    background="ivory"

                ).pack(fill='x')

                #label storing the data
                Label(
                    dayFrame,
                    text=f"Max: {daily['temperature_2m_max'][i]}°C\n" #max temperature
                         f"Min: {daily['temperature_2m_min'][i]}°C\n" #min temperature
                         f"Precipitation: {daily['precipitation_probability_max'][i]}%\n" #max precipitation 
                         f"Max UV Index: {daily['uv_index_max'][i]}\n" #max uv index
                         f"Sunrise: {sunrise}\n" #sunrise time
                         f"Sunset: {sunset}", # sunset time
                    justify="center",
                    background="lightblue",
                    fg="white", font=("Arial",10,"bold"),
                    borderwidth=1,
                    padx=10, pady=10,
                    relief="solid",
                ).pack(pady=10,padx=10)
        else:
            #no available data
            Label(
                currentFrame,
                text="No weather data",
                font=('Arial', 10, 'bold'),
                justify="center"
            ).pack(pady=10, padx=10)
    else:
        #invalid city entered
        Label(
            currentFrame,
            text="Invalid city",
            font=('Arial', 10, 'bold'),
            justify="center",
            background="ivory",
            fg="red",
        ).pack(pady=10, padx=10)

#create the window
window = Tk()
window.title("Weather App")
window.geometry("350x500")

#frame storing buttons, entry field
frame1 = Frame(window, width=300, height=100,borderwidth=1,relief='solid',pady=5,padx=5,background="ivory")
frame1.place(relx=0.5, y=80,anchor='n')

#title
titleLabel = Label(window, text="Weather App", font=("Arial", 20))
titleLabel.place(relx=0.5, y=30, anchor='n')

cityLabel = Label(frame1, text="Enter a city: ",font=("Arial", 10),padx=2,pady=2)
cityLabel.grid(row=1,column=0,sticky=W+E)

#where user enters city
cityEntry = Entry(frame1)
cityEntry.grid(row=1,column=1,sticky=W+E)

#button that displays the current weather
displayCButton = Button(frame1, text="Display Current Weather", command=displayCurrentWeather, padx=2,pady=2)
displayCButton.grid(row=2,column=0,sticky=W+E)

#button that displays the weather hourly for the whole day
displayHButton = Button(frame1, text="Display Hourly Weather", command=displayHourlyWeather, padx=2,pady=2)
displayHButton.grid(row=2,column=1,sticky=W+E)

#button that displays the weather daily for a week
displayDButton = Button(frame1, text="Display 7 day Forecast", command=displayDailyWeather, padx=2,pady=2)
displayDButton.grid(row=3,column=0,sticky=W+E)

#shut down the window/gui
exitButton = Button(frame1, text="Exit", command=window.destroy, padx=2,pady=2)
exitButton.grid(row=3,column=1, sticky=W+E)

# Canvas for scrolling
canvas = Canvas(window, width=280, height=300)
canvas.place(relx=0.5, y=180, anchor='n')

# Scrollbar to navigate
scrollbar = Scrollbar(window, orient='vertical', command=canvas.yview)
scrollbar.place(x=335, y=180, height=300)

# Frame inside the canvas
frame2 = Frame(canvas)

canvas.create_window(
    (0, 0),
    window=frame2,
    anchor="nw",
    width=280
)

# Connect canvas to scrollbar
canvas.configure(yscrollcommand=scrollbar.set)

frame2.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

#clear the contents of a given frame
def clearFrame(frame):
    for widget in frame.winfo_children():
        widget.destroy()
mainloop()

