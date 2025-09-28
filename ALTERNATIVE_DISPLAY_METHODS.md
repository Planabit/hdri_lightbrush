# 🖼️ HDRI Editor - Alternatív Kép Megjelenítési Módszerek

## 🎯 **Probléma:** 
A `template_icon_view` túl kicsi preview képeket jelenít meg, még a helyes paraméterekkel is.

## 🛠️ **Alternatív Megoldások Teszt Addonok:**

### 📦 **1. hdri_editor_alternative.py**
**5 különböző megjelenítési módszer tesztelése:**

#### **Method 1: template_image**
```python
preview_box.template_image(img, img.image_user, compact=False, multiview=False)
```
- ✅ **Előny:** Natív image megjelenítés
- ❌ **Hátrány:** ImageUser objektum szükséges

#### **Method 2: template_ID_preview**  
```python
row.template_ID_preview(context.scene.hdri_properties, "current_image", 
                       rows=int(prefs.image_scale), cols=int(prefs.image_scale))
```
- ✅ **Előny:** Nagy méretű preview
- ❌ **Hátrány:** Négyzetes megjelenés

#### **Method 3: Custom Draw**
```python
# Operator alapú megjelenítés + image info
col.operator("hdri.show_image_viewer", icon="IMAGE_DATA")
```
- ✅ **Előny:** Teljes kontroll
- ❌ **Hátrány:** Külső ablak szükséges

#### **Method 4: Operator Modal**
```python
# Modal operator a kép megjelenítéshez
def modal(self, context, event): ...
```
- ✅ **Előny:** Interaktív
- ❌ **Hátrány:** Komplex implementáció

#### **Method 5: Image Viewer**
```python
# Image Editor area forced megnyitás
area.type = 'IMAGE_EDITOR'
area.spaces.active.image = img
```
- ✅ **Előny:** Teljes felbontás
- ❌ **Hátrány:** Külön workspace szükséges

### 📦 **2. hdri_editor_large_display.py**
**Nagy méretű megjelenítési módszerek:**

#### **Method 1: Large Template ID**
```python
row.scale_y = prefs.display_height / 100
row.template_ID_preview(props, "current_image", rows=max_size, cols=max_size)
```
- ✅ **Előny:** Nagy preview, állítható méret
- ✅ **Használható:** Jó kompromisszum

#### **Method 2: Dedicated Windows**
```python
bpy.ops.wm.window_new()
area.type = 'IMAGE_EDITOR'  
area.spaces.active.image = img
```
- ✅ **Előny:** Teljes ablak dedikált a képnek
- ✅ **Legjobb:** Editáláshoz ideális

#### **Method 3: Template Image Enhanced**
```python
col_img.scale_y = prefs.display_height / 200
col_img.template_image(img, None, compact=False)
```
- ✅ **Előny:** Direkt kép megjelenítés
- ⚠️ **Teszt:** Működés ImageUser nélkül

#### **Method 4: Large Icon View**
```python
icon_row.scale_y = prefs.display_height / 50
icon_row.label(text="", icon_value=icon_id)
```
- ✅ **Előny:** Nagy icon megjelenítés
- ❌ **Hátrány:** Icon minőség limitált

#### **Method 5: Combination Layout**
```python
# Bal oldal: Nagy preview, jobb oldal: infók és gombok
split = col.split(factor=0.5)
```
- ✅ **Előny:** Kompakt és informatív
- ✅ **Jó:** Teljes funkcionalitás egy panelen

## 🎮 **Tesztelési Útmutató:**

### **1. Telepítés:**
```bash
# Alternative methods addon
cd e:\Projects\HDRI_editor\tools
python test_alternative_display.py

# Large display addon  
python install_large_display.py
```

### **2. Tesztelés Blender-ben:**
1. **N-panel** megnyitása
2. **"HDRI Editor - Alternative Display"** panel
3. **"HDRI Editor - Large Display"** panel
4. Különböző **Display Method** opciók tesztelése
5. **Display Height/Width** beállítások módosítása

## 🏆 **Ajánlott Megoldások:**

### **🥇 Legjobb: Dedicated Windows (Method 2)**
- **Új ablak** Image Editor-ral  
- **Teljes felbontás** editáláshoz
- **Zoom, pan, stb.** funkcionalitás

### **🥈 Második: Large Template ID (Method 1)**
- **Nagy preview** a panelen belül
- **Állítható méret** (400-1000px height)
- **Gyors előnézet** betöltés után

### **🥉 Harmadik: Combination Layout (Method 5)**
- **Kompakt megoldás**
- **Preview + infók + gombok**
- **Egy helyen minden**

## 🔧 **Implementációs Javaslat:**

Az eredeti HDRI Editor addon frissítése a **Dedicated Windows** megoldással:

```python
class HDRI_OT_edit_fullscreen(Operator):
    bl_idname = "hdri.edit_fullscreen"
    bl_label = "Edit Fullscreen"
    
    def execute(self, context):
        img = context.scene.hdri_image
        # Create dedicated window
        bpy.ops.wm.window_new()
        # Set to Image Editor + load image
        # Add zoom fit
        return {"FINISHED"}
```

Ez biztosítja a **HD megjelenítést és editálási funkcionalitást** is!