# auth_system_browser.py - 使用系统浏览器的方案
import os, asyncio, subprocess, time
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from settings import LOGIN_URL, SCREEN_DIR
import webbrowser


async def launch_system_browser():
    """使用系统默认浏览器打开快手商业平台"""
    
    print("🌐 使用系统浏览器打开快手商业平台...")
    print("1. 即将打开系统默认浏览器")
    print("2. 请在浏览器中完成完整登录流程")
    print("3. 登录成功后，请保持浏览器打开")
    print("4. 然后我们用Playwright连接到该浏览器")
    
    # 打开系统浏览器
    webbrowser.open(LOGIN_URL)
    
    print("\n请在系统浏览器中完成登录，完成后按 Enter 继续...")
    input()
    
    return True


async def connect_to_existing_browser():
    """连接到已打开的Chrome浏览器"""
    
    print("🔗 尝试连接到现有Chrome浏览器...")
    
    # 启动Chrome的调试模式（如果还没启动的话）
    debug_port = 9222
    
    try:
        async with async_playwright() as p:
            # 连接到现有的Chrome实例
            browser = await p.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
            
            if not browser:
                print("❌ 无法连接到Chrome浏览器")
                print("请确保Chrome浏览器已用调试模式启动：")
                print(f"chrome.exe --remote-debugging-port={debug_port} --user-data-dir=./chrome-debug-profile")
                return False
                
            contexts = browser.contexts
            if not contexts:
                print("❌ 没有找到浏览器上下文")
                return False
                
            context = contexts[0]
            pages = context.pages
            
            if not pages:
                print("❌ 没有找到打开的页面")
                return False
                
            page = pages[0]
            
            # 检查当前页面
            current_url = page.url
            print(f"📄 当前页面: {current_url}")
            
            # 检查登录状态
            login_indicators = [
                "text=退出登录", 
                "text=控制台", 
                "text=工作台"
            ]
            
            logged_in = False
            for indicator in login_indicators:
                if await page.locator(indicator).count() > 0:
                    logged_in = True
                    break
            
            if logged_in:
                print("✅ 检测到已登录状态！")
                await page.screenshot(path=f"{SCREEN_DIR}/system_browser_logged_in.png")
                
                # 保持连接，供后续操作使用
                print("🎉 连接成功！现在可以进行数据采集...")
                print("按 Enter 断开连接...")
                input()
            else:
                print("⚠️ 未检测到登录状态，请确认登录完成")
                
            await browser.close()
            return logged_in
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def launch_chrome_debug_mode():
    """启动Chrome调试模式"""
    debug_port = 9222
    profile_dir = "./chrome-debug-profile"
    
    # 创建配置文件目录
    os.makedirs(profile_dir, exist_ok=True)
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "chrome.exe",  # 如果在PATH中
        "google-chrome",  # Linux
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path) or path in ["chrome.exe", "google-chrome"]:
            chrome_path = path
            break
    
    if not chrome_path:
        print("❌ 未找到Chrome浏览器")
        return False
    
    cmd = [
        chrome_path,
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={profile_dir}",
        "--disable-features=VizDisplayCompositor",
        LOGIN_URL
    ]
    
    try:
        print(f"🚀 启动Chrome调试模式: {' '.join(cmd)}")
        subprocess.Popen(cmd)
        time.sleep(3)  # 等待浏览器启动
        return True
    except Exception as e:
        print(f"❌ 启动Chrome失败: {e}")
        return False


async def system_browser_workflow():
    """完整的系统浏览器工作流程"""
    
    print("🎯 系统浏览器登录方案")
    print("="*50)
    
    choice = input("选择操作:\n1. 启动Chrome调试模式并登录\n2. 连接到现有Chrome\n3. 使用默认浏览器登录\n请输入选择 (1/2/3): ")
    
    if choice == "1":
        if launch_chrome_debug_mode():
            print("✅ Chrome已启动，请在浏览器中完成登录")
            print("登录完成后按 Enter 继续...")
            input()
            await connect_to_existing_browser()
        else:
            print("❌ 启动Chrome失败")
            
    elif choice == "2":
        await connect_to_existing_browser()
        
    elif choice == "3":
        await launch_system_browser()
        
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    asyncio.run(system_browser_workflow())