import { IsString, IsEnum, Length } from 'class-validator';
import { MfaType } from '../mfa.service';

export class VerifyMfaDto {
  @IsString()
  @Length(6, 6)
  code: string;

  @IsEnum(MfaType)
  type: MfaType;
}