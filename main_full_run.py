# main_full_run.py
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from settings import (
    HEADLESS, USER_DATA_DIR, PROXY, TIMEOUT,
    START_PAGE, MAX_PAGES_PER_RUN, OUT_XLSX
)
from auth_and_nav import ensure_login, go_to_short_video_square
from list_scraper_kuaishou import iter_pages_and_items
from detail_scraper_kuaishou import scrape_detail_full
from storage_excel import export_records_to_excel

async def run():
    # 反检测浏览器参数
    launch_args = {
        "headless": HEADLESS,
        "args": [
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "--exclude-switches=enable-automation",
            "--disable-extensions-except=/path/to/extension",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--disable-browser-side-navigation",
            "--disable-gpu",
            "--disable-features=WebRtcHideLocalIpsWithMdns",
            "--disable-ipc-flooding-protection"
        ]
    }
    if PROXY:
        launch_args["proxy"] = {"server": PROXY}

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(user_data_dir=USER_DATA_DIR, **launch_args)
        page = await browser.new_page()
        
        # 手动移除自动化检测特征
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh'],
            });
            
            window.chrome = {
                runtime: {},
            };
        """)
        
        page.set_default_timeout(TIMEOUT)

        # 1) 登录 + 导航到“短视频广场”起始列表
        await ensure_login(page)
        ok = await go_to_short_video_square(page)
        if not ok:
            print("导航失败，退出。")
            await browser.close()
            return

        # 2) 列表翻页 & 采集详情
        all_records = []
        async for bundle in iter_pages_and_items(page, START_PAGE, MAX_PAGES_PER_RUN):
            page_no = bundle["page"]
            items = bundle["items"]
            print(f"[列表 第 {page_no} 页] 共 {len(items)} 条")
            for item in items:
                idx = item["index_on_page"]
                rec = await scrape_detail_full(page, idx)
                if rec:
                    all_records.append(rec)
                # 回到列表以继续
                await page.go_back(wait_until="domcontentloaded")

        # 3) 导出 Excel
        export_records_to_excel(all_records, OUT_XLSX)
        print(f"已写入：{OUT_XLSX}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
