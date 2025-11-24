import { Injectable } from '@nestjs/common';

@Injectable()
export class VehiculosService {
    constructor() { }
    public data: any;

    async getAll() {
        let axios = require('axios');
        const response = await axios.get(process.env.API_URL + '/vehiculos/?perfil_id=' + process.env.API_KEY)

        return {
            msg: 'vehiculos encontrados',
            data: response.data
        };

    }
}
