import { Role } from "@entities/roles.entity";
export declare class User {
    id: string;
    nameuser: string;
    password: string;
    refreshToken: string | null;
    role: Role;
    createdAt: Date;
    updatedAt: Date;
}
