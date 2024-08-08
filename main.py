import asyncio
import os
import ssl
from datetime import datetime

import httpx
from tqdm.asyncio import tqdm
import aioping


async def ping_server(domain: str, timeout=3):
    try:
        delay = await aioping.ping(dest_addr=domain, timeout=timeout)
        return delay * 1000
    except TimeoutError:
        return None


async def check_tls_v1_3_and_http2(client: httpx.AsyncClient, domain: str):
    try:
        url = f'https://{domain}'
        response = await client.get(url=url)
        supports_tls_v1_3 = response.is_success
        supports_http2 = response.http_version == 'HTTP/2'
        return supports_tls_v1_3, supports_http2
    except (httpx.HTTPStatusError, httpx.RequestError, ssl.SSLError):
        return False, False


async def check_domain(client: httpx.AsyncClient, domain: str):
    ping_result = await ping_server(domain)
    if ping_result:
        supports_tls_v1_3, supports_http2 = await check_tls_v1_3_and_http2(client, domain)
        if supports_tls_v1_3 and supports_http2:
            return domain, ping_result
    return None


async def check_domains(domains: list[str], timeout=3):
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.maximum_version = ssl.TLSVersion.TLSv1_3
    bar_format = '{l_bar}{bar:20}| {n_fmt}/{total_fmt} [{elapsed}]'
    desc = 'Progress'

    async with httpx.AsyncClient(http2=True, verify=context, timeout=timeout) as client:
        tasks = [check_domain(client, domain) for domain in domains]
        progress_bar = tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=desc, bar_format=bar_format, leave=True)
        results = [await task for task in progress_bar]
        verified_domains = [result for result in results if result]

    verified_domains.sort(key=lambda tup: tup[1])
    return verified_domains


def extract_domains(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    domains = []
    for line in lines:
        line = line.strip()
        if line and ' ' in line:
            extracted_domains = line[line.index(' '):].split('(')[0].strip()
            extracted_domains = [domain for domain in extracted_domains.split(', ') if not domain.startswith('*')]
            domains.extend(extracted_domains)
    return domains


def find_file(file_path):
    if os.path.isabs(file_path):
        return file_path if os.path.isfile(file_path) else None
    current_dir_file = os.path.join(os.getcwd(), file_path)
    return current_dir_file if os.path.isfile(current_dir_file) else None


def save_verified_domains(domains: list[str], file_to_save):
    with open(file_to_save, 'w') as file:
        file.write('\n'.join(domains))


def save_verified_domains_with_ping(data: list[tuple], file_to_save):
    with open(file_to_save, 'w') as file:
        file.write(f'{"Domain":<26} Ping\n')
        for row in data:
            file.write(f'{row[0]:<26} {int(row[1])}\n')


async def main():
    start = datetime.now()
    file_path = input('Enter the path to the file with the list of domains:\n')
    file = find_file(file_path)

    if not file:
        print(f'File "{file_path}" not found')
        return

    domains = extract_domains(file)
    verified_domains = await check_domains(domains)
    only_domains = [domain[0] for domain in verified_domains]

    save_verified_domains(only_domains, 'verified_domains.txt')
    save_verified_domains_with_ping(verified_domains, 'verified_domains_with_ping.txt')

    print(f'Number of verified domains: {len(verified_domains)}. The result has been saved to "verified_domains.txt"')
    print(f'Total time: {datetime.now() - start}')


if __name__ == '__main__':
    asyncio.run(main())
