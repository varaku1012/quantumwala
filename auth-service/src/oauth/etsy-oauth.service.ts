import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class EtsyOAuthService {
  private readonly ETSY_API_URL = 'https://api.etsy.com/v3';
  private readonly ETSY_OAUTH_URL = 'https://api.etsy.com/v3/public/oauth/token';

  constructor(
    private httpService: HttpService,
    private configService: ConfigService,
  ) {}

  async exchangeCodeForTokens(code: string) {
    const data = {
      grant_type: 'authorization_code',
      client_id: this.configService.get('ETSY_CLIENT_ID'),
      redirect_uri: this.configService.get('ETSY_REDIRECT_URI'),
      code: code,
    };

    const response = await firstValueFrom(
      this.httpService.post(this.ETSY_OAUTH_URL, data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }),
    );

    return response.data;
  }

  async refreshAccessToken(refreshToken: string) {
    const data = {
      grant_type: 'refresh_token',
      client_id: this.configService.get('ETSY_CLIENT_ID'),
      refresh_token: refreshToken,
    };

    const response = await firstValueFrom(
      this.httpService.post(this.ETSY_OAUTH_URL, data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }),
    );

    return response.data;
  }

  async getUserInfo(accessToken: string) {
    const response = await firstValueFrom(
      this.httpService.get(`${this.ETSY_API_URL}/application/users/me`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'x-api-key': this.configService.get('ETSY_CLIENT_ID'),
        },
      }),
    );

    return response.data;
  }

  async getShopInfo(accessToken: string, shopId: string) {
    const response = await firstValueFrom(
      this.httpService.get(`${this.ETSY_API_URL}/application/shops/${shopId}`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'x-api-key': this.configService.get('ETSY_CLIENT_ID'),
        },
      }),
    );

    return response.data;
  }
}