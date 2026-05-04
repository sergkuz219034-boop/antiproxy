import subprocess
import os
from app.services.logger import logger

class AntigravityLauncher:
    def __init__(self):
        self.exe_path = r"C:\Users\sergk\AppData\Local\Programs\Antigravity\Antigravity.exe"
        self.user_data_base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "AntiProxy", "AntigravityProfiles")
        
        if not os.path.exists(self.user_data_base):
            os.makedirs(self.user_data_base, exist_ok=True)

    def launch(self, profile_name, proxy=None):
        logger.info(f"Launching Antigravity.exe for profile: {profile_name}")
        
        profile_dir = os.path.join(self.user_data_base, profile_name)
        os.makedirs(profile_dir, exist_ok=True)
        
        args = [
            self.exe_path,
            f"--user-data-dir={profile_dir}",
            "--remote-debugging-port=9223", # Use a different port than AdsPower
            "--no-sandbox"
        ]
        
        if proxy:
            # Format: protocol://host:port or protocol://user:pass@host:port
            if proxy.username and proxy.password:
                proxy_str = f"{proxy.protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
            else:
                proxy_str = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
            
            args.append(f"--proxy-server={proxy_str}")
            logger.info(f"Using proxy: {proxy.host}:{proxy.port}")

        try:
            # Start process detached
            subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS if os.name == 'nt' else 0)
            logger.info(f"Antigravity.exe started for {profile_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch Antigravity.exe: {str(e)}")
            return False

antigravity_launcher = AntigravityLauncher()
