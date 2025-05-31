# AI-Powered Smart Agriculture System

This project implements an AI-powered smart agriculture system using cloud computing and satellite imagery to optimize resource usage in farming. The system helps reduce pesticide and water wastage while promoting sustainable farming practices.

## Features

- Interactive web interface with Streamlit
- Real-time satellite imagery analysis for crop health monitoring
- Weather monitoring and forecasting with OpenWeatherMap integration
- Soil moisture prediction and water usage optimization
- Pesticide usage recommendations based on crop health
- AI-powered agricultural agent for automated monitoring
- Interactive chatbot for field analysis and insights
- Historical data analysis and trend visualization
- Community insights and local farming tips
- Field boundary management and mapping

## Prerequisites

- Python 3.8 or higher
- Google Earth Engine account (free tier)
- OpenWeatherMap API key (free tier)
- Basic understanding of agriculture and farming practices

## Detailed Setup Guide

This guide will walk you through setting up the project from scratch, including all necessary accounts, API keys, and code setup.

### 1. System Requirements

- Operating System: Windows 10/11, macOS, or Linux
- Python 3.8 or higher
- Git
- Text editor (VS Code recommended)
- Web browser (Chrome or Firefox recommended)

### 2. Initial Setup

1. **Install Python**
   ```bash
   # Check Python version
   python --version  # Should be 3.8 or higher
   
   # If Python is not installed, download from https://www.python.org/downloads/
   ```

2. **Install Git**
   ```bash
   # Check Git version
   git --version
   
   # If Git is not installed:
   # Windows: Download from https://git-scm.com/download/win
   # macOS: brew install git
   # Linux: sudo apt-get install git
   ```

3. **Clone the Repository**
   ```bash
   # Create a directory for the project
   mkdir smart-agriculture
   cd smart-agriculture
   
   # Clone the repository
   git clone https://github.com/yourusername/smart-agriculture.git .
   ```

### 3. Virtual Environment Setup

1. **Create and Activate Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # Verify activation (should show path to venv)
   which python  # macOS/Linux
   where python  # Windows
   ```

2. **Install Dependencies**
   ```bash
   # Upgrade pip
   python -m pip install --upgrade pip
   
   # Install requirements
   pip install -r requirements.txt
   
   # Verify installations
   pip list
   ```

### 4. API Setup

1. **Google Earth Engine Setup**
   ```bash
   # Install Earth Engine Python API
   pip install earthengine-api
   
   # Authenticate Earth Engine
   earthengine authenticate
   
   # Follow the browser prompts to sign in and authorize
   ```

2. **OpenWeatherMap Setup**
   - Go to https://openweathermap.org/api
   - Sign up for a free account
   - Navigate to "My API Keys"
   - Copy your API key
   - Note: New API keys may take a few hours to activate

### 5. Environment Configuration

1. **Create Environment File**
   ```bash
   # Create .env file in project root
   touch .env  # macOS/Linux
   # OR
   echo. > .env  # Windows
   ```

2. **Add Environment Variables**
   ```bash
   # Open .env in your text editor and add:
   EARTH_ENGINE_CREDENTIALS=path/to/your/credentials.json
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

### 6. Project Structure Verification

1. **Verify Directory Structure**
   ```bash
   # Should show all required directories
   ls -R  # macOS/Linux
   # OR
   dir /s  # Windows
   
   # Expected structure:
   smart-agriculture/
   ├── src/
   │   ├── satellite/
   │   ├── ml/
   │   ├── agent/
   │   ├── utils/
   │   └── data/
   ├── notebooks/
   ├── models/
   ├── config/
   ├── app.py
   ├── requirements.txt
   └── .env
   ```

### 7. Testing the Setup

1. **Test Earth Engine Connection**
   ```python
   # Create a test file: test_ee.py
   import ee
   
   try:
       ee.Initialize()
       print("Earth Engine initialized successfully!")
   except Exception as e:
       print(f"Error initializing Earth Engine: {str(e)}")
   ```

2. **Test OpenWeatherMap Connection**
   ```python
   # Create a test file: test_weather.py
   import os
   import requests
   from dotenv import load_dotenv
   
   load_dotenv()
   
   def test_weather_api():
       api_key = os.getenv('OPENWEATHER_API_KEY')
       if not api_key:
           print("OpenWeather API key not found in .env file")
           return
           
       url = f"https://api.openweathermap.org/data/2.5/weather"
       params = {
           'lat': 38.5449,
           'lon': -121.7421,
           'appid': api_key,
           'units': 'metric'
       }
       
       try:
           response = requests.get(url, params=params)
           response.raise_for_status()
           print("OpenWeather API connection successful!")
           print(f"Current temperature: {response.json()['main']['temp']}°C")
       except Exception as e:
           print(f"Error connecting to OpenWeather API: {str(e)}")
   
   if __name__ == "__main__":
       test_weather_api()
   ```

3. **Run the Tests**
   ```bash
   # Make sure virtual environment is activated
   python test_ee.py
   python test_weather.py
   ```

### 8. Running the Application

1. **Start the Streamlit App**
   ```bash
   # Make sure virtual environment is activated
   streamlit run app.py
   ```

2. **Access the Web Interface**
   - Open your web browser
   - Go to http://localhost:8501
   - You should see the Smart Agriculture System interface

### 9. Troubleshooting Common Issues

1. **Earth Engine Authentication Issues**
   ```bash
   # Clear Earth Engine credentials
   earthengine authenticate --clear
   # Then re-authenticate
   earthengine authenticate
   ```

2. **OpenWeather API Issues**
   - Verify API key in .env file
   - Check if API key is activated (may take a few hours)
   - Test API key directly in browser:
     ```
     https://api.openweathermap.org/data/2.5/weather?lat=38.5449&lon=-121.7421&appid=YOUR_API_KEY&units=metric
     ```

3. **Streamlit Issues**
   ```bash
   # Clear Streamlit cache
   streamlit cache clear
   
   # Check Streamlit version
   streamlit --version
   
   # Update Streamlit if needed
   pip install --upgrade streamlit
   ```

4. **Python Package Issues**
   ```bash
   # Recreate virtual environment if needed
   deactivate  # Exit current venv
   rm -rf venv  # Delete old venv (macOS/Linux)
   # OR
   rmdir /s /q venv  # Windows
   
   # Create new venv and install dependencies
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # OR
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

### 10. Next Steps

After successful setup:
1. Explore the Field Analysis tab
2. Try the weather report feature
3. Test the chatbot with field coordinates
4. Add fields to the agent monitoring system
5. Review historical data analysis

For any issues or questions:
- Check the troubleshooting guide above
- Review the project's issue tracker
- Submit a new issue if needed

## Project Structure

- `src/`
  - `satellite/` - Satellite imagery processing and analysis
  - `ml/` - Machine learning models for predictions
  - `agent/` - AI agent for automated monitoring
  - `utils/` - Utility functions and helpers
  - `data/` - Data processing and management
- `notebooks/` - Jupyter notebooks for analysis and visualization
- `models/` - Saved ML models
- `config/` - Configuration files
- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies

## Usage

1. Activate the virtual environment
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. Access the web interface at http://localhost:8501

### Key Features Usage

1. **Field Analysis**
   - Search for locations or input coordinates
   - Draw field boundaries
   - Get real-time weather data
   - Analyze crop health
   - View resource optimization recommendations

2. **Agent Management**
   - Add fields for automated monitoring
   - Schedule regular analysis
   - View automated insights and alerts

3. **Chatbot Assistant**
   - Ask questions about field conditions
   - Request analysis reports
   - Get recommendations for specific fields

4. **Historical Data**
   - View trends in crop health
   - Analyze resource usage over time
   - Track field performance

## Free Resources Used

- Google Earth Engine (free tier)
- OpenWeatherMap API (free tier)
- Sentinel-2 satellite imagery (free)
- Open-source machine learning libraries
- Public agricultural datasets

## Contributing

Feel free to submit issues and enhancement requests! When contributing, please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Earth Engine team for satellite imagery
- OpenWeatherMap for weather data
- Streamlit for the web interface framework
- All open-source libraries used in this project 