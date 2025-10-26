# Script PowerShell pour installer et démarrer Apache Fuseki
# Fichier: installe_fuseki.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALLATION APACHE FUSEKI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Fuseki est déjà installé
$fusekiPath = "C:\fuseki"
$version = "4.10.0"
$downloadUrl = "https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-$version.zip"

if (Test-Path "$fusekiPath\apache-jena-fuseki-$version") {
    Write-Host "✅ Fuseki semble déjà installé dans C:\fuseki" -ForegroundColor Green
    Write-Host ""
    Write-Host "Pour démarrer Fuseki, exécutez:" -ForegroundColor Yellow
    Write-Host "  cd C:\fuseki\apache-jena-fuseki-$version" -ForegroundColor White
    Write-Host "  .\fuseki-server" -ForegroundColor White
    Write-Host ""
    
    # Proposer de démarrer
    $start = Read-Host "Voulez-vous démarrer Fuseki maintenant ? (O/N)"
    if ($start -eq "O" -or $start -eq "o") {
        Write-Host ""
        Write-Host "🚀 Démarrage de Fuseki..." -ForegroundColor Green
        cd "$fusekiPath\apache-jena-fuseki-$version"
    Write-Host ""
    Write-Host "Fuseki sera accessible sur: http://localhost:3030" -ForegroundColor Cyan
    Write-Host "Appuyez sur CTRL+C pour arreter" -ForegroundColor Yellow
        Write-Host ""
        .\fuseki-server
        exit
    }
    exit
}

Write-Host "📦 Fuseki n'est pas installé." -ForegroundColor Yellow
Write-Host ""

# Créer le répertoire
Write-Host "1️⃣  Création du répertoire C:\fuseki..." -ForegroundColor Cyan
if (-not (Test-Path $fusekiPath)) {
    New-Item -ItemType Directory -Path $fusekiPath -Force | Out-Null
    Write-Host "✅ Répertoire créé" -ForegroundColor Green
} else {
    Write-Host "✅ Répertoire existe déjà" -ForegroundColor Green
}

# Télécharger
Write-Host ""
Write-Host "2️⃣  Téléchargement de Fuseki..." -ForegroundColor Cyan
Write-Host "   URL: $downloadUrl" -ForegroundColor Gray
$zipFile = "$fusekiPath\fuseki.zip"

try {
    # Télécharger
    Write-Host "   Téléchargement en cours..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "✅ Téléchargement terminé" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur de téléchargement: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Téléchargez manuellement depuis:" -ForegroundColor Yellow
    Write-Host "https://jena.apache.org/download/" -ForegroundColor White
    exit
}

# Extraire
Write-Host ""
Write-Host "3️⃣  Extraction de l'archive..." -ForegroundColor Cyan
try {
    Expand-Archive -Path $zipFile -DestinationPath $fusekiPath -Force
    Write-Host "✅ Extraction terminée" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur d'extraction: $_" -ForegroundColor Red
    exit
}

# Configurer
Write-Host ""
Write-Host "4️⃣  Configuration de Fuseki..." -ForegroundColor Cyan
$configDir = "$fusekiPath\apache-jena-fuseki-$version\run\configuration"
$dbDir = "$fusekiPath\apache-jena-fuseki-$version\run\databases\transport"

# Créer les répertoires
New-Item -ItemType Directory -Path $configDir -Force | Out-Null
New-Item -ItemType Directory -Path $dbDir -Force | Out-Null
Write-Host "✅ Répertoires créés" -ForegroundColor Green

# Créer le fichier de configuration
$configContent = @"
@prefix fuseki:  <http://jena.apache.org/fuseki#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ja:      <http://jena.hpl.hp.com/2005/11/Assembler#> .

<#transport_dataset> rdf:type fuseki:DataService ;
    fuseki:name                        "transport" ;
    fuseki:serviceQuery                "sparql" ;
    fuseki:serviceQueryGraphStore      "data" ;
    fuseki:serviceReadWriteGraphStore  "upload" ;
    fuseki:serviceUpdate               "update" ;
    fuseki:dataset                     <#dataset> ;
    .

<#dataset> rdf:type ja:DatasetTxnMem ;
    ja:defaultGraph <#graph> ;
    .

<#graph> rdf:type ja:MemoryModel .
"@

$configFile = "$configDir\transport.ttl"
Set-Content -Path $configFile -Value $configContent
Write-Host "✅ Fichier de configuration créé" -ForegroundColor Green

# Supprimer le fichier zip
Remove-Item $zipFile -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ INSTALLATION TERMINÉE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour démarrer Fuseki:" -ForegroundColor Cyan
Write-Host "  cd C:\fuseki\apache-jena-fuseki-$version" -ForegroundColor White
Write-Host "  .\fuseki-server --conf=run\configuration\transport.ttl" -ForegroundColor White
Write-Host ""
Write-Host "Ou simplement:" -ForegroundColor Cyan
Write-Host "  .\fuseki-server" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Fuseki sera accessible sur: http://localhost:3030" -ForegroundColor Yellow
Write-Host ""

# Proposer de démarrer
$start = Read-Host "Voulez-vous démarrer Fuseki maintenant ? (O/N)"
if ($start -eq "O" -or $start -eq "o") {
    Write-Host ""
    Write-Host "🚀 Démarrage de Fuseki..." -ForegroundColor Green
    cd "$fusekiPath\apache-jena-fuseki-$version"
    Write-Host ""
    Write-Host "Fuseki sera accessible sur: http://localhost:3030" -ForegroundColor Cyan
    Write-Host "Appuyez sur CTRL+C pour arreter" -ForegroundColor Yellow
    Write-Host ""
    .\fuseki-server --conf=run\configuration\transport.ttl
}

