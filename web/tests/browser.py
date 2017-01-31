from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

class TestBrowser(object):

    def test_sample(self):
        driver = webdriver.Firefox()
        driver.get("http://qrel.openliveq.net/")
        for j in range(100):
            driver.get("http://qrel.openliveq.net/next/OLQ-0001/%s" % j)
            print(j)
        assert 'class="code"' in driver.page_source
        driver.close()
        driver.quit()
