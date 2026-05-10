import { RutasService } from './rutas.service';
export declare class RutasController {
    private readonly rutasService;
    constructor(rutasService: RutasService);
    getAll(): Promise<{
        msg: string;
        data: any;
    }>;
    create(body: any): Promise<{
        msg: string;
        data: any;
    }>;
    findOneBy(id: string): Promise<{
        msg: string;
        data: any;
    }>;
}
