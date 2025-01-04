from selenium import webdriver
from selenium.webdriver.common.by import By

# Specify the path to the ChromeDriver executable
driver = webdriver.Chrome(executable_path="install_chromedriver.py")

# Open a website
driver.get("https://example.com")

# Print the title of the page
print("Page Title:", driver.title)

# Close the browser
driver.quit()
