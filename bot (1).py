import logging
from telegram import Update, ChatMember, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    filters,
    MessageHandler,
    Application,
    ConversationHandler,
)
import random
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Настройки бота
TOKEN = "№токкена"
CHANNEL_ID = "#логинканала"
ADMIN_ID = "админ айди"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ... остальной код без изменений ...

# Хранение статистики пользователей
user_stats = defaultdict(lambda: {'first_name': '', 'username': '', 'interactions': 0, 'last_interaction': None})

# Состояния для ConversationHandler
Q1, Q2, Q3, Q4, Q5 = range(5)
ASCENDANT_TEST = 5
MAIN_MENU = 6  # Добавляем состояние главного меню

# Базовые категории ароматов (шаблон для сброса)
BASE_CATEGORIES = {
    "Цитрусовые": 0,
    "Цветочные": 0,
    "Восточные": 0,
    "Древесные": 0,
    "Кожаные": 0,
    "Шипровые": 0,
    "Фужерные": 0
}

# Результаты теста
RESULTS = {
    "Цитрусовые": {
        "emoji": "🍋",
        "description": "Ты: энергичная, подвижная и лёгкая. С тобой рядом всегда свежо и легко дышать. Ароматы для тебя: добавляют бодрости, как стакан холодной воды в жаркий день.",
        "budget": [
            "Chopard Lemon Dulci (https://goldapple.ru/19000127039-happy-lemon-dulci)",
            "GUERLAIN Aqua Allegoria Mandarine Basilic (https://goldapple.ru/19000107891-aqua-allegoria-mandarine-basilic)",
            "NICOLAI PARFUMEUR-CREATEUR PARIS Cap Néroli (https://goldapple.ru/19000222796-cap-neroli)"
        ],
        "mid": [
            "ESSENTIAL PARFUMS PARIS Nice Bergamote (https://goldapple.ru/19000148357-nice-bergamote-by-antoine-maisondieu)",
            "ACQUA DI PARMA Blu Mediterraneo Mandarino Di Sicilia (https://goldapple.ru/19000322813-blu-mediterraneo-mandarino-di-sicilia)",
            "VILHELM PARFUMERIE Basilico & Fellini (https://goldapple.ru/19760332179-basilico-fellini)"
        ],
        "luxury": [
            "MAISON FRANCIS KURKDJIAN Aqua Universalis (https://goldapple.ru/19760303647-aqua-universalis)",
            "LIQUIDES IMAGINAIRES Pistachio Cousin (https://goldapple.ru/19000420871-pistachio-cousin)",
            "TOM FORD Eau De Soleil Blanc (https://goldapple.ru/19000402314-eau-de-soleil-blanc)"
        ]
    },
    "Цветочные": {
        "emoji": "🌺",
        "description": "Ты: романтичная и нежная, любишь создавать уют вокруг. Ароматы для тебя подчёркивают женственность и гармонию.",
        "budget": [
            "CHOPARD Love Chopard (https://goldapple.ru/19000127038-love-chopard)",
            "NICOLAI PARFUMEUR-CREATEUR PARIS Angelys Pear (https://goldapple.ru/19000222794-angelys-pear)",
            "ESTEE LAUDER Pleasures (https://goldapple.ru/7010100002-pleasures)"
        ],
        "mid": [
            "ETRO White Magnolia (https://goldapple.ru/19000006572-white-magnolia)",
            "ESSENTIAL PARFUMS PARIS Rose Magnetic Refillable (https://goldapple.ru/19000148359-rose-magnetic)",
            "CHOPARD Imperiale Iris Malika (https://goldapple.ru/19000155914-imperiale-iris-malika)"
        ],
        "luxury": [
            "Amouage Blossom Love (https://goldapple.ru/19000235955-blossom-love-woman)",
            "Byredo Flowerhead (https://goldapple.ru/26731500003-flowerhead)",
            "HFC Wear Love Everywhere (https://goldapple.ru/26291200007-wear-love-evrywhere)"
        ]
    },
    "Восточные": {
        "emoji": "🌙",
        "description": "Ты: чувственная и загадочная, умеешь оставлять яркое впечатление. Ароматы для тебя: притягательные, согревающие и соблазнительные.",
        "budget": [
            "ETRO Etra Etro (https://goldapple.ru/26070100006-etra-etro)",
            "ESSENTIAL PARFUMS PARIS Divine Vanille (https://goldapple.ru/19000148354-divine-vanille)",
            "BANANA REPUBLIC Dark Cherry & Amber (https://goldapple.ru/19000132896-dark-cherry-amber)"
        ],
        "mid": [
            "GUERLAIN Shalimar (https://goldapple.ru/7750600006-shalimar)",
            "TOM FORD Black Orchid (https://goldapple.ru/19000166979-black-orchid)",
            "CHOPARD Imperiale Iris Malika (https://goldapple.ru/19000155914-imperiale-iris-malika)"
        ],
        "luxury": [
            "MAISON FRANCIS KURKDJIAN Gentle Fluidity Gold (https://goldapple.ru/19760303656-gentle-fluidity-gold)",
            "CHOPARD Miel D'Arabie (https://goldapple.ru/83290100014-miel-d-arabie)",
            "HFC Nirvanesque (https://goldapple.ru/19000159258-nirvanesque)"
        ]
    },
    "Древесные": {
        "emoji": "🌳",
        "description": "Ты: спокойная и уверенная, ценишь глубину и стабильность. Ароматы для тебя: глубокие и стойкие, создают ощущение гармонии.",
        "budget": [
            "BANANA REPUBLIC 90 Pure White (https://goldapple.ru/19000132887-90-pure-white)",
            "NICOLAI PARFUMEUR-CREATEUR PARIS Patchouli Intense (https://goldapple.ru/19000222748-patchouli-intense)",
            "ESSENTIAL PARFUMS PARIS Mon Vetiver Refillable (https://goldapple.ru/19000148356-mon-vetiver-refillable)"
        ],
        "mid": [
            "MIN NEW YORK Onsen (https://goldapple.ru/19000008793-onsen)",
            "CHOPARD Vetiver D'Haiti Au The Vert (https://goldapple.ru/83290100012-vetiver-d-haiti-au-the-vert)",
            "CHOPARD Cedar Malaki (https://goldapple.ru/19000155915-cedar-malaki)"
        ],
        "luxury": [
            "MAISON FRANCIS KURKDJIAN Grand Soir (https://goldapple.ru/26800300010-grand-soir)",
            "MIND GAMES Gardez (https://goldapple.ru/19000166823-gardez)",
            "INITIO PARFUMS PRIVES Oud For Greatness (https://goldapple.ru/19000318983-oud-for-greatness)"
        ]
    },
    "Кожаные": {
        "emoji": "🧥",
        "description": "Ты: харизматичная и смелая, любишь выделяться и быть уверенной. Ароматы для тебя: статусные и мощные, подчёркивают силу и свободу.",
        "budget": [
            "CHOPARD Leather Malaki (https://goldapple.ru/19000275552-leather-malaki)",
            "TONKA PERFUMES MOSCOW Yuzhnaya Kozha (https://goldapple.ru/19000061966-yuzhnaya-kozha)",
            "L'ATELIER PARFUM Leather Black (K)Night (https://goldapple.ru/19000253162-leather-black-k-night)"
        ],
        "mid": [
            "GUCCI Guilty Absolute Pour Homme (https://goldapple.ru/7231800003-guilty-absolute)",
            "GIVENCHY Gentleman (https://goldapple.ru/19000039709-gentleman)",
            "STATE OF MIND French Gallantry (https://goldapple.ru/83670100011-french-gallantry)"
        ],
        "luxury": [
            "BYREDO Bibliotheque (https://goldapple.ru/26733200002-bibliotheque)",
            "MEMO PARIS French Leather (https://goldapple.ru/82081800001-french-leather)",
            "TOM FORD Ombre Leather Parfum (https://goldapple.ru/19000014662-ombre-leather-parfum)"
        ]
    },
    "Шипровые": {
        "emoji": "🌿",
        "description": "Ты: элегантная, ценишь классику. Ароматы для тебя: строгие и утончённые, делают образ завершённым.",
        "budget": [
            "BANANA REPUBLIC 06 Black Platinum (https://goldapple.ru/19760313106-06-black-platinum)",
            "NEYDO Mossland 12.09 (https://goldapple.ru/19000200197-mossland-12-09)",
            "PARLE MOI DE PARFUM Chypre Mojo/45 (https://goldapple.ru/83710200002-chypre-mojo-45)"
        ],
        "mid": [
            "MIN NEW YORK Stardust (https://goldapple.ru/19760328382-stardust)",
            "SCENTOLOGIA Sen.Sory (https://goldapple.ru/19000051107-sen-sory)",
            "LAURENT MAZZONE La Nuit Des Fleurs (https://goldapple.ru/19000206007-la-nuit-des-fleurs)"
        ],
        "luxury": [
            "SISLEY Eau Du Soir Limited Edition By Ymane Chabi-Gara (https://goldapple.ru/19000214991-eau-du-soir)",
            "ROJA PARFUMS Vetiver Pour Homme (https://goldapple.ru/19000007933-vetiver)",
            "PENHALIGON'S Empressa (https://goldapple.ru/19000126981-empressa)"
        ]
    },
    "Фужерные": {
        "emoji": "🌿",
        "description": "Ты: собранная, аккуратная, любишь порядок и свежесть. Ароматы для тебя: чистые и ухоженные, как белая рубашка.",
        "budget": [
            "L'ATELIER PARFUM Cypress Shadow (https://goldapple.ru/19000186469-cypress-shadow)",
            "COMPTOIR SUD PACIFIQUE Rhum&Tabac (https://goldapple.ru/26044900002-rhum-tabac)",
            "BANANA REPUBLIC Neroli Woods (https://goldapple.ru/19000132892-neroli-woods)"
        ],
        "mid": [
            "VILHELM PARFUMERIE Chicago High (https://goldapple.ru/19760332182-chicago-high)",
            "NOBILE 1942 Anti Malocchio (https://goldapple.ru/19000311839-anti-malocchio)",
            "BORNTOSTANDOUT Drunk Lovers (https://goldapple.ru/19000382674-drunk-lovers)"
        ],
        "luxury": [
            "ETAT LIBRE D'ORANGE La Fin Du Monde (https://goldapple.ru/19000121034-la-fin-du-monde)",
            "LIQUIDES IMAGINAIRES Phantasma (https://goldapple.ru/19760302866-phantasma)",
            "ROJA PARFUMS Elysium Pour Homme (https://goldapple.ru/19000007930-elysium)"
        ]
    }
}

# Результаты теста по асценденту
ASCENDANT_RESULTS = {
    "овен♈️": {
        "description": "идеальным выбором для тебя будут универсальные ароматы, которые ты можешь использовать как днем, так и вечером! они должны подчеркивать твой стиль, но не выбиваться из образа",
        "perfume": "CHOPARD Vetiver D'Haiti Au The Vert",
        "link": "https://randewoo.ru/product/chopard-vetver-d-haiti-au-the-vert?preferred=402967"
    },
    "телец♉️": {
        "description": "тебе подойдет классика, что-то статусное, вайб old money – твой выбор:)",
        "perfume": "Tom Ford White Suede",
        "link": "https://randewoo.ru/product/tom-ford-white-suede?preferred=401524"
    },
    "близнецы♊️": {
        "description": "твой сигнатурный аромат – что-то лёгкое и расслабленное, идеально подходящее под любую жизненную ситуацию и период",
        "perfume": "JULIETTE HAS A GUN Not A Perfume",
        "link": "https://randewoo.ru/product/juliette-has-a-gun-not-a-perfume?preferred=400964"
    },
    "рак♋️": {
        "description": "нежные, девичьи, воздушные ароматы, раскрывающие твою женственность",
        "perfume": "BYBOZO Decent",
        "link": "https://randewoo.ru/product/decent?preferred=388170"
    },
    "лев♌️": {
        "description": " ты – ярчная, запоминающаяся, а твой парфюм должен тебе соответствовать и показывать тебя статусной и особенной",
        "perfume": "HFC Indian Venus",
        "link": "https://randewoo.ru/product/haute-fragrance-company-indian-venus?preferred=383326"
    },
    "дева♍️": {
        "description": "твой выбор – женственные, изысканные, но не сложные ароматы",
        "perfume": "FRANCIS KURKDJIAN Gentle Fluidity Gold",
        "link": "https://randewoo.ru/product/francis-kurkdjian-gentle-fluidity-silver?preferred=415163"
    },
    "весы♎️": {
        "description": "ты любишь аккуратные и спокойные композиции, но! они должны обращать на себя внимание",
        "perfume": "INITIO Musk Therapy",
        "link": "https://randewoo.ru/product/musk-therapy?preferred=392553"
    },
    "скорпион♏️": {
        "description": "что-то ярчное, заметное, немного с вызовом – точно твой вариант!",
        "perfume": "FRANCIS KURKDJIAN Oud Satin Mood",
        "link": "https://randewoo.ru/product/francis-kurkdjian-oud-satin-mood?preferred=442221"
    },
    "стрелец♐️": {
        "description": "твой знак – любитель креатива и падок на тренды, поэтому твой аромат должен быть необычным и актуальным",
        "perfume": "Kilian Angels Share PARADIS",
        "link": "https://randewoo.ru/product/angels-share-paradis?preferred=519829"
    },
    "козерог♑️": {
        "description": "тебе отлично подойдут строгие, не вычурные варианты, которые подчеркнут твой статус",
        "perfume": "MIN New York Plush",
        "link": "https://randewoo.ru/product/min-new-york-plush?preferred=131552"
    },
    "водолей♒️": {
        "description": "в аромате тебе важна индивидуальность и нишевость, ты не хочешь быть «как все» и всегда выбираешь самое интересное",
        "perfume": "ETAT LIBRE D`ORANGE La Fin Du Monde",
        "link": "https://randewoo.ru/product/etat-libre-d-orange-la-fin-du-monde?preferred=45573"
    },
    "рыбы♓️": {
        "description": " ты – воплощение романтики и женственности, твой аромат, в первую очередь, должен тебя дополнять и звучать с тобой в унисон",
        "perfume": "BYREDO Young Rose",
        "link": "https://randewoo.ru/product/young-rose?preferred=408907"
    }
}

def update_user_stats(user_id: int, first_name: str, username: str):
    """Обновление статистики пользователя"""
    user_stats[user_id]['first_name'] = first_name
    user_stats[user_id]['username'] = username
    user_stats[user_id]['interactions'] += 1
    user_stats[user_id]['last_interaction'] = datetime.now()

async def check_subscription(user_id: int, context: CallbackContext) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        return False

async def check_subscription_during_test(update: Update, context: CallbackContext) -> bool:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    is_member = await check_subscription(user_id, context)
    
    if not is_member:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton("Я подписался", callback_data="check_subscription")]
        ])
        
        await query.edit_message_text(
            "Для продолжения теста необходимо быть подписанным на мой канал.\n"
            "Пожалуйста, подпишись и нажми кнопку 'Я подписался'.",
            reply_markup=keyboard
        )
        return False
    return True

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update_user_stats(user.id, user.first_name, user.username)
    
    # Очищаем состояние ConversationHandler
    if context.user_data.get('conversation_active'):
        context.user_data.clear()
    
    # Проверяем подписку
    is_member = await check_subscription(user.id, context)
    
    if is_member:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ИДЕАЛЬНЫЙ АРОМАТ ЗА 10 СЕКУНД", callback_data="start_test")],
            [InlineKeyboardButton("ИДЕАЛЬНЫЕ ДУХИ ПО АСЦЕНДЕНТУ", callback_data="ascendant_test")]
        ])
        
        # Отправляем новое сообщение
        await context.bot.send_message(
            chat_id=user.id,
            text=f"Привет, {user.first_name}! 👋\n\n"
                 "Хочешь узнать, какие духи идеально подойдут именно тебе?\n\n"
                 "Выбери тест, который хочешь пройти:",
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton("Я подписался", callback_data="check_subscription")]
        ])
        
        await context.bot.send_message(
            chat_id=user.id,
            text=f"Привет, {user.first_name}!\n\n"
                 "Для использования бота необходимо подписаться на мой канал - там, кстати, куча полезностей об ароматам, декоре и уходе!\n"
                 "После подписки нажми кнопку 'Я подписался'.",
            reply_markup=keyboard
        )

async def start_test_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    # Проверяем подписку перед началом теста
    if not await check_subscription_during_test(update, context):
        return Q1
    
    # Сбрасываем счетчики категорий в контексте пользователя
    context.user_data['categories'] = BASE_CATEGORIES.copy()
    context.user_data['conversation_active'] = True
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Лёгкость и свежесть", callback_data="q1_Цитрусовые")],
        [InlineKeyboardButton("Романтичность и женственность", callback_data="q1_Цветочные")],
        [InlineKeyboardButton("Таинственность и чувственность", callback_data="q1_Восточные")],
        [InlineKeyboardButton("Спокойствие и надёжность", callback_data="q1_Древесные")],
        [InlineKeyboardButton("Сила и дерзость", callback_data="q1_Кожаные")],
        [InlineKeyboardButton("Классика и элегантность", callback_data="q1_Шипровые")],
        [InlineKeyboardButton("Строгость и чистота", callback_data="q1_Фужерные")]
    ])
    
    await query.edit_message_text(
        "Вопрос 1. Какое настроение тебе ближе?",
        reply_markup=keyboard
    )
    
    return Q1

async def ascendant_test_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    # Проверяем подписку перед началом теста
    if not await check_subscription_during_test(update, context):
        return ASCENDANT_TEST
    
    # Кнопки знаков зодиака в 2 столбца
    zodiac_buttons = [
        [InlineKeyboardButton("овен♈️", callback_data="asc_овен♈️"), InlineKeyboardButton("телец♉️", callback_data="asc_телец♉️")],
        [InlineKeyboardButton("близнецы♊️", callback_data="asc_близнецы♊️"), InlineKeyboardButton("рак♋️", callback_data="asc_рак♋️")],
        [InlineKeyboardButton("лев♌️", callback_data="asc_лев♌️"), InlineKeyboardButton("дева♍️", callback_data="asc_дева♍️")],
        [InlineKeyboardButton("весы♎️", callback_data="asc_весы♎️"), InlineKeyboardButton("скорпион♏️", callback_data="asc_скорпион♏️")],
        [InlineKeyboardButton("стрелец♐️", callback_data="asc_стрелец♐️"), InlineKeyboardButton("козерог♑️", callback_data="asc_козерог♑️")],
        [InlineKeyboardButton("водолей♒️", callback_data="asc_водолей♒️"), InlineKeyboardButton("рыбы♓️", callback_data="asc_рыбы♓️")]
    ]
    
    keyboard = InlineKeyboardMarkup(zodiac_buttons)
    
    await query.edit_message_text(
        "твой идеальный парфюм по асценденту🪐🌙\n"
        "благодаря выбору парфюма по асценденту ты станешь ярче, уверенне и заметнее для окружающих!\n\n"
        "(все ароматы представлены на randewoo, а с моим промокодом 10INN ты получишь скидку -10%)\n\n"
        "выбери свой знак👇🏻",
        reply_markup=keyboard
    )
    
    return ASCENDANT_TEST

async def ascendant_result(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    # Проверяем подписку перед показом результата
    if not await check_subscription_during_test(update, context):
        return ConversationHandler.END
    
    selected_sign = query.data.replace("asc_", "")
    result = ASCENDANT_RESULTS[selected_sign]
    
    message = (
        f"{selected_sign}\n\n"
        f"{result['description']}\n\n"
        f"{result['perfume']}\n"
        f"{result['link']}\n\n"
        "Не забудь использовать промокод 10INN для скидки -10% на randewoo!"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="back_to_start")]
    ])
    
    await query.edit_message_text(
        message,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    
    # Очищаем состояние ConversationHandler
    context.user_data.clear()
    return ConversationHandler.END

async def back_to_start(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    # Очищаем состояние ConversationHandler
    context.user_data.clear()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ИДЕАЛЬНЫЙ АРОМАТ ЗА 10 СЕКУНД", callback_data="start_test")],
        [InlineKeyboardButton("ИДЕАЛЬНЫЕ ДУХИ ПО АСЦЕНДЕНТУ", callback_data="ascendant_test")]
    ])
    
    await query.edit_message_text(
        f"Привет, {query.from_user.first_name}! 👋\n\n"
        "Хочешь узнать, какие духи идеально подойдут именно тебе?\n\n"
        "Выбери тест, который хочешь пройти:",
        reply_markup=keyboard
    )
    
    return ConversationHandler.END

async def question_1(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    # Проверяем подписку перед вопросом
    if not await check_subscription_during_test(update, context):
        return Q1
    
    selected_category = query.data.replace("q1_", "")
    
    # Используем категории из user_data
    if 'categories' not in context.user_data:
        context.user_data['categories'] = BASE_CATEGORIES.copy()
    
    context.user_data['categories'][selected_category] += 1
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Лимонад / цитрус", callback_data="q2_Цитрусовые")],
        [InlineKeyboardButton("Цветочный чай", callback_data="q2_Цветочные")],
        [InlineKeyboardButton("Пряный глинтвейн", callback_data="q2_Восточные")],
        [InlineKeyboardButton("Виски / ром", callback_data="q2_Древесные")],
        [InlineKeyboardButton("Эспрессо или крепкий чай", callback_data="q2_Кожаные")],
        [InlineKeyboardButton("Белое сухое вино", callback_data="q2_Шипровые")],
        [InlineKeyboardButton("Минеральная вода", callback_data="q2_Фужерные")]
    ])
    
    await query.edit_message_text(
        "Вопрос 2. Какой напиток тебе ближе?",
        reply_markup=keyboard
    )
    
    return Q2

async def question_2(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    # Проверяем подписку перед вопросом
    if not await check_subscription_during_test(update, context):
        return Q2
    
    selected_category = query.data.replace("q2_", "")
    
    if 'categories' not in context.user_data:
        context.user_data['categories'] = BASE_CATEGORIES.copy()
    
    context.user_data['categories'][selected_category] += 1
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Белая рубашка, джинсы", callback_data="q3_Цитрусовые")],
        [InlineKeyboardButton("Платье с цветочным принтом", callback_data="q3_Цветочные")],
        [InlineKeyboardButton("Бархат, шёлк", callback_data="q3_Восточные")],
        [InlineKeyboardButton("Кашемировый свитер", callback_data="q3_Древесные")],
        [InlineKeyboardButton("Кожаная куртка", callback_data="q3_Кожаные")],
        [InlineKeyboardButton("Классический костюм", callback_data="q3_Шипровые")],
        [InlineKeyboardButton("Свежевыстиранный хлопок", callback_data="q3_Фужерные")]
    ])
    
    await query.edit_message_text(
        "Вопрос 3. Какая одежда тебя вдохновляет?",
        reply_markup=keyboard
    )
    
    return Q3

async def question_3(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    # Проверяем подписку перед вопросом
    if not await check_subscription_during_test(update, context):
        return Q3
    
    selected_category = query.data.replace("q3_", "")
    
    if 'categories' not in context.user_data:
        context.user_data['categories'] = BASE_CATEGORIES.copy()
    
    context.user_data['categories'][selected_category] += 1
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Лето", callback_data="q4_Цитрусовые")],
        [InlineKeyboardButton("Весна", callback_data="q4_Цветочные")],
        [InlineKeyboardButton("Осень", callback_data="q4_Восточные")],
        [InlineKeyboardButton("Зима", callback_data="q4_Древесные")],
        [InlineKeyboardButton("Поздняя осень", callback_data="q4_Кожаные")],
        [InlineKeyboardButton("Ранная весна", callback_data="q4_Шипровые")],
        [InlineKeyboardButton("Свежее утро круглый год", callback_data="q4_Фужерные")]
    ])
    
    await query.edit_message_text(
        "Вопрос 4. Какое время года тебе комфортнее всего?",
        reply_markup=keyboard
    )
    
    return Q4

async def question_4(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    # Проверяем подписку перед вопросом
    if not await check_subscription_during_test(update, context):
        return Q4
    
    selected_category = query.data.replace("q4_", "")
    
    if 'categories' not in context.user_data:
        context.user_data['categories'] = BASE_CATEGORIES.copy()
    
    context.user_data['categories'][selected_category] += 1
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Энергию и бодрость", callback_data="q5_Цитрусовые")],
        [InlineKeyboardButton("Романтику и нежность", callback_data="q5_Цветочные")],
        [InlineKeyboardButton("Сексуальность", callback_data="q5_Восточные")],
        [InlineKeyboardButton("Чувство уюта", callback_data="q5_Древесные")],
        [InlineKeyboardButton("Власть и статус", callback_data="q5_Кожаные")],
        [InlineKeyboardButton("Стиль и утончённость", callback_data="q5_Шипровые")],
        [InlineKeyboardButton("Чистоту и свежесть", callback_data="q5_Фужерные")]
    ])
    
    await query.edit_message_text(
        "Вопрос 5. Что должны дарить тебе духи?",
        reply_markup=keyboard
    )
    
    return Q5

async def question_5(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    # Проверяем подписку перед показом результата
    if not await check_subscription_during_test(update, context):
        return Q5
    
    selected_category = query.data.replace("q5_", "")
    
    if 'categories' not in context.user_data:
        context.user_data['categories'] = BASE_CATEGORIES.copy()
    
    context.user_data['categories'][selected_category] += 1
    
    # Определяем результат
    categories = context.user_data['categories']
    max_count = max(categories.values())
    candidates = [k for k, v in categories.items() if v == max_count]
    result_category = random.choice(candidates)
    
    result = RESULTS[result_category]
    
    # Формируем сообщение с результатом
    message = (
        f"{result['emoji']} {result_category.upper()} {result['emoji']}\n\n"
        f"{result['description']}\n\n"
        "ТОП-3 аромата для тебя:\n\n"
        "💰 БЮДЖЕТНЫЕ:\n" + "\n".join(result['budget']) + "\n\n"
        "💎 СРЕДНЕЙ ЦЕНЫ:\n" + "\n".join(result['mid']) + "\n\n"
        "💎💎💎 ПРЕМИУМ:\n" + "\n".join(result['luxury'])
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="back_to_start")]
    ])
    
    await query.edit_message_text(
        message,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    
    # Очищаем состояние ConversationHandler
    context.user_data.clear()
    return ConversationHandler.END

async def check_subscription_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    update_user_stats(query.from_user.id, query.from_user.first_name, query.from_user.username)
    
    is_member = await check_subscription(query.from_user.id, context)
    
    if is_member:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ИДЕАЛЬНЫЙ АРОМАТ ЗА 10 СЕКУНД", callback_data="start_test")],
            [InlineKeyboardButton("ИДЕАЛЬНЫЕ ДУХИ ПО АСЦЕНДЕНТУ", callback_data="ascendant_test")]
        ])
        
        await query.edit_message_text(
            f"Отлично, {query.from_user.first_name}! 👋\n\n"
            "Хочешь узнать, какие духи идеально подойдут именно тебе?\n\n"
            "Выбери тест, который хочешь пройти:",
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton("Я подписался", callback_data="check_subscription")]
        ])
        
        await query.edit_message_text(
            "Я всё ещё не вижу твою подписку 😔\n"
            "Пожалуйста, подпишись на канал и нажми кнопку 'Я подписался'.",
            reply_markup=keyboard
        )

async def stats_command(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав для просмотра статистики.")
        return
    
    total_users = len(user_stats)
    active_today = sum(1 for user in user_stats.values() 
                      if user['last_interaction'] and 
                      user['last_interaction'] > datetime.now() - timedelta(hours=24))
    
    message = (
        f"📊 Статистика бота:\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"🔥 Активных за 24 часа: {active_today}\n\n"
        f"Последние 10 пользователей:\n"
    )
    
    # Сортируем пользователей по времени последнего взаимодействия
    sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['last_interaction'] or datetime.min, reverse=True)
    
    for i, (user_id, data) in enumerate(sorted_users[:10], 1):
        last_interaction = data['last_interaction'].strftime("%Y-%m-%d %H:%M") if data['last_interaction'] else "никогда"
        message += f"{i}. {data['first_name']} (@{data['username']}) - {data['interactions']} взаимодействий, последнее: {last_interaction}\n"
    
    await update.message.reply_text(message)

async def export_stats_command(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав для экспорта статистики.")
        return
    
    # Создаем CSV файл
    filename = f"bot_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user_id', 'first_name', 'username', 'interactions', 'last_interaction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for user_id, data in user_stats.items():
            writer.writerow({
                'user_id': user_id,
                'first_name': data['first_name'],
                'username': data['username'],
                'interactions': data['interactions'],
                'last_interaction': data['last_interaction'].strftime("%Y-%m-%d %H:%M:%S") if data['last_interaction'] else ''
            })
    
    # Отправляем файл администратору
    with open(filename, 'rb') as file:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=file,
            caption="📊 Экспорт статистики пользователей"
        )
    
    # Удаляем временный файл
    os.remove(filename)

async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)
    
    if update and update.effective_user:
        try:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="Произошла ошибка. Пожалуйста, попробуйте начать заново с команды /start"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение об ошибке: {e}")

def main() -> None:
    # Создаем Application
    application = Application.builder().token(TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("export_stats", export_stats_command))
    
    # ConversationHandler для основного теста
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_test_handler, pattern="^start_test$")],
        states={
            Q1: [CallbackQueryHandler(question_1, pattern="^q1_")],
            Q2: [CallbackQueryHandler(question_2, pattern="^q2_")],
            Q3: [CallbackQueryHandler(question_3, pattern="^q3_")],
            Q4: [CallbackQueryHandler(question_4, pattern="^q4_")],
            Q5: [CallbackQueryHandler(question_5, pattern="^q5_")],
        },
        fallbacks=[
            CallbackQueryHandler(back_to_start, pattern="^back_to_start$"),
            CommandHandler("start", start)
        ],
        per_message=False,  # Явно указываем настройку
        map_to_parent={
            ConversationHandler.END: MAIN_MENU
        }
    )
    
    # ConversationHandler для теста по асценденту
    ascendant_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ascendant_test_handler, pattern="^ascendant_test$")],
        states={
            ASCENDANT_TEST: [CallbackQueryHandler(ascendant_result, pattern="^asc_")],
        },
        fallbacks=[
            CallbackQueryHandler(back_to_start, pattern="^back_to_start$"),
            CommandHandler("start", start)
        ],
        per_message=False,  # Явно указываем настройку
        map_to_parent={
            ConversationHandler.END: MAIN_MENU
        }
    )
    
    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_handler(ascendant_conv_handler)
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(check_subscription_handler, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(back_to_start, pattern="^back_to_start$"))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота (исправленная строка)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
