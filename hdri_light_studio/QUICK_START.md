# Gyors Telepítési Útmutató - HDRI Light Studio

## 🚀 Azonnali Telepítés

### 1. Addon Telepítése Blenderbe
```
1. Nyisd meg Blender 4.2+
2. Edit → Preferences → Add-ons
3. Install from Disk → hdri_light_studio mappát válaszd
4. Pipáld be az "HDRI Light Studio" addon-t
```

### 2. Használat Megkezdése
```
1. 3D Viewport → Sidebar (N) → "HDRI Studio" tab
2. Canvas Size: 2K (ajánlott kezdéshez)
3. "Create Canvas" gomb
4. Ha hiba: "Debug Info" gomb a részletekért
```

## ⚡ Gyors Hibaelhárítás

### Problémamegoldás Lépésről Lépésre
1. **"Create Canvas"** → Viewport kettéválik
2. **Ha két 3D viewport**: "Fix Editor" → Jobb oldali 3D viewport → Image Editor
3. **"Create Test"** → Egyszerű teszt kép létrehozása és megjelenítése
4. **Ha látszik színes gradient**: Image Editor rendben működik!
5. **"Debug Info"** → Console részletes állapot jelentés

### GPU Problémák
- Az addon **automatikus fallback**-et használ
- Első: GPU texture renderelés (bgl + triangle fan)
- Második: Egyszerű BGL rajzolás
- Mindkettő működik különböző GPU konfigurációkban

### Konzol Üzenetek
```
✅ "Canvas successfully created" = Működik
⚠️  "Advanced canvas failed, trying simple" = Fallback mód
❌ "Both canvas creation methods failed" = Driver probléma
```

## 🎯 Első Tesztek

### 1. Canvas Létrehozás
```
Canvas Size: 2K (2048x1024) → Create Canvas
→ 3D viewport automatikusan ketté válik
→ Ha még két 3D viewport: "Fix Editor" gomb!
→ "Test Pattern" → Színes gradient látszik jobb oldalon?
→ Ha igen: Image Editor rendben működik
```

### 2. Debug Információ
```
Debug Info gomb → Console-ban:
✅ GPU module available
✅ BGL module available  
✅ NumPy available
✅ Canvas renderer: True
```

### 3. Kép Megjelenítés Tesztelése
```
"Test Pattern" gomb → Gradient teszt minta
→ Jobb oldali Image Editor-ban megjelenik színes minta
→ Ha látod: Image editor rendben működik!
"Update Display" → Canvas frissítés manuálisan
```

### 4. Egyszerű Festés
```
Tools → Paint kiválasztása
Brush Size: 50
"Start Painting" → Bal egér + mozgás a bal oldali viewport-ban
→ Festés automatikusan frissül jobb oldali képen
ESC = Kilépés festő módból
```

## 📋 Rendszerkövetelmények

- **Blender**: 4.2+
- **Python**: 3.11+ (Blenderrel jön)
- **OpenGL**: 3.3+ (legtöbb modern GPU)
- **NumPy**: Általában Blenderrel telepített

## 🔧 Fejlesztői Mód

Console üzenetek követése:
```
Window → Toggle System Console
→ Valós idejű debug információ
→ GPU és renderelési részletek
→ Hibaüzenetek és megoldások
```