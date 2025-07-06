import secrets

def generate_key():
    secret = secrets.token_hex(32) # Generates a 64-character (256-bit) hex token
    print(secret)
    
if __name__ == "__main__":
    generate_key()