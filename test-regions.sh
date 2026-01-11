#!/bin/bash

# ========================================
# Script de Test Automatique des Régions
# Trouve la première région qui fonctionne
# ========================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_header "🔍 Recherche de Région Disponible pour Azure for Students"

# Configuration
RESOURCE_GROUP="recruitment-rg-test"
DB_NAME="recruitment_db"
DB_ADMIN_USER="recruitment_admin"
DB_ADMIN_PASSWORD="salmasalma2025"

# Liste COMPLÈTE de régions à tester
REGIONS_TO_TEST=(
    "centralus"
    "eastus2"
    "westus2"
    "westus3"
    "southcentralus"
    "northcentralus"
    "canadacentral"
    "canadaeast"
    "brazilsouth"
    "uksouth"
    "ukwest"
    "francecentral"
    "francesouth"
    "germanywestcentral"
    "norwayeast"
    "switzerlandnorth"
    "swedencentral"
    "eastus"
    "westus"
    "northeurope"
    "westeurope"
    "southeastasia"
    "eastasia"
    "australiaeast"
    "australiasoutheast"
    "japaneast"
    "japanwest"
    "koreacentral"
    "koreasouth"
    "southafricanorth"
    "uaenorth"
    "centralindia"
    "southindia"
    "westindia"
)

WORKING_REGION=""

print_info "Nombre de régions à tester : ${#REGIONS_TO_TEST[@]}"
echo ""

for region in "${REGIONS_TO_TEST[@]}"; do
    print_info "Test de la région : $region"
    
    # Nettoyer le resource group s'il existe
    if az group exists --name $RESOURCE_GROUP | grep -q "true"; then
        az group delete --name $RESOURCE_GROUP --yes --no-wait 2>/dev/null || true
        sleep 5
    fi
    
    # Créer le resource group
    if az group create --name $RESOURCE_GROUP --location $region --output none 2>/dev/null; then
        print_info "Resource group créé dans $region"
        
        # Tester la création PostgreSQL
        TIMESTAMP=$(date +%s)
        TEST_DB_NAME="test-db-$TIMESTAMP"
        
        print_info "Tentative de création PostgreSQL..."
        
        if az postgres flexible-server create \
            --resource-group $RESOURCE_GROUP \
            --name $TEST_DB_NAME \
            --location $region \
            --admin-user $DB_ADMIN_USER \
            --admin-password $DB_ADMIN_PASSWORD \
            --sku-name Standard_B1ms \
            --tier Burstable \
            --version 14 \
            --storage-size 32 \
            --public-access 0.0.0.0 \
            --yes \
            --output none 2>/dev/null; then
            
            print_success "✅ SUCCÈS ! Région fonctionnelle trouvée : $region"
            WORKING_REGION=$region
            
            # Nettoyer
            az group delete --name $RESOURCE_GROUP --yes --no-wait 2>/dev/null || true
            break
        else
            print_error "Région $region bloquée"
            # Nettoyer
            az group delete --name $RESOURCE_GROUP --yes --no-wait 2>/dev/null || true
        fi
    else
        print_error "Impossible de créer resource group dans $region"
    fi
    
    echo ""
    sleep 2
done

echo ""
print_header "🎯 RÉSULTAT"
echo ""

if [ -n "$WORKING_REGION" ]; then
    print_success "Région fonctionnelle trouvée : $WORKING_REGION"
    echo ""
    print_info "Utilisez cette région pour déployer votre application :"
    echo ""
    echo "LOCATION=\"$WORKING_REGION\""
    echo ""
    print_info "Commandes pour déployer :"
    echo ""
    echo "RESOURCE_GROUP=\"recruitment-rg\""
    echo "LOCATION=\"$WORKING_REGION\""
    echo ""
    echo "az group create --name \$RESOURCE_GROUP --location \$LOCATION"
    echo ""
    echo "DB_SERVER_NAME=\"recruitment-db-\$(date +%s)\""
    echo "DB_NAME=\"recruitment_db\""
    echo "DB_ADMIN_USER=\"recruitment_admin\""
    echo "DB_ADMIN_PASSWORD=\"salmasalma2025\""
    echo ""
    echo "az postgres flexible-server create \\"
    echo "  --resource-group \$RESOURCE_GROUP \\"
    echo "  --name \$DB_SERVER_NAME \\"
    echo "  --location \$LOCATION \\"
    echo "  --admin-user \$DB_ADMIN_USER \\"
    echo "  --admin-password \$DB_ADMIN_PASSWORD \\"
    echo "  --sku-name Standard_B1ms \\"
    echo "  --tier Burstable \\"
    echo "  --version 14 \\"
    echo "  --storage-size 32 \\"
    echo "  --public-access 0.0.0.0 \\"
    echo "  --yes"
    echo ""
else
    print_error "AUCUNE région fonctionnelle trouvée"
    echo ""
    print_info "Votre abonnement Azure for Students est très restrictif"
    print_info "Options :"
    echo "  1. Contactez le support Azure for Students"
    echo "  2. Demandez l'activation de régions supplémentaires"
    echo "  3. Utilisez une alternative comme Render.com ou Railway.app"
    echo ""
    print_info "Pour contacter le support :"
    echo "  https://azure.microsoft.com/support/community/"
fi