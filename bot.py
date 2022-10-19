import os
import redis
import re
import api

from dotenv import load_dotenv
from functools import partial
from textwrap import dedent
from geo_distance import calculate_distances, CalculateDistanceError

from telegram.ext import Filters, Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

_database = None

BUTTON_CART = InlineKeyboardButton('Корзина', callback_data='cart')
BUTTON_BACK = InlineKeyboardButton('Назад', callback_data='back')
MENU_ITEMS_NUMBER = 8


def generate_keyboard_for_handle_menu(products: list) -> list:
    keyboard = []
    for product in products:
        button = [
            InlineKeyboardButton(
                product['name'],
                callback_data=product['id']
            )
        ]
        keyboard.append(button)
    return keyboard


def start(bot, update, user_data, client_id, client_secret):
    """
    Хэндлер для состояния START.
    """
    products = api.get_products(client_id, client_secret)['data']
    pages_total_number = len(products)//MENU_ITEMS_NUMBER
    user_data['products'] = products
    user_data['pages_total_number'] = pages_total_number
    keyboard = generate_keyboard_for_handle_menu(
        products[:MENU_ITEMS_NUMBER]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                f'<1/{pages_total_number}>',
                callback_data='pages_total_number'
                ),
            InlineKeyboardButton('Вперед->', callback_data='next_page_2')
            ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        text='Добро пожаловать к нам в пиццерию!!',
        reply_markup=reply_markup
        )
    return "HANDLE_MENU"


def handle_menu(bot, update, user_data, client_id, client_secret):
    user_reply = update.callback_query.data
    products = user_data['products']
    pages_total_number = user_data['pages_total_number']
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat_id

    if 'next_page' in user_reply:
        page = int(re.search(r'next_page_(.*)', user_reply).group(1))
        product_start = MENU_ITEMS_NUMBER*(page-1)
        product_end = MENU_ITEMS_NUMBER*page

        if page <= pages_total_number:
            if page == pages_total_number:
                keyboard = generate_keyboard_for_handle_menu(
                    products[product_start:]
                    )
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            '<-Назад',
                            callback_data=f'previous_page_{page-1}'
                            ),
                        InlineKeyboardButton(
                            f'<{page}/{pages_total_number}>',
                            callback_data='pages_total_number'
                            ),
                    ]
                )
            else:
                keyboard = generate_keyboard_for_handle_menu(
                     products[product_start:product_end]
                )
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            '<-Назад',
                            callback_data=f'previous_page_{page-1}'
                            ),
                        InlineKeyboardButton(
                            f'<{page}/{pages_total_number}>',
                            callback_data='pages_total_number'
                            ),
                        InlineKeyboardButton(
                            'Вперед->',
                            callback_data=f'next_page_{page+1}'
                            )
                    ]
                )
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.edit_message_text(
                'Меню',
                reply_markup=reply_markup,
                chat_id=chat_id,
                message_id=message_id
                )
        return "HANDLE_MENU"
    elif 'previous_page' in user_reply:
        page = int(re.search(r'previous_page_(.*)', user_reply).group(1))
        product_start = MENU_ITEMS_NUMBER*(page-1)
        product_end = MENU_ITEMS_NUMBER*page

        if page >= 1:
            if page == 1:
                keyboard = generate_keyboard_for_handle_menu(
                    products[:product_end]
                    )
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f'<{page}/{pages_total_number}>',
                            callback_data='pages_total_number'
                            ),
                        InlineKeyboardButton(
                            'Вперед->',
                            callback_data=f'next_page_{page+1}'
                            )
                    ]
                )
            else:
                keyboard = generate_keyboard_for_handle_menu(
                     products[product_start:product_end]
                )
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            '<-Назад',
                            callback_data=f'previous_page_{page-1}'
                            ),
                        InlineKeyboardButton(
                            f'<{page}/{pages_total_number}>',
                            callback_data='pages_total_number'
                            ),
                        InlineKeyboardButton(
                            'Вперед->',
                            callback_data=f'next_page_{page+1}'
                            )
                    ]
                )
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.edit_message_text(
                'Меню',
                reply_markup=reply_markup,
                chat_id=chat_id,
                message_id=message_id
                )
        return "HANDLE_MENU"
    elif user_reply == 'back' or user_reply == 'handle_menu':
        keyboard = generate_keyboard_for_handle_menu(products[:MENU_ITEMS_NUMBER])
        keyboard.append(
            [
                InlineKeyboardButton(
                    f'<1/{pages_total_number}>',
                    callback_data='pages_total_number'
                    ),
                InlineKeyboardButton('Вперед->', callback_data='next_page_2')
                ]
        )
        keyboard.append([BUTTON_CART])
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.callback_query.message.reply_text(
            'Меню',
            reply_markup=reply_markup
            )
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        return "HANDLE_MENU"
    elif user_reply == 'cart':
        view_cart(bot, update, user_data, client_id, client_secret)
        return 'CART'

    handle_description(bot, update, user_data, client_id, client_secret)
    return "HANDLE_DESCRIPTION"


def handle_description(bot, update, user_data, client_id, client_secret):
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat_id
    user_reply = update.callback_query.data

    if user_reply == 'add_cart':
        api.add_product_cart(
            user_data['product'],
            client_id,
            client_secret,
            1,
            chat_id
            )
        return "HANDLE_DESCRIPTION"
    elif user_reply == 'cart':
        view_cart(bot, update, user_data, client_id, client_secret)
        return 'CART'
    elif user_reply == 'back':
        handle_menu(bot, update, user_data, client_id, client_secret)
        return 'HANDLE_MENU'
    product_id = user_reply
    response_get_product = api.get_product(
        client_id,
        client_secret,
        product_id
        )
    product = response_get_product['data']
    user_data['product'] = product

    product_image_id = product['relationships']['main_image']['data']['id']
    image = api.get_image_product(client_id, client_secret, product_image_id)
    image_link = image['data']['link']['href']

    keyboard = [
        [BUTTON_BACK],
        [InlineKeyboardButton('Положить в корзину', callback_data='add_cart')],
        [BUTTON_CART]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text_blocks = f'''
                    {product['name']}
                    Стоимость: {product['price'][0]['amount']}

                    {product['description']}
                '''

    bot.send_photo(
        chat_id=chat_id,
        photo=image_link,
        caption=dedent(text_blocks),
        reply_markup=reply_markup
        )
    bot.delete_message(chat_id=chat_id, message_id=message_id)

    return "HANDLE_DESCRIPTION"


def generate_cart(chat_id, client_id, client_secret):
    keyboard = [
        [
            InlineKeyboardButton('В меню', callback_data='handle_menu'),
            InlineKeyboardButton('Оплатить', callback_data='pay')
            ]
        ]
    cart = api.get_cart(chat_id, client_id, client_secret)
    total_price_cart = api.get_cart_total(chat_id, client_id, client_secret)
    products_cart = cart['data']
    message_block = []
    for product in products_cart:
        product_price = product['meta']['display_price']['with_tax']['unit']['formatted']
        product_price_cart = product['meta']['display_price']['with_tax']['value']['formatted']
        message = f'''
                    {product["name"]}

                    {product["description"]}
                    {product_price} руб.

                    В корзине {product["quantity"]} пицц на
                    сумму {product_price_cart}
                    '''

        message_block.append(dedent(message))
        product_delete_button = [
            InlineKeyboardButton(
                f'Убрать из корзины {product["name"]}',
                callback_data=f'delete_{product["id"]}'
                )
            ]
        keyboard.append(product_delete_button)
    if not message_block:
        message_block = ["Ваша корзина пуста"]
        api.remove_cart(chat_id, client_id, client_secret)
    message_block.append(f'Общая сумма заказа: {total_price_cart}')
    reply_markup = InlineKeyboardMarkup(keyboard)
    return message_block, reply_markup


def view_cart(bot, update, user_data, client_id, client_secret):
    user_reply = update.callback_query.data
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat_id

    if user_reply == 'back' or user_reply == 'handle_menu':
        handle_menu(bot, update, user_data, client_id, client_secret)
        return 'HANDLE_MENU'
    elif 'delete' in user_reply:
        product_id = re.search(r'delete_(.*)', user_reply).group(1)
        api.remove_product_from_cart(
            chat_id,
            product_id,
            client_id,
            client_secret
            )
        message_block, reply_markup = generate_cart(
            chat_id,
            client_id,
            client_secret
            )
        bot.send_message(
            chat_id=chat_id,
            text='\n'.join(message_block),
            reply_markup=reply_markup
            )
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        return "CART"
    elif user_reply == 'pay':
        bot.send_message(
            chat_id=chat_id,
            text='Пришлите мне свой e-mail'
            )
        return "WAITING_EMAIL"

    message_block, reply_markup = generate_cart(
        chat_id,
        client_id,
        client_secret
        )
    bot.send_message(
        chat_id=chat_id,
        text='\n'.join(message_block),
        reply_markup=reply_markup
        )
    bot.delete_message(chat_id=chat_id, message_id=message_id)
    return "CART"


def waiting_email(bot, update, user_data, client_id, client_secret):
    email = update.message.text
    chat_id = update.message.chat_id
    api.create_customer(str(chat_id), email, client_id, client_secret)
    bot.send_message(
        chat_id=chat_id,
        text='Хорошо, пришлите нам ваш адрес текстом или геолокацию',
        )
    return 'WAITING_ADDRESS'


def waiting_address(bot, update, user_data, geocoder_token, client_id, client_secret):
    delivery_address = update.message.text
    chat_id = update.message.chat_id
    keyboard = [
        [InlineKeyboardButton('Самовывоз', callback_data='pickup')],
        [InlineKeyboardButton('Доставка', callback_data='delivery')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not delivery_address:
        if update.edited_message:
            message = update.edited_message
        else:
            message = update.message
        delivery_address = (
            message.location.latitude,
            message.location.longitude
            )
    pizzerias = api.get_pizzerias(
        'Pizzeria',
        client_id,
        client_secret
        )
    pizzerias_addresses = [
        {
            'coordinates': (pizzeria['Longitude'], pizzeria['Latitude']),
            'address': pizzeria['Address'],
            'courier_id': pizzeria['courier']
            }
        for pizzeria in pizzerias
        ]
    try:
        delivery_coordinates, nearest_pizzeria = calculate_distances(
            geocoder_token,
            delivery_address,
            pizzerias_addresses
        )
        user_data['nearest_pizzeria'] = nearest_pizzeria
        user_data['delivery_coordinates'] = delivery_coordinates
        if float(nearest_pizzeria['distance']) <= 0.5:
            message = f'''
            Может, заберете пиццу в нашей пиццеррии неподалеко?
            Она всего в {nearest_pizzeria['distance']} км от вас!
            Вот ее адрес: {nearest_pizzeria['address']}.

            А можем и бесплатно доставит, нам не сложно
            '''
            user_data['delivery_price'] = 0
        elif float(nearest_pizzeria['distance']) <= 5.0:
            message = '''
            Похлже придется ехать до вас на самокате.
            Доставка будет стоить 100 рублей.
            Доставляем или самовывоз?
            '''
            user_data['delivery_price'] = 100
        elif float(nearest_pizzeria['distance']) <= 20.0:
            message = '''
            Доставка до вас будет стоить 300 рублей. Доставляем или самовывоз?
            '''
            user_data['delivery_price'] = 300
        else:
            message = '''
            Простите, мы не можем осуществить до вас доставку.
            Вы можете забрать пиццу самостоятельно
            '''
            keyboard.pop(1)
    except CalculateDistanceError:
        bot.send_message(
            chat_id=chat_id,
            text='Не понял Вас. Проверте адресс и повторите ввод',
        )
        return 'WAITING_ADDRESS'

    bot.send_message(
        chat_id=chat_id,
        text=dedent(message),
        reply_markup=reply_markup
        )
    return 'DELIVERY_METHOD'


def choice_delivery_method(bot, update, user_data, job_queue, client_id, client_secret):
    user_reply = update.callback_query.data
    chat_id = update.callback_query.message.chat_id

    keyboard = [
        [InlineKeyboardButton('Оплатить', callback_data='pay')],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if user_reply == 'pickup':
        message = f"Ждем Вас в нашей пицерри. Адресс:\
                    {user_data['nearest_pizzeria']['address']}"
        bot.send_message(
            chat_id=chat_id,
            text=dedent(message),
            reply_markup=reply_markup
            )
        return 'HANDLE_MENU'
    if user_reply == 'delivery':
        courier_id = user_data['nearest_pizzeria']['courier_id']
        lon, lat = user_data['delivery_coordinates']
        keyboard = [
            [InlineKeyboardButton('Оплатить', callback_data='pay')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_location(
            chat_id=courier_id,
            latitude=lat,
            longitude=lon
            )
        message_block = generate_cart(
            chat_id,
            client_id,
            client_secret
            )
        delivery_price = user_data['delivery_price']
        cart_price = re.match(
            r'(.*) руб',
            api.get_cart_total(chat_id, client_id, client_secret)
            ).group(1)
        total_price = int(cart_price) + int(delivery_price)
        user_data['total_price'] = total_price
        message_block[0].append(
            (f"Стоимость доставки {delivery_price} руб.\n"
             f"К оплате {total_price} руб.")
            )

        bot.send_message(
            chat_id=chat_id,
            text='\n'.join(message_block[0]),
            reply_markup=reply_markup
            )

        job_queue.run_once(callback_alarm, 60, context=chat_id)

    return 'WAINING_PAY'


def callback_alarm(bot, job):
    bot.send_message(
        chat_id=job.context,
        text=('Приятного аппетита!. В случаи если пицца не'
              'доставленна обратитесь в техподдержку')
    )


def pay(bot, update, user_data, job_queue, provider_pay_token, client_id, client_secret):
    chat_id = update.callback_query.message.chat_id
    message_id = update.callback_query.message.message_id

    prices = [LabeledPrice("Test", user_data['total_price']*100)]
    currency = "RUB"
    title = "Order payment"
    description = f"User order payment {chat_id}"
    payload = f"Payload - {chat_id}"
    start_parameter = "test-payment"

    keyboard = [
            [InlineKeyboardButton('Оплатить', callback_data='pay')],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.sendInvoice(
        chat_id,
        title,
        description,
        payload,
        provider_pay_token,
        start_parameter,
        currency,
        prices,
        )

    bot.delete_message(chat_id=chat_id, message_id=message_id)
    bot.send_message(
        chat_id=chat_id,
        text=('Приятного аппетита!. В случаи если пицца не'
              'доставленна обратитесь в техподдержку'),
        reply_markup=reply_markup
    )
    print("Оплачено")
    return "HANDLE_MENU"


def successful_payment_callback(bot, update):
    # do something after successful receive of payment?
    update.message.reply_text("Thank you for your payment!")


def handle_users_reply(bot, update, user_data, job_queue, client_id, client_secret, provider_pay_token, geocoder_token=None):

    """
    Функция, которая запускается при любом сообщении от пользователя и решает
    как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую
    функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в
    базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его
    написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может
    воспользоваться этой командой.
    """

    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")
    states_functions = {
        'START': partial(
            start,
            client_id=client_id,
            client_secret=client_secret
            ),
        'HANDLE_MENU': partial(
            handle_menu,
            client_id=client_id,
            client_secret=client_secret
            ),
        'HANDLE_DESCRIPTION': partial(
            handle_description,
            client_id=client_id,
            client_secret=client_secret
            ),
        'CART': partial(
            view_cart,
            client_id=client_id,
            client_secret=client_secret
        ),
        'WAITING_EMAIL': partial(
            waiting_email,
            client_id=client_id,
            client_secret=client_secret
            ),
        'WAITING_ADDRESS': partial(
            waiting_address,
            geocoder_token=geocoder_token,
            client_id=client_id,
            client_secret=client_secret
            ),
        'DELIVERY_METHOD': partial(
            choice_delivery_method,
            job_queue=job_queue,
            client_id=client_id,
            client_secret=client_secret
            ),
        'WAINING_PAY': partial(
            pay,
            job_queue=job_queue,
            client_id=client_id,
            client_secret=client_secret,
            provider_pay_token=provider_pay_token
            )
    }
    state_handler = states_functions[user_state]
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(bot, update, user_data)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis,
    либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_host = os.getenv("REDIS_HOST")
        redis_port = os.getenv("REDIS_PORT")
        _database = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password
            )
    return _database


def main():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    token = os.getenv("TG_TOKEN")
    provider_pay_token = os.getenv("PROVIDER_PAY_TOKEN")
    geocoder_token = os.getenv("YANDEX_GEOCODER_TOKEN")

    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        CallbackQueryHandler(
            partial(
                handle_users_reply,
                client_id=client_id,
                client_secret=client_secret,
                provider_pay_token=provider_pay_token
                ),
            pass_user_data=True,
            pass_job_queue=True
            )
        )
    dispatcher.add_handler(
        MessageHandler(
            Filters.text,
            partial(
                handle_users_reply,
                client_id=client_id,
                client_secret=client_secret,
                geocoder_token=geocoder_token,
                provider_pay_token=provider_pay_token
                ),
            pass_user_data=True,
            pass_job_queue=True
            )
        )
    dispatcher.add_handler(
        MessageHandler(
            Filters.location,
            partial(
                handle_users_reply,
                client_id=client_id,
                client_secret=client_secret,
                geocoder_token=geocoder_token,
                provider_pay_token=provider_pay_token
                ),
            pass_user_data=True,
            pass_job_queue=True
            )
        )
    dispatcher.add_handler(
        CommandHandler(
            'start',
            partial(
                handle_users_reply,
                client_id=client_id,
                client_secret=client_secret,
                provider_pay_token=provider_pay_token
                ),
            pass_user_data=True,
            pass_job_queue=True
            )
        )

    updater.start_polling()


if __name__ == '__main__':
    main()
