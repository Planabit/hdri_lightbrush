# HDRI Light Studio
## KeyShot-style HDRI Editor for Blender

Egy interaktív HDRI szerkesztő addon Blenderhez, amely KeyShot-stílusú inline szerkesztési funkciókat biztosít GPU-alapú custom draw handler technológiával.

## Főbb Funkciók

### 🎨 Real-Time HDRI Szerkesztés ⭐
- **2K/4K Canvas**: 2048x1024 és 4096x2048 HDRI standard felbontások
- **Automatikus Viewport Felosztás**: 3D viewport ketté válik Image Editor-ral
- **Real-Time World Sync**: Image Editor változások azonnal megjelennek a 3D világban
- **Instant Preview**: Material viewport shading automatikus beállítása

### 🖌️ Fejlett Festő Eszközök
- **Modal Painting**: Interaktív egér-alapú festés real-time frissítéssel
- **Brush System**: 1-200 pixel méret, 0-200% intenzitás kontroll
- **Dual Color Mode**: RGB színválasztás VAGY Kelvin hőmérséklet (1000K-40000K)
- **Temperature Conversion**: Fizikai alapú Kelvin→RGB konverzió
- **Brush Falloff**: Smooth, Linear, Sharp ecset szélsimítás opciók

### 💡 Intelligens Fény Elhelyezés
- **Shape-Based Lights**: Kör, négyzet, téglalap alakú fény generáló
- **Interactive Placement**: "Click to Place" modal operátor
- **Smart Falloff**: Természetes fény elhalás minden alakzatnál  
- **Temperature Control**: 1000K (meleg narancs) - 40000K (hideg kék) tartomány
- **Intensity Control**: 0.0-10.0x fényerő szorzó

## Telepítés

1. **Blender Megnyitása**: Blender 4.2+ szükséges
2. **Addon Telepítés**: 
   - Edit → Preferences → Add-ons → Install from Disk
   - Válaszd ki a `hdri_light_studio` mappát
3. **Aktiválás**: Pipáld be az "HDRI Light Studio" addon-t
4. **Használat**: 3D Viewport → Sidebar → "HDRI Studio" tab

## Használat

### 🚀 Gyors Kezdés
1. **Panel Elérése**: 3D Viewport → Sidebar (N) → HDRI Studio tab
2. **Canvas Létrehozás**: "Create Canvas" gomb → 2K vagy 4K méret kiválasztása
   - Viewport automatikusan ketté válik
   - Jobb oldalon Image Editor jelenik meg
   - World HDRI automatikusan beállításra kerül
3. **Viewport Shading**: Material view automatikusan aktiválódik a real-time preview-hoz

### 🎨 Festési Módok
#### Traditional Painting
- **Paint Tool**: Ecset eszköz kiválasztása
- **Color Settings**: RGB színválasztás VAGY Temperature mód (1000K-40000K)
- **Brush Settings**: Méret (1-200px), Intenzitás (0-200%)
- **Start Painting**: Modal festés indítása → egér mozgatásával festés

#### Smart Light Placement
- **Light Tool**: Fény eszköz kiválasztása  
- **Shape Selection**: Kör/Négyzet/Téglalap alakzat választás
- **Size & Intensity**: Fényméret (10-500px), erősség (0-10x)
- **Placement Options**:
  - **Add Center**: Fény a canvas közepére
  - **Click to Place**: Modal mód → kattintással bárhova

### ⚡ Real-Time Features
- **Instant World Update**: Image Editor minden változása azonnal megjelenik a 3D világban
- **Temperature Preview**: Kelvin értékek élő RGB konverziója
- **Smart Falloff**: Természetes fény elhalás és keverés
- **Viewport Sync**: Automatikus Material shading beállítás

## Technikai Részletek

### Architektúra
```
hdri_light_studio/
├── __init__.py           # Főmodul és regisztráció
├── properties.py         # Scene és eszköz tulajdonságok
├── operators.py          # Canvas és festő operátorok  
├── ui.py                # Panel UI és custom draw handler
└── canvas_renderer.py   # GPU-alapú canvas renderelés
```

### GPU Renderelési Technológia
- **bgl Module**: Low-level OpenGL hívások Blenderben
- **Triangle Fan**: Primitív quad rendereléshez
- **Custom Shader**: Vertex és fragment shader textura megjelenítéshez
- **Real-time Update**: Azonnali GPU textura frissítés

### Kompatibilitás
- **Blender**: 4.2+ (GPU és bgl modulok szükségesek)
- **Python**: 3.11+ (NumPy matematikai műveletekhez)
- **GPU**: OpenGL 3.3+ támogatás ajánlott

## Fejlesztői Jegyzetek

Ez az implementáció a következő kritériumoknak felel meg:
- ✅ Panel-alapú inline szerkesztés (nem viewport!)
- ✅ GPU custom draw handler bgl + triangle fan technológiával
- ✅ KeyShot-stílusú funkcionalitás
- ✅ Real-time interaktív szerkesztés
- ✅ 2K/4K canvas támogatás
- ✅ Moduláris kód architektúra

## Hibaelhárítás

### "Failed to create canvas" Hiba
1. **Kattints a "Debug Info" gombra** - Ellenőrzi a GPU és modulok állapotát
2. **Konzol ellenőrzés**: Window → Toggle System Console
3. **Fallback mód**: Az addon automatikusan egyszerű renderelésre vált GPU hiba esetén

### Canvas nem jelenik meg
- Ellenőrizd hogy van-e aktív 3D viewport
- Próbáld újra létrehozni a canvas-t
- Debug Info gomb megmutatja a probléma okát

### GPU Kompatibilitási problémák
Az addon **kétszintű fallback** rendszert használ:
1. **GPU Texture renderelés** (bgl + triangle fan)
2. **Egyszerű BGL rajzolás** (ha GPU texture nem működik)

### Festés nem működik
- Győződj meg róla hogy van aktív canvas
- Ellenőrizd hogy a 3D viewport-ban vagy
- Modal operátor: ESC-cel tudsz kilépni

### Gyakori megoldások
- **OpenGL driver frissítés** GPU problémák esetén
- **Kisebb canvas méret** (512x512) teszteléshez
- **Blender újraindítás** addon módosítások után

## Jövőbeli Fejlesztések

- Exportálás HDRI formátumokba
- További festő eszközök (gradient, pattern)
- Zoom és pan funkciók
- Undo/Redo rendszer
- Preset színhőmérséklet értékek