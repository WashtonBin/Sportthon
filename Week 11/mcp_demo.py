from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
api_key = os.getenv("OPEN_API_KEY")

async def run(mcp_server: MCPServer, prompt: str):
    agent = Agent(
        name = "Assistant",
        instructions = "You are a helpful assistant and would use given tools to help user.",
        mcp_servers = [mcp_server],
    )

    message  = prompt
    response = await Runner.run(agent, message)
    return (response.final_output)
    


async def main(prompt: str):
    async with MCPServerStdio(
        name = "Weather Server",
        params= {
            "command" : "mcp",
            "args": ["run", "server.py"]
        }
    ) as server:
        tool_list = await server.list_tools()
        for tool in tool_list:
            print(f"Tool Name: {tool.name}")
        
        print("Starting MCP Server")
        result = await run(server, prompt)
        return result 
        
        
async def currency_exchange(prompt: str):
    async with MCPServerStdio(
        name = "Currency Exchange Server",
        params= {
            "command" : "mcp",
            "args": ["run", "server_temp.py"]
        }
    ) as server_temp:
        tool_list = await server_temp.list_tools()
        for tool in tool_list:
            print(f"Tool Name: {tool.name}")
        
        print("Starting MCP Server")
        result = await run(server_temp, prompt)
        return result


        
"""SQLite3 demo"""        
async def sqlite(prompt: str):
    async with MCPServerStdio(
        name = "SQLite3 Server",
        params= {
            "command" : "mcp",
            "args": ["run", "sqlite_demo.py"]
        }
    ) as sqlite_demo:
        tool_list = await sqlite_demo.list_tools()
        for tool in tool_list:
            print(f"Tool Name: {tool.name}")
        
        print("Starting MCP Server")
        result = await run(sqlite_demo, prompt)
        return result
    
    
def sql_prompt (prompt):
    return asyncio.run(sqlite(prompt))
        
#run the server
if __name__ == "__main__":
#     prompt = "delete name DDD Adams and print the all data in subscribe.db"
    #   prompt = "fetch names which subscription dates are 2023 in table name as subscribers in subscribe.db"
    # prompt = "load data from ./sample.csv, put data in table_name sample1 in SAMPLE.db"
    prompt = "Show Washington DC weather"
    result = asyncio.run(main(prompt))
    # prompt = "currency rate of 1 dollor to 1 euro"
    # result = asyncio.run(currency_exchange(prompt))
    # result = sql_prompt(prompt)
    print(result)

