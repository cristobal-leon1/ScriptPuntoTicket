import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import time

# Función para leer los proxies del archivo
def read_proxies(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Función para verificar la posición en la cola
def check_queue_position(proxy, url):
    session = requests.Session()
    session.proxies = {
        "http": f"socks5://{proxy}",
        "https": f"socks5://{proxy}"
    }
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        # Aquí debes implementar la lógica para extraer la posición real de la cola
        # Por ahora, seguimos simulando una posición aleatoria
        import random
        position = random.randint(1, 2000)
        print(f"Proxy: {proxy}, Posición: {position}")
        return proxy, position
    except Exception as e:
        print(f"Error con proxy {proxy}: {e}")
        return proxy, None

# Función para abrir Chrome con el proxy adecuado
def open_chrome(proxy, url):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=socks5://{proxy}')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')
    
    service = Service('/path/to/chromedriver')  # Asegúrate de tener el chromedriver correcto
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Página cargada con éxito")
        input("Presiona Enter para cerrar el navegador...")
    finally:
        driver.quit()

# Función principal
def main():
    proxies = read_proxies("proxys.txt")
    queue_url = "https://queue.puntoticket.com/?c=puntoticket&e=anf038&t_cal=1&t_ct=2"
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(check_queue_position, proxy, queue_url): proxy for proxy in proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                _, position = future.result()
                if position is not None and position <= 1000:
                    print(f"¡Posición favorable encontrada con proxy {proxy}! Abriendo Chrome...")
                    executor.submit(open_chrome, proxy, queue_url)
                    return  # Terminar el programa después de abrir Chrome
            except Exception as exc:
                print(f'{proxy} generó una excepción: {exc}')

if __name__ == "__main__":
    main()