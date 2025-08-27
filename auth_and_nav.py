# auth_and_nav.py
import os, asyncio
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from settings import (
    LOGIN_URL, BASE_URL, HEADLESS, USER_DATA_DIR,
    PROXY, TIMEOUT, ACCOUNT, PASSWORD, SEL, SCREEN_DIR
)
from utils import click, wait_visible, rand_wait


async def ensure_login(page):
    # 打开登录页
    await page.goto(LOGIN_URL, wait_until="domcontentloaded")
    await page.screenshot(path=f"{SCREEN_DIR}/step_1_login_page.png")

    # 点击“我是客户”
    ok = await click(page, SEL["btn_i_am_customer_primary"]) or await click(page, SEL["btn_i_am_customer_fallback_text"])

    # 如果在 settings.py 里配置了账号密码，自动填充
    if ACCOUNT and PASSWORD:
        try:
            await page.fill(SEL["input_account"], ACCOUNT, timeout=TIMEOUT)
            await page.fill(SEL["input_password"], PASSWORD, timeout=TIMEOUT)
        except Exception:
            pass

        for sel in SEL["btn_login_candidates"]:
            if await click(page, sel):
                break

    print("请在弹出浏览器中手动完成验证/扫码（最多等 5 分钟）…")
    try:
        await page.wait_for_selector(", ".join(SEL["login_ok_indicators"]), timeout=300_000)
        print("检测到登录成功标识。")
    except PWTimeout:
        print("未检测到登录成功标识，但会话可能已保存；如失败可重试。")

    await page.screenshot(path=f"{SCREEN_DIR}/step_3_logged_in.png")


async def go_to_short_video_square(page) -> bool:
    await page.goto(BASE_URL, wait_until="load")
    await page.screenshot(path=f"{SCREEN_DIR}/step_4_at_base.png")

    # 找 User_xxx → 点击“进入”
    space_row = page.locator(SEL["space_row_by_text"]).first
    try:
        await space_row.wait_for(state="visible", timeout=120_000)
    except PWTimeout:
        print("未找到包含目标空间的条目。")
        await page.screenshot(path=f"{SCREEN_DIR}/error_no_space_row.png")
        return False

    enter_btn = space_row.locator(SEL["space_enter_link"]).first
    try:
        await enter_btn.click(timeout=10_000)
    except Exception:
        container = space_row.locator("xpath=..").first
        await container.locator("a.entry:has-text('进入')").first.click()

    await page.wait_for_load_state("domcontentloaded")
    await page.screenshot(path=f"{SCREEN_DIR}/step_5_after_enter.png")

    # 页面2：找达人 → 短视频广场
    await click(page, SEL["tab_find_creator"])
    await page.screenshot(path=f"{SCREEN_DIR}/step_6_after_find_creator.png")
    await click(page, SEL["cat_short_video_square"])
    await page.wait_for_load_state("domcontentloaded")
    await page.screenshot(path=f"{SCREEN_DIR}/step_7_short_video_square.png")
    return True


async def auth_and_nav():
    # 用 Playwright 自带 Chromium，不再用系统 Chrome
    launch_args = {
        "headless": HEADLESS,
        "args": ["--start-maximized"],
    }
    if PROXY:
        launch_args["proxy"] = {"server": PROXY}

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,  # 存储会话在本地目录
            **launch_args
        )
        page = await browser.new_page()
        page.set_default_timeout(TIMEOUT)

        # 登录 + 导航
        await ensure_login(page)
        ok = await go_to_short_video_square(page)
        if ok:
            print("导航完成。")
            await asyncio.sleep(3)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(auth_and_nav())
