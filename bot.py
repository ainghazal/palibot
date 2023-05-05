#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

from operator import itemgetter

from telegram import __version__ as TG_VER

# for fuzzy-matching strings
import jaro

TOKEN = os.getenv('TOKEN')

BANNED = ['Opera VPN',
 'Vypr VPN',
 'Hola VPN',
 'Ipvanish VPN',
 'Keepsolid VPN',
 'Nord VPN',
 'Speedify VPN',
 'Express VPN',
 'RedShield VPN',
 'Tunnelbear',
 'Hidemyass',
 'Trustzone',
 'Krot',
 'Psiphon',
 'Thunder VPN',
 'Torguard',
 'Tachoyn VPN',
 'Lantern',
 'X-VPN',
 'WarpVPN',
 'PrivateTunnel',
 'Betternet',
 'Secure VPN',
 'VPN Master',
 'Super VPN',
 'TouchVPN',
 'SkyVPN',
 'Security Master',
 'Turbo VPN',
 'Протокол openVPN',
 'VPN Proxy Master',
 'Browsec VPN',
 'vpn-super unlimited proxy',
 'Melon VPN',
 'Windscribe VPN',
 'VPN RedCat secure unlimited',
 'Proton VPN',
 'AdGuard VPN',
 'Antivirus - Cleaner + VPN',
 'Atlas VPN',
 'BigMama VPN',
 'Gecko VPN',
 'GO VPN',
 'HotBot VPN',
 'Key VPN',
 'Kuto VPN',
 'Near VPN',
 'Ravo VPN',
 'Riseup VPN',
 'SoloVPN',
 'Tik VPN',
 'Tiny VPN',
 'Tube VPN',
 'UFO VPN',
 'Ultimate VPN',
 'VeilDuck VPN',
 'VPN GO',
 'VPN_Lat',
 'VPN_Private',
 'Vpnify']


CUTOFF = 0.6


def get_closer_provider_match(name):
    scores = [[x, jaro.jaro_winkler_metric(name, x)] for x in BANNED]
    top = sorted(filter(lambda x: x[1] > CUTOFF, scores), key=itemgetter(1), reverse=True)
    if len(top) > 0:
        return top[0][0]
    return ""


try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CONFIRM, PROVIDER, LOCATION, QUALITY = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["Yes", "No"]]

    await update.message.reply_text(
        "Hi! My name is VPNMeterBot. I will hold a conversation with you, and use your input to survey the quality of VPN tools. "
        "Send /cancel to stop talking to me at any moment.\n\n"
        "Are you here to report about the quality of a VPN tool?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes or No?"
        ),
    )

    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected confirmation and asks for a location ."""
    user = update.message.from_user
    logger.info("Confirmation for %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "I see! Please send me the VPN provider you're reporting about",
        reply_markup=ReplyKeyboardRemove(),
    )

    return PROVIDER


async def provider(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the provider and asks for a location."""
    user = update.message.from_user
    provider = update.message.text
    logger.info("User entered provider: %s", provider)
    msg = "Thank you! If you feel comfortable, you can now share your location, or send /skip if you don't want to."

    banned = False
    if provider in BANNED:
        banned = True
    else:
        _provider = get_closer_provider_match(provider)
        if _provider:
            logger.info("Assuming user meant: %s", _provider)
            provider = _provider
            banned = True

    if banned:
        logger.info("This provider is known to be banned")
        msg = "That provider is known to be blocked!\n" + msg

    await update.message.reply_text(
            msg
    )

    return LOCATION


async def skip_provider(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the provider and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a provider.", user.first_name)
    await update.message.reply_text(
        "Send me your location please, or send /skip."
    )

    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for quality."""
    user = update.message.from_user
    # TODO: how to receive location?
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    await update.message.reply_text(
        "Thank you! Now, can you evaluate the quality of this VPN?"
    )

    return QUALITY


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)

    reply_keyboard = [["BAD", "MEDIOCRE", "GOOD!"]]

    await update.message.reply_text(
        "How would you describe the quality of this VPN?", 
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="How do you rate the quality?"
        ),
    )

    return QUALITY


async def quality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the quality and ends the conversation."""
    user = update.message.from_user
    logger.info("Quality for %s: %s", user.first_name, update.message.text)

    await update.message.reply_text("Thank you for your time! Please report again whenever you feel like.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope to receive more reports any other day!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states CONFIRM, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONFIRM: [MessageHandler(filters.Regex("^(Yes|No)$"), confirm)],
            PROVIDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, provider)],
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
            ],
            QUALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, quality)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
