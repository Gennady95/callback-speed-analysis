# Скорость перезвонов
Скрипт не принимает excel файлы и работает только с БД (диапазоны дат лидов можно настроить в таблице mySQL "call_calculation"). Покажет насколько быстро сотрудники колл-центра или ТТ отвечают на звонки клиентов и перезванивают ли.

# Callback Speed Analysis

> Python tool for analyzing customer callback speed and employee response time using SQL call data.

## Description

This project analyzes how quickly employees respond to customer requests by matching incoming requests with outgoing calls.

The script combines Excel customer data with historical call records from SQL database and evaluates whether callbacks were completed within the required time limit.

## Business Goal

The main objective is to monitor customer service quality and measure response time performance.

The analysis helps answer:

- Was the customer contacted?
- How quickly did the employee call back?
- Was the callback completed within SLA?
- Did the customer call again before receiving a callback?

## Features

- SQL database connection
- Call history extraction
- Excel file processing
- Phone number cleaning and normalization
- Incoming and outgoing call matching
- Callback time calculation
- SLA compliance check
- Customer response classification
- Automatic Excel report generation
- Telegram execution notifications

## Tech Stack

- Python
- pandas
- SQLAlchemy
- PyMySQL
- pyTelegramBotAPI
- tqdm
- openpyxl
- python-dotenv

## How It Works

1. Loads customer request data from Excel
2. Extracts incoming and outgoing calls from SQL database
3. Cleans and standardizes phone numbers
4. Matches calls by phone number
5. Finds the first callback after customer request
6. Calculates response time
7. Classifies result:
   - callback completed on time
   - callback completed late
   - no callback
   - customer called back first
8. Adds analytics sheet to Excel report
9. Sends Telegram notification after execution

## Example / Demo

### Input

Excel file containing:

- Customer phone numbers
- Request creation datetime

SQL database containing:

- Incoming calls
- Outgoing calls
- Call timestamps

### Output

Excel report containing:

- First outgoing call time
- First incoming call time
- Callback status
- SLA result

This project can be used for:

- customer service analytics
- call center performance monitoring
- SLA control
- sales team efficiency analysis
