import { IsEnum } from 'class-validator';
import { MfaType } from '../mfa.service';

export class EnableMfaDto {
  @IsEnum(MfaType)
  type: MfaType;
}