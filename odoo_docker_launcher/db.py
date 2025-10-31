import asyncio
import subprocess

import typer
from playwright.async_api import async_playwright

from odoo_docker_launcher.services.custom_logger import CustomLogger

app = typer.Typer(
    no_args_is_help=True,
    add_completion=True,
    help="Configuration files operations"
)

logger = CustomLogger()

@app.command(help="Create Odoo database")
def create(port: str = "8069"):
    asyncio.run(create_database(port))

async def create_database(port: str) -> None:
    logger.print_status("Creating database")

    for i in range(2):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(f"http://localhost:{port}/web/database/manager")
                await page.fill("input[name=\"master_pwd\"]", "master")
                await page.fill("input[name=\"name\"]", "master")
                await page.fill("input[name=\"login\"]", "master")
                await page.fill("input[name=\"password\"]", "master")
                await page.select_option('#lang', 'es_ES')
                await page.select_option('#country', 'es')
                await page.click("text=Create database")

            logger.print_success("Database created successfully")
            return
        except Exception as e:
            # Try again if Playwright is not installed
            if i == 0 and "playwright install" in str(e):
                _check_playwright()
            else:
                logger.print_error(f"Failed to create database: {e}")


def _check_playwright():
    # Verify that Playwright is installed
    logger.print_warning("Playwright is not installed, attempting installation")
    try:
        subprocess.run(
            "playwright install chromium",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )

        logger.print_success("Playwright installed successfully")
    except subprocess.CalledProcessError as e:
        logger.print_error(f"Failed to install Playwright: {e}")

if __name__ == "__main__":
    app()