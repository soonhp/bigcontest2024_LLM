import pandas as pd
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor
import re

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(executable_path="/media/jys/ssd/workspace/003_Competition/006_KAIT-2024-Big-Contest/chromedriver-linux64/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

def get_store_id(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    try:
        first_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cid]')))
        store_id = first_element.get_attribute('data-cid')
        return store_id
    except TimeoutException:
        print("요소를 찾을 수 없습니다. 스토어 ID를 가져오지 못했습니다.")
        return None
    except Exception as e:
        print(f"스토어 ID를 가져오는 중 오류 발생: {str(e)}")
        return None

def crawl_menu(driver, store_id):
    store_url = f"https://m.place.naver.com/restaurant/{store_id}/menu/list"
    driver.get(store_url)
    time.sleep(random.uniform(0.5, 1.5))
    
    menu_sections = driver.find_elements(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div/div[@class="place_section gkWf3"]')
    
    if menu_sections:
        return crawl_menu_with_sections(driver)
    else:
        return crawl_menu_without_sections(driver)

def crawl_menu_with_sections(driver):
    return driver.execute_script("""
        const sections = document.querySelectorAll('.place_section.gkWf3');
        const menuData = {};
        let menuIndex = 1;
        
        sections.forEach(section => {
            const menuItems = section.querySelectorAll('ul._d0Hx li');
            menuItems.forEach(item => {
                const menuName = item.querySelector('.lPzHi')?.textContent || '';
                const priceText = item.querySelector('.GXS1X')?.textContent || '0';
                const price = parseInt(priceText.replace(/[^0-9]/g, '')) || 0;
                
                menuData[menuIndex.toString()] = {
                    name: menuName,
                    price: price
                };
                menuIndex++;
            });
        });
        
        return menuData;
    """)

def crawl_menu_without_sections(driver):
    return driver.execute_script("""
        const menuItems = document.querySelectorAll('.place_section_content ul li.E2jtL');
        const menuData = {};
        let menuIndex = 1;
        
        menuItems.forEach(item => {
            const menuName = item.querySelector('.lPzHi')?.textContent || '';
            const priceText = item.querySelector('.GXS1X')?.textContent || '0';
            const price = parseInt(priceText.replace(/[^0-9]/g, '')) || 0;
            
            menuData[menuIndex.toString()] = {
                name: menuName,
                price: price
            };
            menuIndex++;
        });
        
        return menuData;
    """)

def crawl_review(driver, store_id):
    store_url = f"https://m.place.naver.com/restaurant/{store_id}/review/visitor?reviewSort=recent"
    driver.get(store_url)
    time.sleep(2)

    result = {"unique_id": store_id}

    result["image_url"] = get_image_url(driver)
    result["coordinate"] = get_coordinates(driver)
    result["rating"], result["rating_count"] = get_rating_info(driver)
    
    reviews = get_reviews(driver)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        parsed_reviews = list(executor.map(parse_review, reviews[:100]))
    
    result["review"] = {str(i+1): review for i, review in enumerate(parsed_reviews)}
    
    return result

def get_image_url(driver):
    try:
        image_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'img.K0PDV._div'))
        )
        return image_element.get_attribute('src')
    except (NoSuchElementException, TimeoutException):
        return None

def get_coordinates(driver):
    try:
        find_way_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="longitude"][href*="latitude"]'))
        )
        href = find_way_element.get_attribute('href')
        
        longitude = re.search(r'longitude%5E([\d.]+)', href).group(1)
        latitude = re.search(r'latitude%5E([\d.]+)', href).group(1)

        return {
            "lat": float(latitude),
            "lng": float(longitude)
        }
    except (NoSuchElementException, TimeoutException):
        return None

def get_rating_info(driver):
    try:
        rating_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.vWSFS span.xobxM.fNnpD em'))
        )
        rating = float(rating_element.text)

        rating_count_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.vWSFS span.xobxM:nth-child(2)'))
        )
        rating_count = int(rating_count_element.text.split('개')[0].replace(',', ''))

        return rating, rating_count
    except (NoSuchElementException, TimeoutException, ValueError):
        return None, None
        
def get_reviews(driver):
    reviews = []
    more_button_xpath = '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[3]/div[2]/div/a/span'
    
    while len(reviews) < 100:
        try:
            more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, more_button_xpath))
            )
            driver.execute_script("arguments[0].click();", more_button)
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            break
        
        reviews = driver.find_elements(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[3]/div[1]/ul/li')
    
    return reviews

def parse_review(review):
    parsed_data = {}
    
    try:
        user_info = review.find_element(By.CSS_SELECTOR, '.pui__JiVbY3')
        parsed_data['user_id'] = user_info.find_element(By.CSS_SELECTOR, '.pui__NMi-Dp').text
    except:
        parsed_data['user_id'] = '알 수 없음'
    
    visit_keywords = review.find_elements(By.CSS_SELECTOR, '.pui__V8F9nN')
    parsed_data['visit_keywords'] = list(set(keyword.text.replace("대기 시간 ", "") if "대기 시간 " in keyword.text else keyword.text for keyword in visit_keywords))
    
    try:
        review_content = review.find_element(By.CSS_SELECTOR, '.pui__xtsQN-')
        parsed_data['review'] = review_content.text
    except:
        parsed_data['review'] = ''
    
    return parsed_data

def main():
    # CSV 파일 읽기
    df = pd.read_csv('/media/jys/ssd/workspace/003_Competition/006_KAIT-2024-Big-Contest/unique_mct_cleaned.csv')

    # 키워드 리스트 생성
    keywords = []
    for _, row in df.iterrows():
        addr_parts = row['ADDR'].split()[:3]
        keyword = ' '.join(addr_parts + [row['MCT_NM']])
        keywords.append((urllib.parse.quote(keyword), row['MCT_NM'], row['ADDR'], row['OP_YMD'], row['pk']))

    # 결과를 저장할 딕셔너리
    results = {}

    # 기존 결과 파일이 있다면 로드
    try:
        with open('/media/jys/ssd/workspace/003_Competition/006_KAIT-2024-Big-Contest/results.json', 'r', encoding='utf-8') as f:
            results = json.load(f)
    except FileNotFoundError:
        pass

    # 키워드 루프
    for i, (encoded_keyword, mct_nm, addr, op_ymd, pk) in enumerate(keywords, start=1):
        print(encoded_keyword)
        if str(pk) in results:
            print(f"이미 처리된 키워드: {urllib.parse.unquote(encoded_keyword)}")
            continue
        
        print(f"상호명: {mct_nm}")
        url = f"https://m.map.naver.com/search2/search.naver?query={encoded_keyword}"
        
        driver = setup_driver()
        try:
            store_id = get_store_id(driver, url)
            if store_id is None:
                print("스토어 ID를 가져오지 못했습니다. 다음 가게로 넘어갑니다.")
                continue
            
            review_data = crawl_review(driver, store_id)
            menu_data = crawl_menu(driver, store_id)
            
            results[str(pk)] = {
                "MCT_NM": mct_nm,
                "ADDR": addr,
                "OP_YMD": op_ymd,
                **review_data,
                "menu": menu_data
            }
            
            # 각 키워드 처리 후 결과 저장
            with open('/media/jys/ssd/workspace/003_Competition/006_KAIT-2024-Big-Contest/results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4, default=lambda x: list(x) if isinstance(x, set) else x)
            
        finally:
            driver.quit()

    print("모든 처리 완료")

if __name__ == "__main__":
    main()