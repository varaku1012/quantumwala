import {
  Controller,
  Get,
  Query,
  Redirect,
  UseGuards,
  Request,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { OAuthService } from './oauth.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@Controller('auth')
export class OAuthController {
  constructor(
    private readonly oauthService: OAuthService,
    private readonly configService: ConfigService,
  ) {}

  @Get('etsy')
  @Redirect()
  initiateEtsyOAuth(@Query('redirect_uri') redirectUri?: string) {
    const state = this.oauthService.generateState(redirectUri);
    const authUrl = this.oauthService.getEtsyAuthorizationUrl(state);
    
    return { url: authUrl };
  }

  @Get('etsy/callback')
  async handleEtsyCallback(
    @Query('code') code: string,
    @Query('state') state: string,
    @Query('error') error?: string,
  ) {
    if (error) {
      throw new HttpException(
        `OAuth error: ${error}`,
        HttpStatus.BAD_REQUEST,
      );
    }

    if (!code || !state) {
      throw new HttpException(
        'Missing code or state parameter',
        HttpStatus.BAD_REQUEST,
      );
    }

    const result = await this.oauthService.handleEtsyCallback(code, state);
    
    // Redirect to frontend with tokens
    const frontendUrl = this.configService.get('FRONTEND_URL');
    const redirectUrl = new URL(`${frontendUrl}/auth/callback`);
    redirectUrl.searchParams.append('token', result.tokens.accessToken);
    redirectUrl.searchParams.append('refresh', result.tokens.refreshToken);
    
    return { url: redirectUrl.toString() };
  }

  @UseGuards(JwtAuthGuard)
  @Get('etsy/disconnect')
  async disconnectEtsy(@Request() req) {
    await this.oauthService.disconnectEtsy(req.user.id);
    return { message: 'Etsy account disconnected successfully' };
  }

  @UseGuards(JwtAuthGuard)
  @Get('etsy/refresh')
  async refreshEtsyToken(@Request() req) {
    await this.oauthService.refreshEtsyToken(req.user.id);
    return { message: 'Etsy token refreshed successfully' };
  }
}