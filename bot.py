import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import time
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


async def check_boosters(url):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    driver.get(url)

    boosts_section = wait.until(EC.element_to_be_clickable(('xpath', '//*[@id="Header assets-item-numeric-traits-3"]/div/div')))
    driver.execute_script("arguments[0].scrollIntoView(true);", boosts_section)
    driver.execute_script("arguments[0].click();", boosts_section)
    mining=""
    range=""
    sell=""
    m_value=""
    r_value=""
    s_value=""
    try:
        mining = wait.until(EC.presence_of_element_located(('xpath', '//*[@id="Body assets-item-numeric-traits-3"]/div/div/a[1]/div/div[2]/h6')))
        print(mining.text)
        m_value = driver.find_element('xpath','//*[@id="Body assets-item-numeric-traits-3"]/div/div/a[1]/div/div[2]/p')
        print(m_value.text)
        range = wait.until(EC.presence_of_element_located(('xpath', '//*[@id="Body assets-item-numeric-traits-3"]/div/div/a[2]/div/div[2]/h6')))
        print(range.text)
        r_value = driver.find_element('xpath', '//*[@id="Body assets-item-numeric-traits-3"]/div/div/a[2]/div/div[2]/p')
        print(r_value.text)
        sell = wait.until(EC.presence_of_element_located(('xpath', '//*[@id="Body assets-item-numeric-traits-3"]/div/div/a[3]/div/div[2]/h6')))
        print(sell.text)
        s_value = driver.find_element('xpath','//*[@id="Body assets-item-numeric-traits-3"]/div/div/a[3]/div/div[2]/p')
        print(s_value.text)
    except TimeoutException:
        pass
    return f"{mining.text if mining else ''} {m_value.text if m_value else ''}\n" \
           f"{range.text if range else ''} {r_value.text if r_value else ''},\n" \
           f"{sell.text if sell else ''} {s_value.text if s_value else ''}"


async def poll_updates(message: types.Message, CURRENT_NAME):
    try:
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 15)
        driver.get(
            "https://opensea.io/collection/metaline-heropet?search%5BsortAscending%5D=false&search%5BsortBy%5D=LISTING_DATE")
        e = driver.find_element(By.XPATH,
                                '//*[@id="main"]/div/div/div/div[5]/div/div[6]/div[2]/div/div/div[1]/article/a')
        driver.execute_script("arguments[0].scrollIntoView(true);", e)
        elem = driver.find_element(By.XPATH,
                                   '//*[@id="main"]/div/div/div/div[5]/div/div[6]/div[2]/div/div/div[1]/article/a/div[3]/div[1]/div/div/span')
        if elem.text not in CURRENT_NAME:
            CURRENT_NAME = elem.text
            print(CURRENT_NAME)
            price = driver.find_element('xpath',
                                        '//*[@id="main"]/div/div/div/div[5]/div/div[6]/div[2]/div/div/div[1]/article/a/div[3]/div[2]/div[1]/div/div/span/span[1]')
            PRICE = f"{price.text} ETH"
            print(PRICE)
            url = e.get_attribute("href")
            driver.quit()
            boosters = await check_boosters(url)
            await message.answer(f"Обнаружен новый лот 🔮\n\n👤 Имя:{CURRENT_NAME}\n💰 Цена:{PRICE}\n\n💎 Бустеры:\n{boosters}")
        else:
            driver.quit()
    except:
        pass
    time.sleep(120)
    return CURRENT_NAME


# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Создание объектов бота и диспетчера
bot = Bot(token='ТОКЕН')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


btnBegin = KeyboardButton('🤖 Запуск бота')
begin = ReplyKeyboardMarkup(resize_keyboard=True).add(btnBegin)


# Обработка команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Нажмите Запуск и я начну работу", reply_markup=begin)


# Обработка всех остальных сообщений
@dp.message_handler()
async def echo_message(message: types.Message):
    if message.text == "🤖 Запуск бота":
        await message.answer("Бот запущен")
        with open("last_lot.txt", 'r') as file:
            CURRENT_NAME = file.readline()
        print(f"Последний лот: {CURRENT_NAME if CURRENT_NAME else 'Нет'}")
        while True:
            CURRENT_NAME = await poll_updates(message, CURRENT_NAME)
            with open("last_lot.txt", 'w') as file:
                file.write(CURRENT_NAME)
            print(f"Текущий актуальный лот: {CURRENT_NAME}")
    else:
        await message.answer("Команда не распознана")

    # Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
