import pandas as pd, time, re, glob, getpass, platform, telebot, mysql.connector, numpy as np, requests
from datetime import datetime, timedelta, timezone
from datetime import datetime
from mysql.connector import Error
from sqlalchemy import create_engine
from tqdm import tqdm
import os
from dotenv import load_dotenv

#Паттерны
load_dotenv()
engine = create_engine(os.getenv("DB_URL"))
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
chat_id = os.getenv("CHAT_ID")
re_1 = r'[^0-9,.;/]'                                                                                                     # Регулярное выражение для отсева букв, пробелов
re_2 = r'[^0-9]'                                                                                                         # Регулярное выражение для отсева знаков

def CombinetedConv(Base, WestcallIcxo, WestcallVxod):                                                                    # Формирование базы данных
	# Добавелние в базу колонок с первым и последнийм контактом
	dfSQLwestcallIcxo = WestcallIcxo.groupby('Номер телефона').agg({'Дата': ['min']}).reset_index()                      # Группировка с удалением дубликатов и выбором наименьшей даты
	dfSQLwestcallIcxo.columns = ['Номер телефона', 'Первый исходящий звонок']
	#dfSQLwestcallIcxo.rename(columns={'Дата': 'Первый исходящий звонок'}, inplace=True)
	dfSQLwestcallVxod = WestcallVxod.groupby('Номер телефона').agg({'Дата': ['min']}).reset_index()                      # Группировка с удалением дубликатов и выбором наименьшей даты
	dfSQLwestcallVxod.columns = ['Номер телефона', 'Первый входящий звонок']
	#dfSQLwestcallVxod.rename(columns={'Дата': 'Первый входящий звонок'}, inplace=True)
	# Объединение таблицы с данными (страница "По переданному списку клиентов")
	print("Объединение наборов данных")
	print(Base)
	print(dfSQLwestcallIcxo)
	print(dfSQLwestcallVxod)
	ClientsBase = Base.merge(dfSQLwestcallIcxo, on='Номер телефона', how='outer')
	ClientsBase = ClientsBase.merge(dfSQLwestcallVxod, on='Номер телефона', how='outer')
	ClientsBase['Исходящий звонок'] = ClientsBase.apply(
		lambda x: 'Не звонков'                                                                                           # Если вообще не перезвонили
		if (x['Первый исходящий звонок'] is pd.NaT)
		else ('Перезвонили, но поздно'                                                                                   # Если дельта больше 15 мин
		if (x['Первый исходящий звонок'] > (x['Дата'] + timedelta(minutes=15)))
		else 'Перезвонили вовремя'), axis=1)                                                                             # Если позвонили вовремя
	ClientsBase['Входящий звонок'] = ClientsBase.apply(
		lambda x: 'Нет звонков'                                                                                          # Если вообще не звонил
		if (x['Первый входящий звонок'] is pd.NaT)
		else ('Позвонил, но позднее'                                                                                     # Если дельта больше 15 мин
		if (x['Первый входящий звонок'] > (x['Дата'] + timedelta(minutes=15)))
		else 'Перезвонил сам в течение 15 минут'), axis=1)                                                               # Если позвонили вовремя
	print("Объединили")
	return ClientsBase
def SendTelegram(status):                                                                                                #Передача сообщения в telegram
	# Получение информации о компьютере
	UserName = getpass.getuser()                                                                                         # Имя пользователя (обычно оно User - не информативно)
	CompName = platform.node()                                                                                           # Имя компьютера
	chat_id = '*'                                                                                                        # ID моей телеги
	if status == "try": # Если связь с телегой установлена
		bot.send_message(chat_id, date+" пользователь "+UserName+" ("+CompName+") успешно воспользовался скриптом для определения перезвонов мастеров") # Отправка сообщения
	elif status == "except1": # Если нет подключения к SQL серверу
		bot.send_message(chat_id, "ERROR: "+date+" пользователь "+UserName+" ("+CompName+") неудачно запустил скрипт для определения перезвонов мастеров - не подключил VPN") # Отправка сообщения
	elif status == "except2": # Если нет подключения к SQL серверу
		bot.send_message(chat_id, "ERROR: "+date+" пользователь "+UserName+" ("+CompName+") неудачно запустил скрипт для определения перезвонов мастеров - некорректно указал вводные параметры в SQL") # Отправка сообщения
def GetSQL():
	global dfSQLIcxo, dfSQLVxod
	# SQL запросы
	try:
		lightquery_1 = "SELECT `Телефон`, `Дата звонка`, `Направление`, `Принадлежность`, `Время ожидания`, `Длительность разговора` FROM westcall WHERE `Тип` = 'Исходящий'" # SQL запрос в базу westcal
		lightquery_2 = "SELECT `Телефон`, `Дата звонка`, `Направление`, `Принадлежность`, `Время ожидания` FROM westcall WHERE `Тип` = 'Входящий'" # SQL запрос в базу westcal
		dfSQLIcxo = pd.read_sql(lightquery_1, engine)
		dfSQLVxod = pd.read_sql(lightquery_2, engine)
		dfSQLIcxo.rename(columns={'Телефон': 'Номер телефона', 'Дата звонка': 'Дата', 'Направление': 'Направление', 'Принадлежность': 'Принадлежность', 'Время ожидания': 'Время ожидания', 'Длительность разговора': 'Длительность разговора'}, inplace=True)  # Переименование колонок в единый тип
		dfSQLVxod.rename(columns={'Телефон': 'Номер телефона', 'Дата звонка': 'Дата', 'Направление': 'Направление', 'Принадлежность': 'Принадлежность', 'Время ожидания': 'Время ожидания', 'Длительность разговора': 'Длительность разговора'}, inplace=True)  # Переименование колонок в единый тип
	except RequestError as e:
		print(str(e))
		print("Не могу подключится к SQL серверу. Проверьте подключение к VPN"); SendTelegram("except1"); time.sleep(5); exit()
def GetLists(FileLocation):
	GroupFile = [item for item in glob.glob(FileLocation)]                                                               # Собираем файлы в список
	itter = 0
	for Filename in tqdm(GroupFile): # Вводные для progress bar
		if not 'Результат валидации' in str(Filename):
			print(Filename, "Началась загрузка excel файла: ", datetime.time(datetime.now()))
			File = pd.read_excel(Filename)                                                                           # Чтение excel-файла
			dfEX = pd.DataFrame(File)                                                                                # Формирование dataframe
			#Обработка фрейма данных
			dfEX['Номер телефона'].astype('str')                                                                     # Преобразование столбца с номерами телефонов в строчный формат
			dfEX['Номер телефона'] = dfEX['Номер телефона'].apply(lambda x: max(re.sub(re_2, ',', re.sub(re_1, '', str(x))).lstrip(',').split(',', 10), key=len)[-10:])
			dfEX['Номер телефона'] = dfEX['Номер телефона'].loc[dfEX['Номер телефона'].str.len().between(10, 11)]    # Выбор номера телефона определённого формата
			# Создание списков для итерирования
			list_of_numbers = list(filter(None, dfEX['Номер телефона'].tolist()))                                    # Получение списка из номеров телефонов в excel файле
			list_of_date_start = list(filter(None, dfEX['Дата'].tolist()))                                           # Получение списка из номеров дат начала в excel файле
			first_date = min(list_of_date_start)                                                                     # Присвоение нижней и верхней границы из списка (для обрезки базы)
			last_date = max(list_of_date_start)                                                                     # Присвоение нижней и верхней границы из списка (для обрезки базы)
			dfSQLIcxoCenter = dfSQLIcxo.loc[((dfSQLIcxo['Дата'] >= (first_date)) & (dfSQLIcxo['Дата'] <= (last_date + timedelta(minutes=15))))] # Обрезка исходящих по датам
			dfSQLIcxoCenter = dfSQLIcxoCenter.loc[dfSQLIcxoCenter['Номер телефона'].isin(list(filter(None, list_of_numbers)))] # Обрезка исходящих по номерам
			dfSQLVxodCenter = dfSQLVxod.loc[((dfSQLVxod['Дата'] >= (first_date)) & (dfSQLVxod['Дата'] <= (last_date + timedelta(minutes=15))))] # Обрезка входящих по датам
			dfSQLVxodCenter = dfSQLVxodCenter.loc[dfSQLVxodCenter['Номер телефона'].isin(list(filter(None, list_of_numbers)))] # Обрезка входящих по номерам
			print("Созданы списки для проверки по файлу " + FileLocation + " . Теперь начнём считать...")
			WestcallIcxo = pd.DataFrame(); WestcallVxod = pd.DataFrame()
			for Num, Start in zip(list_of_numbers, list_of_date_start):                                              # Цикл проходит по списку SQL n количество раз, равному len(list) базы
				WestcallIcxo = pd.concat([WestcallIcxo, dfSQLIcxoCenter.loc[(dfSQLIcxoCenter['Номер телефона'] == Num) & (dfSQLIcxoCenter['Дата'] >= Start)]], ignore_index=True)
				WestcallVxod = pd.concat([WestcallVxod, dfSQLVxodCenter.loc[(dfSQLVxodCenter['Номер телефона'] == Num) & (dfSQLVxodCenter['Дата'] >= Start)]], ignore_index=True)
			Convert = CombinetedConv(dfEX, WestcallIcxo, WestcallVxod)
			try:
				with pd.ExcelWriter(Filename, engine='openpyxl', mode='a') as writer:                                # Дополнение excel файла новыми листами
					try:
						Convert.to_excel(writer, sheet_name='Результаты перезвонов', index=False)
						itter += 1
					except: pass
			except:	print("В файле" + Filename + " уже присутствуют листы с аналитикой :("); time.sleep(5)

	print("Все файлы обработаны")
	if itter > 0: SendTelegram("try")
	else: SendTelegram("except2")

GetSQL()
GetLists('*.xlsx')