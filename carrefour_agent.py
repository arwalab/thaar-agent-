from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def add_to_cart_carrefour(item_name):
    driver = attach_to_thaar_session()
    driver.get("https://www.carrefourksa.com/mafksa/en/")

    try:
        # ✅ Use correct ID selector for the search bar
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "search-bar"))
        )
        search_box.clear()
        search_box.send_keys(item_name)
        search_box.send_keys(Keys.ENTER)  # simulate hitting Enter

        print(f"🔎 Searching for: {item_name}")

        # ✅ Wait for search results to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-grid .product-card"))
        )

        # 🔄 Adjust this selector if needed for "Add to cart" button
        add_button = driver.find_element(By.CSS_SELECTOR, ".add-to-cart-button, .addBtn")
        add_button.click()

        print(f"🛒 Added to cart: {item_name}")

    except Exception as e:
        print(f"❌ Failed to reorder: {e}")
    finally:
        driver.quit()
