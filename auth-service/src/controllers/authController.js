const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { validateRegistration, validateLogin } = require('../validators/auth');
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');

class AuthController {
    async register(req, res, next) {
        try {
            const { error } = validateRegistration(req.body);
            if (error) {
                return res.status(400).json({ error: error.details[0].message });
            }
            
            const { email, password } = req.body;
            
            // Check if user exists
            // In real app, this would check database
            // For demo, we'll simulate
            
            const user = await User.create(email, password);
            
            res.status(201).json({
                message: 'User registered successfully',
                user: user.toJSON()
            });
        } catch (error) {
            next(error);
        }
    }
    
    async login(req, res, next) {
        try {
            const { error } = validateLogin(req.body);
            if (error) {
                return res.status(400).json({ error: error.details[0].message });
            }
            
            const { email, password } = req.body;
            
            // In real app, fetch user from database
            // For demo, we'll create a mock user
            const user = await User.create(email, password);
            
            const isValid = await user.verifyPassword(password);
            if (!isValid) {
                return res.status(401).json({ error: 'Invalid credentials' });
            }
            
            const token = jwt.sign(
                { userId: user.id, email: user.email },
                process.env.JWT_SECRET || 'secret',
                { expiresIn: '24h' }
            );
            
            res.json({
                message: 'Login successful',
                token,
                user: user.toJSON()
            });
        } catch (error) {
            next(error);
        }
    }
    
    async setupMFA(req, res, next) {
        try {
            const secret = speakeasy.generateSecret({
                name: `AuthService (${req.user.email})`
            });
            
            const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);
            
            res.json({
                secret: secret.base32,
                qrCode: qrCodeUrl
            });
        } catch (error) {
            next(error);
        }
    }
    
    async verifyMFA(req, res, next) {
        try {
            const { token, secret } = req.body;
            
            const verified = speakeasy.totp.verify({
                secret,
                encoding: 'base32',
                token,
                window: 2
            });
            
            res.json({ verified });
        } catch (error) {
            next(error);
        }
    }
    
    async forgotPassword(req, res, next) {
        try {
            const { email } = req.body;
            
            // Generate reset token
            const resetToken = jwt.sign(
                { email, type: 'password-reset' },
                process.env.JWT_SECRET || 'secret',
                { expiresIn: '1h' }
            );
            
            // In real app, send email with reset link
            // For demo, return token
            res.json({
                message: 'Password reset email sent',
                resetToken // In production, don't return this
            });
        } catch (error) {
            next(error);
        }
    }
    
    async resetPassword(req, res, next) {
        try {
            const { token, newPassword } = req.body;
            
            // Verify reset token
            const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secret');
            
            if (decoded.type !== 'password-reset') {
                return res.status(400).json({ error: 'Invalid reset token' });
            }
            
            // In real app, update user password in database
            res.json({
                message: 'Password reset successful'
            });
        } catch (error) {
            if (error.name === 'JsonWebTokenError') {
                return res.status(400).json({ error: 'Invalid or expired token' });
            }
            next(error);
        }
    }
}

module.exports = new AuthController();
