# Guía de usuario — AuraAgenda 2.0.4

Al iniciar por primera vez, el asistente permite elegir idioma, nombre, país, zona horaria, moneda, formato de fecha, módulos opcionales, objetivo de agua, tema y PIN local opcional. Ningún dato de salud es obligatorio.

La barra lateral agrupa Organización, Personal, Bienestar, Estilo, Vida y Sistema. Los módulos opcionales pueden ocultarse desde Configuración. La búsqueda superior localiza eventos, tareas, diario, personas, metas, listas, biblioteca, multimedia, productos y prendas.

El Dashboard resume eventos, tareas, agua, balance, hábitos, sueño, ánimo y cumpleaños. Los accesos rápidos crean registros en los módulos principales.

La Papelera restaura elementos eliminados o permite borrarlos definitivamente con confirmación. Backup crea archivos ZIP locales; Restaurar valida el ZIP y crea primero un backup de seguridad.

Los módulos de ciclo, salud, sueño y bienestar sirven para organización personal. No diagnostican ni sustituyen asesoramiento médico.

## Seguridad y recuperación del propietario — V2.0.4

En **Configuración → Privacidad** podés generar una clave maestra única para esa instalación. Guardala fuera de la PC. No existe una contraseña universal del desarrollador.

Para una recuperación rápida ante pérdida del programa o del equipo:

1. Generá la clave maestra.
2. Creá un **kit de recuperación cifrado** `.aurarecovery`.
3. Guardá kit y clave en lugares separados.
4. En una instalación nueva, ejecutá `RECUPERAR_AURAAGENDA.bat`.
5. Elegí el kit e ingresá la clave maestra.

La restricción por IP/red es opcional. AuraAgenda sólo usa IPv4 local/CIDR y no consulta tu IP pública. Una IP no reemplaza al PIN ni a la clave maestra.
