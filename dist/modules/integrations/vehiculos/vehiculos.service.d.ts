export declare class VehiculosService {
    constructor();
    data: any;
    getAll(): Promise<{
        msg: string;
        data: any;
    }>;
    create(dto: any): Promise<{
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
    update(id: string, dto: any): Promise<{
        msg: string;
        data: any;
    }>;
    remove(id: string): Promise<{
        msg: string;
    }>;
}
