import asyncio
import httpx

async def main():
    url = "https://apirecoleccion.gonzaloandreslucio.com/api/vehiculos"
    payload = {
        "placa": "ZZZ-999",
        "modelo": "Test",
        "activo": True,
        "perfil_id": "f105a9d3-13b3-4066-b5f7-edae6801e366",
    }
    async with httpx.AsyncClient(timeout=30.0, headers={"Accept": "application/json"}) as client:
        # First test without marca
        print("Testing duplicate placa:")
        payload["placa"] = "ZZZ-991"
        resp = await client.post(url, json=payload)
        print(resp.status_code, resp.text)

if __name__ == "__main__":
    asyncio.run(main())
