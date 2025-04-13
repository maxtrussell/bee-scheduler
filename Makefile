build:
	python3 -m build

upload: build
	python3 -m twine upload --skip-existing dist/*
