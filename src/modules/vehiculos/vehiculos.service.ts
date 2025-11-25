import { Injectable } from '@nestjs/common';

@Injectable()
export class VehiculosService {
    constructor() { }
    public data: any;

    async getAll() {
        const axios = require('axios');

        const response = await axios.get(process.env.API_URL + '/vehiculos/?perfil_id=' + process.env.API_KEY)

        return {
            msg: 'Vehículos encontrados exitosamente.',
            data: response.data
        };
    }

    async create(dto: any) {
        const axios = require('axios');

        const data = {
            ...dto,
            perfil_id: process.env.API_KEY,
            activo: true
        };

        try {
            const res = await axios.post(process.env.API_URL + '/vehiculos', data);
            return {
                msg: 'Vehículo registrado correctamente',
                data: res.data
            };

        } catch (err) {
            const backendMsg = err.response?.data?.message;

            if (backendMsg?.includes('placa has already been taken')) {
                return { msg: 'Esa placa ya está registrada.' };
            }

            return {
                msg: 'Error creando vehículo.',
                error: backendMsg || 'Error desconocido'
            };
        }
    }

    async findOne(id: string) {
        const axios = require('axios');

        const response = await axios.get(`${process.env.API_URL}/vehiculos/${id}?perfil_id=${process.env.API_KEY}`);

        return {
            msg: 'Vehículo encontrado exitosamente.',
            data: response.data
        };
    }

    async update(id: string, dto: any) {
        const axios = require('axios');

        const data = {
            ...dto,
            activo: true,
            perfil_id: process.env.API_KEY
        };

        const url = `${process.env.API_URL}/vehiculos/${id}`;

        const response = await axios.put(url, data);

        return {
            msg: 'Vehículo actualizado exitosamente.',
            data: response.data
        };
    }

    async remove(id: string) {
        const axios = require('axios');

        const url = `${process.env.API_URL}/vehiculos/${id}?perfil_id=${process.env.API_KEY}`;

        await axios.delete(url);

        return {
            msg: 'El vehículo se ha eliminado exitosamente.'
        };
    }
}
