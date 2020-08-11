from django.shortcuts import render

# Create your views here.
from django.conf import settings
from telegram import Bot
from telegram import Update
from telegram import KeyboardButton 
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext import ConversationHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import Job
from telegram.ext import JobQueue

from telegram.utils.request import Request
import datetime
from django.http import HttpResponse
from telegram.ext import Dispatcher
from telegram.utils import helpers
import json
from relax.models import Profile
import logging

bot = Bot(settings.TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

def web_hook_view(request):
	if request.method == 'POST':
		dispatcher.process_update(Update.de_json(json.loads(request.body), bot))
		return HttpResponse(status=200)
	return HttpResponse('404 not found')


updater = Updater(
	token=settings.TOKEN,
	use_context=True,
)
#j = updater.job_queue
CALLBACK_BUTTON1_LEFT = "callback_button1_left"
CALLBACK_BUTTON2_RIGHT = "callback_button2_right"

BUTTON1_ARTICLES = "Полезные статьи"
BUTTON1_SIGNS = "Признаки"
BUTTON1_PROF = "Профилактика"
BUTTON1_NAZAD = "Назад"

TITLES = {
	CALLBACK_BUTTON1_LEFT: "Да",
	CALLBACK_BUTTON2_RIGHT: "НЕТ",
	}





def get_keyboard1():
	""" Получить клавиатуру для сообщения
	Эта клавиатура будет видна под каждым сообщением, где её прикрепили
	"""
	# Каждый список внутри `keyboard` -- это один горизонтальный ряд кнопок
	keyboard = [
		# Каждый элемент внутри списка -- это один вертикальный столбец.
		# Сколько кнопок -- столько столбцов
		[
			InlineKeyboardButton(TITLES[CALLBACK_BUTTON1_LEFT], callback_data=CALLBACK_BUTTON1_LEFT),
			InlineKeyboardButton(TITLES[CALLBACK_BUTTON2_RIGHT], callback_data=CALLBACK_BUTTON2_RIGHT),
		],
		]
	return InlineKeyboardMarkup(keyboard)



def get_keyboard2():
	keyboard = [
        
		[
			KeyboardButton(BUTTON1_ARTICLES),
		],
		]
	return ReplyKeyboardMarkup(
		keyboard = keyboard,
		resize_keyboard=True,)

def get_keyboard3():
    
	keyboard = [
    
		[
			KeyboardButton(BUTTON1_SIGNS),
			KeyboardButton(BUTTON1_PROF),
			KeyboardButton(BUTTON1_NAZAD),
		],
		]
	return ReplyKeyboardMarkup(keyboard = keyboard,
		resize_keyboard=True,)


INTRO, TIME = range(2)


def general_ask(bot: Bot, update: Update):
	chat_id = update.message.chat_id
	p, _ = Profile.objects.get_or_create(
		external_id = chat_id,  
	)
	text = "Данная проблема встречается у 60% людей активно использующих смартофоны, компьютеры, ноутбуки и т.д."  \
			"Бот будет присылать вам набор упражнении на выполнение которых уйдет не больше 2-минут день. Вы хотите продолжить?"
	update.message.reply_text(
		text = text,
		reply_markup = get_keyboard1(),
		)
	return INTRO

def callback_alarm(bot: Bot, job: Job):
	bot.send_message(chat_id = job.context , text="Друг, настало время для упражнении. Всего 2 минуты и твои глаза здоровы.\n\n" \
		\
		"Упражнение 1. Частое моргание: начни быстро и легко сжимать и открывать веки в течение 10-20 секунд. Затем сомкни веки и ненадолго расслабься. \n\n" \
		\
		" Упражнение 2. Большие глаза: Сядь ровно. Крепко зажмурь глаза на 5 секунд, затем широко раскрой их.\n\n" \
		\
		" Упражнение 3. Геометрические фигуры: Попытайся нарисовать взглядом простые геометрические фигуры, держа глаза открытыми. Начни с круга, овала, прямоугольника, квадрата или треугольника.\n\n"\
		\
		" Упражнение 4. Темнота: Закрой глаза и посчитай до 10 и открой.\n\n" \
		"Ты молодец. Удачного дня! 😃")


def intro_handler(bot:Bot, update:Update):
	#chat_id = update.message.chat_id
	#p, _ = Profile.objects.get_or_create(
	#	external_id = chat_id,
	###	}  
	#)
	intro = update.callback_query.data
	j = JobQueue()
	j.set_dispatcher(dispatcher) 
	if intro == CALLBACK_BUTTON1_LEFT:
		chat_id = update.effective_message.chat_id
		text = "Прекрасно! Теперь я буду каждый день отправлять тебе упражнения. Береги глаза друг!"
		j.run_repeating(callback_alarm, 60*60*24, 60, context=chat_id)
		j.start()
		update.effective_message.reply_text(
			text = text,
			reply_markup = get_keyboard2(),
			)
		return ConversationHandler.END
	elif intro == CALLBACK_BUTTON2_RIGHT:
		text = "Тогда ты можешь просто насладиться статьями, которые будут только улучшаться"
		update.callback_query.message.reply_text(
			text = text,
			reply_markup = get_keyboard2(),
			)
		return ConversationHandler.END


def cancel_handler(bot: Bot, update: Update):
	update.message.reply_text('Отмена. Для начала с нуля нажмите /start')
	return ConversationHandler.END

def help_instruct(bot: Bot, update: Update):
	chat_id = update.message.chat_id
	text = update.message.text
	if text == BUTTON1_ARTICLES:
		update.message.reply_text(
			text = "Выбери название статьи!",
			reply_markup = get_keyboard3(),
			)
	elif text == BUTTON1_PROF:
		update.message.reply_text(
			text = "Поставьте компьютер так, чтобы экран находился ниже уровня глаз. Время от времени протирайте пыль с экрана компьютера."\
			\
			" При необходимости приобретите антибликовое покрытие для экрана."\
			\
			" Если нужно, поменяйте настольную лампу на ту, которую можно регулировать, чтобы свет не отражался от экрана. Если Вы замечаете, что свет от лампы или солнечный свет мешает Вам работать, то поменяйте угол, по которым Вы сидите так, чтобы свет не светил в глаза",
			)
	elif text == BUTTON1_SIGNS:
		update.message.reply_text(
			text = "1)Усталость глаз: в легких случаях усталость глаз может представлять собой сложность фокусировки на объектах, особенно при быстрой перефокусировке с одного расстояния на другое. По мере ухудшения усталость глаз может привести к боли или дискомфорту вокруг глаз." \
			\
			"2)Раздражение глаз: сначала ваши глаза могут чувствовать покалывание, и по мере ухудшения состояния они могут даже начать гореть. У вас может даже развиться значительное покраснение. Все это признаки того, что ваши глаза высыхают." \
			\
			" 3)Помутнение зрения: текст и изображения могут начать выглядеть нечеткими, даже когда кажется, что ваши глаза правильно сфокусированы. Если виновником является компьютерное напряжение глаз, размытость будет устранена после того, как вы отдохнете." \
			\
			" 4)Головная боль или головокружение: как головные боли, так и головокружение - это признаки того, что компьютерное напряжение глаз превратилось в нечто более серьезное. Вы должны обратиться к врачу, если головные боли или головокружение продолжаются больше суток."\
			\
			" 5)Боль в шее и плечах: по мере того как ваше зрение ухудшается и дискомфорт увеличивается, ваше тело подсознательно настраивается, чтобы вы могли видеть лучше. Это приводит к неправильной позе, которая поражает шею, плечи и даже спину.",
			)
	elif text == BUTTON1_NAZAD:
		update.message.reply_text(
			text = "Назад",
			reply_markup = get_keyboard2(),
			)
	

conv_handler = ConversationHandler(
entry_points=[
	CommandHandler('start', general_ask ),
],
states={
INTRO: [
		CallbackQueryHandler(intro_handler),
	],
},
fallbacks=[
	CommandHandler('cancel', cancel_handler),
],
)
dispatcher.add_handler(conv_handler)

help_handler = MessageHandler(Filters.text, help_instruct)
dispatcher.add_handler(help_handler)
