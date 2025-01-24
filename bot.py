from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from curl_cffi import requests
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, time, json, os, uuid, pytz

wib = pytz.timezone('Asia/Jakarta')

class Nodepay:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://app.nodepay.ai",
            "Referer": "https://app.nodepay.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

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
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
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

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
            
    def generate_browser_id(self):
        browser_id = str(uuid.uuid4())
        return browser_id
    
    def mask_account(self, account):
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account
    
    def print_message(self, account, proxy, action, reason):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {account} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT} {action} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT} {str(reason)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
    
    async def users_session(self, token: str, proxy=None):
        url = "http://api.nodepay.ai/api/auth/session"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "2",
            "Content-Type": "application/json",
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                async with session.post(url=url, headers=headers, json={}) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']
        except (Exception, ClientResponseError) as e:
            return self.print_message(self.mask_account(token), proxy, "GET User Id Failed", e)
    
    async def users_earning(self, token: str, username: str, proxy=None, retries=5):
        url = "http://api.nodepay.ai/api/earn/info"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(username, proxy, "GET Earning Data Failed", e)
    
    async def mission_lists(self, token: str, username: str, proxy=None, retries=5):
        url = "http://api.nodepay.ai/api/mission"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(username, proxy, "GET Available Mission Failed", e)
    
    async def complete_missions(self, token: str, username: str, mission_id: str, proxy=None, retries=5):
        url = "http://api.nodepay.ai/api/mission/complete-mission"
        data = json.dumps({'mission_id':mission_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(username, proxy, "Complete Available Mission Failed", e)

    async def process_user_earning(self, token: str, username: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(token) if use_proxy else None
            earning = await self.users_earning(token, username, proxy)
            if earning:
                season_name = earning.get('season_name', 'Season #N/A')
                today_point = earning.get('today_earning', 'N/A')
                total_point = earning.get('total_earning', 'N/A')
                current_point = earning.get('current_point', 'N/A')
                pending_point = earning.get('pending_point', 'N/A')

                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Earning {season_name}: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Today {today_point} PTS{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Total {total_point} PTS{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Current {current_point} PTS{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Pending {pending_point} PTS{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                )

            await asyncio.sleep(60 * 60)

    async def process_user_missions(self, token: str, username: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(token) if use_proxy else None
            missions = await self.mission_lists(token, username, proxy)
            if missions:
                completed = False
                for mission in missions:
                    mission_id = mission['id']
                    status = mission['status']

                    if mission and status == "AVAILABLE":
                        complete = await self.complete_missions(token, username, mission_id, proxy)
                        if complete:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Mission: {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{mission['title']}{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{mission['point']} PTS{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )

                    else:
                        completed = True

                if completed:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Mission: {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}All Available Missions Is Completed{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                    )

            await asyncio.sleep(24 * 60 * 60)

    async def send_ping(self, token: str, username: str, id: str, browser_id: str, use_proxy: bool, count: int, proxy=None, retries=60):
        url = "https://nw.nodepay.org/api/network/ping"
        data = json.dumps({"id":id, "browser_id":browser_id, "timestamp":int(time.time()), "version":"2.2.7"})
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="safari15_5")
                response.raise_for_status()
                result = response.json()
                return result['data']['ip_score']
            except (Exception, requests.RequestsError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                    continue

                self.print_message(username, proxy, f"PING Browser ID {count} Failed", e)

                if use_proxy:
                    self.rotate_proxy_for_account(token)
                    continue

                return None
        
    async def connection_state(self, token: str, username: str, id: str, browser_id: str, use_proxy: bool, count: int, proxy=None):
        while True:
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}                                   ",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

            result = await self.send_ping(token, username, id, browser_id, use_proxy, count, proxy)
            if result:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Browser ID {count}:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {browser_id} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}PING Success{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}IP Score:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {result} {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                )

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 55 Minutes For Next Ping...{Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(55 * 60)
        
    async def process_accounts(self, token: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(token) if use_proxy else None
        user = None
        while user is None:
            user = await self.users_session(token, proxy)
            if not user:
                proxy = self.rotate_proxy_for_account(token) if use_proxy else None
                continue
            
            username = user['name']
            id = user['uid']

            tasks = []
            tasks.append(asyncio.create_task(self.process_user_earning(token, username, use_proxy)))
            tasks.append(asyncio.create_task(self.process_user_missions(token, username, use_proxy)))

            if use_proxy:
                for i in range(3):
                    count = i + 1
                    browser_id = self.generate_browser_id()
                    proxy = self.rotate_proxy_for_account(token)
                    tasks.append(asyncio.create_task(self.connection_state(token, username, id, browser_id, use_proxy, count, proxy)))
            else:
                count = 1
                browser_id = self.generate_browser_id()
                tasks.append(asyncio.create_task(self.connection_state(token, username, id, browser_id, use_proxy, count, proxy)))

            await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]

            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for token in tokens:
                    token = token.strip()
                    if token:
                        tasks.append(self.process_accounts(token, use_proxy))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'tokens.txt' tidak ditemukan.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

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