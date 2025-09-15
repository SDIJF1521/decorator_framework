import asyncio
from decorators.on import re_on
from nucleus.dispatcher import ReTaskScheduler

# 测试正则任务
@re_on(
    name="test_hello",
    content="hello",
    pattern=r"hello",
    priority=1
).execute()
async def test_hello():
    print("hello world")
    return "hello"

async def main():
    print("=== 测试正则任务 ===")
    rd = ReTaskScheduler()
    
    print("\n1. 触发正则任务 'test_hello' 匹配 'hello':")
    results = await rd.trigger("test_hello", "hello")
    print(f"结果: {results}")
    
    print("\n2. 触发正则任务 'test_hello' 匹配 'say hello world':")
    results = await rd.trigger("test_hello", "say hello world")
    print(f"结果: {results}")
    
    print("\n3. 触发正则任务 'test_hello' 匹配 'hi':")
    results = await rd.trigger("test_hello", "hi")
    print(f"结果: {results}")

if __name__ == "__main__":
    asyncio.run(main())