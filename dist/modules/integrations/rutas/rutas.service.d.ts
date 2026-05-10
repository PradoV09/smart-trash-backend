export declare class RutasService {
    constructor();
    data: any;
    getAll(): Promise<{
        msg: string;
        data: any;
    }>;
    create(dto: any): Promise<{
        msg: string;
        data: any;
    }>;
    finOneBy(id: string): Promise<{
        msg: string;
        data: any;
    }>;
}
