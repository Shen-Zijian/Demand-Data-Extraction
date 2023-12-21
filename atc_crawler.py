from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
# 初始化WebDriver
driver = webdriver.Chrome(ChromeDriverManager().install())

# 打开目标网页
driver.get('https://atc.td.gov.hk/aadt')

# 使用显式等待来确保页面已加载并且元素可交互
wait = WebDriverWait(driver, 20)

# 定位<select>元素，它嵌套在<div class="col-sm-1">元素下面
station_select_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@id="analysis"]//div[@class="container-fluid"]//form[@class]//div[@class="row"]//div[@class="col-sm-1"]//select[@id="stationSelect"]')))

# 使用Select类来与<select>元素交互
select = Select(station_select_element)
res_dict = {}
options = select.options
start_index = None
for i, option in enumerate(options):
    if option.text == "5042":  # 或者是option.get_attribute("value") == "5041"，取决于<select>的实际使用方式
        start_index = i
        break
#
# 通过选项值选择选项
submit_button_xpath = '/html/body/div/div/div[3]/div[2]/div/button'
#submit_button_xpath = '//div[@id="analysis"]//div[@class="container-fluid"]//div[@class="calBackground row"]//div[@class="chartBackground allsideBorder col"]//div//button[@class="downloadBtn btn btn-primary"]'

link_name_xpath = '/html/body/div/div/form[2]/div/div[2]/div/div[1]/input'
#
for option in options[start_index:]:
    # 选择<option>
    select.select_by_visible_text(option.text)
    # link_name = wait.until(EC.visibility_of_element_located((By.XPATH, link_name_xpath)))
    # value = link_name.get_attribute('value')
    # res_dict[option.text] = value

    submit_button_element = wait.until(EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button_element)
    time.sleep(5)
    submit_button_element.click()
    time.sleep(1)
# print(res_dict)
# with open('link_name.json', 'w') as handle:
#     json.dump(res_dict, handle)



