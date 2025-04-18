from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Currency Exchange Server")


@mcp.tool()
def get_exchange_temp(a: str) -> str:
    endpoint = "https://api.frankfurter.dev/v1/latest?base="
    response = requests.get(f"{endpoint}{a}")
    return response.text

#run the server
if __name__ == "__main__":
    mcp.run()