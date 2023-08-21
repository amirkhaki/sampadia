import requests
from bs4 import BeautifulSoup

base_url = 'https://www.sampadia.com'
Username = '{Please type your username}'
Password = '{Please type your pass}'
depth = 0


def get_logged_in_sess():
    sess = requests.Session()
    resp = sess.get(base_url + '/forum' + "/login/")
    soup = BeautifulSoup(resp.content, 'html.parser')
    token = soup.select_one('input[name="_xfToken"]')['value']
    login_data = {
        "login": Username,
        "password": Password,
        "remember": "1",
        "_xfRedirect": "/",
        "_xfToken": token
    }
    login = sess.post(base_url + '/forum' + "/login/login", data=login_data)
    return sess


def get_xf_token(soup):
    token = soup.select_one('input[name="_xfToken"]')['value']
    return token


def parse_posts_page(soup):
    posts = soup.select('.contentRow-title a')
    token = get_xf_token(soup)
    return [post['href'] for post in posts], token


def len_posts(soup):
    posts = soup.select('.contentRow-title a')
    token = get_xf_token(soup)
    return len(posts)


def parse_posts_page_10(soup):
    global depth
    depth += 1
    posts = soup.select('.contentRow-title a')
    token = get_xf_token(soup)
    new_url = base_url + soup.select_one(".block-footer-controls a")['href']
    print(str(depth) + "th depth end")
    return [post['href'] for post in posts], token, new_url


def get_post_links_and_token(sess, url, maxdepth):
    post_urls = []
    resp = sess.get(url)
    url = resp.url
    soup = BeautifulSoup(resp.content, 'html.parser')
    maxd = soup.find_all(class_="contentRow-title")
    for i in range(1, len(maxd)):
        global depth
        if i == 10:
            print("crawling posts in page " + str(i))
            resp = sess.get(url + "&page=" + str(i))
            new_posts, token, new_url = parse_posts_page_10(BeautifulSoup(resp.content, 'html.parser'))
            post_urls += new_posts
            if depth >= maxdepth:
                break
            else:
                new_posts, token = get_post_links_and_token(sess, new_url, maxdepth)
                post_urls += new_posts
        else:
            print("crawling posts in page " + str(i))
            resp = sess.get(url + "&page=" + str(i))
            new_posts, token = parse_posts_page(BeautifulSoup(resp.content, 'html.parser'))
            if new_posts != "":
                post_urls += new_posts
    return post_urls, token


def like(sess, uid, maxdepth):
    posts, token = get_post_links_and_token(sess, 'https://www.sampadia.com/forum/search/member?user_id=' + uid,
                                            maxdepth)
    i = 0
    for post in posts:
        i += 1
        if i % 10 == 0:
            print("end of liking posts in depth " + str(i / 10).split('.')[0])
        post_id = post.split("/")[-1].replace("post-", "")
        like_data = {
            "_xfRequestUri": post,
            "_xfWithData": "1",
            "_xfToken": token,
            "_xfResponseType": "json"
        }
        if post_id != "":
            resp = sess.post(f"{base_url}/forum/posts/{post_id}/react?reaction_id=1", data=like_data)
            resp = sess.post(f"{base_url}/forum/posts/{post_id}/react?reaction_id=8", data=like_data)
            print("post with id " + post_id + " liked")


if __name__ == '__main__':
    sess = get_logged_in_sess()
    userid = '1'
    maxdepth = 200
    like(sess, userid, maxdepth)
