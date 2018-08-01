from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import telegram
import json
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

admins = [10086747, 23616716, 34419226]  # Nico, Uba, Fede
raid = {}


def load_json(filename):
    """Load the data contained in a JSON file into a Python dictionary."""
    with open(filename + '.json') as f:
        return json.load(f)


def save_json(filename, data):
    """Save the data of a Python dictionary into a JSON file."""
    with open(filename + '.json', 'w') as f:
        json.dump(data, f)


def findWholeWord(target, text):
    return re.compile(r'\b({0})\b'.format(target), flags=re.IGNORECASE).search(text) is not None


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!', quote=True)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def admin_functions(bot, update):
    """Called only if the chat_id passes the filter of admin IDs."""
    update.message.reply_text('This is some admin function.', quote=True)


def search_text(bot, update):
    """Called for every text that isn't a command, searches a precise word in the message."""
    if findWholeWord("arezzo", update.message.text):
        update.message.reply_text('Ar...cosa?', quote=True)
    print(update)


def raid_organizer(bot, update):
    keyboard = [[InlineKeyboardButton("Divora-Mondi", callback_data='divoramondi')],
                [InlineKeyboardButton("Pinnacolo Siderale", callback_data='pinnacolo')],
                [InlineKeyboardButton("Leviatano", callback_data='leviatano')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Seleziona il raid che vuoi organizzare:', reply_markup=reply_markup)


def choose_day(bot, query):
    global raid
    raid = {'type': "{}".format(query.data), 'day': None, 'players': {'yes': [], 'no': [], 'maybe': []}}

    keyboard = [[InlineKeyboardButton("Lun", callback_data='Lunedì'), InlineKeyboardButton("Mar", callback_data='Martedì'),
                 InlineKeyboardButton("Mer", callback_data='Mercoledì')], [InlineKeyboardButton("Gio", callback_data='Giovedì'),
                 InlineKeyboardButton("Ven", callback_data='Venerdì'), InlineKeyboardButton("Sab", callback_data='Sabato')],
                [InlineKeyboardButton("Dom", callback_data='Domenica')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.edit_message_text(text="Raid selezionato: {}".format(query.data) + "\n\nSeleziona il giorno:",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup)


def get_participants(bot, query):
    global raid
    first_time = False
    if raid['day'] is None:
        raid['day'] = "{}".format(query.data)
        first_time = True

    keyboard = [[InlineKeyboardButton("Presente", callback_data='yes')],
                [InlineKeyboardButton("Forse", callback_data='maybe')],
                [InlineKeyboardButton("Assente", callback_data='no')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if first_time:
        bot.edit_message_text(text=query.message.text + "\n\nGiorno stabilito: " + raid['day'],
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)


def update_participants(bot, query):
    vote = "{}".format(query.data)
    for key in raid['players']:
        if query.from_user.first_name in raid['players'][key]:
            raid['players'][key].remove(query.from_user.first_name)

    raid['players'][vote].append(query.from_user.first_name)

    keyboard = [[InlineKeyboardButton("Presente", callback_data='yes')],
                [InlineKeyboardButton("Forse", callback_data='maybe')],
                [InlineKeyboardButton("Assente", callback_data='no')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.edit_message_text(text="Raid selezionato: " + raid['type'] + "\nGiorno stabilito: " + raid['day'] +
                          "\n\nPresenti: " + print_list(raid['players']['yes']) + "\nForse: " +
                          print_list(raid['players']['maybe']) + "\nAssenti: " + print_list(raid['players']['no']),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup)


def inline_button(bot, update):
    query = update.callback_query
    choice = "{}".format(query.data)

    if choice in ['divoramondi', 'pinnacolo', 'leviatano'] and query.from_user.id in admins:
        choose_day(bot, query)
    elif choice in ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']\
            and query.from_user.id in admins:
        get_participants(bot, query)
    elif choice in ['yes', 'maybe', 'no']:
        update_participants(bot, query)


def print_list(a_list):
    string = ""
    for item in a_list:
        string += item + "\n"
    return string


def main():
    updater = Updater("BOT-TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", admin_functions, filters=Filters.user(admins)))
    dp.add_handler(CommandHandler("raid", raid_organizer, filters=Filters.user(admins)))
    dp.add_handler(CallbackQueryHandler(inline_button))

    dp.add_handler(MessageHandler(Filters.text, search_text))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
