from Config import Config
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class Telegram:
    def __init__(self, faceRecog, db):
        self.faceRecog = faceRecog
        self.db = db
        self.updater = Updater(Config.TG_TOKEN)
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler("start", self.startHandler))
        self.dp.add_handler(CommandHandler("help", self.helpHandler))
        self.dp.add_handler(CommandHandler("tag", self.tagHandler))
        self.dp.add_handler(MessageHandler(Filters.photo, self.photoHandler))
        self.dp.add_error_handler(self.error)

    def start(self):
        logger.info('started')
        self.updater.start_polling()
        self.updater.idle()

    def startHandler(self, bot, update):
        logger.info('/start')
        self.helpHandler(bot, update)

    def helpHandler(self, bot, update):
        logger.info('/help')
        msg = ('Send me a photo for query.' +
               '\n' +
               'Or use /tag [id] [tag]')
        update.message.reply_text(msg)

    def error(self, bot, update):
        logger.warning('Update "%s" caused error "%s"', update, error)
        update.message.reply_text('Error occurred.')

    def extractArg(self, request):
        try:
            request = request[5:] # Skip /tag[.]
            endIndexOfId = request.index(" ")
            id = request[:endIndexOfId]
            startIndexOfTag = endIndexOfId + 1
            tag = request[startIndexOfTag:]
            return id, tag
        except:
            return None, None

    def tagHandler(self, bot, update):
        logger.info('tag: ' + update.message.text)
        id, tag = self.extractArg(update.message.text)
        if (id == None or tag == None):
            update.message.reply_text('/tag [id] [tag]')
            return
        result = self.db.updateFace(id, tag)
        if (result):
            update.message.reply_text('Updated.')
        else:
            update.message.reply_text('Update failed.')

    def photoHandler(self, bot, update):
        logger.info('photo uploaded by: ' +
            update.message.from_user.first_name + ' - @' +
            update.message.from_user.username )
        self.faceRecog.msg(bot, update.message)
