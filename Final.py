#!/usr/bin/env python
# coding: utf-8

# In[2]:


# # Import dependencies
# !pip install langchain
# !pip install google_genai
# !pip install langchain_experimental
# !pip install langchain_google_genai
# !pip install python-dotenv
# !pip install openai
# !pip install streamlit
# !pip install requests
# !pip install pandas


# In[2]:


import os
from dotenv import load_dotenv
import requests
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import APIChain


# Model and API Key

# In[4]:


# Load environment variables
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# In[6]:


# Set up the Google Gemini model
GEMINI_MODEL = "gemini-1.5-flash"
llm = ChatGoogleGenerativeAI(google_api_key=GEMINI_API_KEY, model=GEMINI_MODEL, temperature=0.9)


# In[8]:


# Fetch weather data
def fetch_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }
    else:
        return {"error": f"Failed to fetch weather data: {response.status_code}"}



# In[21]:


# Fetch GDP data from World Bank API
def fetch_gdp_data(country_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.CD?format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1:
            gdp_data = data[1][:5]  # Fetch the most recent 5 years
            return [{"year": gdp["date"], "gdp": gdp["value"]} for gdp in gdp_data if gdp["value"]]
        else:
            return {"error": "No GDP data available"}
    else:
        return {"error": f"Failed to fetch GDP data: {response.status_code}"}



# In[23]:


# Generate relocation insights using Gemini
def generate_relocation_insights(city, weather_summary, gdp_summary):
    prompt = f"""
    Provide detailed relocation insights for {city}:
    - Consider the following weather context: {weather_summary}.
    - Economic context: {gdp_summary}.
    - Include cultural aspects, job opportunities, and challenges for expats.
    """
    response = llm.predict(prompt)
    return response


# In[25]:


# Streamlit App
st.title("Relocation Insights Tool")
st.write("Get detailed insights about relocating to your favorite city!")


# In[27]:


def combined_relocation_info(city, country_code):
    # Fetch weather data
    weather_info = fetch_weather_data(city)
    if "error" in weather_info:
        weather_summary = weather_info["error"]
    else:
        weather_summary = (
            f"The current temperature in {city} is {weather_info['temperature']}°C "
            f"with {weather_info['description']}."
        )

    # Fetch GDP data
    gdp_info = fetch_gdp_data(country_code)
    if "error" in gdp_info:
        gdp_summary = gdp_info["error"]
    else:
        # Safely build the GDP summary
        gdp_items = [f"{item['year']}: {item['gdp']}" for item in gdp_info if 'year' in item and 'gdp' in item]
        if gdp_items:
            gdp_summary = "GDP data for recent years: " + ", ".join(gdp_items)
        else:
            gdp_summary = "No GDP data available."

    # Generate relocation insights
    relocation_insights = generate_relocation_insights(city, weather_summary, gdp_summary)

    return {
        "weather_summary": weather_summary,
        "gdp_summary": gdp_summary,
        "relocation_insights": relocation_insights
    }


# In[ ]:


# User Input
city = st.text_input("Enter the city you want to relocate to:", "Berlin")
country_code = st.text_input("Enter the country code for the city:", "DE")

if st.button("Get Insights"):
    with st.spinner("Fetching data and generating insights..."):
        results = combined_relocation_info(city, country_code)

        st.subheader("Weather Summary")
        st.write(results["weather_summary"])

        st.subheader("Economic Summary")
        st.write(results["gdp_summary"])

        st.subheader("Relocation Insights")
        st.write(results["relocation_insights"])

# Feedback Section
st.subheader("Feedback")
rating = st.slider("Rate the quality of the insights (1-5):", 1, 5)
comments = st.text_area("Additional Comments:")

if st.button("Submit Feedback"):
    st.success("Thank you for your feedback!")
    # Save feedback to a file or database if needed



# Documentation
# ### Summary of How All Components Fit Together in the App
# 

# The app provides **relocation insights** for users by integrating data from multiple sources (weather, GDP, and AI-generated insights). Below is a high-level summary of how each section contributes to the overall functionality:
# 

# 1. **Dependencies**
# 
# 	•	Libraries: The app relies on key Python libraries:
# 	•	requests: For making API calls to external services like OpenWeather and the World Bank API.
# 	•	streamlit: For building an interactive web interface.
# 	•	dotenv: For securely loading API keys from environment variables.
# 	•	langchain-google-genai: For integrating the Gemini AI model to generate insights.
# 	•	pandas: For potential data manipulation and processing (if needed).
# 	•	Purpose: These libraries ensure smooth data fetching, AI interaction, and user interface development.
# 
# 

# 2. **Environment Variables**
# 
# 	•	Environment Variables:
# 	•	OPENWEATHER_API_KEY: The API key for accessing weather data from OpenWeather.
# 	•	Google_Gemini_API_KEY: The API key for interacting with the Gemini AI model.
# 	•	How It Fits:
# 	•	These variables are stored securely in a .env file and loaded using the dotenv library.
# 	•	They are used in API calls and AI model initialization, ensuring sensitive information (like API keys) is not hardcoded in the script.

# 3. **Weather Data Fetching**
# 
# def fetch_weather_data(city):
#     ...
# 
# 	•	Purpose: Fetches real-time weather data for the selected city using the OpenWeather API.
# 	•	Integration:
# 	•	Displays the weather summary (e.g., temperature, weather conditions) in the app.
# 	•	Adds contextual information for relocation insights generated by the AI model.

# 4. **GDP Data Fetching**
# 
# def fetch_gdp_data(country_code):
#     ...
# 
# 	•	Purpose: Retrieves GDP data for the country using the World Bank API.
# 	•	Integration:
# 	•	Provides an economic context (e.g., recent GDP trends) for relocation insights.
# 	•	Displays a concise GDP summary in the app.

# 5. **AI-Generated Insights**
# 
# def generate_relocation_insights(city, weather_summary, gdp_summary):
#     ...
# 
# 	•	Purpose: Combines weather, GDP, and the city name into a prompt for the Gemini AI model to generate detailed relocation insights.
# 	•	Integration:
# 	•	The model produces insights covering cultural aspects, job opportunities, and challenges.
# 	•	Outputs are displayed in the “Relocation Insights” section of the app.

# 6. **Streamlit App Logic**
# 
# # User Input
# city = st.text_input("Enter the city you want to relocate to:", "Berlin")
# country_code = st.text_input("Enter the country code for the city:", "DE")
# ...
# 
# 	•	Streamlit Components:
# 	•	User Inputs:
# 	•	Text boxes allow users to input the city and country code.
# 	•	Buttons trigger actions (e.g., fetching insights, submitting feedback).
# 	•	Real-Time Data Fetching:
# 	•	The app fetches weather and GDP data based on user inputs.
# 	•	Displays these summaries in dedicated sections.
# 	•	AI-Generated Insights:
# 	•	Combines all data into a cohesive prompt sent to the Gemini model.
# 	•	Displays the AI’s response as detailed relocation advice.

# 7. **Feedback Collection**
# 
# st.subheader("Feedback")
# rating = st.slider("Rate the quality of the insights (1-5):", 1, 5)
# comments = st.text_area("Additional Comments:")
# ...
# 
# 	•	Purpose: Collects user feedback on the generated insights.
# 	•	Integration:
# 	•	A slider captures a quality rating.
# 	•	A text box collects additional user comments.
# 	•	Feedback can be stored or analyzed for future improvements.
# 

# 8. **Dependencies and Flow**
# 
# 	1.	Setup and Configuration:
# 	•	Dependencies are installed, and environment variables are loaded securely.
# 	•	The app initializes the Gemini model using the provided API key.
# 	2.	User Interaction:
# 	•	Users input the city and country code in the app.
# 	•	They click “Get Insights” to trigger the data fetching and AI generation.
# 	3.	Data Flow:
# 	•	Weather data (fetch_weather_data) and GDP data (fetch_gdp_data) are fetched using their respective APIs.
# 	•	The collected data is combined into a structured prompt for the Gemini AI model.
# 	4.	AI Interaction:
# 	•	The Gemini model generates detailed relocation insights using the provided data.
# 	•	Results are displayed in the app under dedicated sections.
# 	5.	Feedback:
# 	•	Users provide feedback, which can be saved for analysis or improvement.

# 9. **App Workflow**
# 
# 	1.	Initialization:
# 	•	Environment variables are loaded.
# 	•	Gemini AI model is initialized.
# 	2.	User Input:
# 	•	The user enters the city and country code.
# 	3.	Data Fetching:
# 	•	Weather and GDP data are fetched via APIs.
# 	4.	AI Insights:
# 	•	The data is processed into a prompt, and AI-generated insights are retrieved.
# 	5.	Results Display:
# 	•	Weather, economic summary, and AI-generated relocation insights are shown.
# 	6.	Feedback:
# 	•	Users rate and comment on the quality of the insights.

# ### How It All Fits Together
# 
# 	•	Interactive Interface: Streamlit provides a clean, user-friendly interface for input and display.
# 	•	Data-Driven Insights: APIs (OpenWeather and World Bank) supply real-world data to contextualize the AI model’s output.
# 	•	AI-Powered Analysis: The Gemini model enriches raw data with actionable insights tailored to the user’s input.
# 	•	Feedback Mechanism: Captures user input to improve the app’s functionality and output quality over time.
# 
# 
