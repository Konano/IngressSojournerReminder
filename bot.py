import logging

from pytz import timezone
from telegram import BotCommand, BotCommandScopeAllPrivateChats, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, JobQueue)

from base import network
from base.config import WEBHOOK, accessToken, heartbeatURL
from base.debug import try_except
from base.log import logger
from command.ingress import (already_hacked, cancel_reminder, records,
                             reminder, start_reminder)
from command.notify import channel_add, channel_del, channel_list


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error for debuging."""
    logger.error("Exception while handling an update: %s", context.error)
    logger.debug(msg="The traceback of the exception:", exc_info=context.error)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    logger.debug(update_str)

    if update is not None:
        records.delete(update.effective_chat.id)


@try_except(level=logging.DEBUG, return_value=False)
async def heartbeat(context: ContextTypes.DEFAULT_TYPE) -> None:
    if heartbeatURL is not None:
        await network.get(heartbeatURL)


def main() -> None:
    """Start the bot."""
    app: Application = Application.builder().token(accessToken).build()

    app.add_error_handler(error_handler)

    job: JobQueue = app.job_queue
    tz = timezone("Asia/Shanghai")  # local_tz
    jk = {"misfire_grace_time": None}  # job_kwargs

    job.run_repeating(heartbeat, interval=60, first=0, job_kwargs=jk)

    async def context_init(context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.debug("Set bot commands.")
        await context.bot.set_my_commands([
            BotCommand('hacked', 'Refresh reminder'),
            BotCommand('start', 'Start reminder'),
            BotCommand('cancel', 'Cancel reminder'),
            BotCommand('list', 'List all notification channels'),
            BotCommand('add', 'Add a notification channel'),
            BotCommand('del', 'Delete a notification channel')],
            scope=BotCommandScopeAllPrivateChats())
    job.run_once(context_init, 0)

    app.add_handler(CommandHandler('start', start_reminder))
    app.add_handler(CommandHandler('cancel', cancel_reminder))

    job.run_repeating(reminder, interval=60, first=1, job_kwargs=jk)
    # 刷新 Ingress 签到时间间隔（按钮）
    app.add_handler(CallbackQueryHandler(already_hacked, pattern='HACK'))
    # 刷新 Ingress 签到时间间隔（命令）
    app.add_handler(CommandHandler('hacked', already_hacked))

    # 列出所有通知渠道
    app.add_handler(CommandHandler('list', channel_list))
    # 添加或删除通知渠道
    app.add_handler(CommandHandler('add', channel_add))
    app.add_handler(CommandHandler('del', channel_del))

    app.run_webhook(**WEBHOOK)


if __name__ == "__main__":
    main()
