import asyncio
from playwright.async_api import async_playwright
from app.services.logger import logger

class AutomationService:
    async def run_script(self, ws_endpoint, script_name):
        logger.info(f"Starting script '{script_name}' on {ws_endpoint}")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(ws_endpoint)
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else await context.new_page()
                
                if script_name == "check_login":
                    await self._check_login(page)
                elif script_name == "warmup":
                    await self._warmup(page)
                
                await browser.close()
                logger.info(f"Script '{script_name}' finished successfully")
        except Exception as e:
            logger.error(f"Automation error: {str(e)}")

    async def _check_login(self, page):
        await page.goto("https://accounts.google.com/", wait_until="networkidle")
        content = await page.content()
        if "Sign in" in content or "identifier" in content:
            logger.info("Result: Not logged in")
        else:
            logger.info("Result: Logged in")

    async def _warmup(self, page):
        sites = ["https://www.google.com", "https://www.youtube.com", "https://www.wikipedia.org"]
        for site in sites:
            logger.info(f"Visiting {site}...")
            await page.goto(site, wait_until="networkidle")
            await asyncio.sleep(2)

automation = AutomationService()
