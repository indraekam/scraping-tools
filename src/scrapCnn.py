# import requests as req
from bs4 import BeautifulSoup as bs
from datetime import datetime
import csv
import time
import asyncio
from arsenic import get_session, keys, browsers, services

async def scrape_article(url, index):
    # Create a session with the service and browser
    async with get_session(services.Chromedriver(), browsers.Chrome()) as session:
        # Go to the article URL
        await session.get(url)

        # Wait for the page to load
        await asyncio.sleep(5)

        # Get the page source
        page_source = await session.get_page_source()
        
        # Parse the HTML with BeautifulSoup
        sop = bs(page_source, 'lxml')
        
        # Example: Extract the article content
        author = sop.find('span', class_='text-cnn_red')  
        if author:
            author_text = author.get_text(strip=True)
            print(f'\n =====> Article author {index} : {author_text}') 
        else :
            author_text = 'Not found'

        blockContent = sop.find('div', class_ ='detail-text text-cnn_black text-sm grow')
        tagP = blockContent.find_all('p')
        print(f'\n=====> Len Tagp {index} : {len(tagP)} ')
        text =[]
        for tag in tagP:
            t = tag.get_text(separator = ' ', strip=True)
            text.append(t)

        f_text = ' '.join(text).replace("ADVERTISEMENT", '') 
        print(f'\n =====> Article content {index}:  {f_text}')
    
        date = sop.find('div', class_='text-cnn_grey text-sm mb-4')
        contents = date.contents
        date = contents[0].strip()
        date_text = date.replace(",","")
        full_date = None
        month_number = None
        parts = date_text.split(' ')
        print(f'\n =====> Article date {index}:  {parts}')

        day = parts[1]
        month = parts[2]
        year = parts[3]

        months = {
            "Jan": "Januari",
            "Feb": "Februari",
            "Mar": "Maret",
            "Apr": "April",
            "Mei": "Mei",
            "May": "Mei",
            "Jun": "Juni",
            "Jul": "Juli",
            "Aug": "Agustus",
            "Agu": "Agustus",
            "Sep": "September",
            "Okt": "Oktober",
            "Oct": "Oktober",
            "Nov": "November",
            "Des": "Desember",
            "Dec": "Desember"
          }
        
        month_full = months.get(month, month)
        month_mapping = {
              "Januari": 1,
              "Februari": 2,
              "Maret": 3,
              "April": 4,
              "Mei": 5,
              "Juni": 6,
              "Juli": 7,
              "Agustus": 8,
              "September": 9,
              "Oktober": 10,
              "November": 11,
              "Desember": 12
            }
        
        month_number = month_mapping[month_full]

        # Buat objek datetime
        full_date = datetime(int(year), month_number, int(day))

        return {'author' : author_text, 'content':f_text, 'date' : full_date}

async def cnn_search(keyword, page=1):
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
