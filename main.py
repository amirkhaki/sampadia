import requests
from bs4 import BeautifulSoup

base_url = input('your xenforo forum address ( for example : https://www.sampadia.com ) : ')
Username = input('your username ( for example : hmiddot )')
Password = input('your password ( for example : 1234 )')
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
    return [post['href'] for post in posts], token, new_url


def get_post_links_and_token(sess, url, maxdepth):
    post_urls = []
    resp = sess.get(url)
    url = resp.url
    soup = BeautifulSoup(resp.content, 'html.parser')
    di = soup.find_all(class_="pageNav-page")[len(soup.find_all(class_="pageNav-page")) - 1]
    di = di.find('a').decode_contents()
    di = int(di)
    for i in range(1, di + 1):
        global depth
        if i == di:
            print("crawling posts in page " + str(i))
            print("end of depth " + str(depth + 1))
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
    userid = str(input("please type id of user ( id is a number not string ) : "))
    maxdepth = int(input("please type max depth to crawl ( 5 is best ): "))
    like(sess, userid, maxdepth)
    print("the end :)")
