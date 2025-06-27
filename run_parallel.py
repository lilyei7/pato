import subprocess
import subprocess
from time import sleep
from scrape_booking import adaptar_url_mexico

# Lista de URLs de hoteles (10 hoteles diferentes para scraping paralelo)
urls = [
    "https://www.booking.com/hotel/mx/marriott-tuxtla-gutierrez.es.html?aid=898224&label=hotel_details-SiL4Ie%401750958832&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&",
    "https://www.booking.com/hotel/mx/best-beach-apartments-cancun-plaza.es.html?aid=898224&label=hotel_details-wCPBNL%401750958868&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&",
    "https://www.booking.com/hotel/mx/gamma-cancun-centro.es.html?aid=898224&label=hotel_details-4P5Jhv%401750958928&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&",
    "https://www.booking.com/hotel/mx/bali-hai-acapulco.es.html?aid=898224&label=hotel_details-byoY0z%401750958969&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&",
    "https://www.booking.com/hotel/mx/suites-jazmin-acapulco.es.html?aid=898224&label=hotel_details-zun4v1b%401750958981&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&",
    "https://www.booking.com/hotel/mx/acapulco-malibu.es.html?aid=898224&label=hotel_details-zvSIh9e%401750958991&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&",
    "https://www.booking.com/hotel/mx/comfort-inn-puerto-vallarta.es.html?aid=898224&label=hotel_details-01CYkx6%401750959030&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&",
    "https://www.booking.com/hotel/mx/hotel-casa-blanca.es.html?aid=898224&label=hotel_details-B3r7k4%401750958745&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&",
    "https://www.booking.com/hotel/mx/ibis-guadalajara-expo.es.html?aid=898224&label=hotel_details-D6m8H3%401750958812&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&",
    "https://www.booking.com/hotel/mx/villa-vera-puerto-vallarta.es.html?aid=898224&label=hotel_details-X9f5M2%401750958856&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&"
]

urls_mexico = [adaptar_url_mexico(u) for u in urls]

processes = []
for url in urls_mexico:
    p = subprocess.Popen(["python", "scrape_booking.py", url])
    processes.append(p)
    sleep(1)  # Pequeña pausa para evitar colisiones de recursos

# Esperar a que todos terminen
for p in processes:
    p.wait()

print("Scraping paralelo terminado para todos los hoteles.")
