const User = require('../src/models/User');

describe('User Model', () => {
    describe('create', () => {
        it('should create a user with hashed password', async () => {
            const user = await User.create('test@example.com', 'password123');
            
            expect(user.email).toBe('test@example.com');
            expect(user.passwordHash).toBeDefined();
            expect(user.passwordHash).not.toBe('password123');
            expect(user.id).toBeDefined();
        });
    });
    
    describe('verifyPassword', () => {
        it('should verify correct password', async () => {
            const user = await User.create('test@example.com', 'password123');
            const isValid = await user.verifyPassword('password123');
            
            expect(isValid).toBe(true);
        });
        
        it('should reject incorrect password', async () => {
            const user = await User.create('test@example.com', 'password123');
            const isValid = await user.verifyPassword('wrongpassword');
            
            expect(isValid).toBe(false);
        });
    });
    
    describe('toJSON', () => {
        it('should not expose sensitive data', async () => {
            const user = await User.create('test@example.com', 'password123');
            const json = user.toJSON();
            
            expect(json).not.toHaveProperty('passwordHash');
            expect(json).not.toHaveProperty('mfaSecret');
            expect(json).toHaveProperty('email');
            expect(json).toHaveProperty('id');
        });
    });
});
