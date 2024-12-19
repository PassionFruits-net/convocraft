import yaml
import streamlit_authenticator as stauth

# Load the existing config.yaml
config_file_path = "../../config.yaml"  # Update with the actual path to your config.yaml file

# Function to hash passwords
def hash_passwords(config_path):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    
    # Iterate over the usernames and hash passwords
    for username, details in config["credentials"]["usernames"].items():
        plain_password = details.get("password")
        if plain_password:
            # Use stauth.Hasher.hash() to hash the password
            hashed_password = stauth.Hasher.hash(plain_password)
            details["password"] = hashed_password  # Replace the plain-text password
    
    # Save the updated config back to the file
    with open(config_path, "w") as file:
        yaml.dump(config, file)
    
    print(f"Passwords in {config_path} have been hashed successfully.")

# Run the hashing function
hash_passwords(config_file_path)
