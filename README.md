# PizzeriaBot

Данный бот выступает в роли пиццери

## Запуск бота локально
Для запуска бота на вашем сервере необходимо выполнить следующие действия:

1. Cоздать бота в Телеграмм  [см.тут](https://core.telegram.org/bots).
2. Инициализировать с вашим ботом чат.
3. Склонировать себе файлы репозитория выполнив команду **https://github.com/AloneRD/FishShop.git**.
4. Установить необходимы зависимости **pip install -r requirements.txt**.
5. В директории с проектом создать файл **.env** со следующим содержимом:
 ```
    CLIENT_ID=апра3jmMOxhZEXLAY5yhUMZ1MFOFTWQXCFPdIsv
    TG_TOKEN=536291вапрвар
    REDIS_PASSWORD=fghfghjg6c55fJA
    REDIS_HOST = fghjgfhjfghj
    PROVIDER_PAY_TOKEN= dfgsdgdfg
    YANDEX_GEOCODER_TOKEN=vcghjgjtgygvn
 ```
   - **CLIENT_ID** токен к CMS (В данном боте используется moltin)
   - **TG_TOKEN** токен к вашему телеграмм боту
   - **REDIS_PASSWORD** пароль Redis
   - **REDIS_PORT** port Redis
   - **PROVIDER_PAY_TOKEN** токен Вашей платежной системы
   - **YANDEX_GEOCODER_TOKEN**ключ API Yandex геокодер
6. запустить бота **.\bot.py**
