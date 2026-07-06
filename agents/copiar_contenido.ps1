# Script para leer todos los archivos en la ruta actual y copiar su contenido a un .txt

# Obtener la ruta actual
$rutaActual = Get-Location

# Definir nombre del archivo de salida con fecha y hora
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
$archivoSalida = "contenido_completo_$fecha.txt"

# Obtener todos los archivos en la ruta actual (excluyendo el archivo de salida)
$archivos = Get-ChildItem -File | Where-Object { $_.Name -ne $archivoSalida }

# Verificar si hay archivos para procesar
if ($archivos.Count -eq 0) {
    Write-Host "No hay archivos en la ruta actual para procesar." -ForegroundColor Yellow
    exit
}

Write-Host "Procesando archivos en: $rutaActual" -ForegroundColor Cyan
Write-Host "Archivos encontrados: $($archivos.Count)" -ForegroundColor Green

# Crear el archivo de salida
$contenidoTotal = @()

# Agregar encabezado
$contenidoTotal += "========================================="
$contenidoTotal += "CONTENIDO DE TODOS LOS ARCHIVOS"
$contenidoTotal += "Ruta: $rutaActual"
$contenidoTotal += "Fecha: $(Get-Date)"
$contenidoTotal += "Total de archivos: $($archivos.Count)"
$contenidoTotal += "========================================="
$contenidoTotal += ""

# Procesar cada archivo
foreach ($archivo in $archivos) {
    Write-Host "Leyendo archivo: $($archivo.Name)" -ForegroundColor Gray
    
    # Agregar separador y nombre del archivo
    $contenidoTotal += "-----------------------------------------"
    $contenidoTotal += "ARCHIVO: $($archivo.Name)"
    $contenidoTotal += "Tamaño: $([math]::Round($archivo.Length/1KB, 2)) KB"
    $contenidoTotal += "Última modificación: $($archivo.LastWriteTime)"
    $contenidoTotal += "-----------------------------------------"
    
    # Intentar leer el contenido del archivo
    try {
        $contenido = Get-Content -Path $archivo.FullName -Raw -ErrorAction Stop
        $contenidoTotal += $contenido
    } catch {
        $contenidoTotal += "[ERROR] No se pudo leer el archivo: $($_.Exception.Message)"
        Write-Host "Error al leer archivo $($archivo.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
    
    $contenidoTotal += ""  # Línea en blanco entre archivos
}

# Agregar pie de página
$contenidoTotal += "========================================="
$contenidoTotal += "FIN DEL CONTENIDO"
$contenidoTotal += "========================================="

# Guardar todo en el archivo de salida
try {
    $contenidoTotal | Out-File -FilePath $archivoSalida -Encoding UTF8
    Write-Host "`nContenido guardado exitosamente en: $archivoSalida" -ForegroundColor Green
    Write-Host "Tamaño del archivo de salida: $([math]::Round((Get-Item $archivoSalida).Length/1KB, 2)) KB" -ForegroundColor Green
} catch {
    Write-Host "Error al guardar el archivo: $($_.Exception.Message)" -ForegroundColor Red
}

# Mostrar estadísticas
Write-Host "`nResumen:" -ForegroundColor Cyan
Write-Host "  - Archivos procesados: $($archivos.Count)" -ForegroundColor White
Write-Host "  - Archivo de salida: $archivoSalida" -ForegroundColor White