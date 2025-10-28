import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from config import config
from database import OlimpField


@dataclass
class OlimpFile:
    date: str
    subject: str
    students_list_link: str
    classes: str
    protocols_link: str


class OlimpLoader:
    _ekis_base_url: str = "https://st.educom.ru/eduoffices/index.php"
    _headless = True
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None
    _page: Optional[Page] = None

    def __init__(self, debug: bool = config.debug):
        self._headless = debug

    async def init(self, login: str, password: str):
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(headless=self._headless is False)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()
        await self._page.goto(self._ekis_base_url)
        await self._page.wait_for_selector(".card-header__ekis")
        await self._page.fill('input[id="username"]', login)
        await self._page.fill('input[id="password"]', password)
        await self._page.locator("#btn_login_submit").click()
        await asyncio.sleep(5)

    async def look_for_olimp_files(self) -> list[OlimpFile]:
        await self._page.goto(self._ekis_base_url)
        await self._page.wait_for_selector(
            ".x-panel-body.x-grid-with-row-lines.x-grid-body.x-panel-body-default.x-panel-body-default.x-noborder-rbl")
        await self._page.locator(
            ".x-panel-body.x-grid-with-row-lines.x-grid-body.x-panel-body-default.x-panel-body-default.x-noborder-rbl").get_by_role(
            "link",
            name="Информация для мест проведения (МПО) муниципального этапа ВсОШ 2025-2026 уч. года").click()
        await self._page.wait_for_selector(
            ".x-panel-body.x-grid-with-col-lines.x-grid-with-row-lines.x-grid-body.x-panel-body-default.x-panel-body-default.x-noborder-rl.x-resizable.x-panel-body-resizable.x-panel-body-default-resizable")
        await asyncio.sleep(5)
        soup = BeautifulSoup(await self._page.locator(".x-panel-body.x-grid-with-col-lines.x-grid-with-row-lines.x-grid-body.x-panel-body-default.x-panel-body-default.x-noborder-rl.x-resizable.x-panel-body-resizable.x-panel-body-default-resizable").locator(".x-grid-item-container").evaluate(
            "el => el.outerHTML"),
                             "html.parser")
        rows = soup.find_all("table")
        current_files: list[OlimpFile] = []
        for table in rows:
            tr = table.find_all("tr")[0]
            date = tr.find_all("td")[2].text
            subject = tr.find_all("td")[3].text
            students_list_link = tr.find_all("td")[6].text if tr.find_all("td")[6].text.startswith("http") else ""
            protocols_link = tr.find_all("td")[8].text if tr.find_all("td")[8].text.startswith("http") else ""
            classes = tr.find_all("td")[4].text if tr.find_all("td")[4].text[0].isdigit() else ""
            current_files.append(
                OlimpFile(
                    date=date,
                    subject=subject,
                    students_list_link=students_list_link,
                    protocols_link=protocols_link,
                    classes=classes
                )
            )
        return current_files

    async def get_new_olimp_files(self, current_files: list[OlimpFile]) -> list[OlimpFile]:
        new_files: list[OlimpFile] = []
        db_files = [
            OlimpFile(
                date=file.date,
                subject=file.subject,
                students_list_link=file.students_list_link,
                protocols_link=file.protocols_link,
                classes=file.classes
            ) for file in OlimpField.select()
        ]
        for current_file in current_files:
            if current_file not in db_files and current_file.students_list_link != "":
                OlimpField.create(
                    date=current_file.date,
                    subject=current_file.subject,
                    students_list_link=current_file.students_list_link,
                    protocols_link=current_file.protocols_link,
                    classes=current_file.classes
                )
                new_files.append(current_file)
        return new_files

    async def download_olimp_file(self, file_url: str, download_dir_path: str) -> str:
        new_page = await self._context.new_page()
        async with new_page.expect_download() as download_info:
            try:
                await new_page.goto(file_url)
            except:
                pass
        download = await download_info.value
        path = Path(download_dir_path) / download.suggested_filename
        await download.save_as(path)
        await new_page.close()
        return str(path)
