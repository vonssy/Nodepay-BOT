from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from curl_cffi import requests
from aiohttp_socks import ProxyConnector
from colorama import *
from datetime import datetime
from fake_useragent import FakeUserAgent
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
    
    async def load_auto_proxies(self):
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    with open('proxy.txt', 'w') as f:
                        f.write(content)

                    self.proxies = content.splitlines()
                    if not self.proxies:
                        self.log(f"{Fore.RED + Style.BRIGHT}No proxies found in the downloaded list!{Style.RESET_ALL}")
                        return
                    
                    self.log(f"{Fore.GREEN + Style.BRIGHT}Proxies successfully downloaded.{Style.RESET_ALL}")
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                    await asyncio.sleep(3)
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed to load proxies: {e}{Style.RESET_ALL}")
            return []
        
    async def load_manual_proxy(self):
        try:
            if not os.path.exists('manual_proxy.txt'):
                print(f"{Fore.RED + Style.BRIGHT}Proxy file 'manual_proxy.txt' not found!{Style.RESET_ALL}")
                return

            with open('manual_proxy.txt', "r") as f:
                proxies = f.read().splitlines()

            self.proxies = proxies
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed to load manual proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        
        return f"http://{proxies}" # Change with yours proxy schemes if your proxy not have schemes [http:// or socks5://]

    def get_next_proxy(self):
        if not self.proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}No proxies available!{Style.RESET_ALL}")
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.check_proxy_schemes(proxy)
    
    def hide_token(self, token):
        hide_token = token[:3] + '*' * 3 + token[-3:]
        return hide_token
    
    async def user_session(self, token: str, proxy: str, retries=3):
        url = "http://api.nodepay.ai/api/auth/session"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "2",
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                    async with session.post(url=url, headers=headers, json={}) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.hide_token(token)} {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}]{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(2)
                else:
                    return None
    
    async def user_earning(self, token: str, proxy: str, retries=3):
        url = "http://api.nodepay.ai/api/earn/info"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.hide_token(token)} {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}]{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(2)
                else:
                    return None
    
    async def mission_lists(self, token: str, username: str, proxy: str, retries=3):
        url = "http://api.nodepay.ai/api/mission"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}]{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(2)
                else:
                    return None
    
    async def complete_missions(self, token: str, username: str, mission_id: str, proxy: str, retries=3):
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
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}]{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(2)
                else:
                    return None

    def send_ping(self, token: str, id: str, proxy: str, retries=60):
        url = "https://nw.nodepay.org/api/network/ping"
        data = json.dumps({
            "id":id, 
            "browser_id":str(uuid.uuid4()), 
            "timestamp":int(time.time()), 
            "version":"2.2.7"
        })
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
                response = requests.post(
                    url=url, 
                    headers=headers, 
                    data=data, 
                    proxies={"http": proxy, "https": proxy} if proxy else None, 
                    timeout=30, 
                    impersonate="safari15_5"
                )
                response.raise_for_status()
                result = response.json()
                return result['data']
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    continue
                return None
        
    async def connection_state(self, token: str, username: str, id: str, proxy: str, connection_count: int):
        ping_count = 1
        while True:
            result = await asyncio.to_thread(self.send_ping, token, id, proxy)
            if result and isinstance(result, dict):
                ip_score = result.get("ip_score")
                if ip_score is not None:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Connection {connection_count} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Proxy {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Status{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} PING {ping_count} Success {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} IP Score {ip_score} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    ping_count += 1
            else:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Connection {connection_count} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Proxy {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}] [ Status{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} PING {ping_count} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Try With Next Proxy... {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
                if proxy:
                    proxy = self.get_next_proxy()

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Next Ping in 1 Minutes.{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} Wait... {Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(60)
        
    async def question(self):
        while True:
            try:
                print("1. Run With Auto Proxy")
                print("2. Run With Manual Proxy")
                choose = int(input("Choose [1/2] -> ").strip())

                if choose in [1, 2]:
                    proxy_type = (
                        "Auto" if choose == 1 else 
                        "Manual"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run With {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")
            
    async def process_accounts(self, token: str):
        proxy = self.get_next_proxy()
        hide_token = self.hide_token(token)

        user = None
        earn = None

        while user is None or earn is None:
            user = await self.user_session(token, proxy)
            earn = await self.user_earning(token, proxy)

            if not user or not earn:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {hide_token} {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Login Failed{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} With Proxy {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
                await asyncio.sleep(1)

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Try With The Next Proxy,{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Wait... {Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )

                proxy = self.get_next_proxy()
                continue
        
            username = user['name']
            id = user['uid']

            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}Login Success{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} ] [ Earning{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} Total {earn['total_earning']} Points {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} Today {earn['today_earning']} Points {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            await asyncio.sleep(1)

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
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}] [ Mission{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {mission['title']} {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {mission['point']} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}] [ Mission{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {mission['title']} {Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT}Isn't Completed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                    else:
                        completed = True

                if completed:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Available Mission Is Completed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Mission Data Is None {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
            await asyncio.sleep(1)

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try to Sent Ping,{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} Wait... {Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

            selected_proxies = []
            
            for _ in range(3):
                proxy = self.get_next_proxy()
                if proxy:
                    selected_proxies.append(proxy)

            tasks = []
            for i, proxy in enumerate(selected_proxies):
                connection_count = i + 1
                tasks.append(asyncio.create_task(self.connection_state(token, username, id, proxy, connection_count)))

            await asyncio.gather(*tasks)
    
    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]

            use_proxy_choice = await self.question()

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            if use_proxy_choice == 1:
                await self.load_auto_proxies()
            elif use_proxy_choice == 2:
                await self.load_manual_proxy()

            while True:
                tasks = []
                for token in tokens:
                    token = token.strip()
                    if token:
                        tasks.append(self.process_accounts(token))

                await asyncio.gather(*tasks)
                await asyncio.sleep(3)

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