from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class TestBrowser(object):
    A_HREF = re.compile(r'<a [^>]*?href="(.*?)"[^>]*?>')
    QID = re.compile(r'OLQ-[0-9]{4}')

    def test_zero_time(self):
        driver = webdriver.Firefox()
        response = driver.get("http://qrel.openliveq.net/")
        btn = driver.find_element_by_css_selector(".btn")
        qid = self.QID.search(btn.get_attribute("href")).group(0)
        for j in range(100):
            driver.get("http://qrel.openliveq.net/next/%s/%s" % (qid, j))
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "question"))
                )
                elem = driver.find_element_by_css_selector(".title")
                elem.click()
            except TimeoutException as e:
                if 'class="code"' in driver.page_source:
                    break
                else:
                    raise e
            print(j)
        assert 'class="code"' in driver.page_source
        driver.close()
        driver.quit()
