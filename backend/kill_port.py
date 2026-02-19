"""
Script pour libérer le port 8000 si il est occupé
"""
import socket
import sys

def kill_port(port):
    """Trouve et tue le processus utilisant le port spécifié"""
    import subprocess
    import platform
    
    try:
        if platform.system() == "Windows":
            # Windows
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        print(f"Processus trouvé sur le port {port}: PID {pid}")
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
                            print(f"✅ Processus {pid} terminé")
                        except subprocess.CalledProcessError:
                            print(f"❌ Impossible de terminer le processus {pid}")
        else:
            # Linux/Mac
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                pid = result.stdout.strip()
                print(f"Processus trouvé sur le port {port}: PID {pid}")
                subprocess.run(['kill', '-9', pid])
                print(f"✅ Processus {pid} terminé")
            else:
                print(f"Aucun processus trouvé sur le port {port}")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    print(f"Recherche de processus sur le port {port}...")
    kill_port(port)
