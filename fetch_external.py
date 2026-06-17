import asyncio
import httpx

async def main():
    url = "https://apirecoleccion.gonzaloandreslucio.com/api/vehiculos"
    
    # We will fetch without pagination if possible, or paginate.
    async with httpx.AsyncClient(timeout=30.0, headers={"Accept": "application/json"}) as client:
        resp = await client.get(url, params={"perfil_id": "f105a9d3-13b3-4066-b5f7-edae6801e366"})
        print("Status:", resp.status_code)
        
        try:
            data = resp.json()
            items = data.get("data", []) if isinstance(data, dict) else data
            if isinstance(items, dict) and "data" in items:
                items = items["data"]
                
            print(f"Total items fetched: {len(items)}")
            
            target_placas = ["IPY428", "IPY 428", "IPY-428", "IPY_428", "IPY429", "IPY 429", "IPY430", "IPY 430"]
            
            found = []
            for item in items:
                if item.get("placa") in target_placas:
                    found.append(item)
                    
            print("Found targets:")
            import json
            print(json.dumps(found, indent=2))
        except Exception as e:
            print("Error parsing JSON:", e)

if __name__ == "__main__":
    asyncio.run(main())
