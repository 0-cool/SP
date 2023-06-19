import asyncio
from flask import Flask, jsonify
from threading import Thread
from pyppeteer import launch

app = Flask(__name__)

def scrape_corotos(search):
    async def main(search):
        url = 'https://www.corotos.com.do/k/' + search + '?q%5Bsorts%5D=price_dop%20asc'
        browser = await launch(
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            headless=True,
            ignoreDefaultArgs=['--disable-extensions'],
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        page = await browser.newPage()
        await page.goto(url, timeout=90000)

        book_data = await page.evaluate('''
            () => {
                const convertPrice = (price) => { return parseFloat(price); }

                const bookPods = Array.from(document.querySelectorAll('.page_content .flex.group'));
                const data = bookPods.map((book) => {
                    const titleElement = book.querySelector('.listing-bottom-info h3');
                    const title = titleElement ? titleElement.innerText : null;

                    const imgElement = book.querySelector('a img');
                    const img = imgElement ? imgElement.getAttribute('src') : null;

                    const currencyElement = book.querySelector('.listing-bottom-info .price-info span.text-overline');
                    const currency = currencyElement ? currencyElement.innerText : null;

                    const priceElement = book.querySelector('.listing-bottom-info .price-info span.text-title-3');
                    const price = priceElement ? priceElement.innerText : null;

                    return {
                        'title': title,
                        'img': img,
                        'currency': currency,
                        'price': price ? convertPrice(price) : null,
                        'company': 'Corotos'
                    };
                });

                return data;
            }
        ''')

        await browser.close()

        return book_data

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    book_data = loop.run_until_complete(main(search))

    return book_data

@app.route('/', methods=['GET'])
def home():
    return "Inicio" 

@app.route('/api/corotos/<search>', methods=['GET'])
def corotos_api(search):
    book_data = scrape_corotos(search)
    return jsonify(book_data)

if __name__ == '__main__':
    def run_flask_app():
        app.run()

    app_thread = Thread(target=run_flask_app)
    app_thread.start()
