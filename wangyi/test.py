from selenium import webdriver

browser = webdriver.Chrome()
browser.implicitly_wait(10)

browser.get("https://www.zhihu.com/people/gu-wan-zhi-40/followers?page=2")

element = browser.find_elements_by_xpath("//span[@class='ContentItem-statusItem'][last()]")
for each in element:
    list = each.text.split(" ")
    print(list[0])
# while 1:
#     try:
#         button = browser.find_element_by_xpath(
#             "//button[@class='Button PaginationButton PaginationButton-next Button--plain'][last()]")
#         button.click()
#     except:
#         print("循环完毕")
#         break

# for index, item in enumerate(element):
#     if item.text != "":
#         print(str(index) + ">>>>>" + item.text)