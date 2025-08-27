# detail_scraper_kuaishou.py
from typing import Dict, List, Optional
from playwright.async_api import Page, TimeoutError as PWTimeout
from settings import SEL, SCREEN_DIR, TIMEOUT
from utils import rand_wait, click, wait_visible, all_texts

# ---- 进入/返回 ----
async def open_detail_from_list(page: Page, index_on_page: int) -> bool:
    titles = page.locator(SEL["item_title_span"])
    count = await titles.count()
    if index_on_page >= count:
        return False
    prev_url = page.url
    await titles.nth(index_on_page).click()
    try:
        await page.wait_for_selector(f"{SEL['audience_tag']}, {SEL['overview_number']}", timeout=20_000)
        await rand_wait()
        await page.screenshot(path=f"{SCREEN_DIR}/detail_open_{index_on_page}.png")
        return True
    except PWTimeout:
        return page.url != prev_url

async def back_to_list(page: Page):
    try:
        await page.go_back(wait_until="domcontentloaded"); await rand_wait()
    except Exception:
        pass

# ---- Part 1: 达人概览 + 观众标签 ----
async def extract_overview_numbers(page: Page) -> List[str]:
    vals = await all_texts(page, SEL["overview_number"])
    return [v for v in vals if v.strip()]

async def extract_audience_tags(page: Page) -> Dict[str, List[str]]:
    tags = await all_texts(page, SEL["audience_tag"])
    return {
        "all_tags": tags,
        "by_guess": {
            "观众特征": [t for t in tags if any(k in t for k in ["男性", "女性", "年龄", "岁", "学生", "为主"])],
            "观众设备": [t for t in tags if any(k in t for k in ["设备", "安卓", "iOS", "价格"])],
            "观众分布": [t for t in tags if any(k in t for k in ["城市", "省", "地区", "观众居多"])],
        }
    }

# ---- Part 2: 传播表现 ----
async def goto_spread_perf_tab(page: Page) -> bool:
    await click(page, SEL["tab_spread_perf"])
    ok = await wait_visible(page, SEL["metric_name"], timeout=15_000)
    await page.screenshot(path=f"{SCREEN_DIR}/perf_tab_open.png")
    return ok

async def select_range_and_content(page: Page, range_btn: str, content_btn: str):
    await click(page, range_btn); await click(page, content_btn); await rand_wait(0.4, 0.9)

async def extract_metrics_on_panel(page: Page) -> Dict[str, str]:
    result: Dict[str, str] = {}
    names = page.locator(SEL["metric_name"])
    n = await names.count()
    for i in range(n):
        name_el = names.nth(i)
        try:
            name = (await name_el.inner_text()).strip()
        except Exception:
            continue
        card = name_el.locator("xpath=ancestor::div[contains(@class,'card') or contains(@class,'item') or contains(@class,'grid')][1]")
        value = ""
        try:
            v = card.locator(SEL["metric_value_generic"])
            if await v.count() == 0:
                v = name_el.locator("xpath=ancestor::div[1]").locator(SEL["metric_value_generic"])
            if await v.count() > 0:
                value = (await v.first.inner_text()).strip()
        except Exception:
            pass
        if not value:
            try:
                sib = name_el.locator("xpath=following::span[1]")
                value = (await sib.inner_text()).strip()
            except Exception:
                value = ""
        result[name] = value
    return result

async def extract_chart_subtitles(page: Page) -> Dict[str, str]:
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.85)"); await rand_wait(0.5, 1.0)
    out: Dict[str, str] = {}
    if await wait_visible(page, SEL["chart_subtitle"], timeout=10_000):
        out["播放量"] = (await page.locator(SEL["chart_subtitle"]).first.inner_text()).strip()
    if await click(page, SEL["chart_tab_like"], timeout=6000):
        await rand_wait(0.3, 0.7)
        out["点赞量"] = (await page.locator(SEL["chart_subtitle"]).first.inner_text()).strip()
    if await click(page, SEL["chart_tab_comment"], timeout=6000):
        await rand_wait(0.3, 0.7)
        out["评论量"] = (await page.locator(SEL["chart_subtitle"]).first.inner_text()).strip()
    if await click(page, SEL["chart_tab_share"], timeout=6000):
        await rand_wait(0.3, 0.7)
        out["分享量"] = (await page.locator(SEL["chart_subtitle"]).first.inner_text()).strip()
    return out

async def scrape_spread_performance(page: Page) -> Dict:
    ok = await goto_spread_perf_tab(page)
    if not ok:
        return {"error": "传播表现未出现"}
    out: Dict[str, Dict[str, str] | Dict] = {}
    await select_range_and_content(page, SEL["btn_last_30d"], SEL["btn_personal_works"])
    out["A_30d_personal"] = await extract_metrics_on_panel(page)
    await select_range_and_content(page, SEL["btn_last_30d"], SEL["btn_juxing_works"])
    out["B_30d_juxing"] = await extract_metrics_on_panel(page)
    await select_range_and_content(page, SEL["btn_last_90d"], SEL["btn_juxing_works"])
    out["C_90d_juxing"] = await extract_metrics_on_panel(page)
    await select_range_and_content(page, SEL["btn_last_90d"], SEL["btn_personal_works"])
    out["D_90d_personal"] = await extract_metrics_on_panel(page)
    out["charts"] = await extract_chart_subtitles(page)
    return out

# ---- Part 3: 受众分析 ----
async def goto_audience_tab(page: Page) -> bool:
    await click(page, SEL["tab_audience_analysis"])
    ok = await wait_visible(page, SEL["growth_title"], timeout=15_000)
    await page.screenshot(path=f"{SCREEN_DIR}/audience_tab_open.png")
    return ok

async def extract_growth(page: Page, range_btn_selector: str) -> Dict[str, str]:
    await click(page, range_btn_selector); await rand_wait(0.3, 0.7)
    titles = await all_texts(page, SEL["growth_title"])
    values = await all_texts(page, SEL["growth_value"])
    result: Dict[str, str] = {}
    vi = 0
    for t in titles:
        if "涨粉" in t:
            val = values[vi] if vi < len(values) else ""
            result[t] = val
            vi += 1
    return result

async def extract_portrait_pair(page: Page, switch_btn: Optional[str]) -> Dict[str, str]:
    if switch_btn:
        await click(page, switch_btn); await rand_wait(0.3, 0.7)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.7)"); await rand_wait(0.3, 0.7)
    out = {"性别分布": "", "年龄分布": ""}
    if await wait_visible(page, SEL["gender_desc"], timeout=8000):
        out["性别分布"] = (await page.locator(SEL["gender_desc"]).first.inner_text()).strip()
    if await wait_visible(page, SEL["age_desc"], timeout=8000):
        out["年龄分布"] = (await page.locator(SEL["age_desc"]).first.inner_text()).strip()
    return out

async def scrape_audience_analysis(page: Page) -> Dict:
    ok = await goto_audience_tab(page)
    if not ok:
        return {"error": "受众分析未出现"}
    out: Dict = {"growth": {}, "portraits": {}}
    out["growth"]["30d"] = await extract_growth(page, SEL["btn_last_30d"])
    out["growth"]["90d"] = await extract_growth(page, SEL["btn_last_90d"])
    out["portraits"]["观众画像"] = await extract_portrait_pair(page, SEL["btn_audience_portrait"])
    out["portraits"]["粉丝画像"] = await extract_portrait_pair(page, SEL["btn_fans_portrait"])
    return out

# ---- 汇总：三大块 ----
async def scrape_detail_full(page: Page, index_on_page: int) -> Optional[Dict]:
    if not await open_detail_from_list(page, index_on_page):
        return None
    part1_numbers = await extract_overview_numbers(page)
    part1_audience_tags = await extract_audience_tags(page)
    part2_spread = await scrape_spread_performance(page)
    part3_audience = await scrape_audience_analysis(page)
    return {
        "index_on_page": index_on_page,
        "detail_url_after_click": page.url,
        "overview_numbers": part1_numbers,
        "audience_tags": part1_audience_tags,
        "spread_performance": part2_spread,
        "audience_analysis": part3_audience,
    }
