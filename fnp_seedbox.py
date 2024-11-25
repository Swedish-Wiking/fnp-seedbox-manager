import re
import argparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(
    prog = "FnP seedbox manager",
    description = "Automagically add or remove seedbox entries on fearnopeer.com",
    usage = f"{Path(__file__).name} username [ip] [options] ",
    epilog = "For bugs/errors, please DM me on FNP or make an issue on GitHub"
)

parser.add_argument("username", type = str, help="FnP username")
parser.add_argument("ip", nargs="?", type = str, help="IP of the seedbox")
parser.add_argument("--print", default = False, action=argparse.BooleanOptionalAction, help="Prints list of seedboxes (default: %(default)s)")
parser.add_argument("--seedbox-name", type = str, default="PikminBox", help="Name of the seedbox (default: %(default)s)")
parser.add_argument("--delete", default = True, action=argparse.BooleanOptionalAction, help="Deletes all old seedbox entries (default: %(default)s)")
parser.add_argument("--cookie-file", type = Path, default=Path(__file__).parent.joinpath("fearnopeer.cookies"), help="Cookies to be used when making requests (default: ./fearnopeer.cookies)")
parsed_args = parser.parse_args()

s = requests.Session()
fnp_headers = {
    "Host": "fearnopeer.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://fearnopeer.com",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def parseCookieFile(file:Path) -> None:
    match_case = re.compile(r"^fearnopeer\.com(?:\t\S+){4}\t(\S+)\t(\S+)", re.MULTILINE)
    raw_cookies = re.findall(match_case, file.read_text())
    try: 
        cookie = next({x[0]: x[1]} for x in raw_cookies if str(x[0]).startswith("remember_web_"))
        s.cookies.update(cookie)
    except:
        print(f"No remember_web_* cookie was found in {file}")
        exit(1)

def getSeedboxes() -> tuple[list[dict], str]: 
    try:
        seedbox_resp = s.get(
            f"https://fearnopeer.com/users/{parsed_args.username}/seedboxes", 
            headers = fnp_headers
        )

        parsed_html = BeautifulSoup(seedbox_resp.content, "html.parser")
        add_token = parsed_html.find("form", attrs={"action": f"https://fearnopeer.com/users/{parsed_args.username}/seedboxes"}).input["value"]
        seedbox_entries = parsed_html.find("table", attrs = {"class": "data-table"}).find_all("tr")[1:]
        
        seedboxes = list()
        for entry in seedbox_entries:
            info = entry.find_all("td")[:2]
            id = Path(entry.find("form")["action"]).name
            token = entry.find("input", attrs = {"name": "_token" })["value"]
            seedboxes.append({"name": info[0].text, "ip": info[1].text, "id": id, "token":token})
        
        return seedboxes, add_token
    
    except Exception as e:
        print(f"Error while getting seedboxes: {e}", flush=True)
        exit(1)

def addSeedbox(token:str) -> bool:
    try:
        add_resp = s.post(f"https://fearnopeer.com/users/{parsed_args.username}/seedboxes",
            data = {"_token": token, "name": parsed_args.seedbox_name, "ip": parsed_args.ip},
            headers = fnp_headers
        )

        parsed_html = BeautifulSoup(add_resp.content, "html.parser")
        error = parsed_html.find("div", attrs={"id": "ERROR_COPY"})

        if error: 
            error_msg = " ".join([x.strip()for x in error.text.split("\n") if x.strip() != ''])
            raise Exception(error_msg)

        return True

    except Exception as e:
        print("Failed to add seedbox", flush=True)
        print(f"Error: {e}", flush=True)
        return False

def main():

    seedboxes, add_token = getSeedboxes()

    if parsed_args.print:
        print(f"\n| {"Name":<25}{"IP":<20}{"ID":<5}")
        print("| "+ "-"*53)
        for sbox in seedboxes:
            print(f"| {sbox["name"]:<25}{sbox['ip']:<20}{sbox['id']:<5}")
        print()

    if parsed_args.delete:
        for sbox in seedboxes:
            print(f"Deleting Seedbox: \"{sbox["name"]}\" ({sbox["ip"]})", flush=True)
            s.post(
                f"https://fearnopeer.com/users/{parsed_args.username}/seedboxes/{sbox["id"]}", 
                data = {"_token": sbox["token"], "_method": "DELETE"}, 
                headers = fnp_headers
            )

    if parsed_args.ip:
        if addSeedbox(add_token):
            print(f"Successfully added Seedbox: \"{parsed_args.seedbox_name}\" ({parsed_args.ip})", flush = True)

if __name__ == "__main__":
    parseCookieFile(parsed_args.cookie_file)
    main()
    