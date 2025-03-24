```python
# Desactivar la detección de Host con nmap
# Comando: nmap -Pn <dirección_ip>
# Ejemplo:
import os

ip_address = "10.10.10.5" # Reemplazar con la IP objetivo
os.system(f"nmap -Pn {ip_address}")

# Escaneo TCP Connect con nmap y desactivando la detección de Host
# Comando: nmap -sT -Pn <dirección_ip>
# Ejemplo:
import os

ip_address = "10.10.10.5" # Reemplazar con la IP objetivo
os.system(f"nmap -sT -Pn {ip_address}")

# Escaneo de puertos con nmap especificando el tiempo y desactivando la detección de Host
# Comando: nmap -T5 -Pn <dirección_ip>
# Ejemplo:
import os

ip_address = "10.10.10.5" # Reemplazar con la IP objetivo
os.system(f"nmap -T5 -Pn {ip_address}")

# Mostrar solo los puertos abiertos con nmap
# Comando: nmap --open <dirección_ip>
# Ejemplo:
import os

ip_address = "10.10.10.5" # Reemplazar con la IP objetivo
os.system(f"nmap --open {ip_address}")

# Escanear todos los puertos (65535) con nmap
# Comando: nmap -p- <dirección_ip>
# Ejemplo:
import os

ip_address = "10.10.10.5" # Reemplazar con la IP objetivo
os.system(f"nmap -p- {ip_address}")

# Escanear puertos específicos con nmap
# Comando: nmap -p <puerto1>,<puerto2>,... <dirección_ip>
# Ejemplo:
import os

ip_address = "10.10.10.5" # Reemplazar con la IP objetivo
ports = "21,22,23,80,443"
os.system(f"nmap -p {ports} {ip_address}")
```
