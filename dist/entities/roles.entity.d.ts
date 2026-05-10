import { User } from "@modules/users/entities/user.entity";
export declare class Role {
    id: string;
    nameRol: string;
    description: string;
    users: User[];
    createdAt: Date;
    updatedAt: Date;
}
