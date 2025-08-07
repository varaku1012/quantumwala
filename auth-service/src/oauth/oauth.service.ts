import { Injectable, BadRequestException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { v4 as uuidv4 } from 'uuid';
import { EtsyOAuthService } from './etsy-oauth.service';
import { UsersService } from '../users/users.service';
import { OAuthToken, OAuthProvider } from '../core/entities/oauth-token.entity';
import { CacheService } from '../cache/cache.service';

@Injectable()
export class OAuthService {
  constructor(
    @InjectRepository(OAuthToken)
    private oauthTokenRepository: Repository<OAuthToken>,
    private etsyOAuthService: EtsyOAuthService,
    private usersService: UsersService,
    private configService: ConfigService,
    private cacheService: CacheService,
  ) {}

  generateState(redirectUri?: string): string {
    const state = uuidv4();
    const stateData = {
      redirectUri,
      timestamp: Date.now(),
    };
    
    // Store state in cache for 10 minutes
    this.cacheService.set(`oauth:state:${state}`, JSON.stringify(stateData), 600);
    
    return state;
  }

  getEtsyAuthorizationUrl(state: string): string {
    const clientId = this.configService.get('ETSY_CLIENT_ID');
    const redirectUri = this.configService.get('ETSY_REDIRECT_URI');
    const scopes = this.configService.get('ETSY_SCOPES') || 'email_r shops_r';

    const params = new URLSearchParams({
      response_type: 'code',
      client_id: clientId,
      redirect_uri: redirectUri,
      scope: scopes,
      state: state,
    });

    return `https://www.etsy.com/oauth/connect?${params.toString()}`;
  }

  async handleEtsyCallback(code: string, state: string) {
    // Validate state
    const stateData = await this.cacheService.get(`oauth:state:${state}`);
    if (!stateData) {
      throw new BadRequestException('Invalid or expired state');
    }

    // Exchange code for tokens
    const tokenData = await this.etsyOAuthService.exchangeCodeForTokens(code);

    // Get user info from Etsy
    const etsyUser = await this.etsyOAuthService.getUserInfo(tokenData.access_token);

    // Create or update user
    let user = await this.usersService.findByEtsyUserId(etsyUser.user_id);
    
    if (!user) {
      // Create new user
      user = await this.usersService.create({
        email: etsyUser.primary_email,
        emailVerified: true,
        etsyUserId: etsyUser.user_id,
        etsyShopId: etsyUser.shop_id,
        metadata: {
          etsyUsername: etsyUser.login_name,
          shopName: etsyUser.shop_name,
        },
      });
    } else {
      // Update existing user
      await this.usersService.update(user.id, {
        etsyShopId: etsyUser.shop_id,
        metadata: {
          ...user.metadata,
          etsyUsername: etsyUser.login_name,
          shopName: etsyUser.shop_name,
        },
      });
    }

    // Store OAuth tokens
    await this.saveOAuthToken(user.id, tokenData, etsyUser);

    // Clean up state
    await this.cacheService.del(`oauth:state:${state}`);

    // Generate auth tokens
    const authService = await import('../auth/auth.service');
    const tokens = await authService.AuthService.prototype.generateTokens.call(
      { jwtService: this.configService, configService: this.configService },
      user,
    );

    return {
      user,
      tokens,
    };
  }

  async saveOAuthToken(userId: string, tokenData: any, etsyUser: any) {
    const existingToken = await this.oauthTokenRepository.findOne({
      where: { userId, provider: OAuthProvider.ETSY },
    });

    const tokenEntity = existingToken || new OAuthToken();
    
    tokenEntity.userId = userId;
    tokenEntity.provider = OAuthProvider.ETSY;
    tokenEntity.accessToken = tokenData.access_token;
    tokenEntity.refreshToken = tokenData.refresh_token;
    tokenEntity.expiresAt = new Date(Date.now() + tokenData.expires_in * 1000);
    tokenEntity.scopes = tokenData.scope.split(' ');
    tokenEntity.providerUserId = etsyUser.user_id;
    tokenEntity.providerData = {
      shopId: etsyUser.shop_id,
      shopName: etsyUser.shop_name,
      username: etsyUser.login_name,
    };

    await this.oauthTokenRepository.save(tokenEntity);
  }

  async refreshEtsyToken(userId: string) {
    const token = await this.oauthTokenRepository.findOne({
      where: { userId, provider: OAuthProvider.ETSY },
    });

    if (!token || !token.refreshToken) {
      throw new BadRequestException('No Etsy connection found');
    }

    // Check if token needs refresh (refresh 5 minutes before expiry)
    const now = new Date();
    const expiryBuffer = new Date(token.expiresAt.getTime() - 5 * 60 * 1000);
    
    if (now < expiryBuffer) {
      return; // Token still valid
    }

    const newTokenData = await this.etsyOAuthService.refreshAccessToken(token.refreshToken);

    // Update stored token
    token.accessToken = newTokenData.access_token;
    token.expiresAt = new Date(Date.now() + newTokenData.expires_in * 1000);
    
    if (newTokenData.refresh_token) {
      token.refreshToken = newTokenData.refresh_token;
    }

    await this.oauthTokenRepository.save(token);
  }

  async disconnectEtsy(userId: string) {
    await this.oauthTokenRepository.delete({
      userId,
      provider: OAuthProvider.ETSY,
    });

    // Update user
    await this.usersService.update(userId, {
      etsyUserId: null,
      etsyShopId: null,
    });
  }

  async getEtsyToken(userId: string): Promise<string> {
    const token = await this.oauthTokenRepository.findOne({
      where: { userId, provider: OAuthProvider.ETSY },
    });

    if (!token) {
      throw new BadRequestException('No Etsy connection found');
    }

    // Auto-refresh if needed
    await this.refreshEtsyToken(userId);

    return token.accessToken;
  }
}