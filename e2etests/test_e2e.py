import os
import re
from urllib.parse import urlencode, urljoin

from playwright.sync_api import Page, expect

from api_utils import create_pteam, create_vuln, get_pteam_services, upload_pteam_packages
from constants import PACKAGE1, PACKAGE2, PTEAM1, USER1, VULN1, VULN2

base_url = os.getenv("BASE_URL", "http://localhost")


def print_console(page: Page):
    page.on("console", lambda msg: print("console:", msg.text, msg.location))


def login(page: Page, user: dict):
    """
    common function to login on login page
    """
    # If you want log console message, uncomment below line
    # https://playwright.dev/python/docs/api/class-consolemessage
    # page.on("console", lambda msg: print(msg.text, msg.args, msg.location))

    # goto Threatconnectome login page
    page.goto(urljoin(base_url, "/login"))

    # page tile should be "Threatconnectome"
    expect(page).to_have_title(re.compile("Threatconnectome"))

    # Login form to be editable
    expect(page.get_by_label("Email Address")).to_be_editable()
    expect(page.get_by_label("Password")).to_be_editable()

    # Login
    page.get_by_label("Email Address").fill(user["email"])
    page.get_by_label("Password").fill(user["pass"])
    page.get_by_role("button", name="Log In with Email").click()

    # Wait login process finish and print menu button
    # https://playwright.dev/python/docs/api/class-locator#locator-wait-for
    drawer_status = page.locator("text=Status")
    drawer_status.wait_for(timeout=10000)


def test_login_first_time(page: Page):
    print_console(page)
    # register user1 by login
    login(page, USER1)

    # navigate to account page
    expect(page).to_have_url(re.compile(".*/"))


def test_show_package_page_directly(page: Page):
    print_console(page)
    # register data via API
    pteam1 = create_pteam(USER1, PTEAM1)
    ext_packages = [
        {
            "package_name": PACKAGE1["package_name"],
            "ecosystem": PACKAGE1["ecosystem"],
            "package_manager": "test_package_manager1",
            "references": [{"target": "target1", "version": "1.0"}],
        },
        {
            "package_name": PACKAGE2["package_name"],
            "ecosystem": PACKAGE2["ecosystem"],
            "package_manager": "test_package_manager1",
            "references": [{"target": "target1", "version": "1.0"}],
        },
    ]
    packages = upload_pteam_packages(USER1, pteam1["pteam_id"], "repoA", ext_packages)
    create_vuln(USER1, VULN1)
    create_vuln(USER1, VULN2)

    # get service id
    services = get_pteam_services(USER1, pteam1["pteam_id"])
    service_id = services[0]["service_id"]

    # goto tag page directly
    params = urlencode({"pteamId": pteam1["pteam_id"], "serviceId": service_id})
    path = "/packages/" + packages[0]["package_id"]
    url = urljoin(base_url, path) + "?" + params
    page.goto(url)

    # navigate to login page
    expect(page).to_have_url(re.compile(".*/login"))
    # Login
    page.get_by_label("Email Address").fill(str(USER1["email"]))
    page.get_by_label("Password").fill(str(USER1["pass"]))
    page.get_by_role("button", name="Log In").click()
    # package page
    expect(page).to_have_url(re.compile(path))

    package_title = f"{packages[0]['package_name']}:{packages[0]['ecosystem']}"
    heading = page.get_by_role("heading", name=package_title)
    heading.wait_for(timeout=10000)
    expect(heading).to_have_text(package_title)

    expect(page.locator("#ssvc-priority-count-chip-immediate")).to_have_text("1")
    expect(page.locator("#ssvc-priority-count-chip-out_of_cycle")).to_have_text("0")
    expect(page.locator("#ssvc-priority-count-chip-scheduled")).to_have_text("0")
    expect(page.locator("#ssvc-priority-count-chip-defer")).to_have_text("0")
    expect(page.locator("#tab-panel-0").locator("td", has_text=str(VULN2["title"]))).to_be_visible()


def test_show_package_page(page: Page):
    print_console(page)
    login(page, USER1)

    page.locator("#team-selector-button").click()
    page.get_by_role("menuitem", name=str(PTEAM1["pteam_name"])).click()
    # status page
    package_title1 = f"{PACKAGE1['package_name']}:{PACKAGE1['ecosystem']}"
    expect(page.get_by_role("heading", name=package_title1)).to_have_text(package_title1)
    expect(page.get_by_role("rowheader", name=package_title1)).to_have_text(
        re.compile(package_title1)
    )
    page.get_by_role("rowheader", name=package_title1).click()

    # tag page
    expect(page.get_by_role("heading", name=package_title1)).to_have_text(package_title1)
    expect(page.locator("#ssvc-priority-count-chip-immediate")).to_have_text("1")
    expect(page.locator("#ssvc-priority-count-chip-out_of_cycle")).to_have_text("0")
    expect(page.locator("#ssvc-priority-count-chip-scheduled")).to_have_text("0")
    expect(page.locator("#ssvc-priority-count-chip-defer")).to_have_text("0")
    expect(page.locator("#tab-panel-0").locator("td", has_text=str(VULN1["title"]))).to_be_visible()
