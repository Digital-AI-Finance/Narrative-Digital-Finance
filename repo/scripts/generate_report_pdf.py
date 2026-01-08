"""Generate PDF version of the SNSF Final Scientific Report using Playwright."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

REPO_DIR = Path(__file__).parent.parent
REPORT_HTML = REPO_DIR / "report.html"
OUTPUT_PDF = REPO_DIR / "docs" / "SNSF_Final_Scientific_Report.pdf"

async def generate_pdf():
    print(f"Reading HTML from: {REPORT_HTML}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Load the HTML file
        await page.goto(f"file:///{REPORT_HTML.as_posix()}")

        # Hide navbar for PDF
        await page.add_style_tag(content="""
            .navbar { display: none !important; }
            body { padding-top: 0 !important; }
        """)

        # Wait for content to load
        await page.wait_for_load_state("networkidle")

        print(f"Generating PDF...")
        await page.pdf(
            path=str(OUTPUT_PDF),
            format="A4",
            margin={"top": "2cm", "bottom": "2cm", "left": "2.5cm", "right": "2.5cm"},
            print_background=True
        )

        await browser.close()

    print(f"PDF saved to: {OUTPUT_PDF}")
    print(f"File size: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB")

def main():
    asyncio.run(generate_pdf())

if __name__ == "__main__":
    main()
