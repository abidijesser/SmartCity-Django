# Script pour charger ontologie.rdf dans Fuseki

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CHARGEMENT ONTOLOGIE DANS FUSEKI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$fusekiUrl = "http://localhost:3030"
$ontologieFile = "ontologie.rdf"

# Verifier que le fichier existe
if (-not (Test-Path $ontologieFile)) {
    Write-Host "ERREUR: Le fichier ontologie.rdf n'existe pas!" -ForegroundColor Red
    Write-Host "Placez votre fichier ontologie.rdf dans le dossier du projet." -ForegroundColor Yellow
    exit
}

Write-Host "Fichier trouve: $ontologieFile" -ForegroundColor Green
Write-Host ""

# Instructions
Write-Host "PROCHAINES ETAPES:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Ouvrez votre navigateur:" -ForegroundColor White
Write-Host "   $fusekiUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Creez un dataset nomme 'transport':" -ForegroundColor White
Write-Host "   - Cliquez sur 'Add dataset' ou 'manage datasets'" -ForegroundColor Gray
Write-Host "   - Dataset name: transport" -ForegroundColor Gray
Write-Host "   - Cliquez sur 'Create' ou 'Add'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Uploadez votre ontologie:" -ForegroundColor White
Write-Host "   - Selectionnez le dataset 'transport'" -ForegroundColor Gray
Write-Host "   - Allez dans l'onglet 'Upload' ou 'Data'" -ForegroundColor Gray
Write-Host "   - Choisissez le fichier: $ontologieFile" -ForegroundColor Gray
Write-Host "   - Cliquez sur 'Upload' ou 'Send'" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Verifiez les donnees:" -ForegroundColor White
Write-Host "   - Allez dans 'Query'" -ForegroundColor Gray
Write-Host "   - Executez: SELECT ?s ?p ?o WHERE { ?s ?p ?o . } LIMIT 10" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Votre application Django utilisera ces donnees!" -ForegroundColor Green
Write-Host ""

