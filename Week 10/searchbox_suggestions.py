import json
import requests

def suggestions(query):
    url = f"http://google.com/complete/search?client=chrome&q={query}"
            
    response = requests.get(url)

    MAXPRINT = 5
    i = 0
    suggestions = []
    for completetion in json.loads(response.text)[1]:
        if i < MAXPRINT:
            suggestions.append(completetion)
            i += 1
        else:
            break
    response = {
        "suggestions" : suggestions
    }
    return response

# if __name__ == "__main__":
#     query = "us stock market"
#     print(suggestions(query))
