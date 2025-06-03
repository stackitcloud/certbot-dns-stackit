#  Certbot with Stackit DNS Plugin (Docker Compose)

- Custom Docker image: Based on certbot/certbot, with the Stackit DNS plugin installed.
- Docker Compose service to request wildcard certificates.

---
## 📂 Certificate File Structure

```
./letsencrypt/live/<your-domain>/
├── cert.pem            # Your domain’s certificate
├── chain.pem           # The Let's Encrypt chain
├── fullchain.pem       # cert.pem + chain.pem (what you usually use)
├── privkey.pem         # Your private key
```


## 🛠️ Setup Instructions


### 1. Create a file named `stackit.ini` in the root directory:

⚠️️️ Make sure the file is secure: (`chmod 600 stackit.ini`)
```
dns_stackit_auth_token = YOUR_API_TOKEN
dns_stackit_project_id = YOUR_PROJECT_ID
```

### 2. Set domain in `.env` file
```
DOMAIN=example.com
WILDCARD=*.example.com
```

### 3. Run Certbot
```
docker compose up certbot
```

### 4. Cert permission

The certs and the live folder will be `root:root`, in order to access them with your user
```bash
sudo chown -R $(id -u):$(id -g) ./letsencrypt
```