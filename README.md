# Скорость перезвонов
Скрипт не принимает excel файлы и работает только с БД (диапазоны дат лидов можно настроить в таблице mySQL "call_calculation"). Покажет насколько быстро сотрудники колл-центра или ТТ отвечают на звонки клиентов и перезванивают ли.

# Callback Speed Analysis

> Python tool for analyzing customer callback speed and employee response time using SQL call data.

## Description

This project analyzes customer callback speed and employee response time using SQL call history data.

The tool supports two analysis modes:

1. Database analysis mode — analyzes callback performance directly from SQL data.
2. Excel file mode — validates a custom list of customer requests from Excel files and checks callback results for each record.

The script matches customer requests with incoming and outgoing calls and evaluates whether employees contacted customers within the required SLA time.

## Business Goal

The main objective is to monitor customer service quality and measure response time performance.

The analysis helps answer:

- Was the customer contacted?
- How quickly did the employee call back?
- Was the callback completed within SLA?
- Did the customer call again before receiving a callback?

## Features

- SQL database connection
- Excel file processing
- Call history extraction
- Phone number cleaning and normalization
- Incoming and outgoing call matching
- Callback time calculation
- SLA compliance analysis
- Multiple analysis modes:
  - full database callback analysis
  - Excel-based customer list validation
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

### Database Mode

1. Loads call history from SQL database
2. Processes incoming and outgoing calls
3. Matches customer requests with employee callbacks
4. Calculates callback response time
5. Checks SLA compliance
6. Generates analytics report

### Excel File Mode

1. Loads customer request list from Excel
2. Extracts relevant calls from SQL database
3. Filters calls by phone number and request date
4. Searches for the first outgoing callback
5. Checks if callback was completed within 15 minutes
6. Determines customer behavior:
   - employee called back on time
   - employee called back late
   - customer called again before callback
   - no callback detected
7. Adds analysis results into the Excel file
## Example / Demo

### Input

Database mode:

- Call history database
- Incoming calls
- Outgoing calls
- Call timestamps

Excel file mode:

Excel file containing:
- Customer phone number
- Request creation datetime

### Output

Generated report containing:

- First outgoing call time
- First incoming call time
- Callback status
- SLA result
- Response time classification
