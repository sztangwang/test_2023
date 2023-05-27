import uiautomator2
import time
import re

driver = None

def get_uiautomator2_driver(ADDRESS):
    global driver
    driver = uiautomator2.connect(ADDRESS)
    return driver

def text_exist(text,ADDRESS):
    global driver
    if not driver:
        driver = get_uiautomator2_driver(ADDRESS)

    return driver(text=text).exists()

def id_exist(text,ADDRESS):
    global driver
    if not driver:
        driver = get_uiautomator2_driver(ADDRESS)

    return driver(text=text).exists()

def class_name_exist(class_name,ADDRESS, timeout=30):
    global driver
    if not driver:
        driver = get_uiautomator2_driver(ADDRESS)
    try:
        if driver.find_elements_by_class_name(class_name).exists(timeout=timeout):
            return True
        return False
    except Exception as e:
        return False


def click(element,ADDRESS):
    global driver
    try:
        if not driver:
            driver = get_uiautomator2_driver(ADDRESS)

        if re.findall(',',element):
            id = element.split(',')[0]
            text = element.split(',')[1]
            driver(resourceId=id,text=text).click()

        elif str(element).startswith("com"): 
            driver(resourceId=element).click()

        elif re.findall("//", str(element)):
            driver.xpath(element).click()
        else: 
            driver(text=element).click()
    except Exception as e:
        print(e)
        return False
    return True

def exist(element,ADDRESS):
    global driver
    try:
        if not driver:
            driver = get_uiautomator2_driver(ADDRESS)
        if re.findall(',',element):
            id = element.split(',')[0]
            text = element.split(',')[1]
            return driver(resourceId=id,text=text).exists()

        elif str(element).startswith("com"): 
            return driver(resourceId=element).exists()

        elif re.findall("//", str(element)):
            return driver.xpath(element).exists()
        else: 
            return driver(text=element).exists()

    except:
        return False


# print(find_element_by_text('拍照',"1709e242"))
# print(text_click('拍照',"1709e242"))
# time.sleep(1)
# print(text_click('直播',"1709e242"))

# print(text_click('录像',"1709e242"))
# time.sleep(1)