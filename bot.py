import os
import json
import logging
import random
import re
from deep_translator import GoogleTranslator
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import (
    Updater, CommandHandler, CallbackContext,
    MessageHandler, Filters, ConversationHandler,
    CallbackQueryHandler
)
from telegram.utils.helpers import escape_markdown

# Configuration
WHITELIST = []  # Replace with admin user IDs
SIGHTS_FILE = 'sights.json'
IMAGES_DIR = 'images'
ITEMS_PER_PAGE = 5

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Translations with kid-friendly content
TRANSLATIONS = {
    'en': {
        'welcome': "🌍 Choose your language / Выберите язык:",
        'start_message': (
            "🎉 Welcome to Arctic Adventures Bot! 🐻❄️\n\n"
            "Let's explore Arkhangelskaya Oblast' together!\n\n"
            "🌟 Did you know?\n"
            "• Home to the Northern Lights! 🌌\n"
            "• There are 300-year-old wooden houses! 🏚️\n"
            "• You can meet real reindeer! 🦌\n"
            "• The region is bigger than France! 🇫🇷\n\n"
            "Type /help to see what we can do!"
        ),
        'help': (
            "🦊 Here's how I can help you:\n\n"
            "/start - Begin our adventure! 🚀\n"
            "/help - Show this help message 📖\n"
            "/lang - Change language 🌐\n"
            "/dev - About this bot 🤖\n"
            "/rand - Random magical place 🎲\n"
            "/list - List all magical places 📜\n"  # New line
            "/add - Add new magic places (Wizards only) ✨\n"
            "/del - Remove magic places (Wizards only) 🧹\n\n"
            "Let's explore the Arctic wonders together! ❄️"
        ),
        'del_start': "🧹 Which magic place should vanish? Type its name:",
        'del_confirm': "Are you sure you want to remove {name}? This magic can't be undone! ✨",
        'del_success': "🧙♂️ Poof! {name} has disappeared from the map!",
        'del_fail': "🔍 Hmm... I can't find {name} in my spellbook",
        'del_cancel': "✨ Deletion magic stopped!",
        'del_list': "🔮 Found these magical places:",
        'lang_change': "🌍 Choose language:",
        'dev_info': (
            "🤖 Arctic Explorer Bot\n"
            "Version: 1.0 🧊\n"
            "Made with ❤️ by Polar Bears Team\n"
            "🛠️ How I work:\n"
            "- Python Magic 🐍\n"
            "- Telegram Bot Powers 📲\n"
            "- Arctic Spirit 🧊\n\n"
            "I'm always learning new tricks! 🎩"
        ),
        'error': "❄️ Oops! Something melted... Try again!",
        'add_name': "🏰 What's the name of this magical place?",
        'add_description': "📖 Describe this place in a fun way for kids:",
        'add_funfact': "🎩 Share a cool fact that kids will love:",
        'add_photo': "📸 Send a photo of this place now!",
        'add_location': "🗺️ Share a Yandex Maps link to this place:",
        'translation_error': "🔍 Oops! Translation magic failed. Try again later!",
        'invalid_link': "⚠️ That doesn't look like a valid link. Please send a proper Yandex Maps URL:",
        'photo_error': "📷 Oh no! Couldn't save the photo. Try again!",
        'add_success': "🌟 New magical place added! Now everyone can find it!",
        'permission_denied': "🛑 Only master wizards can do that!",
        'cancel': "✨ Magic operation cancelled!",
        'random_sight': "🎲 Let's explore a random magical place!",
        'show_location': "🗺️ Show on Map",
        'no_sights': "😞 No magical places found yet!",
        'list_title': "📚 Magical Places List (Page {page}):",
        'details_button': "🔍 Details",
        'prev_button': "⬅️ Previous",
        'next_button': "➡️ Next",
        'back_list': "📜 Back to List"
    },
    'ru': {
        'welcome': "🌍 Выберите язык / Choose your language:",
        'start_message': (
            "🎉 Добро пожаловать в бота 'Арктические приключения'! 🐻❄️\n\n"
            "Давайте исследуем Архангельскую область вместе!\n\n"
            "🌟 А вы знали?\n"
            "• Здесь видят Северное сияние! 🌌\n"
            "• Есть 300-летние деревянные дома! 🏚️\n"
            "• Можно встретить настоящих оленей! 🦌\n"
            "• Область больше Франции! 🇫🇷\n\n"
            "Напишите /help чтобы увидеть возможности!"
        ),
        'help': (
            "🦊 Вот что я умею:\n\n"
            "/start - Начать путешествие! 🚀\n"
            "/help - Показать справку 📖\n"
            "/lang - Изменить язык 🌐\n"
            "/dev - О боте 🤖\n"
            "/rand - Случайное волшебное место 🎲\n"
            "/list - Список всех мест 📜\n"  # New line
            "/add - Добавить волшебные места (Только для волшебников) ✨\n"
            "/del - Удалить волшебные места (Только для волшебников) 🧹\n\n"
            "Давайте исследовать северные чудеса вместе! ❄️"
        ),
        'del_start': "🧹 Какое волшебное место должно исчезнуть? Напиши его название:",
        'del_confirm': "Точно удалить {name}? Это не обратимо! ✨",
        'del_success': "🧙♂️ Пуф! {name} исчезло с карты!",
        'del_fail': "🔍 Хм... Не могу найти {name} в своей книге заклинаний",
        'del_cancel': "✨ Магия удаления остановлена!",
        'del_list': "🔮 Найдены волшебные места:",
        'lang_change': "🌍 Выберите язык:",
        'dev_info': (
            "🤖 Бот-исследователь Арктики\n"
            "Версия: 1.0 🧊\n"
            "Сделано с ❤️ командой 'Полярные медведи'\n"
            "🛠️ Как я работаю:\n"
            "- Python Магия 🐍\n"
            "- Телеграм технологии 📲\n"
            "- Северный дух 🧊\n\n"
            "Я постоянно учусь новым трюкам! 🎩"
        ),
        'error': "❄️ Упс! Что-то растаяло... Попробуйте снова!",
        'add_name': "🏰 Как называется это волшебное место?",
        'add_description': "📖 Опиши это место весело, для детей:",
        'add_funfact': "🎩 Поделись интересным фактом, который понравится детям:",
        'add_photo': "📸 Отправь фотографию этого места!",
        'add_location': "🗺️ Отправь ссылку на Yandex Maps:",
        'translation_error': "🔍 Ой! Перевод не удался. Попробуйте позже!",
        'invalid_link': "⚠️ Это не похоже на правильную ссылку. Отправь корректную ссылку Yandex Maps:",
        'photo_error': "📷 Ой! Не удалось сохранить фото. Попробуй еще раз!",
        'add_success': "🌟 Новое волшебное место добавлено! Теперь все могут его найти!",
        'permission_denied': "🛑 Только главные волшебники могут это делать!",
        'cancel': "✨ Волшебная операция отменена!",
        'random_sight': "🎲 Давайте исследуем случайное волшебное место!",
        'show_location': "🗺️ Показать на карте",
        'list_title': "📚 Список волшебных мест (Страница {page}):",
        'no_sights': "😞 Пока нет волшебных мест!",
        'details_button': "🔍 Подробнее",
        'prev_button': "⬅️ Назад",
        'next_button': "➡️ Вперед",
        'back_list': "📜 Назад к списку"
    }
}

# Create images directory if not exists
os.makedirs(IMAGES_DIR, exist_ok=True)

# Conversation states
NAME, DESCRIPTION, FUN_FACT, PHOTO, LOCATION = range(5)

# Conversation states for deletion
DEL_NAME, DEL_CONFIRM = range(2)


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("English 🇬🇧", callback_data='en'),
            InlineKeyboardButton("Русский 🇷🇺", callback_data='ru')
        ]
    ]
    update.message.reply_text(
        text=TRANSLATIONS['en']['welcome'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def help_command(update: Update, context: CallbackContext) -> None:
    lang = context.user_data.get('lang', 'en')
    help_text = TRANSLATIONS[lang]['help']

    # Remove /add line for non-admins
    if update.effective_user.id not in WHITELIST:
        help_text = help_text.replace("/add - Add new magic places (Wizards only) ✨\n", "")
        help_text = help_text.replace("/add - Добавить волшебные места (Только для волшебников) ✨\n", "")

    update.message.reply_text(help_text)


def lang_command(update: Update, context: CallbackContext) -> None:
    lang = context.user_data.get('lang', 'en')
    keyboard = [
        [
            InlineKeyboardButton("English 🇬🇧", callback_data='en'),
            InlineKeyboardButton("Русский 🇷🇺", callback_data='ru')
        ]
    ]
    update.message.reply_text(
        text=TRANSLATIONS[lang]['lang_change'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def dev_command(update: Update, context: CallbackContext) -> None:
    lang = context.user_data.get('lang', 'en')
    update.message.reply_text(TRANSLATIONS[lang]['dev_info'])


def random_sight(update: Update, context: CallbackContext) -> None:
    lang = context.user_data.get('lang', 'en')

    try:
        with open(SIGHTS_FILE, 'r') as f:
            sights = json.load(f)['sights']

        if not sights:
            update.message.reply_text(TRANSLATIONS[lang]['no_sights'])
            return

        sight = random.choice(sights)

        # Prepare message
        caption = (
            f"✨ *{escape_markdown(sight['name'][lang], version=2)}*\n\n"
            f"📖 {escape_markdown(sight['description'][lang], version=2)}\n\n"
            f"🎩 {escape_markdown(sight['fun_fact'][lang], version=2)}"
        )

        # Create location button
        keyboard = [[InlineKeyboardButton(
            TRANSLATIONS[lang]['show_location'],
            url=sight['location']
        )]]

        # Send photo with caption
        try:
            photo_path = os.path.join(IMAGES_DIR, sight['photo'])
            with open(photo_path, 'rb') as photo_file:
                update.message.reply_photo(
                    photo=InputFile(photo_file),
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='MarkdownV2'
                )
        except Exception as e:
            logger.error(f"Photo error: {str(e)}")
            update.message.reply_text(
                caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MarkdownV2'
            )

    except Exception as e:
        logger.error(f"Random sight error: {str(e)}")
        update.message.reply_text(TRANSLATIONS[lang]['error'])


def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    lang = query.data
    context.user_data['lang'] = lang

    # Edit original message to remove language buttons
    query.edit_message_text(text=f"🌐 Language set to {lang.upper()}!")

    # Send main welcome message
    query.message.reply_text(
        text=TRANSLATIONS[lang]['start_message'],
        parse_mode='Markdown'
    )


def error_handler(update: Update, context: CallbackContext) -> None:
    lang = context.user_data.get('lang', 'en')
    logger.error(msg="Exception while handling update:", exc_info=context.error)

    try:
        if update.message:
            update.message.reply_text(TRANSLATIONS[lang]['error'])
        else:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=TRANSLATIONS[lang]['error']
            )
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")


def sanitize_filename(name):
    # Remove special characters and format for filename
    name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', name)


def translate_text(text, source_lang, target_lang):
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        return None


def add_start(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    if user_id not in WHITELIST:
        lang = context.user_data.get('lang', 'en')
        update.message.reply_text(TRANSLATIONS[lang]['permission_denied'])
        return ConversationHandler.END

    context.user_data['new_sight'] = {}
    lang = context.user_data.get('lang', 'en')
    update.message.reply_text(TRANSLATIONS[lang]['add_name'])
    return NAME


def handle_name(update: Update, context: CallbackContext) -> int:
    user_lang = context.user_data.get('lang', 'en')
    other_lang = 'ru' if user_lang == 'en' else 'en'
    name = update.message.text

    # Translate name
    translated_name = translate_text(name, user_lang, other_lang)
    if not translated_name:
        update.message.reply_text(TRANSLATIONS[user_lang]['translation_error'])
        return ConversationHandler.END

    # Store names
    context.user_data['new_sight']['name'] = {
        user_lang: name,
        other_lang: translated_name
    }

    update.message.reply_text(TRANSLATIONS[user_lang]['add_description'])
    return DESCRIPTION


def handle_description(update: Update, context: CallbackContext) -> int:
    user_lang = context.user_data.get('lang', 'en')
    other_lang = 'ru' if user_lang == 'en' else 'en'
    description = update.message.text

    # Translate description
    translated_desc = translate_text(description, user_lang, other_lang)
    if not translated_desc:
        update.message.reply_text(TRANSLATIONS[user_lang]['translation_error'])
        return ConversationHandler.END

    context.user_data['new_sight']['description'] = {
        user_lang: description,
        other_lang: translated_desc
    }

    update.message.reply_text(TRANSLATIONS[user_lang]['add_funfact'])
    return FUN_FACT


def handle_funfact(update: Update, context: CallbackContext) -> int:
    user_lang = context.user_data.get('lang', 'en')
    other_lang = 'ru' if user_lang == 'en' else 'en'
    funfact = update.message.text

    # Translate fun fact
    translated_funfact = translate_text(funfact, user_lang, other_lang)
    if not translated_funfact:
        update.message.reply_text(TRANSLATIONS[user_lang]['translation_error'])
        return ConversationHandler.END

    context.user_data['new_sight']['fun_fact'] = {
        user_lang: funfact,
        other_lang: translated_funfact
    }

    update.message.reply_text(TRANSLATIONS[user_lang]['add_photo'])
    return PHOTO


def handle_photo(update: Update, context: CallbackContext) -> int:
    user_lang = context.user_data.get('lang', 'en')
    try:
        # Get the highest resolution photo
        photo_file = update.message.photo[-1].get_file()

        # Get English name for filename
        en_name = context.user_data['new_sight']['name'].get('en')
        if not en_name:  # If user was using Russian
            en_name = context.user_data['new_sight']['name']['ru']

        # Generate filename
        filename = f"{sanitize_filename(en_name)}.jpg"
        file_path = os.path.join(IMAGES_DIR, filename)

        # Download and save photo
        photo_file.download(file_path)
        context.user_data['new_sight']['photo'] = filename

        update.message.reply_text(TRANSLATIONS[user_lang]['add_location'])
        return LOCATION

    except Exception as e:
        logging.error(f"Photo error: {str(e)}")
        update.message.reply_text(TRANSLATIONS[user_lang]['photo_error'])
        return ConversationHandler.END


def handle_location(update: Update, context: CallbackContext) -> int:
    user_lang = context.user_data.get('lang', 'en')
    location = update.message.text

    # Basic URL validation
    if not location.startswith(('http://', 'https://')):
        update.message.reply_text(TRANSLATIONS[user_lang]['invalid_link'])
        return LOCATION

    context.user_data['new_sight']['location'] = location

    # Save to JSON
    try:
        with open(SIGHTS_FILE, 'r+') as f:
            data = json.load(f)
            context.user_data['new_sight']['id'] = len(data['sights']) + 1
            data['sights'].append(context.user_data['new_sight'])
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception as e:
        logging.error(f"Save error: {str(e)}")
        return ConversationHandler.END

    update.message.reply_text(TRANSLATIONS[user_lang]['add_success'])
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    lang = context.user_data.get('lang', 'en')
    update.message.reply_text(TRANSLATIONS[lang]['cancel'])
    return ConversationHandler.END


def del_start(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    if user_id not in WHITELIST:
        lang = context.user_data.get('lang', 'en')
        update.message.reply_text(TRANSLATIONS[lang]['permission_denied'])
        return ConversationHandler.END

    lang = context.user_data.get('lang', 'en')
    update.message.reply_text(TRANSLATIONS[lang]['del_start'])
    return DEL_NAME


def handle_del_name(update: Update, context: CallbackContext) -> int:
    lang = context.user_data.get('lang', 'en')
    search_name = update.message.text.strip().lower()

    with open(SIGHTS_FILE, 'r') as f:
        sights = json.load(f)['sights']

    # Find matches in both languages
    matches = []
    for sight in sights:
        if (search_name in sight['name']['en'].lower() or
                search_name in sight['name']['ru'].lower()):
            matches.append(sight)

    if not matches:
        update.message.reply_text(TRANSLATIONS[lang]['del_fail'].format(name=search_name))
        return ConversationHandler.END

    context.user_data['del_candidates'] = matches

    if len(matches) == 1:
        sight = matches[0]
        keyboard = [
            [InlineKeyboardButton("✅ Yes", callback_data='del_confirm'),
             InlineKeyboardButton("❌ No", callback_data='del_cancel')]
        ]
        update.message.reply_text(
            TRANSLATIONS[lang]['del_confirm'].format(name=sight['name'][lang]),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return DEL_CONFIRM
    else:
        text = [TRANSLATIONS[lang]['del_list']]
        for idx, sight in enumerate(matches, 1):
            text.append(f"{idx}. {sight['name'][lang]}")
        update.message.reply_text("\n".join(text))
        update.message.reply_text(TRANSLATIONS[lang]['del_start'])
        return DEL_NAME


def handle_del_confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    lang = context.user_data.get('lang', 'en')

    if query.data == 'del_cancel':
        query.edit_message_text(TRANSLATIONS[lang]['del_cancel'])
        return ConversationHandler.END

    # Get first match (for simplicity, could implement selection)
    sight = context.user_data['del_candidates'][0]

    # Remove from JSON
    with open(SIGHTS_FILE, 'r+') as f:
        data = json.load(f)
        data['sights'] = [s for s in data['sights'] if s['id'] != sight['id']]
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    # Remove associated image
    try:
        if 'photo' in sight:
            os.remove(os.path.join(IMAGES_DIR, sight['photo']))
    except Exception as e:
        logging.error(f"Error deleting image: {str(e)}")

    query.edit_message_text(TRANSLATIONS[lang]['del_success'].format(name=sight['name'][lang]))
    return ConversationHandler.END


def list_sights(update: Update, context: CallbackContext) -> None:
    lang = context.user_data.get('lang', 'en')

    try:
        with open(SIGHTS_FILE, 'r') as f:
            sights = json.load(f)['sights']

        if not sights:
            update.message.reply_text(TRANSLATIONS[lang]['no_sights'])
            return

        context.user_data['current_page'] = 0
        show_sight_list(update, context, sights, 0, lang)

    except Exception as e:
        logger.error(f"List error: {str(e)}")
        update.message.reply_text(TRANSLATIONS[lang]['error'])


def show_sight_list(update, context, sights, page, lang):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_sights = sights[start:end]

    keyboard = []
    for idx, sight in enumerate(page_sights, start + 1):
        keyboard.append([
            InlineKeyboardButton(
                f"{idx}. {sight['name'][lang]}",
                callback_data=f"details_{sight['id']}"
            )
        ])

    # Add navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            TRANSLATIONS[lang]['prev_button'],
            callback_data=f"page_{page - 1}"
        ))
    if end < len(sights):
        nav_buttons.append(InlineKeyboardButton(
            TRANSLATIONS[lang]['next_button'],
            callback_data=f"page_{page + 1}"
        ))

    if nav_buttons:
        keyboard.append(nav_buttons)

    text = TRANSLATIONS[lang]['list_title'].format(page=page + 1)

    try:
        if update.callback_query:
            # Edit existing message if possible
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            # Send new message if editing failed
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )


def handle_list_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    lang = context.user_data.get('lang', 'en')
    data = query.data

    try:
        with open(SIGHTS_FILE, 'r') as f:
            sights = json.load(f)['sights']

        if data.startswith('page_'):
            page = int(data.split('_')[1])
            show_sight_list(update, context, sights, page, lang)

        elif data.startswith('details_'):
            sight_id = int(data.split('_')[1])
            sight = next(s for s in sights if s['id'] == sight_id)
            show_sight_details(update, context, sight, lang)

        elif data == 'back_to_list':
            page = context.user_data.get('current_page', 0)
            show_sight_list(update, context, sights, page, lang)

    except Exception as e:
        logger.error(f"List callback error: {str(e)}")
        try:
            # Send new message instead of editing
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text=TRANSLATIONS[lang]['error']
            )
        except Exception as send_error:
            logger.error(f"Error sending error message: {str(send_error)}")


def show_sight_details(update, context, sight, lang):
    try:
        caption = (
            f"✨ *{escape_markdown(sight['name'][lang], version=2)}*\n\n"
            f"📖 {escape_markdown(sight['description'][lang], version=2)}\n\n"
            f"🎩 {escape_markdown(sight['fun_fact'][lang], version=2)}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    TRANSLATIONS[lang]['show_location'],
                    url=sight['location']
                ),
                InlineKeyboardButton(
                    TRANSLATIONS[lang]['back_list'],
                    callback_data='back_to_list'
                )
            ]
        ]

        try:
            photo_path = os.path.join(IMAGES_DIR, sight['photo'])
            with open(photo_path, 'rb') as photo_file:
                # Send as new message instead of editing
                context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=InputFile(photo_file),
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='MarkdownV2'
                )
        except Exception as e:
            logger.error(f"Detail photo error: {str(e)}")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MarkdownV2'
            )

    except Exception as e:
        logger.error(f"Detail error: {str(e)}")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TRANSLATIONS[lang]['error']
        )


def main() -> None:
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    updater = Updater(token='YOUR_BOT_TOKEN')

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, handle_name)],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, handle_description)],
            FUN_FACT: [MessageHandler(Filters.text & ~Filters.command, handle_funfact)],
            PHOTO: [MessageHandler(Filters.photo & ~Filters.command, handle_photo)],
            LOCATION: [MessageHandler(Filters.text & ~Filters.command, handle_location)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    del_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('del', del_start)],
        states={
            DEL_NAME: [MessageHandler(Filters.text & ~Filters.command, handle_del_name)],
            DEL_CONFIRM: [CallbackQueryHandler(handle_del_confirm, pattern='^(del_confirm|del_cancel)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    # Add handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('lang', lang_command))
    dispatcher.add_handler(CommandHandler('dev', dev_command))
    dispatcher.add_handler(CommandHandler('rand', random_sight))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(del_conv_handler)
    dispatcher.add_handler(CommandHandler('list', list_sights))
    dispatcher.add_handler(CallbackQueryHandler(handle_list_callback, pattern='^(page_|details_|back_to_list)'))
    dispatcher.add_handler(CallbackQueryHandler(button_click, pattern='^(en|ru)$'))

    # Error handling
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()