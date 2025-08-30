from dotenv import load_dotenv
import os
import webbrowser
from selenium import webdriver
import time
import upstox_client
from upstox_client.rest import ApiException



path = os.path.abspath("a.env")
load_dotenv(path)


def get_env_variable():
    # Access the variables
    api = os.getenv("API_KEY")
    secret = os.getenv("SECRET_KEY")
    redirected_url = os.getenv("REDIRECTED_URL")
    state = "Rohit"

    # check if variables are loaded correctly
    if not all([api, secret, redirected_url]):
        raise ValueError("One or more environment variables are missing or not loaded correctly.")
    else:
        print("Environment variables loaded successfully.")

    return api, secret, redirected_url, state    


def get_auth_code(api, redirected_url, state, env_file="a.env"):
    # Construct the URL
    url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={api}&redirect_uri={redirected_url}&state={state}"
    
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(30)  # wait for manual login
    
    final_url = driver.current_url
    if "code=" not in final_url:
        driver.quit()
        raise ValueError("Login failed or redirected URL does not contain authorization code.")
    
    auth_code = final_url[final_url.index("code=") + 5:final_url.index("&state=")]
    driver.quit()

    # Read existing env file
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # Update or add AUTH_CODE
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("AUTH_CODE="):
            lines[i] = f"AUTH_CODE={auth_code}\n"
            updated = True
            break
    if not updated:
        lines.append(f"\nAUTH_CODE={auth_code}\n")

    # Write back to file
    with open(env_file, "w") as f:
        f.writelines(lines)

    print(f"AUTH_CODE updated in {env_file}")
    return auth_code



def get_access_token(secret, api , auth_code, redirected_url):

    api_instance = upstox_client.LoginApi()
    api_version = '2.0'
    code = auth_code
    client_id = api
    client_secret = secret
    redirect_uri = redirected_url
    grant_type = 'authorization_code'

    try:
        # Get token API
        api_response = api_instance.token(api_version, code=code, client_id=client_id, client_secret=client_secret,
                                            redirect_uri=redirect_uri, grant_type=grant_type)
        access_token = api_response.access_token

    except ApiException as e:
        print("Exception when calling LoginApi->token: %s\n" % e)

    with open("acess_token.env", "w") as f:
        f.write(f"ACCESS_TOKEN={access_token}\n")    

    return access_token    


api , secret, redirected_url, state = get_env_variable()
auth_code = get_auth_code(api , redirected_url, state)
access_token = get_access_token(secret, api , auth_code, redirected_url)
print("Access Token:", access_token)
        

