#Author: @demavrin
# GitHub: https://github.com/@demavrin

from decimal import Decimal, InvalidOperation


def _ondaliga_cevir(deger, alan_adi):
    """Girilen değeri Decimal sayısına çevirir ve geçerliliğini kontrol eder."""
    try:
        sayi = Decimal(str(deger).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{alan_adi} geçerli bir sayı olmalıdır.")

    if not sayi.is_finite():
        raise ValueError(f"{alan_adi} sonlu bir sayı olmalıdır.")

    return sayi


def fiyat_hesapla(hedef_fiyat, promosyonlar):
    """
    İndirimler uygulandıktan sonra istenen fiyata ulaşmak için
    gereken başlangıç fiyatını hesaplar.

    Toplamsal indirimleri birleştirir.
    Ardışık indirimleri sırayla uygular.
    """
    hedef = _ondaliga_cevir(hedef_fiyat, "Hedef fiyat")

    if hedef <= 0:
        raise ValueError("Hedef fiyat sıfırdan büyük olmalıdır.")

    toplamsal_indirim = Decimal("0")
    ardisik_carpan = Decimal("1")

    for promosyon in promosyonlar:
        ad = str(promosyon.get("name", "Promosyon")).strip() or "Promosyon"
        indirim = _ondaliga_cevir(
            promosyon.get("discount", 0),
            f"{ad} indirimi",
        )
        mod = promosyon.get("mode")

        if indirim < 0 or indirim >= 100:
            raise ValueError(
                f"{ad} indirimi 0 veya daha büyük, 100'den küçük olmalıdır."
            )

        if mod == "Toplamsal":
            toplamsal_indirim += indirim
        elif mod == "Ardışık":
            ardisik_carpan *= (
                    Decimal("1") - indirim / Decimal("100")
            )
        else:
            raise ValueError(
                f"{ad} için indirim türü Toplamsal veya Ardışık olmalıdır."
            )

    if toplamsal_indirim >= 100:
        raise ValueError("Toplam toplamsal indirim %100'den küçük olmalıdır.")

    toplamsal_carpan = (
            Decimal("1") - toplamsal_indirim / Decimal("100")
    )
    toplam_carpan = toplamsal_carpan * ardisik_carpan

    baslangic_fiyati = hedef / toplam_carpan
    gercek_indirim = (Decimal("1") - toplam_carpan) * Decimal("100")

    return {
        "target_price": hedef.quantize(Decimal("0.01")),
        "original_price": baslangic_fiyati.quantize(Decimal("0.01")),
        "effective_discount": gercek_indirim.quantize(Decimal("0.01")),
    }