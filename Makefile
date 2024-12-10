# Variables
VENV_DIR = venv
PYTHON = python3
REQUIREMENTS = requirements.txt
PYTHON_SCRIPT = final_report/model.py

# Default target
.PHONY: all
all: install run

# Create a virtual environment
$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)

# Install libraries from requirements.txt
install: $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS) > model_output.log 2>&1

# Run the Python script using the virtual environment
.PHONY: run
run: install
	$(VENV_DIR)/bin/python $(PYTHON_SCRIPT)

# Clean up virtual environment
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
