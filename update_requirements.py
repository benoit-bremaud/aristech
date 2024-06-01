import os
import subprocess
import sys

def run_command(command):
    """Exécute une commande shell et affiche la sortie."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Erreur lors de l'exécution de la commande : {command}")
        print(f"Sortie standard : {stdout.decode('utf-8')}")
        print(f"Erreur standard : {stderr.decode('utf-8')}")
        raise subprocess.CalledProcessError(process.returncode, command)
    else:
        print(stdout.decode('utf-8'))

def check_and_install(package):
    """Vérifie si un package est installé, sinon l'installe."""
    try:
        __import__(package)
    except ImportError:
        print(f"Installation de {package}...")
        run_command(f"{sys.executable} -m pip install {package}")

def generate_requirements_with_pipreqs():
    """Génère requirements.txt avec pipreqs."""
    print("Génération de requirements.txt avec pipreqs...")
    run_command("pipreqs . --force")

def convert_requirements_txt_to_in():
    """Convertit requirements.txt en requirements.in."""
    print("Conversion de requirements.txt en requirements.in...")
    if os.path.exists("requirements.txt"):
        os.rename("requirements.txt", "requirements.in")
    else:
        print("Le fichier requirements.txt n'existe pas.")

def compile_requirements():
    """Génère requirements.txt à partir de requirements.in."""
    print("Génération de requirements.txt à partir de requirements.in...")
    run_command("pip-compile --strip-extras requirements.in")

def sync_requirements():
    """Synchronise les dépendances avec requirements.txt."""
    print("Synchronisation des dépendances avec requirements.txt...")
    run_command("pip-sync requirements.txt")

def main():
    check_and_install("pipreqs")
    check_and_install("piptools")
    generate_requirements_with_pipreqs()
    convert_requirements_txt_to_in()
    compile_requirements()
    sync_requirements()
    print("Toutes les étapes sont terminées avec succès !")

if __name__ == "__main__":
    main()
