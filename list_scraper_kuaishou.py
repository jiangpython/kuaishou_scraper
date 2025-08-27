# list_scraper_kuaishou.py
import asyncio
from typing import AsyncGenerator, Dict, List
from playwright.async_api import Page, TimeoutError as PWTimeout
from settings import LIST_URL, SEL, SCREEN_DIR, TIMEOUT, MAX_ITEMS_PER_PAGE
from utils import rand_wait, click, wait_visible

async def within_content_type_group(page: Page):
    anchor = page.locator(SEL["filter_group_content_type_anchor"]).first
    await anchor.wait_for(state="visible", timeout=TIMEOUT)
    group = anchor.locator("xpath=ancestor::section[1] | xpath=ancestor::div[1]").first
    return group

async def apply_filters_and_sort(page: Page):
    await page.goto(LIST_URL, wait_until="domcontentloaded")
    await page.screenshot(path=f"{SCREEN_DIR}/list_1_open.png")

    # 内容类型 → “更多”（可选）
    try:
        group = await within_content_type_group(page)
        more_btn = group.locator(SEL["content_type_more_btn"]).first
        await more_btn.click(timeout=2000)
        await rand_wait()
    except Exception:
        pass

    # 选择“三农”
    try:
        await group.locator(SEL["tag_sannong"]).first.click(timeout=5000)
    except Exception:
        await page.locator(SEL["tag_sannong"]).first.click(timeout=8000)

    await rand_wait()
    await page.screenshot(path=f"{SCREEN_DIR}/list_2_after_sannong.png")

    # 排序：粉丝数（点两次以确保降序，若站点第一次为升序）
    sort_btn = page.locator(SEL["sort_fans"]).first
    try:
        await sort_btn.click(timeout=8000); await rand_wait(0.4, 0.9)
        await sort_btn.click(timeout=8000)
    except Exception:
        pass
    await rand_wait()
    await page.screenshot(path=f"{SCREEN_DIR}/list_3_after_sort.png")

async def extract_items_on_page(page: Page) -> List[Dict]:
    items = []
    title_spans = page.locator(SEL["item_title_span"])
    count = await title_spans.count()
    if MAX_ITEMS_PER_PAGE:
        count = min(count, MAX_ITEMS_PER_PAGE)

    for i in range(count):
        t = title_spans.nth(i)
        title = (await t.inner_text()).strip()
        a = t.locator("xpath=ancestor::a[1]")
        href = None
        try:
            if await a.count() > 0:
                href = await a.first.get_attribute("href")
        except Exception:
            pass
        items.append({"title": title, "href": href, "index_on_page": i})
    return items

async def goto_page(page: Page, page_no: int) -> bool:
    sel = SEL["pager_link_fmt"].format(page=str(page_no))
    try:
        before_first = ""
        try:
            el = page.locator(SEL["item_title_span"]).first
            await el.wait_for(state="visible", timeout=6000)
            before_first = (await el.inner_text()).strip()
        except Exception:
            pass

        await page.locator(sel).first.click(timeout=8000)
        # 等到首条标题变化
        await page.wait_for_function(
            """(prev, sel) => {
                const el = document.querySelector(sel);
                if (!el) return true;
                const first = el.textContent?.trim();
                return !prev || (first && first !== prev);
            }""",
            arg=before_first,
            timeout=15000,
            # 将选择器传入
        )
        await rand_wait()
        await page.screenshot(path=f"{SCREEN_DIR}/list_page_{page_no}.png")
        return True
    except Exception:
        try:
            await page.wait_for_selector(SEL["item_title_span"], timeout=8000)
            await rand_wait(0.3, 0.7)
            return True
        except PWTimeout:
            return False

async def iter_pages_and_items(page: Page, start_page: int, max_pages: int) -> AsyncGenerator[Dict, None]:
    await apply_filters_and_sort(page)
    if start_page and start_page > 1:
        await goto_page(page, start_page)

    page_no = start_page if start_page and start_page > 1 else 1
    for _ in range(max_pages):
        try:
            await page.wait_for_selector(SEL["item_title_span"], timeout=15000)
        except PWTimeout:
            yield {"page": page_no, "items": []}
        else:
            items = await extract_items_on_page(page)
            yield {"page": page_no, "items": items}

        page_no += 1
        ok = await goto_page(page, page_no)
        if not ok:
            break