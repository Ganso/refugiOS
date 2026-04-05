#!/bin/bash
# Re-detección local por si corres el USB en un ordenador del futuro con muchísima potencia extra.
IA_DIR="$HOME/refugiOS/IA"
RAM_MB=$(free -m | awk '/^Mem:/{print $2}')

TIENE_AVANZADO=0; TIENE_MEDIO=0; TIENE_BASICO=0; TIENE_MINIMO=0
[ -f "$IA_DIR/modelo-avanzado.gguf" ] && TIENE_AVANZADO=1
[ -f "$IA_DIR/modelo-medio.gguf" ]    && TIENE_MEDIO=1
[ -f "$IA_DIR/modelo-basico.gguf" ]   && TIENE_BASICO=1
[ -f "$IA_DIR/modelo-minimo.gguf" ]   && TIENE_MINIMO=1

if [ "$RAM_MB" -lt 1024 ] && [ "$TIENE_MINIMO" -eq 1 ]; then
    MODELO="modelo-minimo.gguf"
elif [ "$RAM_MB" -ge 14000 ] && [ "$TIENE_AVANZADO" -eq 1 ]; then
    MODELO="modelo-avanzado.gguf"
elif [ "$RAM_MB" -ge 7000 ] && [ "$TIENE_MEDIO" -eq 1 ]; then
    MODELO="modelo-medio.gguf"
elif [ "$TIENE_BASICO" -eq 1 ]; then
    MODELO="modelo-basico.gguf"
else
    MODELO="modelo-minimo.gguf"
fi

cd "$IA_DIR"
# Generar un servidor de bucle interno sobre el puerto 8080 del navegador (localhost) interactuando con Llamafile
./llamafile -m "$MODELO" --ctx-size 4096 --server &
LLAMA_PID=$!
sleep 5
epiphany-browser http://localhost:8080 2>/dev/null || xdg-open http://localhost:8080 2>/dev/null
echo "Aviso de Servidor: Procediendo a purgar la tarea. Cierra por favor esta ventana negra final para erradicar el consumo del proceso IA de tu ordenador."
wait $LLAMA_PID
