from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Weather Server")

@mcp.tool()
def get_weather(city: str) -> str:
    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text

@mcp.tool()
def get_exchange(a: str) -> str:
    endpoint = "https://api.frankfurter.dev/v1/latest?base="
    response = requests.get(f"{endpoint}{a}")
    return response.text

@mcp.tool()
def add_number(a:int, b:int) -> int:
    return a + b

@mcp.tool()
def print_welcome(name: str) -> int:
    return f"Welcome {name}"

#run the server
if __name__ == "__main__":
    mcp.run()

