import asyncio
import httpx

async def main():
    url = "https://apirecoleccion.gonzaloandreslucio.com/api/vehiculos"
    perfil_id = "f105a9d3-13b3-4066-b5f7-edae6801e366"
    
    placas_a_borrar = [
        "IPY  428", "IPY  429", "IPY  430",
        "IPY_428", "IPY_429", "IPY_430",
        "ipy428", "Ipy428"
    ]
    
    async with httpx.AsyncClient(timeout=30.0, headers={"Accept": "application/json"}) as client:
        # 1. Fetch
        print("Fetching vehicles...")
        resp = await client.get(url, params={"perfil_id": perfil_id})
        
        if resp.status_code != 200:
            print("Failed to fetch:", resp.text)
            return
            
        data = resp.json()
        items = data.get("data", []) if isinstance(data, dict) else data
        if isinstance(items, dict) and "data" in items:
            items = items["data"]
            
        # 2. Find and Delete
        for item in items:
            placa = item.get("placa")
            vid = item.get("id")
            
            if placa in placas_a_borrar:
                print(f"Deleting {placa} (ID: {vid})...")
                del_url = f"{url}/{vid}"
                del_resp = await client.delete(del_url, params={"perfil_id": perfil_id})
                print(f"Result: {del_resp.status_code} {del_resp.text}")

if __name__ == "__main__":
    asyncio.run(main())
