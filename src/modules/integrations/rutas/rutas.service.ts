import { Injectable } from '@nestjs/common';
const axios = require('axios');

@Injectable()
export class RutasService {
    constructor() { }
    public data: any;
    async getAll() {
        const response = await axios.get(process.env.API_URL + '/rutas/?perfil_id=' + process.env.API_KEY)

        return {
            msg: 'Rutas encontrados exitosamente.',
            data: response.data
        };
    }

    async create(dto: any) {
        const data = {
            ...dto,
            perfil_id: process.env.API_KEY,
        };
        const res = await axios.post(process.env.API_URL + '/rutas', data);
        return {
            msg : 'Ruta creada',
            data: res.data
        }
    }

    async finOneBy(id: string){
        const response = await axios.get(`${process.env.API_URL}/rutas/${id}?perfil_id=${process.env.API_KEY}`);

        return {
            msg: 'Ruta encontrado exitosamente.',
            data: response.data
        };
    }
}
