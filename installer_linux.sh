#!/bin/bash

# GMB Scraper Peru - Instalador para Linux/Mac
# Este script configura el entorno y las dependencias necesarias

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "╔════════════════════════════════════════╗"
echo "║     GMB Scraper Peru - Instalador      ║"
echo "║           Linux/Mac Edition            ║"
echo "╚════════════════════════════════════════╝"
echo ""

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_info() {
    echo -e "ℹ $1"
}

check_command() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

echo "═══════════════════════════════════════════"
echo "1. Verificando sistema operativo..."
echo "═══════════════════════════════════════════"

OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    log_success "Sistema Linux detectado"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    log_success "Sistema macOS detectado"
else
    log_error "Sistema operativo no soportado: $OSTYPE"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════"
echo "2. Verificando Python..."
echo "═══════════════════════════════════════════"

if check_command python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        log_success "Python $PYTHON_VERSION detectado"
    else
        log_error "Se requiere Python 3.8 o superior (encontrado: $PYTHON_VERSION)"
        
        if [ "$OS" == "linux" ]; then
            echo "Instale Python 3.8+ con: sudo apt-get install python3.8"
        else
            echo "Instale Python 3.8+ desde: https://www.python.org/downloads/"
        fi
        exit 1
    fi
else
    log_error "Python 3 no encontrado"
    
    if [ "$OS" == "linux" ]; then
        echo "Instalando Python 3..."
        if check_command apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif check_command yum; then
            sudo yum install -y python3 python3-pip
        elif check_command pacman; then
            sudo pacman -S python python-pip
        else
            log_error "No se pudo detectar el gestor de paquetes"
            exit 1
        fi
    else
        log_error "Por favor instale Python 3.8+ desde: https://www.python.org/downloads/"
        exit 1
    fi
fi

echo ""
echo "═══════════════════════════════════════════"
echo "3. Verificando pip..."
echo "═══════════════════════════════════════════"

if ! python3 -m pip --version &> /dev/null; then
    log_warning "pip no encontrado, instalando..."
    
    if [ "$OS" == "linux" ]; then
        if check_command apt-get; then
            sudo apt-get install -y python3-pip
        elif check_command yum; then
            sudo yum install -y python3-pip
        else
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            python3 get-pip.py
            rm get-pip.py
        fi
    else
        python3 -m ensurepip
    fi
fi

log_success "pip instalado"
log_info "Actualizando pip..."
python3 -m pip install --upgrade pip --quiet

echo ""
echo "═══════════════════════════════════════════"
echo "4. Creando entorno virtual..."
echo "═══════════════════════════════════════════"

VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    log_warning "Entorno virtual existente encontrado, eliminando..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
log_success "Entorno virtual creado"

source "$VENV_DIR/bin/activate"
log_success "Entorno virtual activado"

echo ""
echo "═══════════════════════════════════════════"
echo "5. Instalando dependencias de Python..."
echo "═══════════════════════════════════════════"

pip install --upgrade pip --quiet

REQUIREMENTS=(
    "selenium>=4.15.0"
    "webdriver-manager>=4.0.0"
    "pandas>=2.0.0"
    "python-dateutil>=2.8.0"
    "tqdm>=4.66.0"
    "beautifulsoup4>=4.12.0"
    "requests>=2.31.0"
    "openpyxl>=3.1.0"
    "lxml>=4.9.0"
)

for req in "${REQUIREMENTS[@]}"; do
    package_name=$(echo $req | cut -d'>' -f1)
    log_info "Instalando $package_name..."
    pip install "$req" --quiet
    log_success "$package_name instalado"
done

echo ""
echo "═══════════════════════════════════════════"
echo "6. Verificando Google Chrome..."
echo "═══════════════════════════════════════════"

if check_command google-chrome || check_command google-chrome-stable || check_command chromium-browser; then
    log_success "Google Chrome detectado"
else
    log_warning "Google Chrome no detectado"
    
    if [ "$OS" == "linux" ]; then
        echo "Instalando Google Chrome..."
        
        if check_command apt-get; then
            wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
            sudo apt-get update
            sudo apt-get install -y google-chrome-stable
        elif check_command yum; then
            sudo yum install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        else
            log_error "Por favor instale Google Chrome manualmente desde: https://www.google.com/chrome/"
        fi
    else
        log_error "Por favor instale Google Chrome desde: https://www.google.com/chrome/"
    fi
fi

echo ""
echo "═══════════════════════════════════════════"
echo "7. Configurando ChromeDriver..."
echo "═══════════════════════════════════════════"

python3 -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()" > /dev/null 2>&1
log_success "ChromeDriver configurado"

echo ""
echo "═══════════════════════════════════════════"
echo "8. Creando scripts de ejecución..."
echo "═══════════════════════════════════════════"

cat > run_gui.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 gui.py
EOF

chmod +x run_gui.sh
log_success "Script run_gui.sh creado"

cat > run_cli.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 main.py "$@"
EOF

chmod +x run_cli.sh
log_success "Script run_cli.sh creado"

if [ "$OS" == "linux" ]; then
    DESKTOP_FILE="$HOME/.local/share/applications/gmb-scraper.desktop"
    mkdir -p "$HOME/.local/share/applications"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=GMB Scraper Peru
Comment=Google My Business data extractor
Exec=$PWD/run_gui.sh
Icon=$PWD/icon.png
Terminal=false
Categories=Utility;
EOF
    
    chmod +x "$DESKTOP_FILE"
    log_success "Acceso directo creado en el menú de aplicaciones"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "9. Verificando instalación..."
echo "═══════════════════════════════════════════"

MODULES=("selenium" "pandas" "bs4" "requests" "tqdm" "webdriver_manager")
ALL_OK=true

for module in "${MODULES[@]}"; do
    if python3 -c "import $module" 2>/dev/null; then
        log_success "$module funcionando"
    else
        log_error "Error al importar $module"
        ALL_OK=false
    fi
done

echo ""
echo "═══════════════════════════════════════════"
echo "═══════════════════════════════════════════"

if $ALL_OK; then
    echo -e "${GREEN}✅ INSTALACIÓN COMPLETADA CON ÉXITO${NC}"
    echo ""
    echo "Para ejecutar el programa:"
    echo "  • Interfaz gráfica: ./run_gui.sh"
    echo "  • Línea de comandos: ./run_cli.sh [argumentos]"
    echo "  • Ayuda: ./run_cli.sh --help"
    echo ""
    echo "Ejemplos:"
    echo "  ./run_cli.sh restaurantes --departments Lima"
    echo "  ./run_cli.sh hoteles --format csv --headless"
else
    echo -e "${YELLOW}⚠ INSTALACIÓN COMPLETADA CON ADVERTENCIAS${NC}"
    echo "Algunos módulos no se pudieron verificar."
    echo "El programa puede funcionar, pero revise los errores arriba."
fi

echo "═══════════════════════════════════════════"

read -p "¿Desea ejecutar la interfaz gráfica ahora? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    ./run_gui.sh
fi