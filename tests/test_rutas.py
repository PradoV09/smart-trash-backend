import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get("http://127.0.0.1:8000/api/rutas?perfil_id=f105a9d3-13b3-4066-b5f7-edae6801e366")
            print(r.status_code)
            print(r.text)
        except Exception as e:
            print("Error:", e)

asyncio.run(main())
