import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { TypeOrmModule } from '@nestjs/typeorm';
import { OAuthController } from './oauth.controller';
import { OAuthService } from './oauth.service';
import { EtsyOAuthService } from './etsy-oauth.service';
import { OAuthToken } from '../core/entities/oauth-token.entity';
import { UsersModule } from '../users/users.module';
import { AuthModule } from '../auth/auth.module';

@Module({
  imports: [
    HttpModule,
    TypeOrmModule.forFeature([OAuthToken]),
    UsersModule,
  ],
  controllers: [OAuthController],
  providers: [OAuthService, EtsyOAuthService],
  exports: [OAuthService],
})
export class OAuthModule {}