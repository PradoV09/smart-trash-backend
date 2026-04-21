import asyncio
from controllers.controller_rutas import listar_rutas
from schemas.schema_responses import SuccessResponse
from schemas.schema_rutas_externas import RutaResponse
import pydantic

async def main():
    try:
        res = await listar_rutas("f105a9d3-13b3-4066-b5f7-edae6801e366")
        
        # Simulate FastAPI serialization
        class Wrapper(pydantic.BaseModel):
            success: bool
            message: str
            data: list[RutaResponse]
        
        Wrapper(**res)
        print("Serialization successful")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
