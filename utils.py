# utils.py
import os, asyncio, random
from settings import TIMEOUT, SCREEN_DIR

os.makedirs(SCREEN_DIR, exist_ok=True)

async def rand_wait(a=0.5, b=1.2):
    await asyncio.sleep(random.uniform(a, b))

async def click(page, selector: str, timeout: int = TIMEOUT) -> bool:
    try:
        await page.locator(selector).first.click(timeout=timeout)
        await rand_wait(0.2, 0.6)
        return True
    except Exception:
        return False

async def wait_visible(page, selector: str, timeout: int = TIMEOUT) -> bool:
    try:
        await page.locator(selector).first.wait_for(state="visible", timeout=timeout)
        return True
    except Exception:
        return False

async def all_texts(page, selector: str):
    els = page.locator(selector)
    n = await els.count()
    out = []
    for i in range(n):
        try:
            t = (await els.nth(i).inner_text()).strip()
            if t:
                out.append(t)
        except Exception:
            continue
    return out
