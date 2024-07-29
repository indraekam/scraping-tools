from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
from bs4 import BeautifulSoup as bs

def scrape_article_details(url, driver):
    driver.get(url)
    time.sleep(5)  

    page_source = driver.page_source
    soup = bs(page_source, 'lxml')

    
    try:
        date = soup.find('time', class_='read-page--header--author__datetime')['datetime']
    except Exception as e:
        date = 'Not found'
        print(f"Date not found: {e}")


    try:
        author = soup.find('span', class_='read-page--header--author__name fn').text.strip()
    except Exception as e:
        author = 'Not found'
        print(f"Author not found: {e}")


    try:
        content_div = soup.find('div', class_='article-content-body__item-content')
        content = ' '.join([p.text for p in content_div.find_all('p')])
    except Exception as e:
        content = 'Not found'
        print(f"Content not found: {e}")

    return date, author, content

def liputan_enam_search(keyword, nPosting=10):
    keyword_encoded = keyword.replace(" ", "+")
    url = f'https://www.liputan6.com/'
    print(f'\n URL : {url}\n')

    # Setup Chrome options
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Setup the Chrome driver
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(f'https://www.liputan6.com/search?q={keyword_encoded}')

        # Wait for the page to load
        time.sleep(5)

        # # Perform the search
        search_input = driver.find_element(By.CLASS_NAME, 'navbar--top--search__input')
        search_button = driver.find_element(By.CLASS_NAME, 'navbar--top--search__button')

        search_input.clear()
        search_input.send_keys(keyword)
        search_button.click()

        # Wait for search results to load
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, 'articles--iridescent-list--item'))
        # )

        # Get the page source
        page_source = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = bs(page_source, 'lxml')

        posts_data = []
        scroll_pause_time = 3  # Pause time between scrolls
        scroll_count = 0  # Count the number of scrolls
        post_number = 0
        previous_length = 0

        while post_number < nPosting:
            block = soup.find_all('article', class_='articles--iridescent-list--item articles--iridescent-list--text-item')
            for article in block:
                headline = article.find('a')['title']
                link = article.find('a')['href']
                if {'headline': headline, 'link': link} not in posts_data:
                    date, author, content = scrape_article_details(link, driver)
                    posts_data.append({'headline': headline, 'link': link, 'date': date, 'author': author, 'content': content})
                    # posts_data.append({'headline': headline, 'link': link})
                if len(posts_data) >= nPosting:
                    break

                # posts_data.append({'headline': headline, 'link': link})
                # if len(posts_data) >= nPosting:
                #     break
            post_number = len(posts_data)

            if len(posts_data) == previous_length:
                print("No new articles found, stopping the scroll.")
                break

            previous_length = len(posts_data)

            # Scroll down to load more articles
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            # Get the updated page source and parse again
            page_source = driver.page_source
            soup = bs(page_source, 'lxml')

        for post in posts_data:
            print(f"\nHeadline: {post['headline']}")
            print(f"Link: {post['link']}")
            print(f"Date: {post['date']}")
            print(f"Author: {post['author']}")
            print(f"Content: {post['content']}")

        print(f'\nPanjang Posting {len(posts_data)}')
    finally:
        driver.quit()

# Run the search
keyword = 'prabowo gibran'
liputan_enam_search(keyword)
