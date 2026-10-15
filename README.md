# Dynamic_Systems_Project
Repositorio dedicado para la integración de proyectos relacionados con los sistemas dinámicos con el profesor Eduin Salgado para el periodo 2026-2.

El proyecto "Lineal_Dynamics_System" contiene 2 codigos main.py, cada uno usa un método distinto de integración del sistema dinamico lineal:
- main_rk4.py : usa el método de Runge-Kutta de orden 4 para sistemas dinámicos lineales y no lineales con 99% de aproximación.
- main_exp.py : usa el método de Matriz Exponencial / Jacobiano, únicamente para sistemas dinámicos lineales con 100% de exactitud.

Para poder compilar de manera correcta el proyecto y sin problemas se recomienda lo siguiente:
1) Crear un entorno virtual dentro de la carpeta del proyecto e iniciarlo, luego instalar las librerías especificadas en el archivo "requirements.txt". En tu terminal de VSCode:

```bash
  python -m venv .venv
  .venv\Scripts\activate           # En Linux/Mac: source .venv/bin/activate
  pip install -r requirements.txt
```

3) Instalar el software del graficador "Gnuplot" en tu computador. Link directo: https://sourceforge.net/projects/gnuplot/
4) Cuando estés en el Asistente de Instalación de Gnuplot, seleccionar la opción de "Agregar la ruta de instalación a la variable de entorno PATH".
5) En caso de cambiar la ruta de instalación por defecto de los archivos "bin", se debe actualizar dicha ruta en "main.py" del proyecto.

Con estos pasos, podrás utilizar el programa sin problemas.
