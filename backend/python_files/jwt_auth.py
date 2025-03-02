"""
settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

urls.py
path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
"""

url = "http://127.0.0.1:8000/token/"
headers = {"Content-Type": "application/json"}
# data = {'username': 'umesh', 'password': 'admin'}
# response = requests.post(url=url, headers=headers, json=data)
# print(response.status_code)
# print(response.content)
# access = response.json()['access']
# refresh = response.json()['refresh']

# url = 'http://127.0.0.1:8000/'
# headers = {"Authorization": f"Bearer {access}"}
# response = requests.get(url=url, headers=headers)
# print(response.status_code)
# print(response.content)

# url = 'http://127.0.0.1:8000/token/refresh/'
# headers = {"Content-Type": "application/json"}
# data = {'refresh': refresh}
# response = requests.post(url=url, headers=headers, json=data)
# print(response.status_code)
# print(response.content)
