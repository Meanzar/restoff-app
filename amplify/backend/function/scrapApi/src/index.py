import json
import time
import sys
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import boto3
from botocore.exceptions import ClientError

# Add path for AWS Lambda environment
sys.path.append("/var/task/python")

# Function to retrieve the Yelp API key from AWS Secrets Manager
def get_api_key(secret_name="apikey", region_name="eu-north-1"):
    """
    Retrieves the Yelp API key from AWS Secrets Manager.
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            secret_dict = json.loads(secret)
            return secret_dict.get('yelp_api_key')
        else:
            print(f"Secret {secret_name} does not contain a 'SecretString'.")
            return None
            

def get_reviews(business_name, url):
    """
    Scrapes reviews from a restaurant's Yelp page using Selenium.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', './chromedriver/linux-132.0.6834.159/chromedriver-linux64/chromedriver')
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    reviews_data = []
    try:
        driver.get(url)
        # time.sleep(5)

        reviews = driver.find_elements(By.CLASS_NAME, "comment__09f24__D0cxf")

        if not reviews:
            return []

        for review in reviews[:10]:
            reviews_data.append(review.text)

    except Exception as e:
        print(f"Error fetching reviews for {business_name}: {e} \nURL: {url}")

    finally:
        driver.quit()

    return reviews_data

def search_restaurants():
    """
    Fetches restaurant data from the Yelp API and scrapes reviews.
    """
    # Retrieve the API key from Secrets Manager
    API_KEY = get_api_key()
    if not API_KEY:
        return {"error": "API key not found."}

    API_URL = "https://api.yelp.com/v3/businesses/search"
    params = {
        "location": "Paris",
        "categories": "restaurants",
        "limit": 30,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    restaurant_data = []
    index = 0

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        businesses = response.json().get("businesses", [])

        if not businesses:
            return {"error": "No restaurants found."}

        for business in businesses:
            restaurant_info = {
                "id": str(index),
                "restaurantId": business.get("id", "N/A"),
                "name": business.get("name", "N/A"),
                "rating": business.get("rating", "N/A"),
                "price": business.get("price", "N/A"),
                "address": business["location"].get("address1", "N/A"),
                "phone": business.get("display_phone", "N/A"),
                "url": business.get("url", "N/A"),
                "reviews": get_reviews(business["name"], business["url"]),
            }

            restaurant_data.append(restaurant_info)
            index += 1

        # Save data to AWS Lambda temporary storage
        tmp_path = "/tmp/restaurants_data.json"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump({"restaurants": restaurant_data}, f, indent=4, ensure_ascii=False)

        return {"message": "Data successfully saved.", "file_path": tmp_path}

    except requests.RequestException as e:
        return {"error": f"Error fetching data from Yelp API: {str(e)}"}

def handler(event, context):
    """
    AWS Lambda handler function.
    """
    result = search_restaurants()
    return {
        "statusCode": 200 if "error" not in result else 500,
        "body": json.dumps(result),
    }
