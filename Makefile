SHELL := /bin/bash

.PHONY: status public-check secret-grep validate-yaml shellcheck tree security-scripts-check

status:
	@git status --short --untracked-files=all

public-check: status secret-grep validate-yaml security-scripts-check
	@echo "Public safety checks completed. Review all output before committing."

secret-grep:
	@echo "Checking tracked files for high-risk secret markers..."
	@if command -v rg >/dev/null 2>&1; then \
		git ls-files -z | xargs -0 rg -n -S --no-heading 'BEGIN .*PRIVATE KEY|AWS_SECRET_ACCESS_KEY|client_secret|password|token|api[_-]?key|secret|kubeconfig' || true; \
	else \
		echo "WARN: rg is not installed; falling back to grep."; \
		git ls-files -z | xargs -0 grep -n -E 'BEGIN .*PRIVATE KEY|AWS_SECRET_ACCESS_KEY|client_secret|password|token|api[_-]?key|secret|kubeconfig' || true; \
	fi
	@echo "Review matches manually. Example/template placeholders are expected."

validate-yaml:
	@echo "Validating YAML syntax where tools are available..."
	@if command -v yq >/dev/null 2>&1 && yq --version >/dev/null 2>&1; then \
		git ls-files '*.yaml' '*.yml' | while read -r file; do yq eval '.' "$$file" >/dev/null || exit 1; done; \
	elif command -v python3 >/dev/null 2>&1 && python3 -c 'import yaml' >/dev/null 2>&1; then \
		python3 -c 'import subprocess,yaml; files=subprocess.check_output(["git","ls-files","*.yaml","*.yml"], text=True).splitlines(); [list(yaml.safe_load_all(open(f, encoding="utf-8").read())) for f in files]; print(f"Validated {len(files)} YAML files.")'; \
	else \
		echo "WARN: yq or python3 with PyYAML is not installed; skipping YAML validation."; \
	fi

shellcheck:
	@echo "Checking shell scripts..."
	@if command -v shellcheck >/dev/null 2>&1; then \
		git ls-files '*.sh' | xargs -r shellcheck; \
	else \
		echo "WARN: shellcheck is not installed; skipping."; \
	fi

tree:
	@if command -v tree >/dev/null 2>&1; then \
		tree -a -I '.git|node_modules|platform/exports|platform/exports-clean|QloudK-Backup'; \
	else \
		echo "WARN: tree is not installed; using find."; \
		find . -path './.git' -prune -o -path './node_modules' -prune -o -path './platform/exports' -prune -o -path './platform/exports-clean' -prune -o -path './QloudK-Backup' -prune -o -print; \
	fi

security-scripts-check:
	@echo "Checking infra-security shell script permissions and syntax..."
	@for file in infra-security/scripts/*.sh tools/install-security-tools.sh; do \
		if [ -f "$$file" ]; then \
			[ -x "$$file" ] || echo "WARN: $$file is not executable"; \
			bash -n "$$file"; \
		fi; \
	done
