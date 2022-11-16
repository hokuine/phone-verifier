import requests
import time
import json
from typing import Optional
from headers import Session

"""
VAKSMS Api since its 3 cents per number yeah lmfao
"""

class phone_verify:
    def __init__(self, token, password) -> None:
        self.session = requests.Session()
        self.token = token
        self.password = password
        self.key = ""
        self.capkey = ""
        self.headers = self.generate_headers(token)
        self.main()

    def generate_headers(self, token):
        headers = Session().headers()
        headers["authorization"] = token
        return headers

    def _number(self) -> tuple:
        try:
            r = self.session.get(f"https://vaksms.ru/api/getNumber/?apiKey={self.key}&service=dc&country=ru")
            number = r.json()["tel"]
            task_id = r.json()["idNum"]
            number = f"+{number}"
            return str(number), task_id
        except Exception as e:
            print(f"_number {r.text}")
            print(e)

    def _get_msg(self, id: str):
        while True:
            try:
                r = self.session.get(f"https://vaksms.ru/api/getSmsCode/?apiKey={self.key}&idNum={id}&all")
                code = r.json()["smsCode"][0]
                if code != None:
                    return code
                time.sleep(1)
            except Exception as e:
                continue

    def _phone_token(self, number: str, code: str):
        payload = {
            "phone": number,
            "code": code
        }
        self.headers['Content-Length'] = str(len(json.dumps(payload)))
        r = self.session.post("https://discord.com/api/v9/phone-verifications/verify", json=payload, headers=self.headers)
        if r.status_code == 200:
            print(r.text)
            phone_token = r.json()["token"]
            self.headers.pop('Content-Length')
            return phone_token
        else:
            print(f"_phone_token {r.text}")

    def _final(self, phone_token):
        payload = {"phone_token": phone_token,"password": self.password,"change_phone_reason":"user_settings_update"}
        self.headers['Content-Length'] = str(len(json.dumps(payload)))
        r = self.session.post("https://discord.com/api/v9/users/@me/phone", headers=self.headers)
        if r.status_code == 204:
            self.headers.pop('Content-Length')
            return True
        else:
            print(f"{r.text}")
        

    def add_number(self, number):
        url = "https://discord.com/api/v9/users/@me/phone"
        solution = self.solve_captcha("f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34", "https://discord.com/channels/@me")
        print(f"solved captcha {solution}")
        dictionary = {
            "captcha_key": solution,
            "phone": number,
            "change_phone_reason": "user_settings_update"
            }
        self.headers['Content-Length'] = str(len(json.dumps(dictionary)))
        r = self.session.post(url=url, headers=self.headers, json=dictionary)
        if r.status_code == 204:
            self.headers.pop('Content-Length')
            return True
        else:
            print(f"add_number {r.status_code} {r.text}")
            return False
    
    def solve_captcha(self, sitekey: str, siteurl: str, rqdata: Optional[str] = None) -> str:
        if rqdata != None:
            json={
            "clientKey": self.capkey,
            "task": {
            "type": "HCaptchaTaskProxyless",
            "websiteURL": siteurl,
            "websiteKey": sitekey,
            "isInvisible": "true",
            "data": rqdata,
            "userAgent": "Mozilla/5.0 (Linux; Android 12; SM-T870 Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.126 Safari/537.36 OPX/1.6"
            }}
        else:
            json={
            "clientKey": self.capkey,
            "task": {
            "type": "HCaptchaTaskProxyless",
            "websiteURL": siteurl,
            "websiteKey": sitekey
            }}
        task = requests.post(f"https://api.capmonster.cloud/createTask", json=json)
        task = task.json()["taskId"]
        print(f"Created Captcha Task: ({task})")
        while True:
            try:
                get_results = requests.post("https://api.capmonster.cloud/getTaskResult", json={"clientKey": self.capkey, "taskId": task}).json()
                solution = get_results["solution"]["gRecaptchaResponse"]
                return solution
            except:
                continue

    def main(self):
        number, task_id = self._number()
        print(f"got number +{number} ({task_id})")
        self.add_number(number)
        code = self._get_msg(task_id)
        print(f"got discord code ({code})")
        phone_token = self._phone_token(number, code)
        self._final(phone_token)


phone_verify("token", "pass")