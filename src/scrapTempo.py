from bs4 import BeautifulSoup as bs
from datetime import datetime
import csv
import time
import asyncio
from arsenic import get_session, keys, browsers, services


async def tempo_search(keyword, page=1):
    keyword_encoded = keyword.replace(" ", "%20")
    url = f'https://www.cnnindonesia.com/search/?query={keyword_encoded}&page={page}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    # Setup the Firefox service
    service = services.Chromedriver()

    # Setup the browser
    browser = browsers.Chrome()

    # Create a session with the service and browser
    async with get_session(service, browser) as session:
        # Go to the URL
        await session.get(url)

        # Wait for a few seconds to ensure JavaScript has executed
        await asyncio.sleep(5)

        # Get the page source
        page_source = await session.get_page_source()
        
        # Parse the HTML with BeautifulSoup
        sop = bs(page_source, 'lxml')
        
        # Find all articles

        # block =  sop.find_all('div', attrs={'query': 'cnn-id', 'data-target' : 'search'})
        block =  sop.find_all('div', attrs={'idparentkanal' : True})
        if block is None :
            print('\n======> blok tidak ada')
        else : 
            print(f'\n======> panjang blok {len(block)}')

        lin = block[0].find_all('article')
        print(f'\n=> len of article : {len(lin)}\n')
        
        data = []
        # Process each article
        for index, l in enumerate(lin):
            try:
                link = l.find('a')['href']
                print(f'\n=====> link  {index} : {link}')
            except Exception as e:
                print(f'\n =====>article {index} tidak ada link: {e}')

            try :
                headline = l.find('h2').text
                print(f'\n=====> headline {index}  {headline}')
            except Exception as e:
                print(f'\n =====>article {index} tidak ada headline: {e}')

            try :
                pageContent = await scrape_article(link, index)
            except Exception as e:
                print(f'\n =====>article {index} tidak ada author: {e}')
            
                
            data.append({'headline' : headline, 
                         'link' : link, 
                         'author' : pageContent['author'], 
                         'content':pageContent['content'], 
                         'date' : pageContent['date']})

        print(f'\n==> Data : {data}\n')
        print(f'\n==> Panjang Data {len(data)}')

# Run the search
keyword = 'prabowo gibran'
asyncio.run(cnn_search(keyword))
