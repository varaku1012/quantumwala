import { IsString } from 'class-validator';

export class DisableMfaDto {
  @IsString()
  password: string;
}