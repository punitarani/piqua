# Main Streamer file

import asyncio
from lib.tda import StreamClient
from timesale_buysell import TimeSaleFutures


socket = StreamClient()


# Basic Stream Print Handler
def print_handler(msg):
    print(msg)


async def listen():
    await socket.login()

    run = True
    while run:
        await socket.handle_message()


async def level_one():
    equity_symbols = ["AAPL", "AMZN", "FB", "GOOG", "MSFT", "TSLA"]
    equity_options_symbols = ["SPY_122024C500", "QQQ_011924C400"]
    future_symbols = ["/ES", "/NQ"]

    await socket.level_one_equity_sub(symbols=equity_symbols)
    socket.add_level_one_equity_handler(print_handler)

    await socket.level_one_options_sub(symbols=equity_options_symbols)
    socket.add_level_one_options_handler(print_handler)

    await socket.level_one_futures_sub(symbols=future_symbols)
    socket.add_level_one_futures_handler(print_handler)
    socket.add_level_one_futures_handler(TimeSaleFutures)

    run = True

    while run:
        try:
            await socket.handle_message()
        except KeyboardInterrupt:
            await socket.level_one_equity_unsub(symbols=equity_symbols)
            await socket.level_one_options_unsub(equity_options_symbols)
            await socket.level_one_futures_unsub(future_symbols)

            await socket.logout(disconnect=True)

            break


async def book():
    equity_symbols = ["SPY", "AAPL", "AMZN", "FB", "GOOG", "MSFT", "TSLA"]
    equity_options_symbols = ["SPY_122024C500", "QQQ_011924C400"]
    future_symbols = [r"/ES", r"/NQ"]
    futures_options_symbols = [r"/ESH23C4750"]

    await socket.listed_book_sub(symbols=equity_symbols)
    socket.add_listed_book_handler(print_handler)
    await socket.nasdaq_book_sub(symbols=equity_symbols)
    socket.add_nasdaq_book_handler(print_handler)

    await socket.options_book_sub(symbols=equity_options_symbols)
    socket.add_options_book_handler(print_handler)

    run = True

    while run:
        try:
            await socket.handle_message()

        except KeyboardInterrupt:
            await socket.listed_book_unsub(symbols=equity_symbols)
            await socket.nasdaq_book_unsub(symbols=equity_symbols)
            await socket.options_book_unsub(equity_options_symbols)
            await socket.futures_book_unsub(future_symbols)

            await socket.logout(disconnect=True)

            break


async def timesale():
    equity_symbols = ["AAPL", "AMZN", "FB", "GOOG", "MSFT", "TSLA"]
    future_symbols = ["/ES", "/NQ"]

    await socket.update_QOS(level="0")

    await socket.timesale_equity_sub(symbols=equity_symbols)
    socket.add_timesale_equity_handler(print_handler)

    await socket.timesale_futures_sub(symbols=future_symbols)
    socket.add_timesale_futures_handler(print_handler)
    socket.add_timesale_futures_handler(TimeSaleFutures)

    run = True

    while run:
        try:
            await socket.handle_message()

        except KeyboardInterrupt:
            await socket.timesale_equity_unsub(symbols=equity_symbols)
            await socket.timesale_futures_unsub(future_symbols)

            await socket.logout(disconnect=True)

            break


async def news():
    equity_symbols = ["AAPL", "AMZN", "FB", "GOOG", "MSFT", "TSLA"]
    future_symbols = ["/ES", "/NQ"]

    await socket.update_QOS(level="0")

    await socket.news_headline_sub(symbols=equity_symbols + future_symbols)
    socket.add_news_headline_handler(print_handler)

    run = True

    while run:
        try:
            await socket.handle_message()
        except KeyboardInterrupt:
            await socket.news_headline_unsub(equity_symbols + future_symbols)

            await socket.logout(disconnect=True)

            break


async def main():
    """
    Main function incorporating all the other functions
    :return:
    """
    await socket.login()
    l1 = loop.create_task(level_one())
    l2 = loop.create_task(book())
    ts = loop.create_task(timesale())
    ns = loop.create_task(news())

    await asyncio.wait([l1, l2, ts, ns])


# Main Loop
if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.run_until_complete(main())

    loop.close()
