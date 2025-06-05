from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, time, base64, json, os, uuid, pytz

wib = pytz.timezone('Asia/Jakarta')

class Nodepay:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://app.nodepay.ai",
            "Referer": "https://app.nodepay.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.SESSION_API = "https://api.nodepay.ai"
        self.PING_API = "https://nw.nodepay.ai"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.np_tokens = {}
        self.user_ids = {}

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
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Nodepay - BOT
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

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def decode_np_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            user_id = parsed_payload["sub"]
            exp_time = parsed_payload["exp"]
            
            return user_id, exp_time
        except Exception as e:
            return None, None
            
    def generate_ping_payload(self, email: str, browser_id: int):
        payload = {
            "id":self.user_ids[email], 
            "browser_id":browser_id, 
            "timestamp":int(time.time()), 
            "version":"2.4.0"
        }
        return payload
    
    def generate_browser_id(self):
        browser_id = str(uuid.uuid4())
        return browser_id
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
    
    def print_session_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )
    
    def print_ping_message(self, account, idx, browser_id, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Node Id {Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT}{idx}:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {browser_id} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

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
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate

    async def auth_session(self, email: str, proxy=None, retries=5):
        url = f"{self.SESSION_API}/api/auth/session"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.np_tokens[email]}",
            "Content-Length": "2",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, json={}, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                if response.status_code == 401:
                    return self.print_session_message(email, proxy, Fore.RED, f"GET Session Failed: {Fore.YELLOW + Style.BRIGHT}Np Token Already Expired{Style.RESET_ALL}")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_session_message(email, proxy, Fore.RED, f"GET Session Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}")

    async def mission_lists(self, email: str, proxy=None, retries=5):
        url = f"{self.SESSION_API}/api/mission"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.np_tokens[email]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                if response.status_code == 401:
                    return self.print_session_message(email, proxy, Fore.RED, f"GET Mission Lists Failed: {Fore.YELLOW + Style.BRIGHT}Np Token Already Expired{Style.RESET_ALL}")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_session_message(email, proxy, Fore.RED, f"GET Mission Lists Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}")

    async def complete_mission(self, email: str, mission_id: str, title: str, proxy=None, retries=5):
        url = f"{self.SESSION_API}/api/mission/complete-mission"
        data = json.dumps({"mission_id":mission_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.np_tokens[email]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                if response.status_code == 401:
                    return self.print_session_message(email, proxy, Fore.WHITE, f"Mission {title} "
                        f"{Fore.RED + Style.BRIGHT}Not Completed{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}Np Token Already Expired{Style.RESET_ALL}"
                    )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_session_message(email, proxy, Fore.WHITE, f"Mission {title} "
                    f"{Fore.RED + Style.BRIGHT}Not Completed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
            
    async def send_ping(self, email: str, idx: int, browser_id: str, proxy=None, retries=5):
        url = f"{self.PING_API}/api/network/ping"
        data = json.dumps(self.generate_ping_payload(email, browser_id))
        headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": f"Bearer {self.np_tokens[email]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": FakeUserAgent().random
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                if response.status_code == 401:
                    return self.print_ping_message(email, idx, browser_id, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW + Style.BRIGHT}Np Token Already Expired{Style.RESET_ALL}")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_ping_message(email, idx, browser_id, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}")
            
    async def process_auth_session(self, email: str, use_proxy: bool, rotate_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None

        if use_proxy:
            while True:
                session = await self.auth_session(email, proxy)
                if session and session.get("msg") == "Success":
                    season_name = session.get("data", {}).get("balance", {}).get("season_name") or "Season #N/A"
                    current_amount = session.get("data", {}).get("balance", {}).get("current_amount") or "N/A"
                    total_collected = session.get("data", {}).get("balance", {}).get("total_collected") or "N/A"

                    self.print_session_message(email, proxy, Fore.GREEN, f"{season_name}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Today Earning:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {current_amount} PTS {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Total Earning: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{total_collected} PTS{Style.RESET_ALL}"
                    )
                    return True

                await asyncio.sleep(5)
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(email)
                continue

        while True:
            session = await self.auth_session(email, proxy)
            if session and session.get("msg") == "Success":
                season_name = session.get("data", {}).get("balance", {}).get("season_name") or "Season #N/A"
                current_amount = session.get("data", {}).get("balance", {}).get("current_amount") or "N/A"
                total_collected = session.get("data", {}).get("balance", {}).get("total_collected") or "N/A"

                self.print_session_message(email, proxy, Fore.GREEN, f"{season_name}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Today Earning:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {current_amount} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Total Earning: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{total_collected} PTS{Style.RESET_ALL}"
                )
                return True

            await asyncio.sleep(5)
            continue

    async def looping_auth_session(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            await asyncio.sleep(1 * 60 * 60)
            await self.process_auth_session(email, use_proxy, rotate_proxy)

    async def process_complete_missions(self, email: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            mission_lists = await self.mission_lists(email, proxy)
            if mission_lists and mission_lists.get("msg") == "Success":
                missions = mission_lists.get("data", [])

                if mission_lists:
                    for mission in missions:
                        if mission:
                            mission_id = mission["id"]
                            title = mission["title"]
                            reward = mission["point"]
                            status = mission["status"]

                            if status == "AVAILABLE":
                                complete = await self.complete_mission(email, mission_id, title, proxy)
                                if complete and complete.get("msg") == "Success":
                                    self.print_session_message(email, proxy, Fore.WHITE, f"Mission {title}"
                                        f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT}{reward} PTS{Style.RESET_ALL}"
                                    )

            await asyncio.sleep(12 * 60 * 60)
            
    async def process_send_ping(self, email: str, idx: int, browser_id: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(browser_id) if use_proxy else None

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}                                   ",
                end="\r",
                flush=True
            )

            while True:
                ping = await self.send_ping(email, idx, browser_id, proxy)
                if ping and ping.get("msg") == "Success":
                    score = ping.get("data", {}).get("ip_score", 0) or "N/A"

                    self.print_ping_message(email, idx, browser_id, proxy, Fore.GREEN, "PING Success "
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Ip Score: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{score}{Style.RESET_ALL}"
                    )
                    break

                await asyncio.sleep(5)
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(browser_id)
                continue

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 55 Minutes For Next Ping...{Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(55 * 60)
        
    async def process_handle_send_ping(self, email: str, use_proxy: bool, rotate_proxy: bool):
        if use_proxy:
            tasks = []
            for i in range(3):
                browser_id = self.generate_browser_id()
                tasks.append(asyncio.create_task(self.process_send_ping(email, i+1, browser_id, use_proxy, rotate_proxy)))

            await asyncio.gather(*tasks)

        else:
            browser_id = self.generate_browser_id()
            await asyncio.create_task(self.process_send_ping(email, 1, browser_id, use_proxy, rotate_proxy))
        
    async def process_accounts(self, email: str, use_proxy: bool, rotate_proxy: bool):
        session = await self.process_auth_session(email, use_proxy, rotate_proxy)
        if session:
            tasks = [
                asyncio.create_task(self.looping_auth_session(email, use_proxy, rotate_proxy)),
                asyncio.create_task(self.process_complete_missions(email, rotate_proxy)),
                asyncio.create_task(self.process_handle_send_ping(email, use_proxy, rotate_proxy))
            ]
            await asyncio.gather(*tasks)
        
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No Accounts Loaded.{Style.RESET_ALL}")
                return

            use_proxy_choice, rotate_proxy = self.print_question()

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

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*75)

            tasks = []
            for idx, account in enumerate(accounts, start=1):
                if account:
                    email = account["Email"]
                    np_token = account["npToken"]

                    if not "@" in email or not np_token:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    user_id, exp_time = self.decode_np_token(np_token)
                    if not user_id or not exp_time:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{self.mask_account(email)}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Invalid Np Token {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    if int(time.time()) > exp_time:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{self.mask_account(email)}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Np Token Already Expired {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    self.np_tokens[email] = np_token
                    self.user_ids[email] = user_id

                    tasks.append(asyncio.create_task(self.process_accounts(email, use_proxy, rotate_proxy)))

            await asyncio.gather(*tasks)

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
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Nodepay - BOT{Style.RESET_ALL}                                       "                              
        )