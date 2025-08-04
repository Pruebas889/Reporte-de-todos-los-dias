import schedule
import time
import logging
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import holidays # Asegúrate de tener instalado: pip install holidays
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Configuración logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("automatizacion.log", encoding='utf-8')
    ]
)

# --- Configuración de feriados para Colombia ---
co_holidays = holidays.CountryHoliday('CO') # Por defecto usa el año actual y siguientes

# --- Función auxiliar para seleccionar opción ---
def select_option(driver, wait, container_xpath: str, option_text: str):
    try:
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, container_xpath)))
        dropdown.click()
        time.sleep(1)
        option_xpath = f"//div[@role='option' and normalize-space(.)='{option_text}']"
        option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", option)
        option.click()
        time.sleep(1)
    except Exception as e:
        print(f"[ERROR] No se pudo seleccionar la opción '{option_text}': {e}")
        raise

# --- Función para automatizar el proceso con 3 reintentos ---
def run_with_retries(max_retries=3, wait_seconds=10):
    """Ejecuta la automatización con reintentos automáticos."""
    for intento in range(1, max_retries + 1):
        try:
            logging.info(f"🔄 Intento {intento} de {max_retries}")
            run_automation()
            break  # Si funciona, salimos del bucle
        except Exception as e:
            logging.error(f"Fallo en el intento {intento}: {e}", exc_info=True)
            if intento < max_retries:
                logging.info(f"Reintentando en {wait_seconds} segundos...")
                time.sleep(wait_seconds)
            else:
                logging.critical("❌ Todos los intentos fallaron.")

# --- Proceso principal ---
def run_automation():
    # Crear driver dentro de la función
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")  # modo headless moderno
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    try:
        logging.info("Iniciando la automatización...")

        hoy_date = date.today()
        dia_semana = hoy_date.weekday() # Lunes es 0, Martes 1, ..., Viernes 4, Sábado 5, Domingo 6

        # Determinar horario
        horario_seleccionado = '6:30 AM -12:30 PM Y 1:30 PM A 4:30PM'
        if dia_semana == 4:
            horario_seleccionado = '6:30 AM -12:30 PM Y 1:30 PM A 3:30PM (Viernes)'
        elif hoy_date in co_holidays:
            logging.info(f"Hoy es feriado ({co_holidays.get(hoy_date)}). No se enviará el formulario.")
            return
        elif dia_semana in [5, 6]:
            logging.info("Hoy es fin de semana. No se enviará formulario.")
            return

        # Abrir formulario
        driver.get("https://form.asana.com/?k=WGw15u-lXbBnkEa_Dw0pAQ&d=1204083449956184")
        time.sleep(3)

        # Rellenar campos
        driver.find_element(By.XPATH, '//*[@id="1208265916162013"]').send_keys("Santago Vega Pinilla")
        time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="1208286338273781"]').send_keys("1019605034")
        time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="1208265916162015"]').send_keys("Aprendiz")
        driver.find_element(By.XPATH,
            '/html/body/div/div[2]/div[1]/div/div[2]/div[1]/div[4]/div[2]/div/div/input'
        ).send_keys(hoy_date.strftime("%Y-%m-%d"))
        time.sleep(0.5)
        logging.info(f"Fecha de hoy ({hoy_date.strftime('%Y-%m-%d')}) ingresada correctamente.")

        # Seleccionar opciones
        logging.info("Seleccionando opciones del formulario...")
        select_option(driver, wait, '/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[5]/div[2]/div/div[1]/div',
                      'Gerente De Tecnologia'
        )
        logging.info("Opción 'Gerente De Tecnologia' seleccionada.")
        
        select_option(driver, wait, '/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[6]/div[2]/div/div/div',
                      'Jefe De Aseguramiento De Calidad De Software'
        )
        logging.info("Opción 'Jefe De Aseguramiento De Calidad De Software' seleccionada.")
        try:
            select_option(driver, wait,
                '/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[6]/div[2]/div/div[1]/div',
                'Jefe De Aseguramiento De Calidad De Software'
            )
            logging.info("Jefe seleccionado correctamente.")
        except Exception as e:
            select_option(driver, wait,
                '/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[6]/div[2]/div/div[1]/div',
                'Gerente De Tecnologia'
            )
            logging.error("No se pudo seleccionar el jefe. Puede que no haya un jefe asignado.")
            logging.info("Se seleccionó la gerencia como jefe por defecto.")
        
        select_option(driver, wait, 
            '/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[7]/div[2]/div/div/div',
            'Equipo Administrativo'
        )
        logging.info("Equipo Administrativo seleccionado correctamente.")
        select_option(driver, wait, 
            '/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[8]/div[1]/div[2]/div/div/div',
            'Presencial'
        )
        logging.info("Opción 'Presencial' seleccionada.")
        select_option(driver, wait, 
            '/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[8]/div[2]/div[1]/div[2]/div/div/div', 
            'Sede Administrativa'
        )
        logging.info("Lugar de trabajo del día de hoy seleccionado correctamente.")
        
        time.sleep(1)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[8]/div[2]/div[2]/div[1]/div[2]/div/div/div"))
        )

        select_option(driver, wait, 
            "/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[8]/div[2]/div[2]/div[1]/div[2]/div/div/div",
            'Sede administrativa Bogotá'
        )
        logging.info("Opción 'Sede administrativa Bogotá' seleccionada.")
        select_option(driver, wait, 
            "/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[8]/div[2]/div[2]/div[2]/div/div[2]/div/div/div",
            horario_seleccionado # Usamos la variable que ya determinamos
        )
        logging.info(f"Horario de jornada laboral seleccionado: {horario_seleccionado} correctamente.")
        select_option(driver, wait, 
            "/html/body/div[1]/div[2]/div[1]/div/div[2]/div[1]/div[9]/div[2]/div/div[1]/div/span",
            'No'
        )
        logging.info("Respuesta a la pregunta de novedad seleccionada correctamente.")

        driver.find_element(
            By.XPATH, '//input[contains(@placeholder,"email")]'
        ).send_keys("santiago.vega.cop@gmail.com")
        time.sleep(0.5)
        logging.info("Email ingresado correctamente.")

        wait.until(
            EC.element_to_be_clickable((By.XPATH,'//div[@role="button" and contains(.,"Submit")]'))
        ).click()
        time.sleep(3)

        logging.info("✅ Formulario enviado correctamente.")
    except Exception as e:
        logging.error(f"Ocurrió un error: {e}", exc_info=True)
    finally:
        driver.quit()

# --- Main programado ---
def main():
    schedule.every().day.at("06:30").do(run_with_retries, max_retries=3, wait_seconds=15)
    logging.info("⏰ Automatización programada a las 06:30 todos los días (con reintentos).")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
