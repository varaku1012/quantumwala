import { Module } from '@nestjs/common';
import { MfaController } from './mfa.controller';
import { MfaService } from './mfa.service';
import { TotpService } from './totp.service';
import { SmsService } from './sms.service';
import { UsersModule } from '../users/users.module';
import { EmailModule } from '../email/email.module';
import { CacheModule } from '../cache/cache.module';

@Module({
  imports: [
    UsersModule,
    EmailModule,
    CacheModule,
  ],
  controllers: [MfaController],
  providers: [MfaService, TotpService, SmsService],
  exports: [MfaService],
})
export class MfaModule {}