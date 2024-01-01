# Makefile for Flask Translation Management

# Define available languages
AVAILABLE_LANGUAGES := es gl

# Define targets
.PHONY: init_translation_template init_lang_translation_files update_translations execute_translate

# Check if pybabel is installed
PYBABEL := $(shell command -v pybabel 2> /dev/null)

ifeq ($(PYBABEL),)
$(error 'pybabel' is not installed. Please install it using 'pip install flask_babel')
endif


# Target: init_translation_template. It will scan all the files added in babel.cfg and create a template
init_translation_template:
	$(PYBABEL) extract -F babel.cfg -o notlar/translations/messages.pot .; \


# Target: init_lang_translation_files. It will create a folder for each language defined in the AVAILABLE_LANGUAGES variable.
init_lang_translation_files:
	@for lang in $(AVAILABLE_LANGUAGES); do \
		if [ ! -d "notlar/translations/$$lang" ]; then \
			$(PYBABEL) init -i notlar/translations/messages.pot -d notlar/translations -l $$lang; \
		fi \
	done

# Target: update_translations
update_translations:
	$(PYBABEL) update -i notlar/translations/messages.pot -d notlar/translations


# Target: compile_translations. Once we finish the manual translate we should compile and generate the .po files that will be used for Flask-Babel
compile_translations:
	$(PYBABEL) compile -d notlar/translations

# Target: execute_translate. It will execute all the targets in order.
execute_translate: init_translation_template init_lang_translation_files update_translations compile_translations
