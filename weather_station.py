#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import sys
import time
import logging
import requests
import datetime
import json
from PIL import Image, ImageDraw, ImageFont

# Ścieżka do biblioteki Waveshare e-Paper
waveshare_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'waveshare_lib')
if os.path.exists(waveshare_path):
    sys.path.append(waveshare_path)

# Konfiguracja - dostosuj według potrzeb
CONFIG = {
    # Klucz API AccuWeather - uzyskaj na https://developer.accuweather.com/
    'api_key': 'TWÓJ_KLUCZ_API',
    
    # Kod lokalizacji (możesz użyć API AccuWeather do znalezienia kodu dla Twojej lokalizacji)
    'location_key': '275110',  # Łódź, Polska
    
    # Częstotliwość odświeżania w sekundach (3600 = 1 godzina)
    'refresh_interval': 3600,
    
    # Jednostka temperatury ('C' lub 'F')
    'temp_unit': 'C',
    
    # Ścieżka do fontów
    'font_dir': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts'),
    
    # Ścieżka do ikon
    'icon_dir': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons'),
    
    # Język (pl = polski, en = angielski)
    'language': 'pl'
}

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WeatherStation")

# Mapowanie kodów ikon AccuWeather na własne ikony
ICON_MAPPING = {
    1: 'sunny',           # Słonecznie
    2: 'partly_sunny',    # Przeważnie słonecznie
    3: 'partly_cloudy',   # Częściowe zachmurzenie
    4: 'partly_cloudy',   # Zachmurzenie zmienne
    5: 'partly_cloudy',   # Zachmurzenie
    6: 'cloudy',          # Pochmurno
    7: 'cloudy',          # Zachmurzenie
    8: 'cloudy',          # Pochmurno
    11: 'fog',            # Mgła
    12: 'rain',           # Przelotne opady
    13: 'rain',           # Przelotne opady
    14: 'rain',           # Częściowo słonecznie, przelotne opady
    15: 'thunderstorm',   # Burza
    16: 'thunderstorm',   # Częściowo słonecznie, burza
    17: 'thunderstorm',   # Częściowo słonecznie, burza
    18: 'rain',           # Deszcz
    19: 'snow',           # Śnieg
    20: 'snow',           # Częściowo słonecznie, śnieg
    21: 'snow',           # Częściowo słonecznie, śnieg
    22: 'snow',           # Śnieg
    23: 'snow',           # Śnieg
    24: 'ice',            # Lód
    25: 'sleet',          # Deszcz ze śniegiem
    26: 'rain',           # Marznący deszcz
    29: 'sleet',          # Deszcz ze śniegiem
    30: 'hot',            # Gorąco
    31: 'cold',           # Zimno
    32: 'windy',          # Wietrznie
    33: 'clear',          # Pogodnie (noc)
    34: 'partly_clear',   # Przeważnie pogodnie (noc)
    35: 'partly_cloudy',  # Częściowe zachmurzenie (noc)
    36: 'partly_cloudy',  # Zachmurzenie zmienne (noc)
    37: 'partly_cloudy',  # Zachmurzenie (noc)
    38: 'cloudy',         # Pochmurno (noc)
    39: 'rain',           # Przelotne opady (noc)
    40: 'rain',           # Przelotne opady (noc)
    41: 'thunderstorm',   # Burza (noc)
    42: 'thunderstorm',   # Częściowo pogodnie, burza (noc)
    43: 'snow',           # Śnieg (noc)
    44: 'snow',           # Częściowo pogodnie, śnieg (noc)
}

# Tłumaczenia - dostosuj według potrzeb
TRANSLATIONS = {
    'pl': {
        'weather_forecast': 'Prognoza pogody',
        'today': 'Dziś',
        'tomorrow': 'Jutro',
        'updated': 'Zaktualizowano',
        'min': 'min',
        'max': 'max',
        'feels_like': 'Odczuwalna',
        'humidity': 'Wilgotność',
        'wind': 'Wiatr',
        'precipitation': 'Opady',
        'pollen': 'Pyłki',
        'low': 'Niskie',
        'moderate': 'Średnie',
        'high': 'Wysokie',
        'very_high': 'Bardzo wysokie',
        'm/s': 'm/s'
    },
    'en': {
        'weather_forecast': 'Weather Forecast',
        'today': 'Today',
        'tomorrow': 'Tomorrow',
        'updated': 'Updated',
        'min': 'min',
        'max': 'max',
        'feels_like': 'Feels like',
        'humidity': 'Humidity',
        'wind': 'Wind',
        'precipitation': 'Precipitation',
        'pollen': 'Pollen',
        'low': 'Low',
        'moderate': 'Moderate',
        'high': 'High',
        'very_high': 'Very high',
        'm/s': 'm/s'
    }
}

# Funkcja pomocnicza do pobierania tłumaczeń
def _(key):
    lang = CONFIG['language']
    if lang not in TRANSLATIONS:
        lang = 'en'
    return TRANSLATIONS[lang].get(key, key)

class WeatherAPI:
    """Klasa do komunikacji z API AccuWeather"""
    
    def __init__(self, api_key, location_key):
        self.api_key = api_key
        self.location_key = location_key
        self.base_url = "http://dataservice.accuweather.com"
        
    def get_current_conditions(self):
        """Pobiera aktualne warunki pogodowe"""
        try:
            url = f"{self.base_url}/currentconditions/v1/{self.location_key}"
            params = {
                "apikey": self.api_key,
                "language": CONFIG['language'],
                "details": "true"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0:
                return data[0]
            return None
        except Exception as e:
            logger.error(f"Błąd podczas pobierania aktualnych warunków: {e}")
            return None
    
    def get_daily_forecast(self, days=5):
        """Pobiera prognozę na kilka dni"""
        try:
            url = f"{self.base_url}/forecasts/v1/daily/{days}day/{self.location_key}"
            params = {
                "apikey": self.api_key,
                "language": CONFIG['language'],
                "details": "true",
                "metric": CONFIG['temp_unit'] == 'C'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Błąd podczas pobierania prognozy dziennej: {e}")
            return None
            
    def get_pollen_forecast(self):
        """Pobiera prognozę dotyczącą pyłków roślin (jeśli dostępna)"""
        try:
            url = f"{self.base_url}/indices/v1/daily/1day/{self.location_key}/groups/65"
            params = {
                "apikey": self.api_key,
                "language": CONFIG['language'],
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Błąd podczas pobierania prognozy pyłków: {e}")
            return None


class EInkDisplay:
    """Klasa do wyświetlania na e-ink"""
    
    def __init__(self):
        # Spróbuj zaimportować bibliotekę Waveshare dla twojego modelu
        # Dostosuj do swojego modelu e-ink wyświetlacza
        try:
            # Dla Waveshare 2.13" V2 (250x122 piksele)
            from waveshare_epd import epd2in13_V2
            self.epd = epd2in13_V2.EPD()
            self.width = self.epd.height  # Obrócony wyświetlacz
            self.height = self.epd.width
        except ImportError:
            logger.error("Nie można zaimportować biblioteki Waveshare. Sprawdź instalację.")
            raise ImportError("Brak biblioteki dla wyświetlacza e-ink")
        
        # Inicjalizacja fontów
        self.fonts = {}
        try:
            self.fonts = {
                'small': ImageFont.truetype(os.path.join(CONFIG['font_dir'], 'DejaVuSans.ttf'), 10),
                'medium': ImageFont.truetype(os.path.join(CONFIG['font_dir'], 'DejaVuSans.ttf'), 16),
                'large': ImageFont.truetype(os.path.join(CONFIG['font_dir'], 'DejaVuSans-Bold.ttf'), 24),
                'huge': ImageFont.truetype(os.path.join(CONFIG['font_dir'], 'DejaVuSans-Bold.ttf'), 40)
            }
        except Exception as e:
            logger.error(f"Błąd ładowania czcionek: {e}. Używam domyślnych.")
            self.fonts = {
                'small': ImageFont.load_default(),
                'medium': ImageFont.load_default(),
                'large': ImageFont.load_default(),
                'huge': ImageFont.load_default()
            }
    
    def init(self):
        """Inicjalizacja wyświetlacza"""
        self.epd.init()
        self.epd.Clear()
    
    def close(self):
        """Uśpienie wyświetlacza"""
        self.epd.sleep()
    
    def get_icon(self, icon_code):
        """Pobiera ikonę na podstawie kodu AccuWeather"""
        icon_name = ICON_MAPPING.get(icon_code, 'unknown')
        icon_path = os.path.join(CONFIG['icon_dir'], f"{icon_name}.bmp")
        
        if os.path.exists(icon_path):
            return Image.open(icon_path)
        else:
            logger.warning(f"Brak ikony dla kodu {icon_code} ({icon_name}.bmp)")
            # Zwracamy pustą ikonę o wymiarach 64x64
            return Image.new('1', (64, 64), 255)
    
    def create_weather_image(self, current_weather, forecast, pollen_data):
        """Tworzy obraz z danymi pogodowymi"""
        image = Image.new('1', (self.width, self.height), 255)  # 255: biały
        draw = ImageDraw.Draw(image)
        
        # Nagłówek
        draw.text((2, 2), _('weather_forecast'), font=self.fonts['medium'], fill=0)
        
        # Aktualna data i czas
        now = datetime.datetime.now()
        date_str = now.strftime("%d.%m.%Y %H:%M")
        draw.text((self.width - 2, 2), date_str, font=self.fonts['small'], fill=0, anchor="ra")
        
        # Rysowanie linii poziomej
        draw.line([(0, 20), (self.width, 20)], fill=0, width=1)
        
        if current_weather:
            # Aktualna temperatura i ikona
            temp = current_weather['Temperature']['Metric']['Value']
            icon_code = current_weather['WeatherIcon']
            feels_like = current_weather['RealFeelTemperature']['Metric']['Value']
            humidity = current_weather['RelativeHumidity']
            
            # Ikona pogody
            icon = self.get_icon(icon_code)
            icon_resized = icon.resize((64, 64), Image.LANCZOS)
            image.paste(icon_resized, (10, 25))
            
            # Temperatura
            draw.text((90, 30), f"{int(temp)}°{CONFIG['temp_unit']}", font=self.fonts['huge'], fill=0)
            draw.text((90, 75), f"{_('feels_like')}: {int(feels_like)}°", font=self.fonts['small'], fill=0)
            
            # Wilgotność
            draw.text((180, 30), f"{_('humidity')}\n{humidity}%", font=self.fonts['medium'], fill=0)
            
            # Prawdopodobieństwo opadów
            if 'PrecipitationProbability' in current_weather:
                precip = current_weather['PrecipitationProbability']
                draw.text((180, 65), f"{_('precipitation')}\n{precip}%", font=self.fonts['medium'], fill=0)
        
        # Prognoza na 5 dni
        if forecast and 'DailyForecasts' in forecast:
            forecasts = forecast['DailyForecasts']
            start_y = 100
            
            # Rysowanie linii poziomej nad prognozą
            draw.line([(0, start_y - 5), (self.width, start_y - 5)], fill=0, width=1)
            
            # Nagłówek prognozy
            day_width = self.width // min(5, len(forecasts))
            
            for i, day_forecast in enumerate(forecasts[:5]):
                date = datetime.datetime.strptime(day_forecast['Date'], "%Y-%m-%dT%H:%M:%S%z").date()
                day_name = _('today') if date == now.date() else (
                    _('tomorrow') if date == (now.date() + datetime.timedelta(days=1)) else 
                    date.strftime("%a")
                )
                
                x = i * day_width
                
                # Dzień tygodnia
                draw.text((x + day_width//2, start_y), day_name, font=self.fonts['small'], fill=0, anchor="ma")
                
                # Ikona
                icon_code = day_forecast['Day']['Icon']
                icon = self.get_icon(icon_code)
                icon_small = icon.resize((24, 24), Image.LANCZOS)
                image.paste(icon_small, (x + (day_width - 24) // 2, start_y + 15))
                
                # Temperatury min/max
                min_temp = int(day_forecast['Temperature']['Minimum']['Value'])
                max_temp = int(day_forecast['Temperature']['Maximum']['Value'])
                
                draw.text((x + day_width//2, start_y + 45), 
                          f"{min_temp}°/{max_temp}°", 
                          font=self.fonts['medium'], fill=0, anchor="ma")
                
                # Prawdopodobieństwo opadów
                if 'Day' in day_forecast and 'PrecipitationProbability' in day_forecast['Day']:
                    precip = day_forecast['Day']['PrecipitationProbability']
                    draw.text((x + day_width//2, start_y + 65), 
                              f"{precip}%", 
                              font=self.fonts['small'], fill=0, anchor="ma")
        
        # Informacje o pyłkach (jeśli dostępne)
        if pollen_data and len(pollen_data) > 0:
            pollen_level = pollen_data[0]['Category']
            pollen_text = f"{_('pollen')}: {pollen_level}"
            draw.text((self.width - 5, self.height - 5), pollen_text, font=self.fonts['small'], fill=0, anchor="rb")
        
        # Informacja o aktualizacji
        updated_text = f"{_('updated')}: {date_str}"
        draw.text((5, self.height - 5), updated_text, font=self.fonts['small'], fill=0, anchor="lb")
        
        return image
    
    def display_weather(self, current_weather, forecast, pollen_data):
        """Wyświetla dane pogodowe na e-ink"""
        image = self.create_weather_image(current_weather, forecast, pollen_data)
        
        # Obrót obrazu, jeśli potrzebny (zależnie od orientacji wyświetlacza)
        rotated_image = image.rotate(90, expand=True)
        
        # Wyświetlenie
        self.epd.display(self.epd.getbuffer(rotated_image))


def setup_directories():
    """Tworzy niezbędne katalogi, jeśli nie istnieją"""
    os.makedirs(CONFIG['font_dir'], exist_ok=True)
    os.makedirs(CONFIG['icon_dir'], exist_ok=True)


def main():
    """Główna funkcja programu"""
    logger.info("Uruchamianie stacji pogodowej na e-ink...")
    
    # Przygotowanie katalogów
    setup_directories()
    
    # Inicjalizacja API pogodowego
    weather_api = WeatherAPI(CONFIG['api_key'], CONFIG['location_key'])
    
    # Inicjalizacja wyświetlacza
    try:
        display = EInkDisplay()
        display.init()
        
        while True:
            try:
                # Pobieranie danych pogodowych
                logger.info("Pobieranie aktualnych warunków...")
                current = weather_api.get_current_conditions()
                
                logger.info("Pobieranie prognozy na 5 dni...")
                forecast = weather_api.get_daily_forecast(5)
                
                logger.info("Pobieranie danych o pyłkach...")
                pollen = weather_api.get_pollen_forecast()
                
                # Wyświetlanie danych
                if current or forecast:
                    logger.info("Aktualizacja wyświetlacza...")
                    display.display_weather(current, forecast, pollen)
                else:
                    logger.error("Nie udało się pobrać danych pogodowych.")
                
                # Oczekiwanie na kolejne odświeżenie
                logger.info(f"Oczekiwanie {CONFIG['refresh_interval']} sekund do następnej aktualizacji...")
                time.sleep(CONFIG['refresh_interval'])
            
            except KeyboardInterrupt:
                logger.info("Przerwano przez użytkownika.")
                break
            except Exception as e:
                logger.error(f"Błąd podczas aktualizacji pogody: {e}")
                # Oczekiwanie krótszego czasu przed ponowną próbą
                time.sleep(60)
        
        # Zamknięcie wyświetlacza
        display.close()
        
    except Exception as e:
        logger.error(f"Błąd krytyczny: {e}")
        return 1
    
    logger.info("Program zakończony.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
