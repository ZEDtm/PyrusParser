import os
import time
import pickle
import requests
import argparse
import configparser
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='(%(asctime)s)[%(levelname)s]: %(message)s')

class PyrusParser:
    def __init__(self, token: str, chat_id: str, url: str, header: str) -> None:
        self.token = token
        self.chat_id = chat_id
        self.url = url
        self.show = False
        self.header = header
        self.cookie = True
        self.driver = self.chrome_driver_configurate()
        self.start_parse()

    def chrome_driver_configurate(self) -> webdriver.Chrome:
        """Конфигурация ChromeDriver"""
        chrome_options = Options()
        if not(self.show) and self.cookie:
            chrome_options.add_argument("--headless")  # Скрыть браузер
        service = Service()
        service.verbose = False
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def send_to_tg(self, task: str) -> None:
        """Отправка сообщения в телеграм"""
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        params = {
            'chat_id': self.chat_id,
            'text': f'<b>{self.header}</b>\n\n{task}',
            'parse_mode': 'HTML'
        }

        response = requests.post(url, params=params)

        if response.status_code == 200:
            logging.info('Сообщение успешно отправлено в Telegram')
        else:
            logging.error(f'Ошибка при отправке в Telegram: {response.status_code} - {response.text}')
        
    def save_cookies(self, driver):
        cookies = driver.get_cookies()
        if cookies:
            with open('cookie.pkl', 'wb') as filehandler:
                pickle.dump(cookies, filehandler)
            logging.info('Cookies успешно сохранены')
        else:
            logging.error("Cookies не был сохранен. Ошибка авторизации")

    def load_cookies(self, driver) -> bool:
        try:
            with open('cookie.pkl', 'rb') as cookiesfile:
                cookies = pickle.load(cookiesfile)
                for cookie in cookies:
                    driver.add_cookie(cookie)
                driver.refresh()
                logging.info('Cookies успешно загружены')
                return True
        except FileNotFoundError:
            logging.error('Файл с Cookies не найден')
            return False
    
    def get_cookies(self) -> None:
        self.cookie = False
        driver = self.chrome_driver_configurate()
        driver.get(self.url)
        input()
        driver.refresh()
        self.save_cookies(driver)

    
    
    def start_parse(self):
        driver = self.driver
        driver.get(self.url)
        while not(self.load_cookies(driver)):
            logging.info('Вы не авторизованы в Pyrus. Произведите авторизацию и нажмите клавишу [Enter]')
            self.get_cookies()

        driver.get(self.url)

        wait = WebDriverWait(driver, 20)  # Время ожидания ответа

        try:
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.rg__row.selectableLink')))
        except TimeoutException:
            logging.error("Элементы не найдены в течение заданного времени. Выход...")
            os.exit()

        processed_titles = set()
        messages = []
        if links:
            # Этот блок отправит все заявки в телеграм бота, которые лежали в пуле
            for link in reversed(links):
                link_url = link.get_attribute('href')
                name = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[2].text.strip()
                service = ' '.join(link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[8].text.split())
                description = clean_html(link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[13].text.strip())
                author = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[15].text.strip()
                type = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[16].text.strip()
                channel = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[19].text.strip()

                message = f'{link_url}\nПриоитет: {type}\nСервис: <b>{service}</b>\nПроблема: <b>{name}</b>\nОписание:\n{description}\nАвтор: {author}\nКанал связи: {channel}\n\n'

                messages.append(message)
                if len(messages) > 5:
                    self.send_to_tg(''.join(messages))
                    messages = []
                processed_titles.add(name)

            if len(messages) > 0:
                self.send_to_tg(''.join(messages))

        while True:
            # Этот блок отправляет только новые или измененные заявки
            driver.refresh()
            try:
                links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.rg__row.selectableLink')))
            except TimeoutException:
                logging.error("Элементы не найдены в течение заданного времени. Повторная попытка...")
                continue

            if links:

                for link in reversed(links):
                    link_url = link.get_attribute('href')
                    name = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[2].text.strip()
                    service = ' '.join(link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[8].text.split())
                    description = clean_html(link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[13].text.strip())
                    author = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[15].text.strip()
                    type = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[16].text.strip()
                    channel = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[19].text.strip()


                    if name not in processed_titles:

                        processed_titles.add(name)
                        
                        message = f'{link_url}\nПриоитет: {type}\nСервис: <b>{service}</b>\nПроблема: <b>{name}</b>\nОписание:\n{description}\nАвтор: {author}\nКанал связи: {channel}\n\n'

                        self.send_to_tg(message)
                    else:
                        pass
            time.sleep(2)
            logging.info('-----------------------------[Обновление страницы]-----------------------------')


def clean_html(raw_html):
    """Сообщения с почты тянут HTML разметку, еще они очень длинные, поэтмоу мы их срезаем и убираем лишний мусор"""
    soup = BeautifulSoup(raw_html, 'html.parser')
    allowed_tags = ['b', 'i', 'u', 's', 'a', 'code', 'pre']
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
    
    cleaned_text = soup.get_text()
    
    return cleaned_text[:200]


def load_config():
    config = configparser.ConfigParser(interpolation=None)
    logging.info("Читаю файл конфигурации..")
    config.read('config.ini')
    return config

def save_config(token, chat_id, url, header):
    config = configparser.ConfigParser(interpolation=None)
    config['PyrusParser'] = {
        'token': token,
        'chat_id': chat_id,
        'url': url,
        'header': header
    }
    logging.info("Сохраняю файл конфигурации..")
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def main() -> None:
    parser = argparse.ArgumentParser(description='Парсим пайрус')
    parser.add_argument('--token', type=str, help='Токен телеграм бота')
    parser.add_argument('--chat_id', type=str, help='Chat ID, в который бот будет отправлять заявки')
    parser.add_argument('--url', type=str, help='Ссылка на реестр Pyrus')
    parser.add_argument('--header', type=str, help='Заголовок для сообщения в телеграм')

    args = parser.parse_args()

    config = load_config()

    token = args.token or config['PyrusParser']['token']
    chat_id = args.chat_id or config['PyrusParser']['chat_id']
    url = args.url or config['PyrusParser']['url']
    header = args.header or config['PyrusParser']['header']

    save_config(token, chat_id, url, header)

    logging.info(f"Конфигурация:")
    logging.info(f"token: {token}")
    logging.info(f"chat_id: {chat_id}")
    logging.info(f"url: {url}")
    logging.info(f"header: {header}")

    PyrusParser(token, chat_id, url, header)

if __name__ == '__main__':
    main()
