from playwright.sync_api import sync_playwright

def generate_pdf(rendered, pdf_file, format):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(rendered)
        # Wait for loads ensures images are ready
        page.wait_for_load_state("networkidle") 
        page.pdf(path=pdf_file, format=format)
        browser.close()