def call_api(endpoint, params=None):
    base_url = "https://api.example.com"  # Replace this with your API base URL
    url = f"{base_url}/{endpoint}"
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None

# Example usage
if __name__ == "__main__":
    endpoint = "example_endpoint"  # Replace this with the actual endpoint
    params = {"param1": "value1", "param2": "value2"}  # Replace with actual parameters
    response_data = call_api(endpoint, params)
    
    if response_data:
        print("API Response:")
        print(response_data)

