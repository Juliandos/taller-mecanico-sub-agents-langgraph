CARPETA DE DOCUMENTOS TÉCNICOS - TALLER MECÁNICO
=================================================

Agrega aquí tus archivos .txt con manuales, procedimientos o conocimiento técnico.

Formato recomendado por archivo:
- Un tema por archivo
- Nombre descriptivo: vibración_motor.txt, frenos_pastillas.txt, etc.

El script scripts/load_docs.py leerá TODOS los .txt de esta carpeta
y los cargará en la base vectorial pgvector.

Para recargar después de agregar nuevos documentos:
    uv run python scripts/load_docs.py