SHELL := /bin/bash
PROJECT_NAME="."
PYTHON_VERSION="3.10"

# Diretórios principais e subdiretórios
DIRS := \
	$(PROJECT_NAME)/src \
	$(PROJECT_NAME)/src/utils \
	$(PROJECT_NAME)/tests \
	$(PROJECT_NAME)/data \
	$(PROJECT_NAME)/docs \
	$(PROJECT_NAME)/jars \
	$(PROJECT_NAME)/.vscode 

# Arquivos principais
FILES := \
	$(PROJECT_NAME)/README.md \
	$(PROJECT_NAME)/.gitignore \
	$(PROJECT_NAME)/requirements.txt \
	$(PROJECT_NAME)/.env \
	$(PROJECT_NAME)/.vscode/settings.json


# Comando principal
.PHONY: all
all: create_dirs create_files init_git create_virtualenv

# Criação dos diretórios
.PHONY: create_dirs
create_dirs:
	@echo "Criando os diretorios..."
	@for dir in $(DIRS); do \
		mkdir -p $$dir; \
	done

# Criação dos arquivos principais
.PHONY: create_files
create_files: $(FILES)

$(PROJECT_NAME)/README.md:
	@echo "Criando o README.md..."
	@echo "# $(PROJECT_NAME)" > $(PROJECT_NAME)/README.md

$(PROJECT_NAME)/.gitignore:
	@echo "Criando o .gitignore..."
	@echo "venv/" > $(PROJECT_NAME)/.gitignore
	@echo "__pycache__/" >> $(PROJECT_NAME)/.gitignore
	@echo "*.pyc" >> $(PROJECT_NAME)/.gitignore
	@echo ".DS_Store" >> $(PROJECT_NAME)/.gitignore

$(PROJECT_NAME)/requirements.txt:
	@echo "Criando o requirements.txt..."
	@touch $(PROJECT_NAME)/requirements.txt

$(PROJECT_NAME)/.env:
	@echo "Criando o .env..."
	@touch $(PROJECT_NAME)/.env

$(PROJECT_NAME)/.vscode/settings.json:
	@echo "Criando o settings.json..."
	@echo '{"python.pythonPath": "venv/bin/python", "code-runner.executorMap.python": "venv/bin/python"}' > $(PROJECT_NAME)/.vscode/settings.json


# Criação do ambiente virtual
.PHONY: create_virtualenv
create_virtualenv:
	@echo "Criando o ambiente virtual python..."
	@python$(PYTHON_VERSION) -m venv $(PROJECT_NAME)/venv 
	@cd $(PROJECT_NAME) && source venv/bin/activate

# Inicialização do repositório Git
.PHONY: init_git
init_git:
	@echo "Iniciando o repositorio git..."
	@cd $(PROJECT_NAME) && git init

# Limpeza do projeto
.PHONY: clean
clean: clean_dir

.PHONY: clean_dir
clean_dir:
	@echo "Limpando o projeto..."
	@find $(PROJECT_NAME) -type f ! -name 'Makefile' -exec rm {} +
	@find $(PROJECT_NAME) -type d ! -name 'Makefile' ! -name '.' -exec rm -rf {} +

.PHONY: jars
jars:
	@echo "Copiando os jars para a pasta do pyspark..."
	@cp jars/*.jar venv/lib/python$(PYTHON_VERSION)/site-packages/pyspark/jars/
