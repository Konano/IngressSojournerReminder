import asyncio
import functools
import logging
from asyncio.exceptions import TimeoutError

import aiohttp
from aiohttp.client_exceptions import ContentTypeError

from base.debug import archive, eprint


class ErrorStatusCode(Exception):
    def __init__(self, status_code: int, content: str | bytes, *args, **kwargs):
        self.status_code = status_code
        self.archive = archive(content)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'{self.status_code}:{self.archive}'

    def __repr__(self):
        return f'ErrorStatusCode ({self.status_code}:{self.archive})'


def attempt(times: int):
    def decorate(func):
        @functools.wraps(func)
        async def wrap(*args, **kwargs):
            for _ in range(times):
                try:
                    return await func(*args, **kwargs)
                except (ErrorStatusCode, TimeoutError, ContentTypeError) as e:
                    eprint(e, logging.DEBUG)
                except Exception as e:
                    raise e
                await asyncio.sleep(5)
            raise Exception(f'Network error in {times} attempts')
        return wrap
    return decorate


# ==================== GET ====================


@attempt(3)
async def get(url: str, timeout: float = 30, **kwargs) -> bytes:
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.request('GET', url, timeout=timeout, **kwargs) as r:
        content = await r.read()
    return content


@attempt(3)
async def get_noreturn(url: str, timeout: float = 30, **kwargs) -> None:
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.request('GET', url, timeout=timeout, **kwargs) as r:
        await r.read()


@attempt(3)
async def get_str(url: str, timeout: float = 30, **kwargs) -> str:
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.request('GET', url, timeout=timeout, **kwargs) as r:
        content = await r.text()
    if r.status != 200:
        raise ErrorStatusCode(r.status, content)
    return content


@attempt(3)
async def get_json(url: str, timeout: float = 30, **kwargs) -> dict | list:
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.request('GET', url, timeout=timeout, **kwargs) as r:
        data = await r.json()
    return data


# ==================== POST ====================

@attempt(3)
async def post(url: str, data, timeout: float = 30, **kwargs) -> bytes:
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.request('POST', url, data=data, timeout=timeout, **kwargs) as r:
        content = await r.read()
    return content


@attempt(3)
async def post_json(url: str, data, timeout: float = 30, **kwargs) -> bytes:
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.request('POST', url, data=data, timeout=timeout, **kwargs) as r:
        data = await r.json()
    return data


@attempt(3)
async def post_status(url: str, data, timeout: float = 30, **kwargs) -> tuple[dict, int]:
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.request('POST', url, data=data, timeout=timeout, **kwargs) as r:
        content = await r.text()
        status = r.status
    return content, status
