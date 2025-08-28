# quick_test.py - 快速测试登录
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from settings import LOGIN_URL, SCREEN_DIR

async def quick_test():
    """快速测试stealth登录"""
    
    async with async_playwright() as p:
        # 使用Chrome而不是Chromium，更好的反检测效果
        try:
            browser = await p.chromium.launch(
                channel="chrome",  # 使用系统Chrome
                headless=False,
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=VizDisplayCompositor",
                    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                ]
            )
        except Exception:
            print("系统Chrome不可用，使用Chromium...")
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--start-maximized", 
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=VizDisplayCompositor",
                    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                ]
            )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        # 应用stealth
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        print("🚀 浏览器已启动，正在打开快手商业平台...")
        
        # 打开页面
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        await page.screenshot(path=f"{SCREEN_DIR}/quick_test_page.png")
        
        print("✅ 页面已打开！")
        print("请在浏览器中手动完成登录...")
        print("登录完成后请按 Enter 键继续...")
        
        # 等待用户完成登录
        input()
        
        # 检查登录状态
        login_indicators = [
            "text=退出登录", 
            "text=控制台", 
            "text=工作台",
            "[class*='user']"
        ]
        
        logged_in = False
        for indicator in login_indicators:
            if await page.locator(indicator).count() > 0:
                logged_in = True
                print(f"✅ 检测到登录成功标识: {indicator}")
                break
        
        if logged_in:
            print("🎉 登录成功！可以开始数据采集了")
            await page.screenshot(path=f"{SCREEN_DIR}/login_success.png")
        else:
            print("⚠️ 未检测到明确的登录标识，请确认登录状态")
            await page.screenshot(path=f"{SCREEN_DIR}/login_uncertain.png")
            
        print("按 Enter 关闭浏览器...")
        input()
        
        await browser.close()

if __name__ == "__main__":
    print("🧪 快速登录测试")
    asyncio.run(quick_test())