# diagnostic script: run on the deployed server to check DNS/resolution and HTTP egress
import socket, httpx, asyncio, os, time, traceback

HOSTS = [
    "api.chainweb.com",
    "explorer.chainweb.com",
    "us-e1.chainweb.com",
    "eu-e1.chainweb.com",
    "uk-e1.chainweb.com",
    "jp-e1.chainweb.com",
]

async def http_post_test(url):
    payload = {
        "networkId": "mainnet01",
        "payload": {"exec": {"code": '(coin.get-balance "k:0000")', "data": {}}},
        "signers": [], "meta": {"chainId": "0","gasLimit":150000,"gasPrice":1e-6,"ttl":600,"creationTime":int(time.time())}
    }
    async with httpx.AsyncClient(timeout=8) as c:
        try:
            r = await c.post(url, json=payload)
            return r.status_code, r.text[:800]
        except Exception as e:
            return "ERR", repr(e)

async def http_get_test(url):
    async with httpx.AsyncClient(timeout=8) as c:
        try:
            r = await c.get(url)
            return r.status_code, r.text[:800]
        except Exception as e:
            return "ERR", repr(e)

async def main():
    print("ENV KADENA_PACT_BASES:", os.getenv("KADENA_PACT_BASES"))
    for h in HOSTS:
        try:
            ip = socket.gethostbyname(h)
        except Exception as e:
            ip = f"DNS_FAIL: {repr(e)}"
        print(f"{h} -> {ip}")
    urls = [
        "https://api.chainweb.com/chainweb/0.0/mainnet01/chain/0/pact/api/v1/local",
        "https://explorer.chainweb.com/mainnet/api/transactions?limit=1"
    ]
    for u in urls:
        if "pact" in u:
            code, resp = await http_post_test(u)
        else:
            code, resp = await http_get_test(u)
        print("TEST", u, "=>", code)
        print(resp[:600])

if __name__ == "__main__":
    asyncio.run(main())
