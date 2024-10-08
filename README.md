# PyrusParser

## Начало:
1. **Устанавливаем Python версии 3.11.7 (желательно)**
2. **Создаем и запускаем виртуальное окружение. Заходим в CMD, предварительно находясь в папке с pp.py:**
   ```shell
   python -m venv venv
   cd venv/Scripts
   activate
   ```
3. **Возвращаемся в папку с pp.py, подтягиваем зависимости:**
  ```shell
  pip install -r requirements.txt
  ```
## Для jоских проффи 
4. **(По желанию) Можно создать файл config.ini, прописать конфигурацию сразу туда, пример:**
  ```ini
  [PyrusParser]
  token = ТОКЕН ВАШЕГО БОТА В ТЕЛЕГРАМ
  chat_id = CHAT ID, ТУДА БОТ ПРИСЫЛАЕТ СООБЩЕНИЯ
  url = ССЫЛКА НА РЕЕСТР ПАЙРУСА
  header = Общий пул
  ```
5. **Можно прописать аргументы для запуска, они будут сохранены в config.ini. Посмотреть их можно командой:**
  ```shell
  python pp.py --help
  ```
  **Пример для запуска с аргументами:**
  ```shell
  python pp.py --token "ТОКЕН БОТА" --chat_id "CHAT ID" --url "ЧТО БУДЕМ СЕГОДНЯ ПАРСИТЬ?" --header "ЭТО ЗАГОЛОВОК ДЛЯ СООБЩЕНИЙ В ТГ, НА СЛУЧАЙ, КОГДА ПАРСЕРОВ ЗАПУЩЕНО НЕСКОЛЬКО В ОДНОГО БОТА"
  ```
7. **Запускаем, следуем инструкции в консоле. Для начала вам нужно авторизоваться в Pyrus, нажать Enter в консоле, ваш куки будет сохранен, в следующий раз он автоматически авторизуется.**

8. **Вы можете настроить заголовки, которые будут парситься здесь:**
   ```pp.py
   link_url = link.get_attribute('href')
                name = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[2].text.strip()
                service = ' '.join(link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[8].text.split())
                description = clean_html(link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[13].text.strip())
                author = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[15].text.strip()
                type = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[16].text.strip()
                channel = link.find_elements(By.CSS_SELECTOR, 'div.rg__cell')[19].text.strip()

                message = f'{link_url}\nПриоитет: {type}\nСервис: <b>{service}</b>\nПроблема: <b>{name}</b>\nОписание:\n{description}\nАвтор: {author}\nКанал связи: {channel}\n\n'
   ```
