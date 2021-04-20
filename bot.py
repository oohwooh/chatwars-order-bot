import logging
import os
import random
from logging import debug

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, PicklePersistence

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def opt_in(update: Update, context: CallbackContext) -> None:
    send_start = InlineKeyboardMarkup(
        [[InlineKeyboardButton(url=f'https://t.me/{context.bot.username}?start=1', text='/start')]])

    context.chat_data[update.effective_user.id] = True
    if context.user_data.get('messagable', False):
        update.effective_message.reply_text(
            'You will now recieve a DM when orders are posted, to opt out use /opt_out'
        )
    else:
        update.effective_message.reply_text(
            'To allow me to DM you, please click the button below, '
            'once you do, I will start sending you DMs for new orders',
            reply_markup=send_start
        )


def opt_out(update: Update, context: CallbackContext) -> None:
    context.chat_data.pop(update.effective_user.id)
    update.effective_message.reply_text(
        'You will no longer recieve a DM when orders are posted, to opt back in use /opt_in'
    )


def start(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type == 'private':
        if not context.user_data.get('messagable', False):
            context.user_data['messagable'] = True
            update.effective_chat.send_message('Thanks! You\'re all set to start recieving order notifications!')


def on_message(update: Update, context: CallbackContext) -> None:
    debug('pinned message')
    debug(update)
    debug(update.effective_user)
    if update.effective_user.username.lower() == 'PotatoOrderBot'.lower():
        send_start = InlineKeyboardMarkup(
            [[InlineKeyboardButton(url=f'https://t.me/{context.bot.username}?start=1', text='/start')]])
        for user in context.chat_data:
            try:
                member = update.effective_chat.get_member(user_id=user)
            except telegram.error.BadRequest:
                update.effective_chat.send_message(
                    f'An error occured fetching details for a user (ID {user}) - they have been opted out'
                )
                context.chat_data.pop(user)
                break
            if member.status in ['restricted', 'left', 'kicked']:
                update.effective_chat.send_message(
                    f'{member.user.name} will no longer be notified of orders due to `{member.status}` status'
                )
                context.chat_data.pop(user)
                break
            try:
                if user == 355953948: # Ziah
                    context.bot.send_message(chat_id=user, text=random.choice([
                        'Nya!! 😳😳 Orders have been posted',
                        'H-he-hewwo?? owdews hawe beewn powsted UwU 👉👈💜💜💜💜💜',
                        '👉👈 Heyyyyy haha 😳😳😳 the orders just got posted 🥺🥺🥺🥺🥺🥺',
                        'Hiiiiiiiiiiiiii 👉👈 you should check guild chat for the order',
                        '👉👈 Orders posted, uwu 🥺',
                        'raWr x3 orders posted 🏳️‍⚧️:3',
                        '🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺🥺 orders are in 😳😳',
                        '(„ᵕᴗᵕ„) orders are waiting (◡ w ◡)'
                        '(⁄ʘ⁄ ⁄ ω⁄ ⁄ ʘ⁄)♡ just stopping by to say new orders are in ‿︵*𝓇𝒶𝓌𝓇*‿︵ ʘwʘ']))
                else:
                    context.bot.send_message(chat_id=user, text='🔔Orders posted!')
            except telegram.error.Unauthorized:
                update.effective_chat.send_message(
                    f'{member.user.name}: I was unable to send you a notification DM for orders,\
                     can you please click the button below to allow me to send you messages?'
                    f'\nIf you wish to opt out of order notifications please send /opt_out', reply_markup=send_start)


def new_member(update, context):
    for member in update.message.new_chat_members:
        if member.username == context.bot.username:
            update.message.reply_text('''Hello! 👋
I'm a bot to help members of potato castle not miss orders when they are sent
Use the command /opt_in to get a DM whenever orders are posted!''')


debug('bot starting')
updater = Updater(os.getenv('BOT_TOKEN'), persistence=PicklePersistence(filename='data/bot_data.pkl'))
updater.dispatcher.add_handler(MessageHandler(Filters.status_update.pinned_message, on_message))
updater.dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))
updater.dispatcher.add_handler(CommandHandler('opt_in', opt_in))
updater.dispatcher.add_handler(CommandHandler('opt_out', opt_out))
updater.dispatcher.add_handler(MessageHandler(Filters.chat_type.private, start))
updater.start_polling()
updater.idle()
