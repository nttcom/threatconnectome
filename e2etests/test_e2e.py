import os
import re
from urllib.parse import urlencode, urljoin

from playwright.sync_api import Page, expect

from api_utils import create_pteam, create_topic
from constants import ACTION1, ACTION2, PTEAM1, TAG1, TOPIC1, TOPIC2, USER1

base_url = os.getenv("BASE_URL", "http://localhost")


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

    # Wait login process finish and print logout button
    # https://playwright.dev/python/docs/api/class-locator#locator-wait-for
    logout_button = page.locator("text=Logout")
    logout_button.wait_for(timeout=10000)


def test_login_first_time(page: Page):
    # register user1 by login
    login(page, USER1)
    # navigate to account page
    expect(page).to_have_url(re.compile(".*/account"))


def test_show_tag_page_directly(page: Page):
    # register data via API
    pteam1 = create_pteam(USER1, PTEAM1)
    create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    create_topic(USER1, TOPIC2, actions=[ACTION1, ACTION2])

    # goto tag page directly
    params = urlencode({"pteamId": pteam1["pteam_id"]})
    path = "/tags/" + pteam1["tags"][0]["tag_id"]
    url = urljoin(base_url, path) + "?" + params
    page.goto(url)

    # navigate to login page
    expect(page).to_have_url(re.compile(".*/login"))
    # Login
    page.get_by_label("Email Address").fill(str(USER1["email"]))
    page.get_by_label("Password").fill(str(USER1["pass"]))
    page.get_by_role("button", name="Log In").click()

    # tag page
    expect(page).to_have_url(re.compile(path))
    expect(page.get_by_role("heading", name=TAG1)).to_have_text(TAG1)
    expect(page.locator("#threat-impact-count-chip-1")).to_have_text("1")
    expect(page.locator("#threat-impact-count-chip-2")).to_have_text("1")
    expect(page.locator("#threat-impact-count-chip-3")).to_have_text("0")
    expect(page.locator("#threat-impact-count-chip-4")).to_have_text("0")
    expect(page.get_by_role("heading", name=str(TOPIC1["title"]))).to_have_text(
        str(TOPIC1["title"])
    )
    expect(page.get_by_role("heading", name=str(TOPIC2["title"]))).to_have_text(
        str(TOPIC2["title"])
    )


def test_show_tag_page(page: Page):
    login(page, USER1)

    page.locator("#team-selector-button").click()
    page.get_by_role("menuitem", name=str(PTEAM1["pteam_name"])).click()
    # status page
    expect(page.get_by_role("heading", name=str(PTEAM1["pteam_name"]))).to_have_text(
        str(PTEAM1["pteam_name"])
    )
    expect(page.get_by_role("rowheader", name=TAG1)).to_have_text(re.compile(TAG1))
    page.get_by_role("rowheader", name=TAG1).click()

    # tag page
    expect(page.get_by_role("heading", name=TAG1)).to_have_text(TAG1)
    expect(page.locator("#threat-impact-count-chip-1")).to_have_text("1")
    expect(page.locator("#threat-impact-count-chip-2")).to_have_text("1")
    expect(page.locator("#threat-impact-count-chip-3")).to_have_text("0")
    expect(page.locator("#threat-impact-count-chip-4")).to_have_text("0")
    expect(page.get_by_role("heading", name=str(TOPIC1["title"]))).to_have_text(
        str(TOPIC1["title"])
    )
    expect(page.get_by_role("heading", name=str(TOPIC2["title"]))).to_have_text(
        str(TOPIC2["title"])
    )
