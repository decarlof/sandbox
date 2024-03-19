import requests

def get_github_user(username):
    base_url = "https://api.github.com"
    endpoint = f"/users/{username}"
    url = base_url + endpoint
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling GitHub API: {e}")
        return None

# Example usage
if __name__ == "__main__":
    username = "decarlof"  # Replace this with the GitHub username you want to fetch
    user_data = get_github_user(username)
    
    if user_data:
        print("GitHub User Data:")
        print(user_data)