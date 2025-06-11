from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Nodepay:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://app.nodepay.ai",
            "Referer": "https://app.nodepay.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.nodepay.ai/api"
        self.PAGE_URL = "https://app.nodepay.ai"
        self.SITE_KEY = "0x4AAAAAAAx1CyDNL8zOEPe7"
        self.CAPTCHA_KEY = None
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.captcha_tokens = {}
        self.password = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Setup {Fore.BLUE + Style.BRIGHT}Nodepay - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
        
    def save_tokens(self, new_accounts):
        filename = "tokens.json"
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    existing_accounts = json.load(file)
            else:
                existing_accounts = []

            account_dict = {acc["Email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                account_dict[new_acc["Email"]] = new_acc

            updated_accounts = list(account_dict.values())

            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)

        except Exception as e:
            return []
        
    def load_2captcha_key(self):
        try:
            with open("2captcha_key.txt", 'r') as file:
                captcha_key = file.read().strip()

            return captcha_key
        except Exception as e:
            return None

    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                response = await asyncio.to_thread(requests.get, "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text")
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
    
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, user_id):
        if user_id not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[user_id] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[user_id]

    def rotate_proxy_for_account(self, user_id):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[user_id] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if '@' in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
    
    async def solve_cf_turnstile(self, email: str, proxy=None, retries=5):
        for attempt in range(retries):
            try:

                if self.CAPTCHA_KEY is None:
                    return None
                
                url = f"http://2captcha.com/in.php?key={self.CAPTCHA_KEY}&method=turnstile&sitekey={self.SITE_KEY}&pageurl={self.PAGE_URL}"
                response = await asyncio.to_thread(requests.get, url=url, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                result = response.text

                if 'OK|' not in result:
                    await asyncio.sleep(5)
                    continue

                request_id = result.split('|')[1]

                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT} Req Id: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{request_id}{Style.RESET_ALL}"
                )

                for _ in range(30):
                    res_url = f"http://2captcha.com/res.php?key={self.CAPTCHA_KEY}&action=get&id={request_id}"
                    res_response = await asyncio.to_thread(requests.get, url=res_url, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                    res_response.raise_for_status()
                    res_result = res_response.text

                    if 'OK|' in res_result:
                        captcha_token = res_result.split('|')[1]
                        self.captcha_tokens[email] = captcha_token
                        return True
                    elif res_result == "CAPCHA_NOT_READY":
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT} Status: {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}Captcha Not Ready{Style.RESET_ALL}"
                        )
                        await asyncio.sleep(5)
                        continue
                    else:
                        break

            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None

    async def auth_login(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/auth/login?"
        data = json.dumps({"user":email, "password":self.password[email], "remember_me": True, "recaptcha_token":self.captcha_tokens[email]})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
        
    async def process_accounts(self, email: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
    
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {proxy} {Style.RESET_ALL}"
        )

        self.log(f"{Fore.CYAN + Style.BRIGHT}Captcha:{Style.RESET_ALL}")

        cf_solved = await self.solve_cf_turnstile(email, proxy)
        if not cf_solved:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT} Status: {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}Not Solved{Style.RESET_ALL}"
            )
            return
        
        self.log(
            f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
            f"{Fore.BLUE + Style.BRIGHT} Status: {Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT}Solved{Style.RESET_ALL}"
        )
    
        login = await self.auth_login(email, proxy)
        if login and login.get("msg") == "Success":
            np_token = login["data"]["token"]

            self.save_tokens([{"Email":email, "npToken":np_token}])

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status :{Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} Token Have Been Saved Successfully {Style.RESET_ALL}"
            )
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED + Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            capctha_key = self.load_2captcha_key()
            if capctha_key:
                self.CAPTCHA_KEY = capctha_key
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            separator = "="*25
            for idx, account in enumerate(accounts, start=1):
                if account:
                    email = account["Email"]
                    password = account["Password"]
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                    )

                    if not "@" in email or not password:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                        )
                        continue

                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Account:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                    )

                    self.password[email] = password

                    await self.process_accounts(email, use_proxy)
                    await asyncio.sleep(3)

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*68)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Nodepay()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Nodepay - BOT{Style.RESET_ALL}                                      ",                                       
        )