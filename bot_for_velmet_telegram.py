


import telebot
from telebot import types
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки
TOKEN = '8231656744:AAFTUzFcs0B3GOzcQ4ONeC-0fmquObPUY9o'
ADMIN_CHAT_ID = '-1003083819225'

bot = telebot.TeleBot(TOKEN)

user_data = {}

# Товары
products = {
    'hoodie': {
        'name': "Худи 'sand dunes'",
        'sizes': ['S', 'M', 'L', 'XL'],
        'price': 6600,
        'pre-save': 2200
    }
}

# Типы оплаты
payment_types = {
    'full': '💳 Полная оплата',
    'preorder': '🧾 Предзаказ (предоплата)'
}

class UserData:
    def __init__(self):
        self.full_name = None
        self.phone = None
        self.email = None
        self.telegram = None
        self.cart = []
        self.payment_type = None

def get_user_data(user_id):
    """Безопасное получение данных пользователя"""
    if user_id not in user_data:
        user_data[user_id] = UserData()
        logger.info(f"Созданы новые данные для пользователя {user_id}")
    return user_data[user_id]

def clear_user_data(user_id):
    """Очистить данные пользователя"""
    if user_id in user_data:
        user_data[user_id] = UserData()
        logger.info(f"Данные пользователя {user_id} очищены")

def get_main_keyboard():
    """Главное меню с кнопками"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('📦 Сделать заказ')
    item2 = types.KeyboardButton('🔄 Пересоздать заявку')
    markup.add(item1, item2)
    return markup

@bot.message_handler(commands=['start', 'restart'])
def start_message(message):
    try:
        user_id = message.from_user.id
        user = get_user_data(user_id)
        
        bot.send_message(message.chat.id, 
                        "👋 Привет! Я бот для заказа товаров у бренда одежды и аксессуаров 'Velmet'\n\n"
                        "Нажми '📦 Сделать заказ' чтобы начать!\n", 
                        reply_markup=get_main_keyboard())
        logger.info(f"Пользователь {user_id} запустил бота")
    except Exception as e:
        logger.error(f"Ошибка в start_message: {e}")

@bot.message_handler(func=lambda message: message.text == '📦 Сделать заказ')
def start_order(message):
    try:
        user_id = message.from_user.id
        user = get_user_data(user_id)
        
        # Запрашиваем ФИО вместе
        msg = bot.send_message(message.chat.id, 
                              "📝 Введите ваше Фамилию и Имя (например: Иванов Иван), это нужно для того, чтобы мы знали как к вам обращаться :) :\n\n",
                              reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_full_name)
    except Exception as e:
        logger.error(f"Ошибка в start_order: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте снова /start", 
                        reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '🔄 Пересоздать заявку')
def restart_order(message):
    try:
        user_id = message.from_user.id
        clear_user_data(user_id)
        
        bot.send_message(message.chat.id, 
                        "🔄 Заявка пересоздана! Все данные очищены.\n\n"
                        "Теперь вы можете начать новый заказ:",
                        reply_markup=get_main_keyboard())
        logger.info(f"Пользователь {user_id} пересоздал заявку")
        
    except Exception as e:
        logger.error(f"Ошибка в restart_order: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при пересоздании заявки")

def process_full_name(message):
    try:
        # Проверяем, не хочет ли пользователь пересоздать заявку
        if message.text in ['/start', '/restart', '🔄 Пересоздать заявку']:
            restart_order(message)
            return
            
        user_id = message.from_user.id
        user = get_user_data(user_id)
        user.full_name = message.text
        
        # Создаем кнопку для отправки номера телефона
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton('📞 Отправить номер телефона', request_contact=True)
        back_button = types.KeyboardButton('🔄 Начать заново')
        markup.add(item, back_button)
        
        msg = bot.send_message(message.chat.id, 
                              "📞 Теперь нам нужен ваш номер телефона\n\n"
                              "Нажмите кнопку ниже чтобы отправить его автоматически\n", 
                              reply_markup=markup)
        bot.register_next_step_handler(msg, process_phone)
    except Exception as e:
        logger.error(f"Ошибка в process_full_name: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Начните заново /start", 
                        reply_markup=get_main_keyboard())

def process_phone(message):
    try:
        # Проверяем, не хочет ли пользователь пересоздать заявку
        if message.text in ['/start', '/restart', '🔄 Начать заново']:
            restart_order(message)
            return
            
        user_id = message.from_user.id
        user = get_user_data(user_id)
        
        if message.contact:
            user.phone = message.contact.phone_number
        else:
            user.phone = message.text
        
        # Убираем специальную клавиатуру, добавляем кнопку начала заново
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton('🔄 Начать заново')
        markup.add(back_button)
        
        msg = bot.send_message(message.chat.id, 
                              "✈️ Пожалуйста, укажите ваш Telegram username в формате @username. Это самый быстрый способ связи. Если вам удобнее общаться через другие мессенджеры, просто напишите «нет», и мы свяжемся с вами другим удобным для вас способом.\n",
                              reply_markup=markup)
        bot.register_next_step_handler(msg, process_telegram)
    except Exception as e:
        logger.error(f"Ошибка в process_phone: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Начните заново /start", 
                        reply_markup=get_main_keyboard())

def process_telegram(message):
    try:
        # Проверяем, не хочет ли пользователь пересоздать заявку
        if message.text in ['/start', '/restart', '🔄 Начать заново']:
            restart_order(message)
            return
            
        user_id = message.from_user.id
        user = get_user_data(user_id)
        telegram = message.text.strip()
        
        if telegram.lower() in ['нет', 'no', 'skip']:
            user.telegram = "не указан"
        else:
            user.telegram = telegram
        
        # Добавляем кнопку начала заново
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton('🔄 Начать заново')
        markup.add(back_button)
        
        msg = bot.send_message(message.chat.id, 
                              "📧 Введите ваш Email (необязательно):\n"
                              "Если не хотите указывать, напишите 'нет'\n\n",
                              reply_markup=markup)
        bot.register_next_step_handler(msg, process_email)
    except Exception as e:
        logger.error(f"Ошибка в process_telegram: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Начните заново /start", 
                        reply_markup=get_main_keyboard())

def process_email(message):
    try:
        # Проверяем, не хочет ли пользователь пересоздать заявку
        if message.text in ['/start', '/restart', '🔄 Начать заново']:
            restart_order(message)
            return
            
        user_id = message.from_user.id
        user = get_user_data(user_id)
        email = message.text.strip()
        
        if email.lower() in ['нет', 'no', 'skip']:
            user.email = "не указан"
        else:
            user.email = email
        
        # Переходим к выбору товара
        show_catalog(message)
    except Exception as e:
        logger.error(f"Ошибка в process_email: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Начните заново /start", 
                        reply_markup=get_main_keyboard())

def show_catalog(message):
    try:
        user_id = message.from_user.id
        user = get_user_data(user_id)
        
        # Добавляем кнопку начала заново в каталог
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton('🔄 Начать заново')
        markup.add(back_button)
        
        # Inline кнопки для товаров
        inline_markup = types.InlineKeyboardMarkup()
        
        # Кнопка для выбора худи
        hoodie_button = types.InlineKeyboardButton(
            f"🏷️ {products['hoodie']['name']} - {products['hoodie']['price']}₽", 
            callback_data="select_hoodie"
        )
        inline_markup.add(hoodie_button)
        
        # Кнопка просмотра корзины
        if user.cart:
            cart_button = types.InlineKeyboardButton(f"🛒 Корзина ({len(user.cart)})", callback_data="view_cart")
            inline_markup.add(cart_button)
        
        bot.send_message(message.chat.id, 
                        "🛍️ КАТАЛОГ ТОВАРОВ:\n\n"
                        "👇 Выберите товар:",
                        reply_markup=markup)
        
        # Отправляем inline кнопки
        bot.send_message(message.chat.id, "Выберите товар:", reply_markup=inline_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в show_catalog: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Начните заново /start", 
                        reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == 'select_hoodie')
def select_hoodie(call):
    """Показывает выбор размера для худи"""
    try:
        # Создаем клавиатуру с размерами
        markup = types.InlineKeyboardMarkup()
        
        for size in products['hoodie']['sizes']:
            button = types.InlineKeyboardButton(
                f"Размер {size} - {products['hoodie']['price']}₽", 
                callback_data=f"add_hoodie_{size}"
            )
            markup.add(button)
        
        # Кнопка возврата в каталог
        back_button = types.InlineKeyboardButton("⬅️ Назад к каталогу", callback_data="back_to_catalog")
        markup.add(back_button)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🏷️ {products['hoodie']['name']}\n"
                 f"💵 Цена: {products['hoodie']['price']}₽\n"
                 f"🧾 Сумма предзаказа: {products['hoodie']['pre-save']}₽\n"
                 f"📏 Размеры: {', '.join(products['hoodie']['sizes'])}\n\n"
                 "👇 Выберите размер:",
            reply_markup=markup
        )
        
    except Exception as e:
        logger.error(f"Ошибка в select_hoodie: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при выборе товара")

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_catalog')
def back_to_catalog(call):
    """Возврат в каталог"""
    try:
        show_catalog(call.message)
        bot.answer_callback_query(call.id, "Возврат в каталог")
    except Exception as e:
        logger.error(f"Ошибка в back_to_catalog: {e}")

# Обработчик кнопки "Начать заново" в процессе оформления
@bot.message_handler(func=lambda message: message.text == '🔄 Начать заново')
def restart_in_process(message):
    restart_order(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_hoodie_'))
def add_to_cart(call):
    try:
        user_id = call.from_user.id
        user = get_user_data(user_id)
        size = call.data.replace('add_hoodie_', '')
        
        print(f"DEBUG: Добавляем товар для user_id {user_id}")
        
        # Добавляем товар в корзину
        user.cart.append({
            'product': 'hoodie',
            'size': size,
            'price': products['hoodie']['price'],
            'pre_save': products['hoodie']['pre-save'],
            'quantity': 1
        })
        
        print(f"DEBUG: Корзина после добавления: {user.cart}")
        
        # Показываем уведомление о добавлении
        bot.answer_callback_query(call.id, f"✅ Худи размера {size} добавлен в корзину!")
        
        # Показываем обновленный каталог
        show_catalog_updated(call.message)
        
    except Exception as e:
        print(f"ERROR в add_to_cart: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при добавлении товара")

def show_catalog_updated(message):
    """Показывает обновленный каталог"""
    try:
        user_id = message.from_user.id
        user = get_user_data(user_id)
        
        # Добавляем кнопку начала заново
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton('🔄 Начать заново')
        markup.add(back_button)
        
        # Inline кнопки
        inline_markup = types.InlineKeyboardMarkup()
        
        # Кнопка для выбора худи
        hoodie_button = types.InlineKeyboardButton(
            f"🏷️ {products['hoodie']['name']} - {products['hoodie']['price']}₽", 
            callback_data="select_hoodie"
        )
        inline_markup.add(hoodie_button)
        
        # Кнопка просмотра корзины
        if user.cart:
            cart_button = types.InlineKeyboardButton(f"🛒 Корзина ({len(user.cart)})", callback_data="view_cart")
            inline_markup.add(cart_button)
        
        # Кнопка завершения заказа
        if user.cart:
            done_button = types.InlineKeyboardButton("✅ Завершить заказ", callback_data="finish_order")
            inline_markup.add(done_button)
        
        bot.send_message(message.chat.id,
                       "🛍️ КАТАЛОГ ТОВАРОВ\n\n"
                       "👇 Выберите товар:",
                       reply_markup=markup)
        
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=inline_markup)
            
    except Exception as e:
        logger.error(f"Ошибка в show_catalog_updated: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'view_cart')
def view_cart_callback(call):
    """Обработчик кнопки просмотра корзины"""
    show_cart(call)

def show_cart(message_or_call):
    try:
        # Определяем user_id в зависимости от типа входящих данных
        if hasattr(message_or_call, 'from_user'):
            # Если это обычное сообщение
            user_id = message_or_call.from_user.id
            chat_id = message_or_call.chat.id
        else:
            # Если это callback
            user_id = message_or_call.from_user.id
            chat_id = message_or_call.message.chat.id
            
        user = get_user_data(user_id)
        
        print(f"DEBUG: Показываем корзину для user_id {user_id}")
        print(f"DEBUG: Корзина содержит: {user.cart}")
        
        if not user.cart:
            text = "🛒 Ваша корзина пуста"
            markup = types.InlineKeyboardMarkup()
            continue_button = types.InlineKeyboardButton("🛍️ К каталогу", callback_data="continue_shopping")
            markup.add(continue_button)
        else:
            text = "🛒 ВАША КОРЗИНА:\n\n"
            total = 0
            pre_save_total = 0
            
            for index, item in enumerate(user.cart):
                item_total = item['price'] * item['quantity']
                item_pre_save = item['pre_save'] * item['quantity']
                total += item_total
                pre_save_total += item_pre_save
                text += f"{index + 1}. {products[item['product']]['name']} (Размер: {item['size']})\n"
                text += f"   Количество: {item['quantity']} x {item['price']} ₽ = {item_total} ₽\n"
                text += f"   💰 Предоплата: {item_pre_save} ₽\n\n"
            
            text += f"💰 Общая сумма: {total} ₽\n"
            text += f"🧾 Сумма предоплаты: {pre_save_total} ₽"
        
            markup = types.InlineKeyboardMarkup()
            
            # Кнопки для управления корзиной - ВСЕГДА показываем очистку если есть товары
            clear_button = types.InlineKeyboardButton("🗑️ Очистить корзину", callback_data="clear_cart")
            markup.add(clear_button)
            
            continue_button = types.InlineKeyboardButton("➕ Добавить еще товар", callback_data="continue_shopping")
            finish_button = types.InlineKeyboardButton("✅ Подтвердить заказ", callback_data="finish_order")
            markup.add(continue_button, finish_button)
        
        # Всегда отправляем новое сообщение с корзиной
        bot.send_message(chat_id, text, reply_markup=markup)
            
    except Exception as e:
        print(f"ERROR в show_cart: {e}")
        bot.send_message(chat_id, "❌ Ошибка при отображении корзины")

@bot.callback_query_handler(func=lambda call: call.data == 'clear_cart')
def clear_cart(call):
    try:
        user_id = call.from_user.id
        user = get_user_data(user_id)
        
        if not user.cart:
            bot.answer_callback_query(call.id, "❌ Корзина уже пуста!")
            return
        
        # Сохраняем количество товаров для сообщения
        items_count = len(user.cart)
        
        # Очищаем корзину
        user.cart = []
        
        bot.answer_callback_query(call.id, f"🗑️ Корзина очищена! Удалено {items_count} товар(ов)")
        
        # Показываем обновленную корзину
        show_cart(call)
        
    except Exception as e:
        print(f"ERROR в clear_cart: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при очистке корзины")

@bot.callback_query_handler(func=lambda call: call.data == 'continue_shopping')
def continue_shopping(call):
    try:
        show_catalog_updated(call.message)
    except Exception as e:
        logger.error(f"Ошибка в continue_shopping: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")

@bot.callback_query_handler(func=lambda call: call.data == 'finish_order')
def finish_order(call):
    try:
        user_id = call.from_user.id
        user = get_user_data(user_id)
        
        if not user.cart:
            bot.answer_callback_query(call.id, "❌ Корзина пуста! Добавьте товары.")
            return
        
        # Показываем выбор типа оплаты
        show_payment_types(call.message)
        
    except Exception as e:
        logger.error(f"Ошибка в finish_order: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при оформлении заказа")

def show_payment_types(message):
    """Показывает выбор типа оплаты (полная/предзаказ)"""
    try:
        user_id = message.from_user.id
        user = get_user_data(user_id)
        
        # Подсчитываем суммы
        total = sum(item['price'] * item['quantity'] for item in user.cart)
        pre_save_total = sum(item['pre_save'] * item['quantity'] for item in user.cart)
        
        # Создаем клавиатуру с типами оплаты
        markup = types.InlineKeyboardMarkup()
        
        for type_key, type_name in payment_types.items():
            button = types.InlineKeyboardButton(type_name, callback_data=f"paytype_{type_key}")
            markup.add(button)
        
        # Кнопка назад к корзине
        back_button = types.InlineKeyboardButton("⬅️ Назад к корзине", callback_data="view_cart")
        markup.add(back_button)
        
        message_text = (
            "💳 Выберите тип оплаты:"
        )
        
        bot.send_message(message.chat.id, message_text, reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Ошибка в show_payment_types: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при выборе типа оплаты")

@bot.callback_query_handler(func=lambda call: call.data.startswith('paytype_'))
def process_payment_type(call):
    """Обрабатывает выбор типа оплаты"""
    try:
        user_id = call.from_user.id
        user = get_user_data(user_id)
        
        payment_type = call.data.replace('paytype_', '')
        user.payment_type = payment_type
        
        # Формируем финальное сообщение о заказе
        order_text = format_order_message(user)
        
        # Отправляем заказ в группу
        try:
            bot.send_message(ADMIN_CHAT_ID, order_text)
            print(f"✅ Заказ отправлен в группу {ADMIN_CHAT_ID}")
        except Exception as e:
            print(f"❌ Ошибка отправки в группу: {e}")
        
        # Подсчитываем итоги
        total = sum(item['price'] * item['quantity'] for item in user.cart)
        pre_save_total = sum(item['pre_save'] * item['quantity'] for item in user.cart)
        
        # Сообщение пользователю
        success_msg = (
            f"✅ Ваш заказ принят!\n\n"
            f"💰 Общая сумма заказа: {total} ₽\n"
            f"💳 Тип оплаты: {payment_types[payment_type]}\n"
        )
        
        success_msg += f"\n\n📞 Мы свяжемся с вами в ближайшее время по номеру {user.phone}\n\nСпасибо за заказ! ❤️"
        
        bot.send_message(call.message.chat.id, success_msg, parse_mode="Markdown")
        
        # Показываем заказ пользователю
        bot.send_message(call.message.chat.id, f"📋 Детали вашего заказа:\n\n{order_text}")
        
        # Очищаем корзину
        user.cart = []
        
        # Возвращаем главное меню
        bot.send_message(call.message.chat.id, 
                        "🔄 Если хотите сделать новый заказ, нажмите кнопку ниже:",
                        reply_markup=get_main_keyboard())
        
        bot.answer_callback_query(call.id, "✅ Заказ оформлен!")
        logger.info(f"Пользователь {user_id} завершил заказ на сумму {total}₽, тип оплаты: {payment_type}")
        
    except Exception as e:
        logger.error(f"Ошибка в process_payment_type: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при оформлении заказа")
        bot.send_message(call.message.chat.id, "❌ Произошла ошибка. Попробуйте снова /start", 
                        reply_markup=get_main_keyboard())

def format_order_message(user):
    """Форматирует сообщение о заказе в нужном стиле"""
    
    # Подсчет общей суммы и предоплаты
    total = sum(item['price'] * item['quantity'] for item in user.cart)
    pre_save_total = sum(item['pre_save'] * item['quantity'] for item in user.cart)
    
    # Формируем сообщение
    message = "🎉 НОВЫЙ ЗАКАЗ!\n\n"
    message += f"👤 Клиент: {user.full_name}\n"
    message += f"📞 Телефон: {user.phone}\n"
    message += f"📧 Email: {user.email}\n"
    message += f"✈️ Telegram: {user.telegram}\n"
    message += f"💳 Тип оплаты: {payment_types[user.payment_type]}\n\n"
    message += "🛒 ТОВАРЫ:\n\n"
    
    for index, item in enumerate(user.cart):
        item_total = item['price'] * item['quantity']
        item_pre_save = item['pre_save'] * item['quantity']
        message += f"{index + 1}. {products[item['product']]['name']} (Размер: {item['size']})\n"
        message += f"   Количество: {item['quantity']} x {item['price']} ₽ = {item_total} ₽\n"
        message += f"   💰 Предоплата: {item_pre_save} ₽\n\n"
    
    message += f"💰 Общая сумма: {total} ₽\n"
    message += f"🧾 Сумма предоплаты: {pre_save_total} ₽\n"
    message += f"💰 Оставшаяся не оплаченая часть: {total - pre_save_total} ₽"
        
    
    return message

# Команда для проверки отправки в группу
@bot.message_handler(commands=['check_group'])
def check_group(message):
    """Проверить возможность отправки в группу"""
    try:
        test_msg = "🔍 Тестовое сообщение от бота для проверки связи с группой"
        bot.send_message(ADMIN_CHAT_ID, test_msg)
        bot.send_message(message.chat.id, "✅ Сообщение отправлено в группу!")
        print(f"✅ Тестовое сообщение отправлено в группу {ADMIN_CHAT_ID}")
    except Exception as e:
        error_msg = f"❌ Ошибка отправки в группу: {e}"
        bot.send_message(message.chat.id, error_msg)
        print(error_msg)

# Команда для отладки - посмотреть данные пользователя
@bot.message_handler(commands=['debug'])
def debug_info(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    debug_text = (
        f"🔄 ДЕБАГ ИНФОРМАЦИЯ:\n"
        f"User ID: {user_id}\n"
        f"ФИО: {user.full_name}\n"
        f"Телефон: {user.phone}\n"
        f"Telegram: {user.telegram}\n"
        f"Email: {user.email}\n"
        f"Товаров в корзине: {len(user.cart)}\n"
        f"Тип оплаты: {user.payment_type}\n"
        f"Всего пользователей в памяти: {len(user_data)}"
    )
    
    bot.send_message(message.chat.id, debug_text)

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    print(f"ADMIN_CHAT_ID: {ADMIN_CHAT_ID}")
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        print(f"Критическая ошибка: {e}")