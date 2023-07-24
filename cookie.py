from http.cookies import SimpleCookie
cookie = SimpleCookie(http_cookie)
session_cookie = cookie.get