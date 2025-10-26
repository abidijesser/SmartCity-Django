# Script pour créer le dataset "transport" dans Fuseki

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CREATION DU DATASET TRANSPORT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# URL de l'API Fuseki
$fusekiUrl = "http://localhost:3030"

try {
    # Vérifier que Fuseki est accessible
    Write-Host "1. Vérification de l'accès à Fuseki..." -ForegroundColor Cyan
    $response = Invoke-WebRequest -Uri "$fusekiUrl" -Method GET -ErrorAction Stop
    Write-Host "   ✓ Fuseki est accessible" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Fuseki n'est pas accessible. Démarrez-le d'abord!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pour démarrer Fuseki:" -ForegroundColor Yellow
    Write-Host "  cd C:\fuseki\apache-jena-fuseki-5.6.0" -ForegroundColor White
    Write-Host "  .\fuseki-server" -ForegroundColor White
    exit
}

# Créer le dataset via l'interface web (instructions)
Write-Host ""
Write-Host "2. Pour créer le dataset 'transport':" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Ouvrez votre navigateur:" -ForegroundColor White
Write-Host "      $fusekiUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "   2. Cliquez sur 'Add dataset' ou 'manage datasets'" -ForegroundColor White
Write-Host ""
Write-Host "   3. Nom du dataset:" -ForegroundColor White
Write-Host "      transport" -ForegroundColor Yellow
Write-Host ""
Write-Host "   4. Cliquez sur 'Create' ou 'Add'" -ForegroundColor White
Write-Host ""
Write-Host "   5. Le dataset 'transport' sera créé!" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ENSUITE:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Sélectionnez le dataset 'transport'" -ForegroundColor White
Write-Host "2. Allez dans l'onglet 'Upload'" -ForegroundColor White
Write-Host "3. Uploadez le fichier 'donnees_test.rdf'" -ForegroundColor White
Write-Host ""
Write-Host "OU suivez le guide: CHARGER_DONNEES_FUSEKI.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "Votre application Django affichera ensuite les données RDF!" -ForegroundColor Green
Write-Host ""

