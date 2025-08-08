const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');

class User {
    constructor(data) {
        this.id = data.id || uuidv4();
        this.email = data.email;
        this.passwordHash = data.passwordHash;
        this.emailVerified = data.emailVerified || false;
        this.mfaEnabled = data.mfaEnabled || false;
        this.mfaSecret = data.mfaSecret || null;
        this.createdAt = data.createdAt || new Date();
        this.updatedAt = data.updatedAt || new Date();
    }
    
    static async create(email, password) {
        const passwordHash = await bcrypt.hash(password, 10);
        return new User({
            email,
            passwordHash
        });
    }
    
    async verifyPassword(password) {
        return bcrypt.compare(password, this.passwordHash);
    }
    
    toJSON() {
        const { passwordHash, mfaSecret, ...publicData } = this;
        return publicData;
    }
}

module.exports = User;
