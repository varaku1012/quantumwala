import { IsString, IsEnum } from 'class-validator';

export enum MfaType {
  TOTP = 'totp',
  SMS = 'sms',
  EMAIL = 'email',
}

export class MfaVerifyDto {
  @IsString()
  code: string;

  @IsEnum(MfaType)
  type: MfaType;
}