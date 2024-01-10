import logging

from telegram import Bot

from base.debug import try_except


@try_except(level=logging.DEBUG, return_value=False)
async def delete_message(bot: Bot, chat_id: int, message_id: int, **kwargs):
    """
    Delete a message.
    Return True if successful, False otherwise.
    """
    await bot.delete_message(chat_id=chat_id, message_id=message_id, **kwargs)


@try_except(level=logging.DEBUG, return_value=False)
async def send_message(bot: Bot, chat_id: int, text: str, **kwargs):
    """
    Send a message.
    Return True if successful, False otherwise.
    """
    await bot.send_message(chat_id=chat_id, text=text, **kwargs)
