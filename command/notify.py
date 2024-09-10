from apprise import Apprise
from telegram import Update
from telegram.ext import ContextTypes

from base.data import localDict
from base.debug import eprint
from base.log import logger

channels = localDict('channels', digit_mode=True)

SUPPORT_CHANNELS = {
    'Bark': {'protocols': ['bark', 'barks'], 'url': 'https://github.com/caronc/apprise/wiki/Notify_bark', },
    'Feishu': {'protocols': ['feishu'], 'url': 'https://github.com/caronc/apprise/wiki/Notify_feishu', },
    'Ntfy': {'protocols': ['ntfy'], 'url': 'https://github.com/caronc/apprise/wiki/Notify_ntfy', },
    'WeCom Bot': {'protocols': ['wecombot'], 'url': 'https://github.com/caronc/apprise/wiki/Notify_wecombot', },
    'WxPusher': {'protocols': ['wxpusher'], 'url': 'https://github.com/caronc/apprise/wiki/Notify_wxpusher', },
}

HELP_TEXT = 'Supported protocols are now:\n'
SUPPORT_PROTOCOLS = []
for channel in SUPPORT_CHANNELS:
    HELP_TEXT += f'- [{channel}]({SUPPORT_CHANNELS[channel]["url"]})\n'
    SUPPORT_PROTOCOLS += SUPPORT_CHANNELS[channel]['protocols']


async def channel_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in channels:
        await update.effective_message.reply_text('No notification channel added.')
        return
    text = 'Notification channels:\n'
    for channel in channels[chat_id]:
        text += f'{channel}\n'
    await update.effective_message.reply_text(text)


async def channel_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    # every chat can only have three channels at most
    if chat_id in channels and len(channels[chat_id]) >= 3:
        await update.effective_message.reply_text('You can only add three channels at most. Please delete some before adding new ones.')
        return

    logger.debug(
        f'chat_id: {chat_id}, action: channel_add, args: {context.args}')
    arg: str = " ".join(context.args)
    if arg == '':
        await update.effective_message.reply_text(
            text=(
                'Please provide a URL.\n\n'
                f'{HELP_TEXT}'
            ),
            disable_web_page_preview=True,
            parse_mode='Markdown'
        )
        return
    # arg should be a url, check if it is a valid url
    try:
        assert "://" in arg
        protocol = arg.split("://")[0]
        assert protocol in SUPPORT_PROTOCOLS
    except Exception:
        await update.effective_message.reply_text(
            text=(
                'Invalid URL.\n\n'
                f'{HELP_TEXT}'
            ),
            disable_web_page_preview=True,
            parse_mode='Markdown'
        )
        return
    if chat_id not in channels:
        channels[chat_id] = []
    channels[chat_id].append(arg)
    channels.dump()
    await update.effective_message.reply_text('Notification channel added.')


async def channel_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in channels or len(channels[chat_id]) == 0:
        await update.effective_message.reply_text('No notification channel added.')
        return

    logger.debug(
        f'chat_id: {chat_id}, action: channel_del, args: {context.args}')
    arg: str = " ".join(context.args)
    if arg == '':
        await update.effective_message.reply_text('Please provide a URL.\n\n')
        return
    if arg not in channels[chat_id]:
        await update.effective_message.reply_text('Channel not found.')
        return
    channels[chat_id].remove(arg)
    if len(channels[chat_id]) == 0:
        del channels[chat_id]
    channels.dump()
    await update.effective_message.reply_text('Notification channel deleted.')


async def channel_notify(chat_id: int, title: str, body: str) -> None:
    if chat_id not in channels:
        return
    try:
        ret = Apprise(servers=channels[chat_id]).notify(title=title, body=body)
        logger.debug(f'channel_notify: {ret}')
    except Exception as e:
        eprint(e)
        return
