import {
  Controller,
  Post,
  Get,
  Body,
  UseGuards,
  Request,
  Delete,
  Param,
} from '@nestjs/common';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { MfaService } from './mfa.service';
import { EnableMfaDto } from './dto/enable-mfa.dto';
import { VerifyMfaDto } from './dto/verify-mfa.dto';
import { DisableMfaDto } from './dto/disable-mfa.dto';

@Controller('auth/mfa')
export class MfaController {
  constructor(private readonly mfaService: MfaService) {}

  @UseGuards(JwtAuthGuard)
  @Post('enable')
  async enableMfa(@Body() enableMfaDto: EnableMfaDto, @Request() req) {
    return this.mfaService.enableMfa(req.user.id, enableMfaDto.type);
  }

  @UseGuards(JwtAuthGuard)
  @Post('verify-setup')
  async verifySetup(@Body() verifyMfaDto: VerifyMfaDto, @Request() req) {
    return this.mfaService.verifySetup(
      req.user.id,
      verifyMfaDto.code,
      verifyMfaDto.type,
    );
  }

  @UseGuards(JwtAuthGuard)
  @Post('disable')
  async disableMfa(@Body() disableMfaDto: DisableMfaDto, @Request() req) {
    return this.mfaService.disableMfa(req.user.id, disableMfaDto.password);
  }

  @UseGuards(JwtAuthGuard)
  @Get('backup-codes')
  async getBackupCodes(@Request() req) {
    return this.mfaService.getBackupCodes(req.user.id);
  }

  @UseGuards(JwtAuthGuard)
  @Post('backup-codes/regenerate')
  async regenerateBackupCodes(@Request() req) {
    return this.mfaService.regenerateBackupCodes(req.user.id);
  }

  @UseGuards(JwtAuthGuard)
  @Post('send-code')
  async sendCode(@Body() body: { type: string }, @Request() req) {
    return this.mfaService.sendMfaCode(req.user.id, body.type);
  }
}