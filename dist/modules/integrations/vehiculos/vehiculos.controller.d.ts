import { VehiculosService } from './vehiculos.service';
export declare class VehiculosController {
    private readonly vehiculosService;
    constructor(vehiculosService: VehiculosService);
    getAll(): Promise<{
        msg: string;
        data: any;
    }>;
    create(body: any): Promise<{
        msg: string;
        data: any;
        error?: undefined;
    } | {
        msg: string;
        data?: undefined;
        error?: undefined;
    } | {
        msg: string;
        error: any;
        data?: undefined;
    }>;
    findOne(id: string): Promise<{
        msg: string;
        data: any;
    }>;
    update(id: string, body: any): Promise<{
        msg: string;
        data: any;
    }>;
    remove(id: string): Promise<{
        msg: string;
    }>;
}
