### vial-gui

# Docs and getting started

### Please visit [get.vial.today](https://get.vial.today/) to get started with Vial

Vial is an open-source cross-platform (Windows, Linux and Mac) GUI and a QMK fork for configuring your keyboard in real time.


![](https://get.vial.today/img/vial-win-1.png)


---


#### Releases

Visit https://get.vial.today/ to download a binary release of Vial.

#### Development

##### macOS (Apple Silicon)

The native Apple Silicon build uses a modern Python (3.13 in CI) and does not
depend on `fbs` or Rosetta 2.

Install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-macos.txt
```

To launch the application afterwards:

```
source venv/bin/activate
python src/main/python/main.py
```

To build a standalone `Vial.app` (output lands in `dist/`):

```
pyinstaller vial-mac.spec
```

##### Windows, Linux and Intel Macs

Python 3.6 is required (3.6 is the latest version that is officially supported by `fbs`).

Install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To launch the application afterwards:

```
source venv/bin/activate
fbs run
```
