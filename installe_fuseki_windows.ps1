# Script pour installer Apache Fuseki sur Windows
# Version: 5.6.0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALLATION APACHE FUSEKI 5.6.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$fusekiPath = "C:\fuseki"
$version = "5.6.0"
$downloadUrl = "https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-$version.zip"
$fusekiDir = "apache-jena-fuseki-$version"

# Creer le repertoire
Write-Host "1. Creation du repertoire C:\fuseki..." -ForegroundColor Cyan
if (-not (Test-Path $fusekiPath)) {
    New-Item -ItemType Directory -Path $fusekiPath -Force | Out-Null
    Write-Host "   OK" -ForegroundColor Green
} else {
    Write-Host "   Deja existe" -ForegroundColor Yellow
}

# Verifier si deja installe
if (Test-Path "$fusekiPath\$fusekiDir") {
    Write-Host ""
    Write-Host "Fuseki semble deja installe dans $fusekiPath\$fusekiDir" -ForegroundColor Green
    Write-Host ""
    
    $start = Read-Host "Voulez-vous demarrer Fuseki maintenant ? (O/N)"
    if ($start -eq "O" -or $start -eq "o" -or $start -eq "y") {
        Write-Host ""
        Write-Host "Demarrage de Fuseki..." -ForegroundColor Green
        cd "$fusekiPath\$fusekiDir"
        Write-Host ""
        Write-Host "Fuseki sera accessible sur: http://localhost:3030" -ForegroundColor Cyan
        Write-Host "Appuyez sur CTRL+C pour arreter" -ForegroundColor Yellow
        Write-Host ""
        .\fuseki-server
        exit
    }
    exit
}

# Telecharger
Write-Host ""
Write-Host "2. Telechargement de Fuseki 5.6.0..." -ForegroundColor Cyan
Write-Host "   URL: $downloadUrl" -ForegroundColor Gray
$zipFile = "$fusekiPath\fuseki.zip"

try {
    Write-Host "   Telechargement en cours (cela peut prendre quelques minutes)..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "   OK" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "ERREUR de telechargement" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Telechargez manuellement depuis:" -ForegroundColor Yellow
    Write-Host "https://jena.apache.org/download/" -ForegroundColor White
    Write-Host ""
    Write-Host "Puis extrayez-le dans C:\fuseki\" -ForegroundColor White
    exit
}

# Extraire
Write-Host ""
Write-Host "3. Extraction de l'archive..." -ForegroundColor Cyan
try {
    Expand-Archive -Path $zipFile -DestinationPath $fusekiPath -Force
    Write-Host "   OK" -ForegroundColor Green
} catch {
    Write-Host "   ERREUR: $_" -ForegroundColor Red
    exit
}

# Supprimer le zip
Remove-Item $zipFile -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "INSTALLATION TERMINEE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour demarrer Fuseki:" -ForegroundColor Cyan
Write-Host "  cd $fusekiPath\$fusekiDir" -ForegroundColor White
Write-Host "  .\fuseki-server" -ForegroundColor White
Write-Host ""
Write-Host "Fuseki sera accessible sur: http://localhost:3030" -ForegroundColor Yellow
Write-Host ""

# Proposer de demarrer
$start = Read-Host "Voulez-vous demarrer Fuseki maintenant ? (O/N)"
if ($start -eq "O" -or $start -eq "o" -or $start -eq "y") {
    Write-Host ""
    Write-Host "Demarrage de Fuseki..." -ForegroundColor Green
    cd "$fusekiPath\$fusekiDir"
    Write-Host ""
    Write-Host "Fuseki est accessible sur: http://localhost:3030" -ForegroundColor Cyan
    Write-Host "Appuyez sur CTRL+C pour arreter" -ForegroundColor Yellow
    Write-Host ""
    .\fuseki-server
}

