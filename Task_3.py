import requests
import bs4
from tqdm import tqdm
from fake_useragent import UserAgent


# Prints all data to the console in the given format
def printing_articles(all_articles):
    for article in all_articles:
        print(f'<{article[0]}> - <{article[1]}> - <{article[2]}>')

    return print('ГОТОВО')


# Gets a link to the next page
def find_next_page(url, headers):
    url2 = 'https://habr.com'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    text = response.text

    soup = bs4.BeautifulSoup(text, features='html.parser')

    pages = soup.find(class_='tm-pagination')
    try:
        next_page = pages.find_all(
                    class_='tm-pagination__navigation-link tm-pagination__navigation-link_active')[1].attrs['href']
    except IndexError:
        next_page = pages.find(
                    class_='tm-pagination__navigation-link tm-pagination__navigation-link_active').attrs['href']

    return url2 + next_page


# Gets the number of available pages
def find_last_page(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    text = response.text

    soup = bs4.BeautifulSoup(text, features='html.parser')

    pages = soup.find(class_='tm-pagination')
    last_page = pages.find_all(class_='tm-pagination__page')

    return int(last_page[-1].text.strip())


# Scans the full text of the news
def article_search(url, cls, headers, keyword):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    text = response.text

    soup = bs4.BeautifulSoup(text, features='html.parser')

    article = soup.find('article')
    try:
        preview = article.find(class_=cls).text
        if preview.lower().find(keyword) > -1:
            return True
    except AttributeError:
        pass


# Scans all previews and tags on the page, in case of a match, adds a list with data to the resulting list.
def preview_search(url, headers, KEYWORDS, all_articles):
    url2 = 'https://habr.com'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    text = response.text

    soup = bs4.BeautifulSoup(text, features='html.parser')

    articles = soup.find_all('article')

    for article in articles:
        try:
            date = article.find(class_='tm-article-snippet__datetime-published').time.attrs['title'][:10]
            title = article.find(class_='tm-article-snippet__title-link').find('span').text
            link = url2 + article.find(class_='tm-article-snippet__title-link').attrs['href']
            hubs = article.find_all(class_='tm-article-snippet__hubs-item')
            hubs = set(hub.text.strip('*').strip().lower() for hub in hubs)
            cls = 'article-formatted-body article-formatted-body article-formatted-body_version-1'
            preview = article.find(class_=cls).text
        except AttributeError:
            try:
                cls = 'article-formatted-body article-formatted-body article-formatted-body_version-2'
                preview = article.find(class_=cls).text
            except AttributeError:
                pass

        for keyword in KEYWORDS:
            if preview.lower().find(keyword) > -1 or title.lower().find(keyword) > -1 or keyword in hubs:
                news = [date, title, link]
                all_articles.append(news)
                break
            else:
                if article_search(link, cls, headers, keyword):
                    news = [date, title, link]
                    all_articles.append(news)
                    break

    return all_articles


def main():
    all_articles = []
    url = 'https://habr.com/ru'
    KEYWORDS = ['дизайн', 'фото', 'web', 'python']

    ua = UserAgent()
    headers = {'User-Agent': ua.chrome}

    all_pages = find_last_page(url, headers)

    pbar = tqdm(total=all_pages)
    for page in range(all_pages):
        preview_search(url, headers, KEYWORDS, all_articles)
        url = find_next_page(url, headers)
        pbar.update()
    pbar.close()

    printing_articles(all_articles)

# Parsing only the first page with news
    # preview_search(url, headers, KEYWORDS, all_articles)
    #
    # printing_articles(all_articles)


if __name__ == '__main__':
    main()