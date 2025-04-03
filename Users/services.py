# import requests  # ✅ أضفه هنا في أول السطر

# import http.client
# import json
# def get_user_id(username):
#     url = "https://instagram-api-fast-reliable-data-scraper.p.rapidapi.com/user_id_by_username"

#     querystring = {"username":username}

#     headers = {
#         "x-rapidapi-key": "b2b196cfa5msh8925c4c0953161dp100bf3jsn99b08eaa037a",
#         "x-rapidapi-host": "instagram-api-fast-reliable-data-scraper.p.rapidapi.com"
#     }

#     response = requests.get(url, headers=headers, params=querystring)

#     print(response.json())

# def get_instagram_followers(username):
    


#     conn = http.client.HTTPSConnection("instagram-api-fast-reliable-data-scraper.p.rapidapi.com")

#     headers = {
#         'x-rapidapi-key': "b2b196cfa5msh8925c4c0953161dp100bf3jsn99b08eaa037a",
#         'x-rapidapi-host': "instagram-api-fast-reliable-data-scraper.p.rapidapi.com"
#     }

#     user_id = get_user_id(username)
#     conn.request("GET", f"/profile?user_id={user_id}", headers=headers)

#     res = conn.getresponse()
#     data = res.read()
#     # 🔹 تحويل البيانات إلى JSON
#     response_json = json.loads(data)

#     # 🔹 استخراج عدد المتابعين
#     followers_count = response_json.get("follower_count", "❌ لم يتم العثور على المتابعين")

#     return followers_count

# username = "instagram"  # استبدله باسم المستخدم الفعلي
# followers_count = get_instagram_followers(username)
# print(f"عدد المتابعين: {followers_count}")
# print(get_instagram_followers("cristiano"))

# import http.client
# def get_instagram_followers(username):
#     conn = http.client.HTTPSConnection("real-time-instagram-scraper-api1.p.rapidapi.com")

#     headers = {
#         'x-rapidapi-key': "b2b196cfa5msh8925c4c0953161dp100bf3jsn99b08eaa037a",
#         'x-rapidapi-host': "real-time-instagram-scraper-api1.p.rapidapi.com"
#     }

#     conn.request("GET", "/v1/poll_response?poll_id=18055206572134857&code_or_id_or_url=3592156143930432128", headers=headers)

#     res = conn.getresponse()
#     data = res.read()

#     print(data.decode("utf-8"))

import http.client
import json

def get_instagram_followers(username):
    conn = http.client.HTTPSConnection("instagram-api-fast-reliable-data-scraper.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "b2b196cfa5msh8925c4c0953161dp100bf3jsn99b08eaa037a",
        'x-rapidapi-host': "instagram-api-fast-reliable-data-scraper.p.rapidapi.com"
    }

    # 🔹 استخدام username بدلاً من ID ثابت
    conn.request("GET", f"/profile?username={username}", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # 🔹 تحويل البيانات إلى JSON
    response_json = json.loads(data)

    # 🔹 استخراج عدد المتابعين
    followers_count = response_json.get("follower_count", "❌ لم يتم العثور على المتابعين")

    return followers_count

# ✅ تجربة استدعاء الدالة
print(get_instagram_followers("cristiano"))

#http://127.0.0.1:8000/users/get_followers/?username=cristiano&format=json