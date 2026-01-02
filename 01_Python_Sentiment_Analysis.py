import pandas as pd
from textblob import TextBlob
from deep_translator import GoogleTranslator
import matplotlib.pyplot as plt
from datetime import datetime
import time
import os

print("--- 🤖 Vevővélemény Elemző AI v3.0 (File Support) ---")

# --- 1. LÉPÉS: BEÁLLÍTÁSOK (Nyelv és Forrás) ---

# 1.A: Nyelv kiválasztása
while True:
    nyelv_valasztas = input("1. Milyen nyelven elemezzünk? (HU / EN): ").upper().strip()
    if nyelv_valasztas in ['HU', 'EN']:
        kell_forditani = (nyelv_valasztas == 'HU')
        nyelv_cim = "Magyar" if kell_forditani else "English"
        break
    print("Hibás válasz! Csak HU vagy EN fogadható el.")

# 1.B: Adatforrás kiválasztása
while True:
    print("\n2. Honnan jöjjenek az adatok?")
    print("   [T] - Teszt adatok (Beépített demo)")
    print("   [F] - Fájl beolvasása (velemenyek.xlsx)")
    forras_valasztas = input("Választásod (T / F): ").upper().strip()
    
    if forras_valasztas in ['T', 'F']:
        break
    print("Hibás válasz! Csak T vagy F fogadható el.")

# --- 2. LÉPÉS: ADATOK BETÖLTÉSE ---

df = None # Üres változó létrehozása

if forras_valasztas == 'T':
    # --- TESZT ADATOK ---
    print("\nSzimulált adatok betöltése...")
    if nyelv_valasztas == 'HU':
        data = {
            'Ugyfel_Nev': ['Gábor', 'Éva', 'Péter', 'Zsuzsa'],
            'Velemeny': [
                "Ez a termék egyszerűen zseniális, imádom!", 
                "Teljes pénzkidobás volt, soha többet.", 
                "Hát, elmegy. Nem rossz, de nem is extra.", 
                "Gyors szállítás, korrektek voltak."
            ]
        }
    else: # EN
        data = {
            'Ugyfel_Nev': ['John', 'Sarah', 'Mike', 'Emily'],
            'Velemeny': [
                "Absolutely fantastic! Best purchase ever.",
                "Terrible service, very rude staff.",
                "It is okay, does the job.",
                "Fast shipping."
            ]
        }
    df = pd.DataFrame(data)

elif forras_valasztas == 'F':
    # --- FÁJL BETÖLTÉSE ---
    file_nev = 'velemenyek.xlsx'
    
    # Ellenőrizzük, létezik-e a fájl
    if os.path.exists(file_nev):
        print(f"\n📂 '{file_nev}' megnyitása...")
        try:
            df = pd.read_excel(file_nev)
            
            # --- KRITIKUS RÉSZ: Oszlopok ellenőrzése ---
            # Kérés: 'név' és 'vélemény' legyenek az oszlopok.
            # A program viszont 'Ugyfel_Nev' és 'Velemeny' nevekkel dolgozik.
            # Át kell neveznünk őket (Mapping)!
            
            required_columns = ['név', 'vélemény']
            # Ellenőrizzük, hogy megvannak-e a kért oszlopok (kisbetű/nagybetű érzékeny lehet)
            # Itt most feltételezzük, hogy pontosan írta be a user.
            
            if 'név' in df.columns and 'vélemény' in df.columns:
                # Átnevezés a belső logikához
                df = df.rename(columns={'név': 'Ugyfel_Nev', 'vélemény': 'Velemeny'})
                print("✅ Oszlopok sikeresen felismerve és átalakítva.")
            else:
                print("❌ HIBA: A fájl nem tartalmazza a 'név' és 'vélemény' oszlopokat!")
                print(f"Jelenlegi oszlopok a fájlban: {list(df.columns)}")
                exit() # Kilépés, ha rossz a fájl
                
        except Exception as e:
            print(f"❌ Hiba a fájl olvasásakor: {e}")
            exit()
    else:
        print(f"❌ HIBA: Nem találom a '{file_nev}' fájlt a mappában!")
        print("Kérlek hozz létre egy Excel fájlt 'név' és 'vélemény' oszlopokkal.")
        exit()

print(f"📥 {len(df)} vélemény sikeresen betöltve.\n")

# --- 3. LÉPÉS: ELEMZÉS LOGIKA (Változatlan) ---

def elemzo_motor(text, forditani_kell):
    szoveg_elemzeshez = text
    if forditani_kell:
        try:
            translator = GoogleTranslator(source='auto', target='en')
            szoveg_elemzeshez = translator.translate(str(text)) # str(text) biztosítja, hogy szöveg legyen
        except Exception:
            return 'Hiba ⚠️', 0.0

    blob = TextBlob(szoveg_elemzeshez)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1: return 'Pozitív 😊', polarity
    elif polarity < -0.1: return 'Negatív 😠', polarity
    else: return 'Semleges 😐', polarity

# --- 4. LÉPÉS: FUTTATÁS ---
print("⏳ Az AI elemzi az adatokat...")

hangulatok = []
pontszamok = []

for index, row in df.iterrows():
    # Progress bar szerű visszajelzés
    print(f"[{index+1}/{len(df)}] Feldolgozás: {str(row['Ugyfel_Nev'])[:10]}...")
    
    kategoria, pont = elemzo_motor(row['Velemeny'], kell_forditani)
    hangulatok.append(kategoria)
    pontszamok.append(pont)
    
    if kell_forditani: time.sleep(0.1)

df['Hangulat_Kategoria'] = hangulatok
df['Pontszam'] = pontszamok

# --- 5. LÉPÉS: EREDMÉNYEK MENTÉSE ---

# Kördiagram
sentiment_counts = df['Hangulat_Kategoria'].value_counts()
plt.figure(figsize=(9, 6))
colors = {'Pozitív 😊': '#4CAF50', 'Semleges 😐': '#FFC107', 'Negatív 😠': '#F44336', 'Hiba ⚠️': 'gray'}
actual_colors = [colors.get(x, '#999999') for x in sentiment_counts.index]

plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', 
        colors=actual_colors, startangle=140, shadow=True)
plt.title(f'{nyelv_cim} Vélemények Elemzése (Forrás: {forras_valasztas})')

timestamp = datetime.now().strftime("%Y%m%d_%H%M")
img_name = f'elemzes_eredmeny_{timestamp}.png'
excel_name = f'feldolgozott_velemenyek_{timestamp}.xlsx'

plt.savefig(img_name)
# Visszanevezzük az oszlopokat magyarra a mentés előtt, hogy szép legyen
df_export = df.rename(columns={'Ugyfel_Nev': 'Név', 'Velemeny': 'Eredeti Vélemény'})
df_export.to_excel(excel_name, index=False)

print(f"\n✅ Kész! Diagram mentve: {img_name}")
print(f"✅ Eredmény Excel exportálva: {excel_name}")