"""
BIST Teknik Analiz Uygulaması (v2)
Kurulum:  py -m pip install streamlit yfinance pandas plotly
Çalıştır: py -m streamlit run bist_analiz.py
Not: Yatırım tavsiyesi değildir.
"""
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="BIST Teknik Analiz", layout="wide")

# ------------------------------------------------------------------
# HİSSE GRUPLARI
# Hisse eklemek için ilgili listeye kodu yaz. Listede olmayan hisseleri
# bu dosyayla AYNI klasörde "ek_hisseler.txt" açıp içine boşlukla/satırla
# yazarsan "Benim listem" grubu olarak otomatik yüklenir.
# Gruplar yaklaşık olup şirketlerin sınıflandırması/endeks bileşenleri
# zamanla değişir. Geçersiz/işlem görmeyen kodlar taramada atlanır.
# ------------------------------------------------------------------
G = lambda s: s.split()
ENDEKS_GRUPLARI = {
    "BIST 30 (yaklaşık)": G("AKBNK ARCLK ASELS BIMAS EKGYO ENKAI EREGL FROTO GARAN GUBRF HALKB ISCTR KCHOL KRDMD MGROS PETKM PGSUS SAHOL SASA SISE TAVHL TCELL THYAO TOASO TTKOM TUPRS VAKBN YKBNK"),
    "BIST 100 (yaklaşık)": G("""AEFES AKBNK AKSA AKSEN ALARK ALFAS ARCLK ASELS ASTOR BIMAS BRSAN BRYAT BUCIM CANTE CCOLA CIMSA
        CWENE DOAS DOHOL ECILC EGEEN EKGYO ENERY ENJSA ENKAI EREGL EUPWR FROTO GARAN GENIL GESAN GUBRF GWIND HALKB
        HEKTS ISCTR ISMEN KCAER KCHOL KLSER KONTR KONYA KOZAA KOZAL KRDMD MAVI MGROS MIATK ODAS OTKAR OYAKC PETKM
        PGSUS REEDR SAHOL SASA SISE SKBNK SMRTG SOKM TABGD TAVHL TCELL THYAO TKFEN TOASO TSKB TTKOM TTRAK TUKAS TUPRS
        TURSG ULKER VAKBN VESBE VESTL YKBNK YEOTK ZOREN"""),
}
SEKTOR_GRUPLARI = {
    "Bankalar": G("AKBNK ALBRK GARAN HALKB ICBCT ISATR ISBTR ISCTR KLNMA QNBTR SKBNK TSKB VAKBN YKBNK"),
    "Sigorta & Emeklilik": G("AGESA AKGRT ANHYT ANSGR RAYSG TURSG"),
    "Aracı Kurum & Finans": G("A1CAP GEDIK GLBMD GLCVY INFO ISMEN OSMEN GARFA ISFIN SEKFK VAKFN LIDFA"),
    "Holdingler": G("AGHOL AKYHO ALARK AVHOL BERA BRYAT DOHOL EUHOL GLYHO GSDHO IEYHO IHLAS INVEO KCHOL KLRHO MZHLD NTHOL PEHOL SAHOL SNPAM TKFEN TRHOL VERUS YESIL"),
    "GYO (Gayrimenkul)": G("AAGYO ADGYO AGYO AHSGY AKFGY AKMGY AKSGY ALGYO ASGYO AVGYO DGGYO DZGYO EKGYO EYGYO FZLGY HLGYO IDGYO ISGYO KGYO KLGYO KRGYO KZBGY MHRGY MSGYO NUGYO OZGYO OZKGY PAGYO PEKGY RYGYO SEGYO SNGYO SRVGY TDGYO TRGYO TSGYO VKGYO YGGYO YGYO ZRGYO"),
    "Enerji & Elektrik": G("A1YEN AKENR AKFYE AKSEN AKSUE ALFAS ARASE AYDEM AYEN BIOEN CANTE CATES CWENE ENERY ENJSA ENSRI EUPWR GESAN GWIND HUNER IZENR KARYE MAGEN NATEN ODAS PAMEL SMRTG YEOTK ZEDUR ZOREN AHGAZ"),
    "Petrol, Rafineri & Gaz": G("AYGAZ PETKM TUPRS TRCAS"),
    "Havacılık, Ulaştırma & Denizcilik": G("CLEBI DOCO GSDDE PGSUS RYSAS TAVHL THYAO TLMAN"),
    "Otomotiv & Yan Sanayi": G("ASUZU BRISA DITAS DOAS EGEEN FMIZP FROTO GOODY JANTS KARSN OTKAR PARSN TMSN TOASO TTRAK"),
    "Savunma & Teknoloji": G("ALCTL ALTNY ARDYZ ARENA ASELS DESPC DGATE EDATA ESCOM FONET HTTBT INDES KAREL KFEIN KONTR KRONT LINK LOGO MIATK MOBTL NETAS PAPIL PENTA REEDR SDTTR TKNSA VBTYZ ARMDA"),
    "Telekom": G("TCELL TTKOM"),
    "Perakende, Gıda & İçecek": G("AEFES AKHAN ALKLC BANVT BIMAS BIZIM CCOLA CRFSA ERSU FRIGO KERVT KNFRT KRSTL MAVI MGROS OFSYM ORCAY OYLUM PENGD PETUN PINSU SELVA SOKM TABGD TATGD TUKAS ULKER ULUUN YYLGD VAKKO"),
    "Tekstil & Hazır Giyim": G("ARSAN ATEKS BLCYT BOSSA BRKO DAGI DESA DIRIT HATEK KRTEK LUKSK SKTAS YUNSA"),
    "Demir-Çelik & Madencilik": G("BRSAN CELHA CEMTS EREGL IZMDC ISDMR KCAER KOZAA KOZAL KRDMA KRDMB KRDMD SARKY"),
    "Çimento, İnşaat & Yapı": G("AFYON AKCNS AKFIS ALBTN BTCIM BSOKE BUCIM CIMSA EDIP EGSER ENKAI KLSER KONYA KUTPO MRDIN NIBAS NUHCM OYAKC QUAGR"),
    "Kimya, Gübre, İlaç & Plastik": G("AKSA ALKIM BAGFS DEVA DYOBY ECILC ECZYT EGGUB GENIL GUBRF HEKTS KMPUR MRSHL SASA SELEC"),
    "Kağıt & Ambalaj": G("ALKA DGNMO KAPLM KARTN"),
    "Sanayi, Makine & Dayanıklı Tüketim": G("ALCAR ARCLK ARZUM ASTOR BFREN BRYAT EMKEL GEREL IMASM KLMSN MAKIM PRKAB SISE VESBE VESTL"),
    "Turizm, Spor & Sağlık": G("AVTUR BJKAS FENER GSRAY LKMNH MAALT MEDTR MERIT METUR MPARK TSPOR"),
}
# Kullanıcının verdiği tam hisse listesi (yazım hataları düzeltildi: AAVTUR->AVTUR, NETAŞ->NETAS,
# KAFEIN->KFEIN, ALFA->ALFAS). Yukarıdaki sektörlerde olmayanlar otomatik olarak
# "Diğer (sınıflandırılmamış)" grubuna girer. Bir hisseyi doğru sektöre taşımak için
# kodunu yukarıdaki ilgili listeye yaz, burada tekrar silmene gerek yok.
KULLANICI_LISTESI = G("""
        AVTUR ABODV AEFES AFYON AGHOL AGROT AGESA AGYO AHGAZ AKBNK AKCNS AKEBA
        AKFGY AKFYE AKGRT AKMGY AKSA AKSEN AKSUE AKTVN ALARK ALBRK ALCAR ALCTL
        ALFAS ALGYO ALKA ALMAD ALTNY ALVES ANELE ANGEL ANHYT ANSGR ARASE ARCLK
        ARENA ARDYZ ARKEM ARMET ARSFA ARZUM ASELS ASGYO ASTOR ASUZU ATAGY ATAKP
        ATEKS ATIK ATATP ATECH ATLAS ATRX AVHOL AVOD AVGYO AYES AYCES AYDEM
        AYEN AYGAZ AZTEK BAGFS BAKAB BALAT BANVT BARMA BASGZ BAYRK BEGYO BERA
        BEYAZ BFREN BIAST BICKO BIKIM BIMAS BINHO BIOEN BIZIM BJKAS BLCYU BLCKG
        BNTAS BORSK BORUZ BOSSA BRSAN BRKO BRLSM BRMEN BRNS BRRYO BRYAT BSOKE
        BTCIM BUCIM BURCE BURVA BVSAN BYDNR CANTE CATES CCOLA CELHA CEMAS CEMTS
        CEOEM CMBTN CMENT CLEBI CONSE COSMO CRDFA CRFSA CUSAN CWENE DAGI DAGHL
        DARDL DGATE DGBTR DGGYO DITAS DMEWO DOAS DOBUR DOCTA DOHOL DOCKR DOGUB
        DOFER DONGU DPGYO DPA DSI DSN EBEBK ECILC ECZYT EDATA EFORC EGEEN
        EGEPO EGGUB EGPRO EGSER EKIZ EKGYO EKOS EKSUN ELITE EMBAY ENERJ ENJSA
        ENKAI ENSRI ENTRA ERBOS EREGL ERLYS ERSU ESCAR ESEN ETILR EUPWR EUREK
        EUROT EYGYO FADE FENER FLAP FMIZP FONET FORTE FRIGO FROTO FZP GARAN
        GARFA GEDIK GEDZA GENIL GENTS GEREL GESAN GIPTA GLBMD GLYHO GMTAS GOLTS
        GOODY GOZDE GRNYO GRSEL GSDHO GSRAY GUBRF GWIND GZNMI HALKB HATSN HDFGS
        HEDEF HEKTS HKTM HOROZ HUBVC HUNER HURGZ ICBCT IEYHO IHAAS IHEVA IHGZT
        IHLAS IHMAD IKB IMASM INGRM INTEM INVEO INVES IPEKE ISATR ISBTR ISCTR
        ISDMR ISFIN ISGSY ISGYO ISKPL ISMEN ISTUR ISSEN ITTFH IZZET JANTS KAEFO
        KFEIN KAMWE KAPE KAPLM KAREL KARSN KARTN KASAR KATS KATMR KBORU KCAER
        KCHOL KDD KGYO KIMMR KLMSN KLNMA KLRZO KLSER KMSAN KMPUR KNFRT KONTR
        KONYA KOPST KORDS KOZAA KOZAL KRDMD KRGYO KRONT KRPLS KRSTL KRTEK KTLEV
        KTC KTK KUA KUTPO KUZEY LIDER LINK LKMNH LOGO LORAS LRSHA LUKSK
        MAALT MACKO MAGEN MAKIM MAKTK MANAS MARKA MARTI MTRKS MAVI MEDTR MEGAP
        MEGMT MEPET MERCN MERIT MERKO METUR MGROS MIATK MHRGY MNP MOBTL MPARK
        MRSHL MSGYO MTR MTRYO MZX NAAS NATEN NETAS NIBAS NTGAZ NTHOL NUGYO
        OBAMS OFYM ONCSM ORGE ORMA OSE OSTIM OTKAR OYYAT OZKGY OZRDN PAGYO
        PAMEL PAPIL PARSN PAST PASEU PEKGY PENTA PETKM PETUN PGSUS PINSU PKENT
        PKART PLTUR PNLSN PNT POLHO POLTK PRKAB PRKME PRDGS PRZMA PSA PSDTC
        QNBFL RAYSG REEDR RGYO RNPWR RALYH RAYS RTALB RUBNS RYGYO RYSAS SAHOL
        SAMAT SANEL SANFM SANKO SARKY SASA SAYAS SDTTR SEKFK SEKUR SELEC SELVA
        SEYKM SILVR SISE SKBNK SKYMD SMRTG SNGYO SNICA SNKRN SNPAM SODSN SOKM
        SONY TABGD TARKM TATEN TATGD TAVHL TCELL TDGYO TEKTU TERA TETH THYAO
        TKFEN TKNSA TLMAN TMPOL TOASO TRGYO TSKB TUPRS TURSG TUREKS TTKOM ULUFA
        ULKER UNLU VAKBN VAKKO VAKFN VAL VESBE VESTL VKFYO VKGYO YATAS YAYLA
        YEOTK YKBNK YGYO YKSLN YONGA YYLGD ZOREN ZRGYO
""")
_sinifli = {h for l in SEKTOR_GRUPLARI.values() for h in l}
SEKTOR_GRUPLARI["Diğer (sınıflandırılmamış)"] = [h for h in KULLANICI_LISTESI if h not in _sinifli]

GRUPLAR = {**ENDEKS_GRUPLARI, **SEKTOR_GRUPLARI}

# Kullanıcının kendi dosyası (isteğe bağlı)
try:
    from pathlib import Path
    _p = Path(__file__).with_name("ek_hisseler.txt")
    if _p.exists():
        _ek = [k.strip().upper().replace(".IS", "") for k in _p.read_text(encoding="utf-8").replace(",", " ").split()]
        if _ek:
            GRUPLAR["Benim listem"] = _ek
except Exception:
    pass

HISSELER = sorted({h for l in GRUPLAR.values() for h in l})
SEKTOR = {}
for g, l in {**SEKTOR_GRUPLARI, **{k: v for k, v in GRUPLAR.items() if k == "Benim listem"}}.items():
    for h in l:
        SEKTOR.setdefault(h, g)


# ---------- İndikatörler ----------
def rsi(c, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    return 100 - 100 / (1 + up / dn)


def ekle_indikatorler(df):
    c = df["Close"]
    df["SMA20"], df["SMA50"], df["SMA200"] = (c.rolling(w).mean() for w in (20, 50, 200))
    df["EMA12"], df["EMA26"] = c.ewm(span=12, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["MACD_S"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_H"] = df["MACD"] - df["MACD_S"]
    df["RSI"] = rsi(c)
    m, s = c.rolling(20).mean(), c.rolling(20).std()
    df["BB_U"], df["BB_L"] = m + 2 * s, m - 2 * s

    # --- Stochastic (14,3,3 yavaş) ---
    ll, hh = df["Low"].rolling(14).min(), df["High"].rolling(14).max()
    ham = 100 * (c - ll) / (hh - ll).replace(0, float("nan"))
    df["STOCH_K"] = ham.rolling(3).mean()
    df["STOCH_D"] = df["STOCH_K"].rolling(3).mean()

    # --- ADX (14, Wilder) + DI çizgileri ---
    up, dn = df["High"].diff(), -df["Low"].diff()
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([df["High"] - df["Low"], (df["High"] - pc).abs(), (df["Low"] - pc).abs()], axis=1).max(axis=1)
    w = dict(alpha=1 / 14, adjust=False, min_periods=14)
    atr = tr.ewm(**w).mean()
    df["ATR"] = atr
    df["ATR_P"] = 100 * atr / c
    df["DI_P"] = 100 * pdm.ewm(**w).mean() / atr
    df["DI_M"] = 100 * mdm.ewm(**w).mean() / atr
    dx = 100 * (df["DI_P"] - df["DI_M"]).abs() / (df["DI_P"] + df["DI_M"]).replace(0, float("nan"))
    df["ADX"] = dx.ewm(**w).mean()

    # --- OBV (On-Balance Volume) ve 20 günlük ortalaması ---
    yon = c.diff().gt(0).astype(int) - c.diff().lt(0).astype(int)
    df["OBV"] = (yon * df["Volume"]).cumsum()
    df["OBV_SMA"] = df["OBV"].rolling(20).mean()
    return df


def seviyeler(df, n=120, k=5, tol=0.015):
    """Son n barda yerel tepe/dip noktalarını bulup yakın olanları birleştirir.
    Döner: (destekler, dirençler); her biri [(seviye, temas_sayısı), ...] (fiyata en yakın 3 tane)."""
    d = df.tail(n)
    hi, lo = d["High"].values, d["Low"].values
    nokta = []
    for i in range(k, len(d) - k):
        if hi[i] == max(hi[i - k:i + k + 1]): nokta.append(float(hi[i]))
        if lo[i] == min(lo[i - k:i + k + 1]): nokta.append(float(lo[i]))
    nokta.sort()
    kume = []
    for p in nokta:
        if kume and abs(p / (sum(kume[-1]) / len(kume[-1])) - 1) <= tol: kume[-1].append(p)
        else: kume.append([p])
    lv = [(sum(g) / len(g), len(g)) for g in kume]
    fiyat = float(d["Close"].iloc[-1])
    destek = sorted([x for x in lv if x[0] < fiyat], key=lambda t: -t[0])[:3]
    direnc = sorted([x for x in lv if x[0] > fiyat], key=lambda t: t[0])[:3]
    return destek, direnc


FIB_ORANLAR = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]


def fibonacci(df, n=120):
    """Son n bardaki dalganın Fibonacci geri çekilme seviyeleri.
    Döner: ({oran: fiyat}, yükseliş_mi, tepe, dip)."""
    d = df.tail(n)
    ust, alt = float(d["High"].max()), float(d["Low"].min())
    yukselis = d["High"].values.argmax() > d["Low"].values.argmin()  # tepe, dipten sonra geldiyse yükseliş dalgası
    if yukselis: lv = {o: ust - o * (ust - alt) for o in FIB_ORANLAR}
    else: lv = {o: alt + o * (ust - alt) for o in FIB_ORANLAR}
    return lv, yukselis, ust, alt


def sinyaller(df):
    r, p = df.iloc[-1], df.iloc[-2]
    out = []
    if r.RSI < 30: out.append(("RSI", "AL", f"Aşırı satım ({r.RSI:.0f})"))
    elif r.RSI > 70: out.append(("RSI", "SAT", f"Aşırı alım ({r.RSI:.0f})"))
    else: out.append(("RSI", "NÖTR", f"{r.RSI:.0f}"))
    if p.MACD < p.MACD_S and r.MACD > r.MACD_S: out.append(("MACD", "AL", "Yukarı kesişim"))
    elif p.MACD > p.MACD_S and r.MACD < r.MACD_S: out.append(("MACD", "SAT", "Aşağı kesişim"))
    else: out.append(("MACD", "AL" if r.MACD > r.MACD_S else "SAT", "Sinyal üstünde" if r.MACD > r.MACD_S else "Sinyal altında"))
    out.append(("SMA20/50", "AL" if r.SMA20 > r.SMA50 else "SAT", "20 > 50" if r.SMA20 > r.SMA50 else "20 < 50"))
    if pd.notna(r.SMA200):
        out.append(("SMA200", "AL" if r.Close > r.SMA200 else "SAT", "Fiyat üstünde" if r.Close > r.SMA200 else "Fiyat altında"))
    if r.Close < r.BB_L: out.append(("Bollinger", "AL", "Alt bant altı"))
    elif r.Close > r.BB_U: out.append(("Bollinger", "SAT", "Üst bant üstü"))
    else: out.append(("Bollinger", "NÖTR", "Bant içinde"))
    if pd.notna(r.STOCH_K):
        if r.STOCH_K < 20: out.append(("Stochastic", "AL", f"Aşırı satım (%K {r.STOCH_K:.0f})"))
        elif r.STOCH_K > 80: out.append(("Stochastic", "SAT", f"Aşırı alım (%K {r.STOCH_K:.0f})"))
        else: out.append(("Stochastic", "NÖTR", f"%K {r.STOCH_K:.0f}"))
    if pd.notna(r.ADX):
        if r.ADX >= 25:
            yukari = r.DI_P > r.DI_M
            out.append(("ADX", "AL" if yukari else "SAT",
                        f"Güçlü {'yükseliş' if yukari else 'düşüş'} trendi (ADX {r.ADX:.0f})"))
        else:
            out.append(("ADX", "NÖTR", f"Trend zayıf (ADX {r.ADX:.0f})"))
    if pd.notna(r.OBV_SMA) and df.Volume.iloc[-20:].sum() > 0:
        up_ = r.OBV > r.OBV_SMA
        out.append(("OBV", "AL" if up_ else "SAT", "Ortalamasının üstünde (para girişi)" if up_ else "Ortalamasının altında (para çıkışı)"))
    if pd.notna(r.ATR):
        out.append(("ATR", "NÖTR", f"Günlük ort. hareket {r.ATR:.2f} ₺ (%{r.ATR_P:.1f}) | 2xATR stop: {r.Close - 2 * r.ATR:.2f}"))
        destek, direnc = seviyeler(df)
        dd = r.Close - destek[0][0] if destek else float("inf")
        dr = direnc[0][0] - r.Close if direnc else float("inf")
        if dd <= r.ATR and dd <= dr:
            out.append(("Destek/Direnç", "AL", f"Desteğe yakın ({destek[0][0]:.2f})"))
        elif dr <= r.ATR:
            out.append(("Destek/Direnç", "SAT", f"Dirence yakın ({direnc[0][0]:.2f})"))
        else:
            ds = f"{destek[0][0]:.2f}" if destek else "-"
            dn = f"{direnc[0][0]:.2f}" if direnc else "-"
            out.append(("Destek/Direnç", "NÖTR", f"Destek {ds} | Direnç {dn}"))
    lv, yuk, ust, alt = fibonacci(df)
    if ust > alt:
        oran = (ust - r.Close) / (ust - alt) if yuk else (r.Close - alt) / (ust - alt)
        out.append(("Fibonacci", "NÖTR", f"Son dalga ({'yükseliş' if yuk else 'düşüş'}) %{oran * 100:.0f} geri çekilmiş"))
    return out


def skor(sig):
    return sum(1 if s == "AL" else -1 if s == "SAT" else 0 for _, s, _ in sig)


@st.cache_data(ttl=900, show_spinner=False)
def veri_cek(sembol, periyot, aralik):
    df = yf.download(sembol, period=periyot, interval=aralik, auto_adjust=True, progress=False)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return ekle_indikatorler(df.dropna(subset=["Close"]))


@st.cache_data(ttl=900, show_spinner=False)
def toplu_veri(kodlar):
    """Çok sayıda hisseyi 60'ar parça halinde toplu indirir (tek tek indirmekten çok daha hızlı)."""
    sonuc = {}
    for i in range(0, len(kodlar), 60):
        parca = list(kodlar[i:i + 60])
        try:
            data = yf.download([f"{k}.IS" for k in parca], period="1y", interval="1d", auto_adjust=True,
                               group_by="ticker", threads=True, progress=False)
        except Exception:
            continue
        for k in parca:
            try:
                d = data[f"{k}.IS"] if isinstance(data.columns, pd.MultiIndex) else data
                d = d.dropna(subset=["Close"])
                if len(d) > 50:
                    sonuc[k] = ekle_indikatorler(d.copy())
            except Exception:
                pass
    return sonuc


def grafik(df, gos):
    fig = make_subplots(rows=8, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                        row_heights=[0.30, 0.08, 0.11, 0.11, 0.10, 0.10, 0.10, 0.10])
    x = df.index
    # --- Fiyat paneli ---
    fig.add_trace(go.Candlestick(x=x, open=df.Open, high=df.High, low=df.Low, close=df.Close,
                                 increasing=dict(line=dict(color="#0a8f3c", width=2), fillcolor="#0a8f3c"),
                                 decreasing=dict(line=dict(color="#d11a2a", width=2), fillcolor="#d11a2a"),
                                 whiskerwidth=0.6,
                                 name="Mum (yeşil=yükseliş, kırmızı=düşüş)",
                                 legendgroup="fiyat", legendgrouptitle_text="FİYAT"), row=1, col=1)
    renk = {"SMA20": "#1f77b4", "SMA50": "#ff7f0e", "SMA200": "#9467bd"}
    ad = {"SMA20": "SMA20 (20 günlük ort.)", "SMA50": "SMA50 (50 günlük ort.)", "SMA200": "SMA200 (200 günlük ort.)"}
    for k in ("SMA20", "SMA50", "SMA200"):
        if k in gos:
            fig.add_trace(go.Scatter(x=x, y=df[k], name=ad[k], line=dict(width=1.5, color=renk[k]),
                                     legendgroup="fiyat"), row=1, col=1)
    if "Bollinger" in gos:
        fig.add_trace(go.Scatter(x=x, y=df.BB_U, name="Bollinger üst bant", legendgroup="fiyat",
                                 line=dict(width=1, dash="dot", color="#7f7f7f")), row=1, col=1)
        fig.add_trace(go.Scatter(x=x, y=df.BB_L, name="Bollinger alt bant", legendgroup="fiyat",
                                 line=dict(width=1, dash="dot", color="#bcbd22")), row=1, col=1)
    # --- Destek / Direnç ---
    if "Destek/Direnç" in gos:
        destek, direnc = seviyeler(df)
        for i, (lv_, t_) in enumerate(destek):
            fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[lv_, lv_], mode="lines",
                                     name=f"Destek {i + 1}: {lv_:.2f} ({t_} temas)",
                                     line=dict(color="#00c853", width=1.4, dash="dash"), legendgroup="sr",
                                     legendgrouptitle_text="DESTEK / DİRENÇ"), row=1, col=1)
        for i, (lv_, t_) in enumerate(direnc):
            fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[lv_, lv_], mode="lines",
                                     name=f"Direnç {i + 1}: {lv_:.2f} ({t_} temas)",
                                     line=dict(color="#ff1744", width=1.4, dash="dash"), legendgroup="sr",
                                     legendgrouptitle_text="DESTEK / DİRENÇ"), row=1, col=1)
    # --- Fibonacci ---
    if "Fibonacci" in gos:
        lv, yuk, ust, alt = fibonacci(df)
        frenk = {0: "#b0b0b0", 0.236: "#ffd54f", 0.382: "#ffb300", 0.5: "#ff7043",
                 0.618: "#ec407a", 0.786: "#ab47bc", 1: "#b0b0b0"}
        for o, v in lv.items():
            fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[v, v], mode="lines",
                                     name=f"Fib %{o * 100:.1f}: {v:.2f}",
                                     line=dict(color=frenk[o], width=1.1, dash="dot"), legendgroup="fib",
                                     legendgrouptitle_text="FİBONACCI"), row=1, col=1)
    # --- Hacim ---
    fig.add_trace(go.Bar(x=x, y=df.Volume, name="Hacim (işlem adedi)", marker_color="#888888",
                         legendgroup="hacim", legendgrouptitle_text="HACİM"), row=2, col=1)
    # --- RSI ---
    fig.add_trace(go.Scatter(x=x, y=df.RSI, name="RSI (14)", line=dict(color="#c050ff", width=1.8),
                             legendgroup="rsi", legendgrouptitle_text="RSI"), row=3, col=1)
    fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[70, 70], name="70 çizgisi: aşırı alım",
                             line=dict(color="red", dash="dash"), legendgroup="rsi"), row=3, col=1)
    fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[30, 30], name="30 çizgisi: aşırı satım",
                             line=dict(color="limegreen", dash="dash"), legendgroup="rsi"), row=3, col=1)
    # --- MACD ---
    fig.add_trace(go.Bar(x=x, y=df.MACD_H, name="Histogram (MACD - Sinyal farkı)",
                         marker_color=["#2ca02c" if v >= 0 else "#d62728" for v in df.MACD_H],
                         legendgroup="macd", legendgrouptitle_text="MACD"), row=4, col=1)
    fig.add_trace(go.Scatter(x=x, y=df.MACD, name="MACD çizgisi (mavi)", line=dict(color="#3b6cff", width=1.6),
                             legendgroup="macd"), row=4, col=1)
    fig.add_trace(go.Scatter(x=x, y=df.MACD_S, name="Sinyal çizgisi (turuncu)", line=dict(color="orange", width=1.6),
                             legendgroup="macd"), row=4, col=1)
    # --- Stochastic ---
    fig.add_trace(go.Scatter(x=x, y=df.STOCH_K, name="%K (hızlı çizgi, açık mavi)", line=dict(color="#00bcd4", width=1.6),
                             legendgroup="stoch", legendgrouptitle_text="STOCHASTIC"), row=5, col=1)
    fig.add_trace(go.Scatter(x=x, y=df.STOCH_D, name="%D (yavaş çizgi, turuncu)", line=dict(color="orange", width=1.6),
                             legendgroup="stoch"), row=5, col=1)
    fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[80, 80], name="80 çizgisi: aşırı alım",
                             line=dict(color="red", dash="dash"), legendgroup="stoch"), row=5, col=1)
    fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[20, 20], name="20 çizgisi: aşırı satım",
                             line=dict(color="limegreen", dash="dash"), legendgroup="stoch"), row=5, col=1)
    # --- ADX ---
    fig.add_trace(go.Scatter(x=x, y=df.ADX, name="ADX (trend gücü, sarı)", line=dict(color="#f5d742", width=2.2),
                             legendgroup="adx", legendgrouptitle_text="ADX"), row=6, col=1)
    fig.add_trace(go.Scatter(x=x, y=df.DI_P, name="+DI (yükseliş gücü, yeşil)", line=dict(color="#2ca02c", width=1.3),
                             legendgroup="adx"), row=6, col=1)
    fig.add_trace(go.Scatter(x=x, y=df.DI_M, name="-DI (düşüş gücü, kırmızı)", line=dict(color="#d62728", width=1.3),
                             legendgroup="adx"), row=6, col=1)
    fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[25, 25], name="25 çizgisi: güçlü trend eşiği",
                             line=dict(color="gray", dash="dash"), legendgroup="adx"), row=6, col=1)
    # --- OBV ---
    fig.add_trace(go.Scatter(x=x, y=df.OBV, name="OBV (birikimli hacim)", line=dict(color="#00e5ff", width=1.8),
                             legendgroup="obv", legendgrouptitle_text="OBV"), row=7, col=1)
    fig.add_trace(go.Scatter(x=x, y=df.OBV_SMA, name="OBV 20 günlük ortalaması (turuncu)", line=dict(color="#ff9800", width=1.4),
                             legendgroup="obv"), row=7, col=1)
    # --- ATR ---
    fig.add_trace(go.Scatter(x=x, y=df.ATR, name="ATR (14) ₺ - ortalama günlük hareket", line=dict(color="#ff6ec7", width=1.8),
                             legendgroup="atr", legendgrouptitle_text="ATR"), row=8, col=1)
    fig.update_yaxes(title_text="Fiyat ₺", row=1, col=1)
    fig.update_yaxes(title_text="Hacim", row=2, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)
    fig.update_yaxes(title_text="Stoch.", range=[0, 100], row=5, col=1)
    fig.update_yaxes(title_text="ADX", row=6, col=1)
    fig.update_yaxes(title_text="OBV", row=7, col=1)
    fig.update_yaxes(title_text="ATR ₺", row=8, col=1)
    fig.update_layout(height=1500, xaxis_rangeslider_visible=False, margin=dict(t=20, b=10, r=10),
                      legend=dict(orientation="v", x=1.01, y=1, xanchor="left", groupclick="toggleitem"))
    return fig


# ---------- Arayüz ----------
st.title("📈 BIST Teknik Analiz")
tab1, tab2 = st.tabs(["Tek Hisse Analizi", "Gruplar & Tarayıcı"])

with tab1:
    c0, c1, c2, c3 = st.columns([1.5, 1.5, 1, 1])
    grup = c0.selectbox("Grup", ["Tüm hisseler"] + list(GRUPLAR))
    liste = HISSELER if grup == "Tüm hisseler" else GRUPLAR[grup]
    secim = c1.selectbox("Hisse", ["XU100 (Endeks)"] + liste,
                         index=(liste.index("THYAO") + 1) if "THYAO" in liste else 0)
    periyot = c2.selectbox("Periyot", ["6mo", "1y", "2y", "5y"], index=1)
    aralik = c3.selectbox("Aralık", ["1d", "1wk"], index=0)
    ozel = st.text_input("Listede olmayan hisse kodu (isteğe bağlı, örn: KRSTL)", "").strip().upper()
    if ozel:
        sembol = ozel.replace(".IS", "") + ".IS"
    else:
        sembol = "XU100.IS" if secim.startswith("XU100") else f"{secim}.IS"
    gos = st.multiselect("Grafikte göster", ["SMA20", "SMA50", "SMA200", "Bollinger", "Destek/Direnç", "Fibonacci"],
                         default=["SMA20", "SMA50", "Destek/Direnç"])

    df = veri_cek(sembol, periyot, aralik)
    if df.empty or len(df) < 30:
        st.error(f"{sembol} için veri alınamadı veya yetersiz. Hisse kodunu kontrol edin.")
    else:
        st.plotly_chart(grafik(df, gos), use_container_width=True)
        sig = sinyaller(df)
        s = skor(sig)
        genel = "AL eğilimi 🟢" if s >= 3 else "SAT eğilimi 🔴" if s <= -3 else "Nötr 🟡"
        son, onceki = df.Close.iloc[-1], df.Close.iloc[-2]
        m1, m2, m3 = st.columns(3)
        m1.metric(sembol, f"{son:,.2f} ₺", f"{(son / onceki - 1) * 100:+.2f}%")
        m2.metric("Genel Görünüm", genel)
        puanli = len([x for x in sig if x[0] not in ("ATR", "Fibonacci")])  # ATR ve Fibonacci bilgi amaçlıdır, puan vermez
        m3.metric(f"Skor (-{puanli} ile +{puanli})", s)
        st.dataframe(pd.DataFrame(sig, columns=["İndikatör", "Sinyal", "Açıklama"]),
                     hide_index=True, use_container_width=True)
        with st.expander("Destek / Direnç ve Fibonacci seviyeleri (son 120 bar)", expanded=True):
            destek, direnc = seviyeler(df)
            lv, yuk, ust, alt = fibonacci(df)
            a1, a2 = st.columns(2)
            a1.markdown("**Destek / Direnç**")
            a1.dataframe(pd.DataFrame(
                [("Direnç", round(v, 2), t, f"{(v / son - 1) * 100:+.1f}%") for v, t in reversed(direnc)] +
                [("Destek", round(v, 2), t, f"{(v / son - 1) * 100:+.1f}%") for v, t in destek],
                columns=["Tür", "Seviye ₺", "Temas", "Fiyata uzaklık"]), hide_index=True, use_container_width=True)
            a2.markdown(f"**Fibonacci** (son dalga: {'yükseliş' if yuk else 'düşüş'}, tepe {ust:.2f} / dip {alt:.2f})")
            a2.dataframe(pd.DataFrame([(f"%{o * 100:.1f}", round(v, 2)) for o, v in lv.items()],
                                      columns=["Oran", "Seviye ₺"]), hide_index=True, use_container_width=True)

with tab2:
    st.subheader("Hisse grupları")
    with st.expander("Hangi grupta hangi hisseler var?", expanded=False):
        st.dataframe(pd.DataFrame({"Grup": list(GRUPLAR),
                                   "Hisseler": [", ".join(v) for v in GRUPLAR.values()],
                                   "Adet": [len(v) for v in GRUPLAR.values()]}),
                     hide_index=True, use_container_width=True)

    g2 = st.selectbox("Taranacak grup", ["Tüm hisseler"] + list(GRUPLAR), key="g2")
    tarama = HISSELER if g2 == "Tüm hisseler" else GRUPLAR[g2]
    st.caption(f"{len(tarama)} hisse: " + ", ".join(tarama))
    ekstra = st.text_area("Taramaya ek hisse kodları (isteğe bağlı, boşlukla ayırın)", "").upper().replace(",", " ").split()
    tarama = list(dict.fromkeys(tarama + [k.replace(".IS", "") for k in ekstra]))
    if st.button("Taramayı Başlat"):
        with st.spinner(f"{len(tarama)} hisse indiriliyor (büyük listelerde 1-3 dk sürebilir)..."):
            veriler = toplu_veri(tuple(tarama))
        satirlar = []
        for h, d in veriler.items():
            sg = sinyaller(d)
            satirlar.append({"Hisse": h, "Sektör": SEKTOR.get(h, "-"),
                             "Fiyat": round(d.Close.iloc[-1], 2),
                             "Günlük %": round((d.Close.iloc[-1] / d.Close.iloc[-2] - 1) * 100, 2),
                             "RSI": round(d.RSI.iloc[-1], 1), "Skor": skor(sg)})
        atlanan = [h for h in tarama if h not in veriler]
        if satirlar:
            tablo = pd.DataFrame(satirlar).sort_values("Skor", ascending=False)
            st.markdown(f"**Hisse bazında sonuçlar** ({len(tablo)} hisse, skora göre sıralı)")
            st.dataframe(tablo, hide_index=True, use_container_width=True)
            ozet = (tablo.groupby("Sektör").agg(Hisse_Adedi=("Hisse", "count"),
                                                Ort_Günlük_Yüzde=("Günlük %", "mean"),
                                                Ort_Skor=("Skor", "mean"))
                    .round(2).sort_values("Ort_Skor", ascending=False).reset_index())
            st.markdown("**Sektör/grup özeti** (hangi grup güçlü, hangisi zayıf)")
            st.dataframe(ozet, hide_index=True, use_container_width=True)
            if atlanan:
                st.caption(f"Veri alınamayan/atlanan {len(atlanan)} kod: " + ", ".join(atlanan))
        else:
            st.warning("Veri alınamadı. İnternet bağlantınızı kontrol edin.")

st.caption("Veriler Yahoo Finance kaynaklıdır ve gecikmeli olabilir. Yatırım tavsiyesi değildir.")
