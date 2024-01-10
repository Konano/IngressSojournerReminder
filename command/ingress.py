import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from base.data import localDict
from base.log import logger
from base.message import delete_message, send_message

records = localDict('records', digit_mode=True)


SIGNIN_KEYBOARD = InlineKeyboardMarkup([[
    InlineKeyboardButton('Already hacked', callback_data='HACK')]])


async def start_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat.id
    if chat in records:
        await update.effective_message.reply_text('You have already started.')
        return
    rc = {'ts': 0, 'dh': -1}
    text = \
        "Welcome to use Ingress Sojourner Reminder!\n\n" \
        "This bot will remind you to hack a portal in Ingress to prevent you from losing your Sojourner Streak.\n" \
        "You can use /hacked to refresh the hack interval, or you can click the button below the alert to refresh it.\n" \
        "*Remember: Press the button no later than 30 minutes after your hack!*\n\n" \
        "After you have hacked any Ingress portal, click the button below to refresh your record."
    await update.effective_message.reply_text(text, reply_markup=SIGNIN_KEYBOARD, parse_mode='Markdown')
    records.set(chat, rc)
    logger.info(f'START {chat}:{update.effective_chat.effective_name}')


async def cancel_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat.id
    records.delete(chat)
    await update.effective_message.reply_text('You have canceled the reminder. If you want to use it again, please /start.')
    logger.info(f'CANCEL {chat}:{update.effective_chat.effective_name}')


async def already_hacked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat.id
    if chat not in records:
        await update.effective_message.reply_text('Please /start first.')
        return
    if update.callback_query is None:
        await update.effective_message.reply_text('Refresh Ingress Sojourner Reminder OK!')
    else:
        await update.callback_query.answer('Refresh Ingress Sojourner Reminder OK!')
    rc = records[chat]
    if 'alert' in rc:
        await delete_message(context.bot, chat, rc['alert'])
    rc = {'ts': int(time.time() - 1800), 'dh': 0}
    records.set(chat, rc)
    logger.info(f'HACK {chat}:{update.effective_chat.effective_name}')


async def reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    removed_chat = []
    for chat in records:
        rc = records[chat]
        delta_hours = (int(time.time()) - rc['ts']) // 60 // 60
        if delta_hours == rc['dh'] or rc['dh'] == -1:
            continue
        rc['dh'] = delta_hours
        if delta_hours >= 36:
            if 'alert' in rc:
                await delete_message(context.bot, chat, rc['alert'])
                del rc["alert"]
            text = "Sorry, you lost your Sojourner Streak. Please /start to try again."
            await send_message(context.bot, chat, text)
            removed_chat.append(chat)
        elif delta_hours >= 24:
            if delta_hours < 30:
                text = (f'You have not hacked any portals in Ingress for *{delta_hours}* hours, '
                        'please hack immediately!')
            else:
                text = (f'🔴⚠️🔴⚠️🔴\nYou have not hacked any portals in Ingress for *{delta_hours}* hours, '
                        'please hack immediately!\n🔴⚠️🔴⚠️🔴')
            try:
                msg = await context.bot.send_message(chat, text, reply_markup=SIGNIN_KEYBOARD, parse_mode='Markdown')
                if 'alert' in rc:
                    await delete_message(context.bot, chat, rc['alert'])
                rc['alert'] = msg.message_id
                records.set(chat, rc)
            except Exception as e:
                logger.error(f'Error when sending message to {chat}: {e}')
                removed_chat.append(chat)
        else:
            if 'alert' in rc:
                await delete_message(context.bot, chat, rc['alert'])
                del rc['alert']
                records.set(chat, rc)
    for chat in removed_chat:
        records.delete(chat)
