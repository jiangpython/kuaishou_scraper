# auth_and_nav_stealth.py - 使用 stealth 模式的登录方案
import os, asyncio
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from playwright_stealth import Stealth
from settings import (
    LOGIN_URL, BASE_URL, HEADLESS, 
    PROXY, TIMEOUT, ACCOUNT, PASSWORD, SEL, SCREEN_DIR
)
from utils import click, wait_visible, rand_wait


async def ensure_login_stealth(page):
    """使用stealth模式的登录函数"""
    # 应用stealth插件
    stealth = Stealth()
    await stealth.apply_stealth_async(page)
    
    # 1. 打开快手商业平台首页
    await page.goto(LOGIN_URL, wait_until="domcontentloaded")
    await page.screenshot(path=f"{SCREEN_DIR}/stealth_step_1_homepage.png")
    print("已打开快手达人生态营销平台首页")
    
    # 2. 检查是否已登录
    login_indicators = [
        "text=退出登录", 
        "text=控制台", 
        "[class*='user']",
        ".avatar",
        "[data-testid='user-menu']",
        "text=工作台"
    ]
    
    for indicator in login_indicators:
        if await page.locator(indicator).count() > 0:
            print("✅ 检测到已登录状态")
            return True
    
    # 3. 需要登录，等待手动操作
    print("\n" + "="*50)
    print("🚨 需要手动登录，请按以下步骤操作：")
    print("1. 在打开的浏览器中点击'我是客户'或其他角色按钮")
    print("2. 输入账号密码")
    print("3. 完成滑动验证码")
    print("4. 选择身份角色")
    print("5. 确保进入控制台或工作台界面")
    print("="*50 + "\n")
    
    # 4. 智能等待登录完成
    max_wait_time = 600  # 10分钟
    check_interval = 3   # 每3秒检查一次
    
    for i in range(0, max_wait_time, check_interval):
        # 检查登录状态
        for indicator in login_indicators:
            if await page.locator(indicator).count() > 0:
                print("✅ 登录成功！")
                await page.screenshot(path=f"{SCREEN_DIR}/stealth_login_success.png")
                return True
        
        remaining = max_wait_time - i
        print(f"⏳ 等待登录中... 剩余 {remaining} 秒")
        await asyncio.sleep(check_interval)
    
    print("❌ 登录等待超时")
    await page.screenshot(path=f"{SCREEN_DIR}/stealth_login_timeout.png")
    return False


async def auth_and_nav_stealth():
    """使用stealth模式的认证和导航"""
    
    # 更激进的反检测浏览器参数
    launch_args = {
        "headless": HEADLESS,
        "channel": "chrome",  # 使用系统Chrome而不是Chromium
        "args": [
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor,AutomationControlled",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-setuid-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-field-trial-config",
            "--disable-ipc-flooding-protection",
            "--enable-features=NetworkService,NetworkServiceInProcess",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ],
    }
    
    if PROXY:
        launch_args["proxy"] = {"server": PROXY}

    async with async_playwright() as p:
        # 使用普通browser模式，不用persistent_context
        browser = await p.chromium.launch(**launch_args)
        
        # 创建新的上下文和页面
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale='zh-CN',
            timezone_id='Asia/Shanghai'
        )
        
        page = await context.new_page()
        page.set_default_timeout(TIMEOUT)
        
        # 添加额外的反检测脚本
        await page.add_init_script("""
            // 移除webdriver标识
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // 修复chrome对象
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // 修复plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                    {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
                    {name: 'Native Client', filename: 'internal-nacl-plugin', description: 'Native Client'}
                ],
            });
            
            // 修复permission
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // 添加真实的屏幕属性
            Object.defineProperty(screen, 'availHeight', {get: () => 1040});
            Object.defineProperty(screen, 'availWidth', {get: () => 1920});
            Object.defineProperty(screen, 'colorDepth', {get: () => 24});
        """)
        
        # 执行登录
        success = await ensure_login_stealth(page)
        
        if success:
            print("🎉 登录流程完成！")
        else:
            print("⚠️ 登录可能未完成，但浏览器保持打开状态")
            
        # 保持浏览器打开供手动验证
        print("\n按 Enter 关闭浏览器...")
        input()
        
        await browser.close()


if __name__ == "__main__":
    print("🚀 启动 Playwright Stealth 登录模式")
    asyncio.run(auth_and_nav_stealth())