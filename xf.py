from requests import Session
from htmldom import htmldom
import random, string, time

base_url = 'https://www.sampadia.com'
Username = 'your_username'
Password = 'your_pqssword'

def get_logged_in_sess():
	sess = Session()
	resp = sess.get(base_url+'/forum'+"/login/")
	dom = htmldom.HtmlDom().createDom(resp.text)
	token = dom.find("input[name=_xfToken]")[0].attr("value")
	login_data={"login":Username,"password":Password,"remember":"1", "_xfRedirect":"/", "_xfToken":token}
	print(login_data)
	print(sess.cookies.get_dict())
	login = sess.post(base_url+'/forum'+"/login/login", data=login_data)
	print(sess.cookies.get_dict())
	
	return sess

def get_xf_token(page_content):
	dom = htmldom.HtmlDom().createDom(page_content)
	token = dom.find("input[name=_xfToken]")[0].attr("value")
	return token

def parse_posts_page(page_content):
	dom = htmldom.HtmlDom().createDom(page_content)
	posts = dom.find(".contentRow-title a")
	token = get_xf_token(page_content)
	return [post.attr("href") for post in posts], token
    
def parse_posts_page_10(page_content):
	dom = htmldom.HtmlDom().createDom(page_content)
	posts = dom.find(".contentRow-title a")
	token = get_xf_token(page_content)
	new_url = base_url + dom.find(".block-footer-controls a")[0].attr("href")
	return [post.attr("href") for post in posts], token, new_url
def get_post_links_and_token(sess, url ,depth, max_depth):
	post_urls = []
	resp = sess.get(url)
	url = resp.url 
	
	for i in range(1,11):
		if i == 10:
			print("visiting "+url+"?page="+str(i))
			resp = sess.get(url+"?page="+str(i))
			new_posts, token, new_url = parse_posts_page_10(resp.text)
			post_urls += new_posts
			if depth >= max_depth:
				break
			else:
				depth +=1
				new_posts, token = get_post_links_and_token(sess, new_url, depth, max_depth)
				post_urls += new_posts
		else:
			print("visiting "+url+"?page="+str(i))
			resp = sess.get(url+"?page="+str(i))
			new_posts, token = parse_posts_page(resp.text)
			post_urls += new_posts
	return post_urls, token
	
	
def like(sess, uid, post_count):
    posts_per_depth = 200
    max_depth = (post_count / posts_per_depth) - 1
    posts, token = get_post_links_and_token(sess, 'https://www.sampadia.com/forum/search/member?user_id='+uid, 1, max_depth) 
        for post in posts:
            post_id = post.split("/")[-1].replace("post-", "")
            like_data = {"_xfRequestUri": post, "_xfWithData":"1", "_xfToken":token, "_xfResponseType":"json"}
            try:
                reactid = 1 if int(post_id)%2 == 1 else 7
            except Exception:
                reactid = 1
            resp = sess.post(f"{base_url}/forum/posts/{post_id}/react?reaction_id={reactid}", data=like_data)
            print(resp.text)


#TODO: needswork
"""
def post_to_topic(sess, url): 
	resp = sess.get(url) 
	token = get_xf_token(resp.text)
	timestamp = token.split(",")[0]
	threadid = url.split("/")[-2].split(".")[-1]
	hashmd5 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
	postcontent = sess.get("https://api.codebazan.ir/jok/").text
	data = {"message_html":"", "message":postcontent, "attachment_hash": f"{hashmd5}","attachment_hash_combined": f"%7B%22type%22%3A%22post%22%2C%22context%22%3A%7B%22thread_id%22%3A{threadid}%7D%2C%22hash%22%3A%22{hashmd5}%22%7D", "last_date":timestamp, "last_known_date":timestamp,"load_extra":"1","_xfToken":token}
	resp = sess.post(url+"add-reply", data=data)
	return resp

def like_post(sess, post_id):
	resp = sess.get("https://romanik.ir/forums/")
	token = get_xf_token(resp.text)
	like_data = {"_xfRequestUri": f"{base_url}/forum/threads/1/", "_xfWithData":"1", "_xfToken":token, "_xfResponseType":"json"}
	resp = sess.post(f"{base_url}/forum/posts/{post_id}/react?reaction_id=14", data=like_data)
"""	
if __name__ == '__main__':
    sess = get_logged_in_sess()
    userid = '1'
    post_count = 500
    like(sess, userid, post_count)
