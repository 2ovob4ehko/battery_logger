### Конфіги
зберігаються в 
```aiignore
~/.local/share/glib-2.0/schemas/com.mmaaxx.batterylogger.gschema.xml
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<schemalist>
  <schema id="com.mmaaxx.batterylogger" path="/com/mmaaxx/batterylogger/">
    <key name="width" type="i">
      <default>600</default>
      <summary>Window width</summary>
    </key>
    <key name="height" type="i">
      <default>400</default>
      <summary>Window height</summary>
    </key>
  </schema>
</schemalist>
```
Далі після створення треба скомпілить
```bash
glib-compile-schemas ~/.local/share/glib-2.0/schemas/
```
При встановленні пакетом треба буде це створення файлу прописувати. Це типізація конфігів апки

```bash
sudo apt install python3-psutil
```

Всі іконки треба скопіювати в спеціальну папку в залежності від розміру кожного
~/.local/share/icons/hicolor/48x48/apps/battery_logger.png